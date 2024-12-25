import sys
from server_lib import ServerHandler, get_local_ip

class UserConsole:
    def __init__(self):
        self.server_handler = ServerHandler()  # Create an instance of the server handler

    def print_menu(self):
        print("\n--- Пользовательские комманды ---")
        print("1.  server_start - Запускает сервер принятия нажатий")
        print("2.  server_stop - Приостанавливает сервер")
        print("3.  ip_change - Позволяет изменить IP, на котором запускается сервер")
        print("4.  port_change - Позволяет изменить порт, на котором запускается сервер")
        print("5.  set_sensitivity - Позволяет установить чувствительность мыши")
        #print("6.  toggle_debug - Выводит получаемые от телефона сигналы в консоль")
        print("6.  view_socket - Выводит используемые IP и порт") 
        print("7.  get_current_ip - Выводит IP в локальной сети")
        print("8.  reset - Отменяет все выполняющиеся деяствия мыши")
        print("9.  get_macros_list - Выводит список сохраненных макросов")
        print("10. create_macro - Позволяет создать макрос")
        print("11. delete_macro - Позволяет удалить макрос")
        print("12. exit - Закрывает приложение")
        print("---------------------")

    def is_valid_ip(self, ip):
        parts = ip.split('.')
        if len(parts) == 4:
            try:
                return all(0 <= int(part) <= 255 for part in parts)
            except ValueError:
                return False
        return False
    
    def is_valid_port(self, port):
        return (1024 <= port <= 65535)
    
    def change_ip(self):
        new_ip = input("Введите новый IPv4 адрес: ")
        if self.is_valid_ip(new_ip):
            self.server_handler.update_ip_and_port(new_ip, self.server_handler.port)
        else:
            print("Неправильный формат адреса, попробуйте снова")

    def change_port(self):
        new_port = int(input("Введите новый порт: "))
        if self.is_valid_port(new_port):
            self.server_handler.update_ip_and_port(self.server_handler.host, new_port)
        else:
            print("Неправильный формат порта, попробуйте снова")
            
    def macro_creation(self):
        macro_name = input("Введите название макроса:")
        if macro_name == '':
            print('Название не может быть пустым')
            return
        if macro_name in self.server_handler.get_macros_array():
            print("Макрос с таким именем уже существует")
            return
        macro = input("Введите макрос:")
        self.server_handler.create_macro(macro_name, macro)
            
    def delete_macro(self):
        name = input('Введите название макорса:')
        if self.server_handler.delete_macro(name):
            print('Макрос успешно удален')
        else:
            print('Не удалось найти макрос')
            
    def change_sensitivity(self):
        try:
            new_sensitivity = int(input("Введите новую чувствительность(по умолчанию значение 2): "))
            self.server_handler.mouse_handler.set_sensitivity(new_sensitivity)
        except ValueError:
            print("Не удалось установить чувствительность, попробуйте снова")

    def toggle_debug_mode(self):
        self.server_handler.debug = not self.server_handler.debug
        print(f"Режим отладки {'включен' if self.server_handler.debug else 'отключен'}")

    def print_socket(self):
        print(f"Используемый IP: {self.server_handler.host}\nИспользуемый порт:{self.server_handler.port}")

    def run(self):
        print("Добро пожаловать в приложение Mouse on the Go. Введите help для получения списка комманд")
        while True:
            choice = input()
            match(choice):
                case('help'):
                    self.print_menu()
                case('server_start'):
                    self.server_handler.start_server()
                case('server_stop'):
                    self.server_handler.stop_server()
                case('ip_change'):
                    self.change_ip()
                case('port_change'):
                    self.change_port()
                case('set_sensitivity'):
                    self.change_sensitivity()
                #case('toggle_debug'):
                    #self.toggle_debug_mode()
                case('view_socket'):
                    self.print_socket()
                case('exit'):
                    self.server_handler.stop_server()
                    break
                case('get_current_ip'):
                    print(f"IP в локальной сети: {get_local_ip()}")
                case('reset'):
                    self.server_handler.movement_cancel()
                    print("Мышь остановлена")
                case('get_macros_list'):
                    print('Cписок названий макросов:', *self.server_handler.get_macros_array(), sep = '\n')
                case('create_macro'):
                     self.macro_creation()
                case('delete_macro'):
                    self.delete_macro()
                case _:
                    print('Неизвестная комманда. Чтобы получить список комманд введите help')
                    
                

            
if __name__ == "__main__":
    console = UserConsole()
    console.run()
