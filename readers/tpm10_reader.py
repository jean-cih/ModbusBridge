from readers.base_reader import InfoReader
from config.registers import registers_sensor_TPM10
import logging
from Logger.logger import logged

@logged(name="tpm10_reader", level=logging.DEBUG)
class InfoReaderTPM10(InfoReader):
    """Класс для чтения информации с устройств"""
    def __init__(self):
        self.log.info("=== Инициализация объекта InfoReaderTPM10 ===")

    def get_sensor_info(self, device_id: int) -> bool:
        """Получение информации с датчика по каналу"""
        self.log.debug(f"Получение информации с устройства {device_id}")

        value_type = self.slave.read_int(device_id, registers_sensor_TPM10[2]["address"], count=1)

        if value_type is None or value_type > 40:
            print(f" - Датчик не установлен - ")
            self.log.debug(f" - Датчик не установлен - ")
            return False

        print(f"\n == Датчик {registers_sensor_TPM10[2]["name"]} == ")

        self.log.debug(f"Чтение данных с регистров")
        # Всегда можно добавить читаемые регистры
        self._read_sensor_parameter(registers_sensor_TPM10[0]["address"], "float", device_id, 2)
        self._read_sensor_parameter(registers_sensor_TPM10[1]["address"], "float", device_id, 2)

        return True