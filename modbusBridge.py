from pymodbus.client import ModbusTcpClient, ModbusSerialClient
from pymodbus.exceptions import ModbusException
import serial
import struct
import serial.tools.list_ports
import socket
import psutil
from registers import registers_sensor_MB210_101, registers_sensor_TPM10
from devices import devices
from typing import Tuple, Optional, List, Dict, NewType, Any

SlaveID = NewType('SlaveID', int)
ModbusAddress = NewType('ModbusAddress', int)

class ModbusBaseClient:
    """Базовый класс для Modbus клиентов"""

    def _validate_slave_id(self, slave_id: int) -> SlaveID:
        if not 0 <= slave_id <= 247:
            raise ValueError(f"slave_id должен быть в диапазоне 0-247, получено: {slave_id}")
        return SlaveID(slave_id)

    def _validate_address(self, address: int) -> ModbusAddress:
        if not 0 <= address <= 65535:
            raise ValueError(f"address должен быть в диапазоне 0-65535, получено: {address}")
        return ModbusAddress(address)

    def _read_registers(self, slave_id: int, address: int, count: int = 2) -> Tuple[bool, Optional[List[int]]]:
        """Базовый метод чтения регистров"""
        if not self.is_connected():
            print("Нет соединения")
            return False, None

        try:
            valid_slave_id = self._validate_slave_id(slave_id)
            valid_address = self._validate_address(address)

            result = self.client.read_holding_registers(
                address=valid_address,
                count=count,
                device_id=valid_slave_id
            )

            if result.isError():
                raise ModbusException(f"Ошибка чтения регистров: {result}")

            return True, result.registers

        except Exception as e:
            print(f"Ошибка чтения: {e}")
            return False, None

    def _write_registers(self, slave_id: int, address: int, registers: Optional[List[int]]) -> bool:
        """Базовый метод записи регистров"""
        if not self.is_connected():
            print("Нет соединения")
            return False

        try:
            valid_slave_id = self._validate_slave_id(slave_id)
            valid_address = self._validate_address(address)

            result = self.client.write_registers(
                address=valid_address,
                values=registers,
                device_id=valid_slave_id
            )

            if result.isError():
                raise ModbusException(f"Ошибка записи регистров: {result}")
            return True

        except Exception as e:
            print(f"Ошибка записи: {e}")
            return False


class PyModbusClientTCP(ModbusBaseClient):
    """Клиент Modbus TCP"""

    def __init__(self, host, port=502):
        self.host = host
        self.port = port
        self.client = None

    def connect(self) -> bool:
        """Установка соединения"""
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

    def is_connected(self) -> bool:
        """Проверка соединения"""
        if self.client is None:
            return False

        try:
            return self.client.is_socket_open()
        except Exception as e:
            print(f"Ошибка проверки соединения: {e}")
            return False

    def read_int(self, slave_id: int, address: int, count: int = 2) -> Tuple[bool, Optional[int | None]]:
        """Чтение целочисленного значения"""
        success, registers = self._read_registers(slave_id, address, count)

        if not success or registers is None:
            return False, None

        value_int = 0
        for i in range(count):
            value_int |= registers[i] << (i * 16)

        return True, value_int

    def read_float(self, slave_id: int, address: int, count: int = 2) -> Tuple[bool, Optional[float | None]]:
        """Чтение значения с плавающей точкой"""
        success, registers = self._read_registers(slave_id, address, count)

        if not success or registers is None:
            return False, None

        value_float = struct.unpack('f', struct.pack('>HH', registers[1], registers[0]))[0]
        return True, value_float

    def write_int(self, slave_id: int, address: int, value_int: int) -> bool:
        """Запись целочисленного значения"""
        registers = [(value_int & 0xFFFF), (value_int >> 16) & 0xFFFF]
        return self._write_registers(slave_id, address, registers)

    def write_float(self, slave_id: int, address: int, value_float: float) -> bool:
        """Запись значения с плавающей точкой"""
        float_bytes = struct.pack('f', value_float)
        registers = [
            struct.unpack('>H', float_bytes[2:4])[0],
            struct.unpack('>H', float_bytes[0:2])[0]
        ]
        return self._write_registers(slave_id, address, registers)

    def disconnect(self) -> bool:
        """Закрытие соединения"""
        try:
            if self.is_connected():
                self.client.close()
                print(f"\n{'=' * 50}")
                print(" Соединение закрыто")
                print(f"{'=' * 50}")
            return True
        except Exception as e:
            print(f"Ошибка закрытия: {e}")
            return False


