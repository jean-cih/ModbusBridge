from pymodbus.client import ModbusTcpClient, ModbusSerialClient
from pymodbus.exceptions import ModbusException
import serial
import struct
import serial.tools.list_ports
import socket
import psutil


class PyModbusClientTCP:
    def __init__(self, host, port=502):
        self.host = host
        self.port = port
        self.client = None

    def connect(self):
        try:
            self.client = ModbusTcpClient(host=self.host, port=self.port)
            result = self.client.connect()
            if not result:
                raise ModbusException(f"Не удалось подключиться к {self.host}:{self.port}")

            print(f"Успешное подключение к {self.host}:{self.port}")
            return True
        except Exception as e:
            print(f"Ошибка подключения: {e}")
            return False

    def is_connected(self):
        if self.client is None:
            return False
        try:
            return self.client.is_socket_open()
        except Exception as e:
            print(f"Error: {e}")
            return False

    def read_int(self, slave_id, address, count=2):
        if not self.is_connected():
            print("Нет соединения")
            return False, None

        try:
            result = self.client.read_holding_registers(address=address, count=count,
                                                        device_id=slave_id)

            if result.isError():
                raise ModbusException(f"Ошибка чтения регистров: {result}")

            value_int = result.registers[1] << 16 | result.registers[0]
            return True, value_int

        except Exception as e:
            print(f"Error: {e}")
            return False, None

    def read_float(self, slave_id, address, count=2):
        if not self.is_connected():
            print("Нет соединения")
            return False, None

        try:
            result = self.client.read_holding_registers(address=address,count=count,
                                                        device_id=slave_id)

            if result.isError():
                raise ModbusException(f"Ошибка чтения регистров: {result}")

            value_float = struct.unpack('f', struct.pack('>HH', result.registers[1],
                                                         result.registers[0]))[0]
            return True, value_float

        except Exception as e:
            print(f"Error: {e}")
            return False, None

    def write_int(self, slave_id, address, value_int):
        if not self.is_connected():
            print("Нет соединения")
            return False

        try:
            registers = [(value_int & 0xFFFF), (value_int >> 16) & 0xFFFF]
            result = self.client.write_registers(address=address, values=registers,
                                                 device_id=slave_id)

            if result.isError():
                raise ModbusException(f"Ошибка записи регистров: {result}")
            return True

        except Exception as e:
            print(f"Error: {e}")
            return False

    def write_float(self, slave_id, address, value_float):
        if not self.is_connected():
            print("Нет соединения")
            return False

        try:
            float_bytes = struct.pack('f', value_float)
            registers = [struct.unpack('>H', float_bytes[2:4])[0],
                         struct.unpack('>H', float_bytes[0:2])[0]]
            result = self.client.write_registers(address=address, values=registers,
                                                 device_id=slave_id)

            if result.isError():
                raise ModbusException(f"Ошибка записи регистров: {result}")
            return True

        except Exception as e:
            print(f"Error: {e}")
            return False

    def disconnect(self):
        try:
            if self.is_connected():
                self.client.close()
                print("Соединение закрыто")
        except Exception as e:
            print(f"Ошибка закрытия: {e}")


