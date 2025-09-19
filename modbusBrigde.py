from pymodbus.client import ModbusTcpClient
from pymodbus.exceptions import ModbusException
import struct


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
                print(f"Не удалось подключиться к {self.host}:{self.port}")
                return False

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
            result = self.client.read_holding_registers(address=address, count=count, device_id=slave_id)

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
            result = self.client.read_holding_registers(address=address,count=count, device_id=slave_id)

            if result.isError():
                raise ModbusException(f"Ошибка чтения регистров: {result}")

            value_float = struct.unpack('f', struct.pack('>HH', result.registers[1], result.registers[0]))[0]
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
            result = self.client.write_registers(address=address, values=registers, device_id=slave_id)

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
            registers = [struct.unpack('>H', float_bytes[2:4])[0], struct.unpack('>H', float_bytes[0:2])[0]]
            result = self.client.write_registers(address=address, values=registers, device_id=slave_id)

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




if __name__ == "__main__":
    client = PyModbusClientTCP('8.8.8.8', 502)

    client.connect()

    client.is_connected()

    client.disconnect()