class PyModbusClientRTU(ModbusBaseClient):
    """Клиент Modbus RTU"""

    def __init__(self, port="COM4", baudrate=9600, bytesize=8, parity='N', stopbits=1):
        self.port = port
        self.baudrate = baudrate
        self.bytesize = bytesize
        self.parity = parity
        self.stopbits = stopbits
        self.client = None

    def connect(self) -> bool:
        """Установка соединения"""
        try:
            self.client = ModbusSerialClient(
                port=self.port,
                baudrate=self.baudrate,
                bytesize=self.bytesize,
                parity=self.parity,
                stopbits=self.stopbits
            )

            result = self.client.connect()
            if not result:
                raise serial.SerialException(f"Ошибка подключения к порту {self.port}")

            print(f"Успешное подключение по {self.port}")
            return True

        except serial.SerialException as e:
            print(f"Ошибка подключения Modbus: {e}")
            return False
        except Exception as e:
            print(f"Ошибка подключения: {e}")
            return False

    def is_connected(self) -> bool:
        """Проверка соединения"""
        if self.client is None:
            return False

        try:
            result = self.client.read_holding_registers(
                address=0,
                count=1,
                device_id=devices[1]["device_id"]
            )
            return not result.isError()

        except Exception as e:
            print(f"Ошибка проверки соединения: {e}")
            return False

    def read_int(self, slave_id: int, address: int, count: int = 2) -> Tuple[bool, Optional[int | None]]:
        """Чтение целочисленного значения"""
        success, registers = self._read_registers(slave_id, address, count)

        if not success or registers is None:
            return False, None

        value_int = registers[1] << 16 | registers[0]
        return True, value_int

    def read_float(self, slave_id: int, address: int, count: int = 2) -> Tuple[bool, Optional[float | None]]:
        """Чтение значения с плавающей точкой"""
        success, registers = self._read_registers(slave_id, address, count)

        if not success or registers is None:
            return False, None

        value_float = struct.unpack('f', struct.pack('>HH', registers[1], registers[0]))[0]
        return True, value_float

    def write_int(self, slave_id: int, address: int, value_int: int) -> bool:
        """Запись целочисленного значения"""
        registers = [(value_int & 0xFFFF), (value_int >> 16) & 0xFFFF]
        return self._write_registers(slave_id, address, registers)

    def write_float(self, slave_id: int, address: int, value_float: float) -> bool:
        """Запись значения с плавающей точкой"""
        float_bytes = struct.pack('f', value_float)
        registers = [
            struct.unpack('>H', float_bytes[2:4])[0],
            struct.unpack('>H', float_bytes[0:2])[0]
        ]
        return self._write_registers(slave_id, address, registers)

    def disconnect(self) -> bool:
        """Закрытие соединения"""
        try:
            if self.client:
                self.client.close()
                print(f"\n{'=' * 50}")
                print(" Соединение закрыто")
                print(f"{'=' * 50}")
            return True
        except Exception as e:
            print(f"Ошибка закрытия: {e}")
            return False


