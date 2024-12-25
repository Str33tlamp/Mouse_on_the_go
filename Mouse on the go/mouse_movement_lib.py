import time
import threading
from pynput.mouse import Controller as MouseController, Button
from pynput.keyboard import Controller as KeyboardController, Key
import re
class MouseHandler:
        
    def __init__(self, sensitivity=2, scroll_sensitivity = 1, delay=0.01):
        self.mousecontroller = MouseController()
        self.keyboardcontroller = KeyboardController()
        self.sensitivity = sensitivity
        self.scroll_sensitivity = scroll_sensitivity
        self.delay = delay
        self.action_threads = {}
        self.action_running = {}
        self.valid_scripts = {}
    def set_sensitivity(self, new_sensitivity):
        self.sensitivity = new_sensitivity

    def move_up(self):
        while self.action_running.get("Up", False):
            self.mousecontroller.move(0, -self.sensitivity)
            time.sleep(self.delay)

    def move_down(self):
        while self.action_running.get("Down", False):
            self.mousecontroller.move(0, self.sensitivity)
            time.sleep(self.delay)

    def move_left(self):
        while self.action_running.get("Left", False):
            self.mousecontroller.move(-self.sensitivity, 0)
            time.sleep(self.delay)

    def move_right(self):
        while self.action_running.get("Right", False):
            self.mousecontroller.move(self.sensitivity, 0)
            time.sleep(self.delay)

    def press_button(self, button):
        self.mousecontroller.press(button)

    def release_button(self, button):
        self.mousecontroller.release(button)

    def scroll_up(self):
        while self.action_running.get("ScrollUp", False):
            self.mousecontroller.scroll(0, self.scroll_sensitivity)  # Scroll up
            time.sleep(self.delay*2)

    def scroll_down(self):
        while self.action_running.get("ScrollDown", False):
            self.mousecontroller.scroll(0, -self.scroll_sensitivity)  # Scroll down
            time.sleep(self.delay)

    def start_action(self, action_name):
        """Start an action in a separate thread if not already running."""
        if action_name not in self.action_running or not self.action_running[action_name]:
            self.action_running[action_name] = True

            if action_name in ["LMB", "RMB", "MMB", "Mouse4", "Mouse5"]:
                self.press_button_by_name(action_name)  # Execute press directly
            else:
                action_method = self.get_action_method(action_name)
                if action_method:
                    self.action_threads[action_name] = threading.Thread(target=action_method)
                    self.action_threads[action_name].start()

    def stop_action(self, action_name):
        """Stop an action by setting its running state to False."""
        if action_name in self.action_running:
            self.action_running[action_name] = False

            if action_name in ["LMB", "RMB", "MMB", "Mouse4", "Mouse5"]:
                self.release_button_by_name(action_name)
            elif action_name not in ["LMB", "RMB", "MMB", "Mouse4", "Mouse5"]:
                if action_name in self.action_threads:
                    self.action_threads[action_name].join()

    def cancel_all_movements(self):
        """Cancel all movements and stop all ongoing actions."""
        all_actions = ["Up", "Down", "Left", "Right", "ScrollUp", "ScrollDown"]
    
        for action in all_actions:
            self.stop_action(action)
    
        button_actions = ["LMB", "RMB", "MMB", "Mouse4", "Mouse5"]
        for button in button_actions:
            self.stop_action(button)
        
    def press_button_by_name(self, action_name):
        """Press the appropriate mouse button based on the action name."""
        button_map = {
            "LMB": Button.left,
            "RMB": Button.right,
            "MMB": Button.middle,
            "Mouse4": Button.x1,
            "Mouse5": Button.x2
        }
        if action_name in button_map:
            self.press_button(button_map[action_name])

    def release_button_by_name(self, action_name):
        button_map = {
            "LMB": Button.left,
            "RMB": Button.right,
            "MMB": Button.middle,
            "Mouse4": Button.x1,
            "Mouse5": Button.x2
        }
        if action_name in button_map:
            self.release_button(button_map[action_name])

    def get_action_method(self, action_name):
        action_map = {
            "Up": self.move_up,
            "Down": self.move_down,
            "Left": self.move_left,
            "Right": self.move_right,
            "ScrollUp": self.scroll_up,
            "ScrollDown": self.scroll_down
        }
        return action_map.get(action_name, None)

        
    def process_message(self, message):
        if message.startswith("start_"):
            action_name = message.split("_", 1)[1]
            self.start_action(action_name)  # Start action
        elif message.startswith("stop_"):
            action_name = message.split("_", 1)[1]
            self.stop_action(action_name)  # Stop action
        elif message.startswith("set_sensitivity_"):
            try:
                new_sensitivity = int(message.split("_", 1)[1])
                self.set_sensitivity(new_sensitivity)
            except ValueError:
                pass
        elif message.startswith("reset"):
            self.cancel_all_movements()
        elif message.startswith("run_macro_"):
            macro_name = message.split("_", 2)[2]
            if macro_name in self.valid_scripts:
                self.run_script(self.valid_scripts[macro_name])
            else:
                return
                #print(f"Macro '{macro_name}' has not been validated.")

