import socket
import threading
from mouse_movement_lib import MouseHandler  # Import the MouseHandler class
from mouse_movement_lib import MacroHandler  # Import the MacroHandler class

def get_local_ip():
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(("8.8.8.8", 80))
            return s.getsockname()[0]
    except Exception as e:
        return "0.0.0.0"
    
class ServerHandler:
    def __init__(self, host=get_local_ip(), port=12345):
        self.host = host
        self.port = port
        self.running = False
        self.server_socket = None
        self.mouse_handler = MouseHandler()  # Create an instance of the MouseHandler class
        self.macro_handler = MacroHandler()  # Create an instance of the MacroHandler class

    def movement_cancel(self):
        self.mouse_handler.process_message('reset')
        
    def start_server(self):
        if self.running:
            print("Сервер уже запущен")
            return
        if self.is_port_available(self.host, self.port):
            self.running = True
            print(f"Сервер запущен на {self.host}:{self.port}")

            # Start the server in a new thread to avoid blocking
            self.server_thread = threading.Thread(target=self._server_loop)
            self.server_thread.daemon = True  # Make the thread a daemon so it exits when the main program exits
            self.server_thread.start()
        else:
            print(f'Не удалось запустить сервер на IP {self.host}, порте {self.port}. Пожалуйста, введите другие')

    def stop_server(self):
        if not self.running:
            print("Сервер не запущен")
            return
        self.running = False
        print("Сервер был приостановлен")
        if self.server_socket:
            self.server_socket.close()
            self.server_socket = None  # Ensure that the socket is reset after closing
        if hasattr(self, 'server_thread') and self.server_thread.is_alive():
            self.server_thread.join()  # Ensure the server thread is properly stopped

    def _server_loop(self):
        try:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # Allow reusing the port
            self.server_socket.bind((self.host, self.port))
            while self.running:
                try:
                    message, address = self.server_socket.recvfrom(1024)
                    message = message.decode('utf-8')
                    if message == "request_list":
                        self.send_response(address, self.macro_handler.get_macros_array())
                    elif message == "ping":
                        self.server_socket.sendto("pong".encode('utf-8'), address)
                    else:
                        self.process_message(message)
                except Exception as e:
                    try:
                        self.server_socket.close()
                    except Exception as e2:
                        e2 = e2
                    self.server_socket = None
                    if self.running:
                        self.running = False
        except Exception:
            self.running = False
            raise

    def send_response(self, client_address, response=[]):
        try:
            response = ",".join(response).encode('utf-8')  # Handles empty lists too
            self.server_socket.sendto(response, client_address)
        except Exception as e:
            print(e)
            
    def create_macro(self, macro_name, macro):
        if self.macro_handler.validate_input(macro_name, macro):
            print(f"Макрос {macro_name} прошел валидацию и был сохранен.")
            self.stop_server()
            self.start_server()
        else:
            print(f"Макрос {macro_name} не прошел валидацию, попробуйте снова.")
            
    def run_macro(self, macro_name):
        self.macro_handler.run_script(macro_name)

    def delete_macro(self, macro_name):
        if self.macro_handler.delete_macro(macro_name):
            self.stop_server()
            self.start_server()
            return True
        else:
            return False

    def get_macros_array(self):
        return self.macro_handler.get_macros_array()
    
    def process_message(self, message):
        if message.startswith("start_") or message.startswith("stop_") or message.startswith("set_sensitivity_") or message == "reset":
            self.mouse_handler.process_message(message)
        elif message.startswith("run_macro_"):
            macro_name = message.split("_", 2)[2]
            self.run_macro(macro_name)

    def is_port_available(self, host, port):
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as temp_socket:
            try:
                temp_socket.bind((host, port))
                return True
            except OSError as e:
                print(f"Порт {port} на {host} недоступен: {e}")
                return False
        
    def update_ip_and_port(self, new_host, new_port):
        if self.is_port_available(new_host, new_port):
            self.stop_server()
            old_host = self.host
            old_port = self.port
            self.host = new_host
            self.port = new_port
            self.start_server()
            print(f"Сервер обновлен на IP {self.host} и порт {self.port}")
        else:
            print(f"Не удалось запустить сервер на IP {new_host} и порте {new_port}, возврат на {self.host}, {self.port}")
