class DeviceDisconnectedError(Exception):
    """Устройство отключено или недоступно"""
    pass


class MonitoringStoppedError(Exception):
    """Мониторинг остановлен по команде"""
    pass


class DeviceWorkError(Exception):
    """Ошибка работы с устройством"""
    pass