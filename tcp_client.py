from base import ModbusBaseClient
from pymodbus.client import ModbusTcpClient
from pymodbus.exceptions import ModbusException
import struct
import logging
from Logger.logger import logged

@logged(name="tcp_client", level=logging.DEBUG)
class PyModbusClientTCP(ModbusBaseClient):
    """Клиент Modbus TCP"""

    def __init__(self, host, port=502):
        self.host = host
        self.port = port
        self.client = None

    def connect(self):
        """Установка соединения"""
        try:
            self.client = ModbusTcpClient(host=self.host, port=self.port)
            result = self.client.connect()

            if not result:
                raise ModbusException(f"Не удалось подключиться к {self.host}:{self.port}")

            print(f"Успешное подключение к {self.host}:{self.port}")
            tcp_logger.info(f"Успешное подключение к {self.host}:{self.port}")

        except ModbusException:
            raise
        except Exception as e:
            raise ModbusException(f"Ошибка подключения: {e}") from e

    def is_connected(self) -> bool:
        """Проверка соединения"""
        if self.client is None:
            return False

        try:
            return self.client.is_socket_open()
        except Exception:
            return False

    def read_int(self, slave_id: int, address: int, count: int = 1) -> int:
        """Чтение целочисленного значения"""
        registers = self._read_registers(slave_id, address, count)

        if registers is None:
            raise ValueError("Данные с устройства не получены")

        tcp_logger.info(f"read_int: данные получены: {registers[0]}")
        return registers[0]

    def read_float(self, slave_id: int, address: int, count: int = 2) -> float:
        """Чтение значения с плавающей точкой"""
        registers = self._read_registers(slave_id, address, count)

        if registers is None:
            raise ValueError("Даные с устройства не получены")

        value_float = struct.unpack('f', struct.pack('>HH', registers[1], registers[0]))[0]
        tcp_logger.info(f"read_float: данные получены: {value_float}")
        return value_float

    def write_int(self, slave_id: int, address: int, value_int: int) -> bool:
        """Запись целочисленного значения"""
        registers = [value_int & 0xFFFF]
        result = self._write_registers(slave_id, address, registers)

        if result:
            tcp_logger.info(f"write_int: успешная запись значения {value_int} в регистр {address} устройства {slave_id}")
        else:
            tcp_logger.error(f"write_int: ошибка записи значения {value_int} в регистр {address} устройства {slave_id}")

        return result

    def write_float(self, slave_id: int, address: int, value_float: float) -> bool:
        """Запись значения с плавающей точкой"""
        float_bytes = struct.pack('f', value_float)
        registers = [
            struct.unpack('>H', float_bytes[2:4])[0],
            struct.unpack('>H', float_bytes[0:2])[0]
        ]
        result = self._write_registers(slave_id, address, registers)

        if result:
            tcp_logger.info(f"write_int: успешная запись значения {value_float} в регистр {address} устройства {slave_id}")
        else:
            tcp_logger.error(f"write_int: ошибка записи значения {value_float} в регистр {address} устройства {slave_id}")

        return result

    def disconnect(self):
        """Закрытие соединения"""
        try:
            if self.client():
                self.client.close()
                print(f"Соединение с {self.host}:{self.port} закрыто")
                tcp_logger.info(f"Соединение с {self.host}:{self.port} закрыто")
        except Exception as e:
            raise ModbusException(f"Ошибка закрытия: {e}") from e
        finally:
            self.client = None