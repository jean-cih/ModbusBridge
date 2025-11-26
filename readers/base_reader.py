class InfoReader:
    def __init__(self, slave_client):
        self.slave = slave_client

    def _read_sensor_parameter(self, address: int, data_type: str, device_id: int, count: int) -> None:
        """Чтение параметра датчика"""

        if data_type == "float":
            success, value = self.slave.read_float(device_id, address, count=count)
        else:
            success, value = self.slave.read_int(device_id, address, count=count)

        if success:
            print(f"  {address}: {value}")
        else:
            print(f"  Ошибка чтения {address}")