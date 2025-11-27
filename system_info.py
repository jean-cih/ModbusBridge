from typing import Optional, Dict, Any, List
import serial
import socket
import psutil
import logging
from Logger.logger import logged

@logged(name="system_info", level=logging.DEBUG)
class SystemInfo:
    """Класс для получения системной информации"""

    @staticmethod
    def get_ports_info() -> List[str]:
        """Получение информации о COM портах"""
        try:
            ports = serial.tools.list_ports.comports()
            port_names = [port.name for port in ports]

            if not port_names:
                print("COM порты не найдены")
            else:
                print(f"Доступно портов для Modbus RTU: {len(port_names)} - {port_names}")

            sys_logger.info("get_ports_info: Получение информации о COM портах: успешно")

            return port_names

        except Exception as e:
            print(f"Ошибка опроса COM портов: {e}")
            sys_logger.error(f"get_ports_info: Ошибка опроса COM портов: {e}")
            return []

    @staticmethod
    def get_port_settings(port_name) -> Optional[Dict[str, Any] | None]:
        """Получение настроек порта"""
        try:
            with serial.Serial(port_name) as ser:
                settings = {
                    'name': port_name,
                    'baudrate': ser.baudrate,
                    'bytesize': ser.bytesize,
                    'parity': ser.parity,
                    'stopbits': ser.stopbits,
                    'timeout': ser.timeout,
                    'xonxoff': ser.xonxoff,
                    'rtscts': ser.rtscts,
                    'dsrdtr': ser.dsrdtr
                }
                sys_logger.info("get_port_settings: Получение настроек порта: успешно")

                return settings

        except Exception as e:
            print(f"Ошибка получения настроек порта {port_name}: {e}")
            sys_logger.error(f"get_port_settings: Ошибка получения настроек порта {port_name}: {e}")
            return None

    @staticmethod
    def get_network_interfaces() -> List[str]:
        """Получение списка сетевых интерфейсов"""
        interfaces = list(psutil.net_if_addrs().keys())

        if not interfaces:
            print("Сетевые интерфейсы не найдены")
        else:
            print(f"Доступные сетевые интерфейсы: {interfaces}")

        sys_logger.info("get_network_interfaces: Получение настроек порта: успешно")

        return interfaces

    @staticmethod
    def get_interface_addresses(interface_name: str) -> Optional[Dict[str, Any] | None]:
        """Получение адресов сетевого интерфейса"""
        try:
            interface_info = psutil.net_if_addrs().get(interface_name)
            if not interface_info:
                print(f"Информация об интерфейсе {interface_name} не найдена")
                return None

            for addr in interface_info:
                if addr.family == socket.AF_INET:
                    sys_logger.info(f"get_interface_addresses: Получение адресов сетевого интерфейса: успешно")
                    return {
                        'interface': interface_name,
                        'ip_address': addr.address,
                        'netmask': addr.netmask,
                        'broadcast': addr.broadcast,
                    }

            print(f"IPv4 адреса не найдены для интерфейса {interface_name}")
            sys_logger.info(f"get_interface_addresses: IPv4 адреса не найдены для интерфейса {interface_name}")
            return None

        except Exception as e:
            print(f"Ошибка получения информации об адресах для {interface_name}: {e}")
            sys_logger.error(f"get_interface_addresses: Ошибка получения информации об адресах для {interface_name}: {e}")
            return None

    @staticmethod
    def check_ethernet_connection(host: str, port: int, timeout: float = 2) -> bool:
        """Проверка Ethernet соединения"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(timeout)
            sock.connect((host, port))
            sock.close()
            print(f"Проверка соединения к {host}:{port} прошла успешно")
            sys_logger.error(f"check_ethernet_connection: Проверка соединения к {host}:{port} прошла успешно")
            return True
        except Exception as e:
            print(f"Не удалось подключиться к {host}:{port}: {e}")
            sys_logger.error(f"check_ethernet_connection: Не удалось подключиться к {host}:{port}: {e}")
            return False