class PyModbusClientRTU:
    def __inti__(self, port='COM4', baudrate=9600, bytesize=8, parity='N', stopbits=1):
        self.port = port
        self.baudrate = baudrate
        self.bytesize = bytesize
        self.parity = parity
        self.stopbits = stopbits
        self.client = None

    def connect(self):
        try:
            self.client = ModbusSerialClient(port=self.port, baudrate=self.baudrate,
                                             bytesize=self.bytesize, parity=self.parity,
                                             stopbits=self.stopbits)
            result = self.client.connect()
            if not result:
                raise serial.SerialException(f"Ощибка подключенияпо к порту {self.port}")

            print(f"Успешное подключение по {self.port}")
            return True
        except serial.SerialException as e:
            print(f"Error: {e}")
            return False
        except Exception as e:
            print(f"Error: {e}")
            return False

    def is_connected(self, address, slave_id):
        if self.client is None:
            return False

        try:
            result = self.client.read_holding_registers(address=address, count=1, device_id=slave_id)
            return not result.isError()

        except Exception as e:
            print(f"Error: {e}")
            return False

    def read_int(self, slave_id, address, count=2):
        if not self.is_connected():
            print("Нет соединения")
            return False, None

        try:
            result = self.client.read_holding_registers(address=address, count=count,
                                                        device_id=slave_id)

            if result.isError():
                raise ModbusException(f"Ошибка чтения регистров: {result}")

            value_int = result.registers[1] << 16 | result.registers[0]
            return True, value_int

        except Exception as e:
            print(f"Error: {e}")
            return False, None

    def read_float(self, slave_id, address, count=2):
        if not self.is_connected():
            print("Нет соединения")
            return False, None

        try:
            result = self.client.read_holding_registers(address=address, count=count,
                                                        device_id=slave_id)

            if result.isError():
                raise ModbusException(f"Ошибка чтения регистров: {result}")

            value_float = struct.unpack('f', struct.pack('>HH', result.registers[1],
                                                         result.registers[0]))[0]
            return True, value_float

        except Exception as e:
            print(f"Error: {e}")
            return False, None

    def write_int(self, slave_id, address, value_int):
        if not self.is_connected():
            print("Нет соединения")
            return False

        try:
            registers = [(value_int & 0xFFFF), (value_int >> 16) & 0xFFFF]
            result = self.client.write_registers(address=address, values=registers,
                                                 device_id=slave_id)

            if result.isError():
                raise ModbusException(f"Ошибка записи регистров: {result}")
            return True

        except Exception as e:
            print(f"Error: {e}")
            return False

    def write_float(self, slave_id, address, value_float):
        if not self.is_connected():
            print("Нет соединения")
            return False

        try:
            float_bytes = struct.pack('f', value_float)
            registers = [struct.unpack('>H', float_bytes[2:4])[0],
                         struct.unpack('>H', float_bytes[0:2])[0]]
            result = self.client.write_registers(address=address, values=registers,
                                                 device_id=slave_id)

            if result.isError():
                raise ModbusException(f"Ошибка записи регистров: {result}")
            return True

        except Exception as e:
            print(f"Error: {e}")
            return False

    def disconnect(self):
        try:
            if self.is_connected():
                self.client.close()
                print("Соединение закрыто")
        except Exception as e:
            print(f"Ошибка закрытия: {e}")


class GetInfo:
    def get_ports_info(self):
        try:
            ports = serial.tools.list_ports.comports()

            port_names = [port.name for port in ports]
            if not port_names:
                print(" - COM порты не найдены - ")
            else:
                print(f"- Доступно портов для Modbus RTU: {len(port_names)} - {port_names} - ")

            return port_names

        except Exception as e:
            print(f" - Ошибка опроса COM портов: {e} - ")
            return []


    def get_port_settings(self, port_name):
        try:
            with serial.Serial(port_name) as ser:
                settings = {
                    'name': port_name,
                    'baudrate': ser.baudrate,
                    'bytesize': ser.bytesize,
                    'parity': ser.parity,
                    'stopbits': ser.stopbits,
                    'timeout': ser.timeout,
                    'xonxoff': ser.xonxoff,
                    'rtscts': ser.rtscts,
                    'dsrdtr': ser.dsrdtr
                }
                return settings

        except Exception as e:
            print(f" - Ошибка получения настроек порта {port_name}: {e} - ")
            return None

    def get_network_interfaces(self):
        interfaces = list(psutil.net_if_addrs().keys())
        if not interfaces:
            print(" - Сетевые интерфейсы не найдены - ")
        else:
            print(f"- Доступные сетевые интерфейсы: {interfaces} -")
        return interfaces

    def get_interface_addresses(self, interface_name):
        try:
            interface_info = psutil.net_if_addrs().get(interface_name)
            if not interface_info:
                print(f" - Информация об интерфейсе {interface_name} не найдена -")
                return None

            for addr in interface_info:
                if addr.family == socket.AF_INET:
                    return {
                        'interface': interface_name,
                        'ip_address': addr.address,
                        'netmask': addr.netmask,
                        'broadcast': addr.broadcast,
                    }

            print(f" - IPv4 адреса не найдены для интерфейса {interface_name} -")
            return None

        except Exception as e:
            print(f" - Ошибка получения информации об адресах для интерфейса {interface_name}: {e} - ")
            return None

    def check_ethernet_connection(self, host, port, timeout=2):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(timeout)
            sock.connect((host, port))
            sock.close()
            print(f" - Проверка соединения к {host}:{port} прошла успешно - ")
            return True
        except Exception as e:
            print(f" - Не удалось подключиться к {host}:{port}: {e} - ")
            return False


if __name__ == "__main__":
    print("\n === Программа для работы с протоколами Modbus TCP/RTU === \n")

    mb_protocol = input("С каким протоколом нужно работать tcp/rtu: ").strip()
    if mb_protocol == '1':
        info = GetInfo()
        for interface in info.get_network_interfaces():
            print(info.get_interface_addresses(interface))
        info.check_ethernet_connection("127.0.0.1", 502)
    elif mb_protocol == '2':
        info = GetInfo()
        for port_name in info.get_ports_info():
            print(info.get_port_settings(port_name))
    else:
        print("Пока есть поддержка только двух протоколов...")

    print("\n == Программа успешно завершилась == ")


