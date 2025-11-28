import logging
from readers.base_reader import InfoReader
from config.registers import registers_sensor_MB210_101
from Logger.logger import logged

@logged(name="mb210101_reader", level=logging.DEBUG)
class InfoReaderMB210101(InfoReader):
    """Класс для чтения информации с устройств"""
    def __init__(self):
        self.log.info("=== Инициализация объекта InfoReaderMB210101 ===")

    def get_sensor_info(self, channel: int, device_id: int) -> bool:
        """Получение информации с датчика по каналу"""
        self.log.debug(f"Получение информации с устройтсва {device_id} по каналу {channel}")

        value_type = self.slave.read_int(device_id, registers_sensor_MB210_101[3]["address"] + 3 * (channel - 1), count=2)

        if value_type is None or value_type > 40:
            print(f" - Тип датчика по каналу {channel} не установлен - ")
            self.log.debug(f" - Тип датчика по каналу {channel} не установлен - ")
            return False

        print(f"\n == Канал {channel}: Тип датчика {value_type} == ")

        self.log.debug(f"Чтение данных с регистров датчика {value_type}")
        # Всегда можно добавить читаемые регистры
        self._read_sensor_parameter(registers_sensor_MB210_101[0]["address"] + 3 * (channel - 1), "float", device_id, 2)
        self._read_sensor_parameter(registers_sensor_MB210_101[1]["address"] + 3 * (channel - 1), "int", device_id, 1)
        self._read_sensor_parameter(registers_sensor_MB210_101[2]["address"] + 3 * (channel - 1), "int", device_id, 1)

        return True