class MacroHandler:
    def __init__(self, sensitivity=2, scroll_sensitivity = 1, delay=0.01):
        self.mousecontroller = MouseController()
        self.keyboardcontroller = KeyboardController()
        self.sensitivity = sensitivity
        self.scroll_sensitivity = scroll_sensitivity
        self.delay = delay
        self.action_threads = {}
        self.action_running = {}
        self.valid_scripts = {}
    def validate_input(self, macro_name, macro):
        valid_macro_pattern = (
            r"^(?:"  
            r"[a-z]|" 
            r"TIMER\(\d+(\.\d+)?\)|"  
            r"LMB\((down|up)\)|"  
            r"RMB\((down|up)\)|"  
            r"SCROLL\(-?\d+\)|"  
            r"UP\(\d+(\.\d+)?\)|"  
            r"DOWN\(\d+(\.\d+)?\)|" 
            r"LEFT\(\d+(\.\d+)?\)|"  
            r"RIGHT\(\d+(\.\d+)?\)|"  
            r"' '|"  
            r"SHIFT\((down|up)\)|"  
            r"CTRL\((down|up)\)|"
            r"ALT\((down|up)\)|"
            r" |"
            r"\+)+" 
        )
        
        if re.fullmatch(valid_macro_pattern, macro):
            button_state = {"LMB": False, "RMB": False, "SHIFT": False, "CTRL": False, "ALT": False} 
            commands = macro.split("+")
            for command in commands:
                command = command.strip()
                
                if command == "' '":
                    continue
                elif command.startswith("LMB") or command.startswith("RMB"):
                    button_name = "LMB" if "LMB" in command else "RMB"
                    action = re.search(rf"{button_name}\((down|up)\)", command).group(1)
                    
                    if action == "down" and button_state[button_name]:
                        print(f"Некорректный макрос: {button_name} уже нажата.")
                        return False
                    elif action == "up" and not button_state[button_name]:
                        print(f"Invalid macro: {button_name} already up.")
                        return False
                    button_state[button_name] = action == "down"
                elif command.startswith("SHIFT"):
                    action = re.search(r"SHIFT\((down|up)\)", command).group(1)
                    if action == "down" and button_state["SHIFT"]:
                        print("Invalid macro: SHIFT already down.")
                        return False
                    elif action == "up" and not button_state["SHIFT"]:
                        print("Invalid macro: SHIFT already up.")
                        return False
                    button_state["SHIFT"] = action == "down"
                elif command.startswith("CTRL"):
                    action = re.search(r"CTRL\((down|up)\)", command).group(1)
                    if action == "down" and button_state["CTRL"]:
                        print("Invalid macro: CTRL already down.")
                        return False
                    elif action == "up" and not button_state["CTRL"]:
                        print("Invalid macro: CTRL already up.")
                        return False
                    button_state["CTRL"] = action == "down"
                elif command.startswith("ALT"):
                    action = re.search(r"ALT\((down|up)\)", command).group(1)
                    if action == "down" and button_state["ALT"]:
                        print("Invalid macro: ALT already down.")
                        return False
                    elif action == "up" and not button_state["ALT"]:
                        print("Invalid macro: ALT already up.")
                        return False
                    button_state["ALT"] = action == "down"
            self.valid_scripts[macro_name] = macro
            return True
        else:
            print("Invalid macro format.")
            return False

    def get_macros_array(self):
        return list(self.valid_scripts.keys())
    

    def run_script(self, macro):
        commands = macro.split("+")
        for command in commands:
            command = command.strip()

            if command == "' '":  
                self.keyboardcontroller.press(Key.space)
                self.keyboardcontroller.release(Key.space)
            elif re.match(r"[a-z]", command): 
                self.keyboardcontroller.press(command)
                self.keyboardcontroller.release(command)
            elif command.startswith("TIMER"):
                timer_value = float(re.search(r"TIMER\((\d+(\.\d+)?)\)", command).group(1))
                time.sleep(timer_value)
            elif command.startswith("LMB"):
                if "down" in command:
                    self.press_button(Button.left)
                elif "up" in command:
                    self.release_button(Button.left)
            elif command.startswith("RMB"):
                if "down" in command:
                    self.press_button(Button.right)
                elif "up" in command:
                    self.release_button(Button.right)
            elif command.startswith("SHIFT"):
                if "down" in command:
                    self.keyboardcontroller.press(Key.shift)
                elif "up" in command:
                    self.keyboardcontroller.release(Key.shift)
            elif command.startswith("ALT"):
                if "down" in command:
                    self.keyboardcontroller.press(Key.alt)
                elif "up" in command:
                    self.keyboardcontroller.release(Key.alt)
            elif command.startswith("CTRL"):
                if "down" in command:
                    self.keyboardcontroller.press(Key.ctrl)
                elif "up" in command:
                    self.keyboardcontroller.release(Key.ctrl)
            elif command.startswith("scroll"):
                scroll_amount = int(re.search(r"scroll\((-?\d+)\)", command).group(1))
                self.mousecontroller.scroll(0, scroll_amount)
            elif command.startswith(("UP", "DOWN", "LEFT", "RIGHT")):
                self.run_mouse_movement_in_thread(command)
            
    def run_mouse_movement_in_thread(self, command):
        direction_map = {
            "UP": (0, -self.sensitivity),
            "DOWN": (0, self.sensitivity),
            "LEFT": (-self.sensitivity, 0),
            "RIGHT": (self.sensitivity, 0)
        }
        match = re.match(r"(UP|DOWN|LEFT|RIGHT)\((\d+(\.\d+)?)\)", command)
        if match:
            direction, duration = match.group(1), float(match.group(2))
            dx, dy = direction_map[direction]
            
            def move_mouse():
                end_time = time.time() + duration
                while time.time() < end_time:
                    self.mousecontroller.move(dx, dy)
                    time.sleep(self.delay)
            
            threading.Thread(target=move_mouse, daemon=True).start()

    def delete_macro(self, macro_name):
        if macro_name in self.valid_scripts:
                del self.valid_scripts[macro_name]  # Remove the macro
                return True
        return False
