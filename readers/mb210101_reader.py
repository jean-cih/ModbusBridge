from readers.base_reader import InfoReader
from config.registers import registers_sensor_MB210_101


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