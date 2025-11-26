from readers.base_reader import InfoReader
from config.registers import registers_sensor_TPM10


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