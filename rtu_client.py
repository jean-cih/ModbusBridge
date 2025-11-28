from base import ModbusBaseClient
from pymodbus.client import ModbusSerialClient
from pymodbus.exceptions import ModbusException
import serial
import struct
from config.devices import devices
import logging
from Logger.logger import logged


@logged(name="rtu_client", level=logging.DEBUG)
class PyModbusClientRTU(ModbusBaseClient):
    """Клиент Modbus RTU"""

    def __init__(self, port="COM4", baudrate=9600, bytesize=8, parity='N', stopbits=1):
        self.log.info("=== Инициализация объекта PyModbusClientRTU ===")
        self.port = port
        self.baudrate = baudrate
        self.bytesize = bytesize
        self.parity = parity
        self.stopbits = stopbits
        self.client = None

    def connect(self):
        """Установка соединения"""
        try:
            self.log.debug("Установка соединения")

            self.client = ModbusSerialClient(
                port=self.port,
                baudrate=self.baudrate,
                bytesize=self.bytesize,
                parity=self.parity,
                stopbits=self.stopbits
            )

            result = self.client.connect()
            if not result:
                self.log.exception(f"Ошибка подключения к порту {self.port}")
                raise serial.SerialException(f"Ошибка подключения к порту {self.port}")

            print(f"Успешное подключение по {self.port}")
            self.log.debug(f"connect: успешное подключение по {self.port}")

        except serial.SerialException as e:
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
            result = self.client.read_holding_registers(
                address=1,
                count=1,
                device_id=devices[0]["device_id"]
            )
            self.log.debug(f"Соединение: {not result.isError()}")
            return not result.isError()
        except Exception as e:
            self.log.exception(f"Ошибка соединения: {e}")
            return False


    def read_int(self, slave_id: int, address: int, count: int = 1) -> int:
        """Чтение целочисленного значения"""
        self.log.debug("Чтение целочисленного значения")

        registers = self._read_registers(slave_id, address, count)

        if registers is None:
            self.log.exception("Данные не получены с устройства")
            raise ValueError("Данные не получены с устройства")

        self.log.debug(f"read_int: данные получены: {registers[0]}")
        return registers[0]

    def read_float(self, slave_id: int, address: int, count: int = 2) -> float:
        """Чтение значения с плавающей точкой"""
        self.log.debug("Чтение значения с плавающей точкой")

        registers = self._read_registers(slave_id, address, count)

        if registers is None:
            self.log.exception("Данные не получены с устройства")
            raise ValueError("Данные не получены с устройства")

        value_float = struct.unpack('f', struct.pack('>HH', registers[1], registers[0]))[0]

        self.log.debug(f"read_float: данные получены: {value_float}")
        return value_float

    def write_int(self, slave_id: int, address: int, value_int: int) -> bool:
        """Запись целочисленного значения"""
        self.log.debug("Запись целочисленного значения")

        registers = [value_int & 0xFFFF]
        result = self._write_registers(slave_id, address, registers)

        if result:
            self.log.debug(f"write_int: успешная запись значения {value_int} в регистр {address} устройства {slave_id}")
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
            self.log.debug(f"write_float: успешная запись значения {value_float} в регистр {address} устройства {slave_id}")
        else:
            self.log.exception(f"write_float: ошибка записи значения {value_float} в регистр {address} устройства {slave_id}")

        return result

    def disconnect(self):
        """Закрытие соединения"""
        self.log.debug("Закрытие соединения")
        try:
            if self.client:
                self.client.close()
                print(f" Соединение с {self.port} закрыто")
                self.log.debug(f" Соединение с {self.port} закрыто")
        except Exception as e:
            self.log.exception(f"Ошибка закрытия: {e}")
            raise ModbusException(f"Ошибка закрытия: {e}") from e
        finally:
            self.client = None