from base import ModbusBaseClient
from pymodbus.client import ModbusSerialClient
from pymodbus.exceptions import ModbusException
import serial
import struct
from config.devices import devices


class PyModbusClientRTU(ModbusBaseClient):
    """Клиент Modbus RTU"""

    def __init__(self, port="COM4", baudrate=9600, bytesize=8, parity='N', stopbits=1):
        self.port = port
        self.baudrate = baudrate
        self.bytesize = bytesize
        self.parity = parity
        self.stopbits = stopbits
        self.client = None

    def connect(self):
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

        except serial.SerialException:
            raise
        except Exception as e:
            raise ModbusException(f"Ошибка подключения: {e}") from e

    def is_connected(self) -> bool:
        """Проверка соединения"""
        if self.client is None:
            return False

        try:
            result = self.client.read_holding_registers(
                address=1,
                count=1,
                device_id=devices[0]["device_id"]
            )

            return not result.isError()

        except Exception:
            return False


    def read_int(self, slave_id: int, address: int, count: int = 1) -> int:
        """Чтение целочисленного значения"""
        registers = self._read_registers(slave_id, address, count)

        if registers is None:
            raise ValueError("Данные не получены с устройства")

        return registers[0]

    def read_float(self, slave_id: int, address: int, count: int = 2) -> float:
        """Чтение значения с плавающей точкой"""
        registers = self._read_registers(slave_id, address, count)

        if registers is None:
            raise ValueError("Данные не получены с устройства")

        value_float = struct.unpack('f', struct.pack('>HH', registers[1], registers[0]))[0]
        return value_float

    def write_int(self, slave_id: int, address: int, value_int: int) -> bool:
        """Запись целочисленного значения"""
        registers = [value_int & 0xFFFF]
        return self._write_registers(slave_id, address, registers)

    def write_float(self, slave_id: int, address: int, value_float: float) -> bool:
        """Запись значения с плавающей точкой"""
        float_bytes = struct.pack('f', value_float)
        registers = [
            struct.unpack('>H', float_bytes[2:4])[0],
            struct.unpack('>H', float_bytes[0:2])[0]
        ]
        return self._write_registers(slave_id, address, registers)

    def disconnect(self):
        """Закрытие соединения"""
        try:
            if self.client:
                self.client.close()
                print(f" Соединение с {self.port} закрыто")
        except Exception as e:
            raise ModbusException(f"Ошибка закрытия: {e}") from e
        finally:
            self.client = None