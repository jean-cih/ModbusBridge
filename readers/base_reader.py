import logging
from Logger.logger import logged

@logged(name="base_reader", level=logging.DEBUG)
class InfoReader:
    def __init__(self, slave_client):
        self.log.info("=== Инициализация объекта InfoReader ===")
        self.slave = slave_client

    def _read_sensor_parameter(self, address: int, data_type: str, device_id: int, count: int) -> None:
        """Чтение параметра датчика"""
        try:
            self.log.debug(f"Чтение параметра: address={address}, type={data_type}, device={device_id}")

            if data_type == "float":
                value = self.slave.read_float(device_id, address, count=count)
            else:
                value = self.slave.read_int(device_id, address, count=count)

            self.log.debug(f"Из {address} прочитано значение: {value}")
            print(f"  {address}: {value}")

        except Exception as e:
            self.log.exception(e)