class SystemInfo:
    """Класс для получения системной информации"""

    @staticmethod
    def get_ports_info() -> List[str]:
        """Получение информации о COM портах"""
        try:
            ports = serial.tools.list_ports.comports()
            port_names = [port.name for port in ports]

            if not port_names:
                print("COM порты не найдены")
            else:
                print(f"Доступно портов для Modbus RTU: {len(port_names)} - {port_names}")

            return port_names

        except Exception as e:
            print(f"Ошибка опроса COM портов: {e}")
            return []

    @staticmethod
    def get_port_settings(port_name) -> Optional[Dict[str, Any] | None]:
        """Получение настроек порта"""
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
            print(f"Ошибка получения настроек порта {port_name}: {e}")
            return None

    @staticmethod
    def get_network_interfaces() -> List[str]:
        """Получение списка сетевых интерфейсов"""
        interfaces = list(psutil.net_if_addrs().keys())

        if not interfaces:
            print("Сетевые интерфейсы не найдены")
        else:
            print(f"Доступные сетевые интерфейсы: {interfaces}")

        return interfaces

    @staticmethod
    def get_interface_addresses(interface_name: str) -> Optional[Dict[str, Any] | None]:
        """Получение адресов сетевого интерфейса"""
        try:
            interface_info = psutil.net_if_addrs().get(interface_name)
            if not interface_info:
                print(f"Информация об интерфейсе {interface_name} не найдена")
                return None

            for addr in interface_info:
                if addr.family == socket.AF_INET:
                    return {
                        'interface': interface_name,
                        'ip_address': addr.address,
                        'netmask': addr.netmask,
                        'broadcast': addr.broadcast,
                    }

            print(f"IPv4 адреса не найдены для интерфейса {interface_name}")
            return None

        except Exception as e:
            print(f"Ошибка получения информации об адресах для {interface_name}: {e}")
            return None

    @staticmethod
    def check_ethernet_connection(host: str, port: int, timeout: float = 2) -> bool:
        """Проверка Ethernet соединения"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(timeout)
            sock.connect((host, port))
            sock.close()
            print(f"Проверка соединения к {host}:{port} прошла успешно")
            return True
        except Exception as e:
            print(f"Не удалось подключиться к {host}:{port}: {e}")
            return False


class InfoReader:
    def __init__(self, slave_client):
        self.slave = slave_client

    def _read_sensor_parameter(self, address: int, data_type: str, device_id: int, count: int) -> None:
        """Чтение параметра датчика"""

        if data_type == "float":
            success, value = self.slave.read_float(device_id, address, count=count)
        else:
            success, value = self.slave.read_int(device_id, address, count=count)

        if success:
            print(f"  {address}: {value}")
        else:
            print(f"  Ошибка чтения {address}")


class InfoReaderMB210101(InfoReader):
    """Класс для чтения информации с устройств"""

    def get_sensor_info(self, channel: int, device_id: int) -> bool:
        """Получение информации с датчика по каналу"""
        success, value_type = self.slave.read_int(device_id, registers_sensor_MB210_101[3]["address"] + 3 * (channel - 1), count=2)

        if not success or value_type is None or value_type > 40:
            print(f" - Канал {channel} не установлен - ")
            return False

        print(f"\n == Канал {channel} == ")

        # Всегда можно добавить читаемые регистры
        self._read_sensor_parameter(registers_sensor_MB210_101[0]["address"] + 3 * (channel - 1), "float", device_id, 2)
        self._read_sensor_parameter(registers_sensor_MB210_101[1]["address"] + 3 * (channel - 1), "int", device_id, 1)
        self._read_sensor_parameter(registers_sensor_MB210_101[2]["address"] + 3 * (channel - 1), "int", device_id, 1)

        return True


class InfoReaderTPM10(InfoReader):
    """Класс для чтения информации с устройств"""

    def get_sensor_info(self, device_id: int) -> bool:
        """Получение информации с датчика по каналу"""
        success, value_type = self.slave.read_int(device_id, registers_sensor_TPM10[2]["address"], count=1)

        if not success or value_type is None or value_type > 40:
            print(f" - Датчик не установлен - ")
            return False

        print(f"\n == Датчик 1 == ")

        # Всегда можно добавить читаемые регистры
        self._read_sensor_parameter(registers_sensor_TPM10[0]["address"], "float", device_id, 2)
        self._read_sensor_parameter(registers_sensor_TPM10[1]["address"], "float", device_id, 2)

        return True


def read_all_system_info() -> None:
    """Чтение системных данных"""
    print("\n Чтение системных данных...")

    info = SystemInfo()
    info.get_ports_info()
    info.get_network_interfaces()

def read_all_devices() -> None:
    """Чтение данных со всех устройств"""
    print("\n Чтение данных со всех устройств...")

    for device in devices:

        name = device.get('name', 'Unknown')
        print(f"\n{'=' * 50}")
        print(f" Устройство: {name}")
        print(f"{'=' * 50}")

        if name == "AnalogInputModul_TCP_Room1":
            read_mb210_101(device)
        elif name == "MeasureModuleMicroprocessor_RTU_Slave1":
            read_tpm10(device)
        else:
            print(f"Для устройства {name} логика еще не прописана")


def read_mb210_101(device: Dict[str, Any]) -> None:
    """Логика для работы с MB210-101, он работает только по tcp"""
    client = None
    try:
        client = PyModbusClientTCP(device["ip"], device["port"])
        if client.connect():
            info_reader = InfoReaderMB210101(client)
            for channel in range(1, 9):
                info_reader.get_sensor_info(channel, device["device_id"])

    except Exception as e:
        print(f"Ошибка работы с устройством {device["name"]}: {e}")
    finally:
        if client:
            client.disconnect()

def read_tpm10(device: Dict[str, Any]) -> None:
    """Логика для работы с TPM10, он работает только по rtu"""
    client = None
    try:
        client = PyModbusClientRTU(device["port"], device.get("baudrate", 9600))
        if client.connect():
            # success, registers = client._read_registers(device["device_id"], 1, 2)
            # print(registers)
            info_reader = InfoReaderTPM10(client)
            info_reader.get_sensor_info(device["device_id"])

    except Exception as e:
        print(f"Ошибка работы с устройством {device["name"]}: {e}")
    finally:
        if client:
            client.disconnect()


def main():
    """Основная функция программы"""
    print("\n" + "=" * 60)
    print(" === Программа для работы с протоколами Modbus TCP/RTU === ")
    print("=" * 60)

    read_all_system_info()
    read_all_devices()

    print("\n == Программа успешно завершилась == ")


if __name__ == "__main__":
    main()