from pymodbus.exceptions import ModbusException
from typing import Tuple, Optional, List, NewType
import logging

bc_logger = logging.getLogger(__name__)
bc_logger.setLevel(logging.INFO)

bc_handler = logging.FileHandler(f"log_status/{__name__}.log", mode="w", encoding="utf-8")
bc_formatter = logging.Formatter("%(name)s %(asctime)s %(levelname)s %(message)s")

bc_handler.setFormatter(bc_formatter)
bc_logger.addHandler(bc_handler)

bc_logger.info(" == Логгирование базового класса Modbus клиентов ==")

SlaveID = NewType('SlaveID', int)
ModbusAddress = NewType('ModbusAddress', int)


class ModbusBaseClient:
    """Базовый класс для Modbus клиентов"""

    def _validate_slave_id(self, slave_id: int) -> SlaveID:
        if not 0 <= slave_id <= 247:
            raise ValueError(f"slave_id должен быть в диапазоне 0-247, получено: {slave_id}")
        bc_logger.info("_validate_slave_id: успешно")
        return SlaveID(slave_id)

    def _validate_address(self, address: int) -> ModbusAddress:
        if not 0 <= address <= 65535:
            raise ValueError(f"address должен быть в диапазоне 0-65535, получено: {address}")
        bc_logger.info("_validate_address: успешно")
        return ModbusAddress(address)

    def _read_registers(self, slave_id: int, address: int, count: int = 2) -> Tuple[Optional[List[int]]]:
        """Базовый метод чтения регистров"""
        if not self.is_connected():
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
                raise ModbusException(f"Ошибка чтения регистров: {result}")

            bc_logger.info("_read_registers: успешно")
            return result.registers

        except (ValueError, ConnectionError, ModbusException):
            raise
        except Exception as e:
            raise ModbusException(f"Ошибка чтения: {e}") from e

    def _write_registers(self, slave_id: int, address: int, registers: Optional[List[int]]):
        """Базовый метод записи регистров"""
        if not self.is_connected():
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
                raise ModbusException(f"Ошибка записи регистров: {result}")

            bc_logger.info("_write_registers: успешно")

        except (ValueError, ConnectionError, ModbusException):
            raise
        except Exception as e:
            raise ModbusException(f"Ошибка записи: {e}") from e