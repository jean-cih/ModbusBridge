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
        self.log.info("=== Инициализация объекта PyModbusClientTCP ===")
        self.host = host
        self.port = port
        self.client = None

    def connect(self):
        """Установка соединения"""
        try:
            self.log.debug("Установка соединения")

            self.client = ModbusTcpClient(host=self.host, port=self.port)
            result = self.client.connect()

            if not result:
                self.log.exception(f"Не удалось подключиться к {self.host}:{self.port}")
                raise ModbusException(f"Не удалось подключиться к {self.host}:{self.port}")

            print(f"Успешное подключение к {self.host}:{self.port}")
            self.log.debug(f"Успешное подключение к {self.host}:{self.port}")

        except ModbusException as e:
            self.log.exception(e)
            raise
        except Exception as e:
            self.log.exception(f"Ошибка подключения: {e}")
            raise ModbusException(f"Ошибка подключения: {e}") from e

    def is_connected(self) -> bool:
        """Проверка соединения"""
        self.log.debug("Проверка соединения")

        if self.client is None:
            return False

        try:
            self.log.debug(f"Соединение: {self.client.is_socket_open()}")
            return self.client.is_socket_open()
        except Exception as e:
            self.log.exception(e)
            return False

    def read_int(self, slave_id: int, address: int, count: int = 1) -> int:
        """Чтение целочисленного значения"""
        self.log.debug("Чтение целочисленного значения")

        registers = self._read_registers(slave_id, address, count)

        if registers is None:
            self.log.exception("Данные с устройства не получены")
            raise ValueError("Данные с устройства не получены")

        self.log.info(f"read_int: данные получены: {registers[0]}")
        return registers[0]

    def read_float(self, slave_id: int, address: int, count: int = 2) -> float:
        """Чтение значения с плавающей точкой"""
        self.log.debug("Чтение значения с плавающей точкой")

        registers = self._read_registers(slave_id, address, count)

        if registers is None:
            self.log.exception("Данные с устройства не получены")
            raise ValueError("Даные с устройства не получены")

        value_float = struct.unpack('f', struct.pack('>HH', registers[1], registers[0]))[0]
        self.log.info(f"read_float: данные получены: {value_float}")
        return value_float

    def write_int(self, slave_id: int, address: int, value_int: int) -> bool:
        """Запись целочисленного значения"""
        self.log.debug("Запись целочисленного значения")

        registers = [value_int & 0xFFFF]
        result = self._write_registers(slave_id, address, registers)

        if result:
            self.log.info(f"write_int: успешная запись значения {value_int} в регистр {address} устройства {slave_id}")
        else:
            self.log.exception(f"write_int: ошибка записи значения {value_int} в регистр {address} устройства {slave_id}")

        return result

    def write_float(self, slave_id: int, address: int, value_float: float) -> bool:
        """Запись значения с плавающей точкой"""
        self.log.debug("Запись значения с плавающей точкой")

        float_bytes = struct.pack('f', value_float)
        registers = [
            struct.unpack('>H', float_bytes[2:4])[0],
            struct.unpack('>H', float_bytes[0:2])[0]
        ]
        result = self._write_registers(slave_id, address, registers)

        if result:
            self.log.info(f"write_int: успешная запись значения {value_float} в регистр {address} устройства {slave_id}")
        else:
            self.log.exception(f"write_int: ошибка записи значения {value_float} в регистр {address} устройства {slave_id}")

        return result

    def disconnect(self):
        """Закрытие соединения"""
        self.log.debug("Закрытие соединения")

        try:
            if self.client():
                self.client.close()
                print(f"Соединение с {self.host}:{self.port} закрыто")
                self.log.info(f"Соединение с {self.host}:{self.port} закрыто")
        except Exception as e:
            self.log.exception(f"Ошибка закрытия: {e}")
            raise ModbusException(f"Ошибка закрытия: {e}") from e
        finally:
            self.client = None