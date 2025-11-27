from pymodbus.exceptions import ModbusException
from typing import Tuple, Optional, List, NewType
import logging
from Logger.logger import logged

SlaveID = NewType('SlaveID', int)
ModbusAddress = NewType('ModbusAddress', int)

@logged(name="base", level=logging.DEBUG)
class ModbusBaseClient:
    """Базовый класс для Modbus клиентов"""
    def __init__(self):
        self.log.info("Инициализация объекта ModbusBaseClient")

    def _validate_slave_id(self, slave_id: int) -> SlaveID:
        self.log.debug("Валидация slave_id")
        if not 0 <= slave_id <= 247:
            self.log.exception(f"slave_id должен быть в диапазоне 0-247, получено: {slave_id}")
            raise ValueError(f"slave_id должен быть в диапазоне 0-247, получено: {slave_id}")
        self.log.debug("_read_registers: успешно")
        return SlaveID(slave_id)

    def _validate_address(self, address: int) -> ModbusAddress:
        self.log.debug("Валидация address")
        if not 0 <= address <= 65535:
            self.log.exception(f"address должен быть в диапазоне 0-65535, получено: {address}")
            raise ValueError(f"address должен быть в диапазоне 0-65535, получено: {address}")
        self.log.debug("_read_registers: успешно")
        return ModbusAddress(address)

    def _read_registers(self, slave_id: int, address: int, count: int = 2) -> Tuple[Optional[List[int]]]:
        """Базовый метод чтения регистров"""
        self.log.debug("Базовый метод чтения регистров")

        if not self.is_connected():
            self.log.exception("Нет соединения")
            raise ConnectionError("Нет соединения")

        try:
            valid_slave_id = self._validate_slave_id(slave_id)
            valid_address = self._validate_address(address)

            result = self.client.read_holding_registers(
                address=valid_address,
                count=count,
                device_id=valid_slave_id
            )

            if result.isError():
                self.log.exception(f"Ошибка чтения регистров: {result}")
                raise ModbusException(f"Ошибка чтения регистров: {result}")

            self.log.debug("_read_registers: успешно")
            return result.registers

        except (ValueError, ConnectionError, ModbusException) as e:
            self.log.exception(e)
            raise
        except Exception as e:
            self.log.exception(f"Ошибка чтения: {e}")
            raise ModbusException(f"Ошибка чтения: {e}") from e

    def _write_registers(self, slave_id: int, address: int, registers: Optional[List[int]]):
        """Базовый метод записи регистров"""
        self.log.debug("Базовый метод записи регистров")

        if not self.is_connected():
            self.log.exception("Нет соединения")
            raise ConnectionError("Нет соединения")

        try:
            valid_slave_id = self._validate_slave_id(slave_id)
            valid_address = self._validate_address(address)

            result = self.client.write_registers(
                address=valid_address,
                values=registers,
                device_id=valid_slave_id
            )

            if result.isError():
                self.log.exception(f"Ошибка записи регистров: {result}")
                raise ModbusException(f"Ошибка записи регистров: {result}")

            self.log.debug("_write_registers: успешно")

        except (ValueError, ConnectionError, ModbusException) as e:
            self.log.exception(e)
            raise
        except Exception as e:
            self.log.exception(f"Ошибка записи: {e}")
            raise ModbusException(f"Ошибка записи: {e}") from e