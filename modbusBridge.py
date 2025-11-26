from system_info import SystemInfo
from config.devices import devices
from readers.mb210101_reader import InfoReaderMB210101
from readers.tpm10_reader import InfoReaderTPM10
from tcp_client import PyModbusClientTCP
from rtu_client import PyModbusClientRTU
import serial.tools.list_ports
from typing import Dict, Any
import time
import sys
import msvcrt
from exceptions import DeviceWorkError, DeviceDisconnectedError, MonitoringStoppedError
import logging

mb_logger = logging.getLogger(__name__)
mb_logger.setLevel(logging.INFO)

mb_handler = logging.FileHandler(f"log_status/{__name__}.log", mode="w")
mb_formatter = logging.Formatter("%(name)s %(asctime)s %(levelname)s %(message)s")

mb_handler.setFormatter(mb_formatter)
mb_logger.addHandler(mb_handler)

mb_logger.info(f" === Логгирование главного модуля {__name__} === ")

def read_all_system_info() -> None:
    """Чтение системных данных"""
    print("\n Чтение системных данных...")

    info = SystemInfo()
    info.get_ports_info()
    info.get_network_interfaces()
    mb_logger.info("read_all_system_info: успешно")

def read_all_devices() -> None:
    """Чтение данных со всех устройств"""
    print("\n Чтение данных со всех устройств...")

    for device in devices:

        name = device.get('name', 'Unknown')
        print(f"\n{'=' * 50}")
        print(f" Устройство: {name}")
        print(f"{'=' * 50}")

        if name == "AnalogInputModul_TCP_Room1":
            read_mb210_101(device)
            mb_logger.info("Вызов функции read_mb210_101")
        elif name == "MeasureModuleMicroprocessor_RTU_Slave1":
            read_tpm10(device)
            mb_logger.info("Вызов функции read_tpm10")
        elif name == "ElectroDynamometer":
            constant_read_med(device)
            mb_logger.info("Вызов функции constant_read_med")
        else:
            print(f"Для устройства {name} логика еще не прописана")

    mb_logger.info("read_all_devices: успешно")


def read_mb210_101(device: Dict[str, Any]) -> None:
    """Логика для работы с MB210-101, он работает только по tcp"""
    client = None
    try:
        client = PyModbusClientTCP(device["ip"], device["port"])
        mb_logger.info("Создание экземпляра PyModbusClientTCP")
        if client.connect():
            info_reader = InfoReaderMB210101(client)
            mb_logger.info("Создание экземпляра InfoReaderMB210101")
            for channel in range(1, 9):
                info_reader.get_sensor_info(channel, device["device_id"])
                mb_logger.info("Вызов функции get_sensor_info")

        mb_logger.info("read_mb210_101: успешно")
    except Exception as e:
        raise DeviceWorkError(f"Ошибка работы с устройством {device["name"]}") from e
    finally:
        if client:
            client.disconnect()
            mb_logger.info("read_mb210_101: соединение закрыто")

def read_tpm10(device: Dict[str, Any]) -> None:
    """Логика для работы с TPM10, он работает только по rtu, rs 485"""
    client = None
    try:
        client = PyModbusClientRTU(device["port"], device.get("baudrate", 9600), timeout=1)
        mb_logger.info("Создание экземпляра PyModbusClientRTU")
        if client.connect():
            registers = client._read_registers(device["device_id"], 1, 2)
            mb_logger.info("Вызов функции _read_registers")
            print(registers)
            info_reader = InfoReaderTPM10(client)
            mb_logger.info("Создание экземпляра InfoReaderTPM10")
            info_reader.get_sensor_info(device["device_id"])
            mb_logger.info("Вызов функции get_sensor_info")

        mb_logger.info("read_tpm10: успешно")
    except Exception as e:
        raise DeviceWorkError(f"Ошибка работы с устройством {device["name"]}") from e
    finally:
        if client:
            client.disconnect()
            mb_logger.info("read_tpm10: соединение закрыто")

def constant_read_med(device: Dict[str, Any]) -> None:
    """Логика постоянного отслеживания данных НПО 'МЭД'"""
    while True:
        if _stop_process():
            print()
            mb_logger.info("constant_read_med: успешно завершен по команде")
            break

        data = _read_med(device)
        mb_logger.info("Вызов функции _read_med")
        if data:
            print(f"Значение: {data}", end=" ")
        else:
            raise DeviceDisconnectedError(f"Устройство {device["name"]} отключено")

        time.sleep(0.1)
        _clean_stdout()


def _read_med(device: Dict[str, Any]) -> str | None:
    """Внутренняя функция: Логика для работы с НПО 'МЭД', он работает по rs 232"""
    try:
        with serial.Serial(device["port"], device["baudrate"], timeout=1) as ser:
            data = str(ser.readline()).strip("b'rn\\")
            mb_logger.info("_read_med: успешно")
            return data if data else None
    except serial.SerialTimeoutException:
        raise serial.SerialTimeoutException(f"Таймаут при чтении из порта {device["port"]}")
    except serial.SerialException as e:
        raise serial.SerialException(f"Ошибка при работе с портом {device["port"]}: {e}")


def _stop_process() -> bool:
    if msvcrt.kbhit():
        key = msvcrt.getch()
        if key == b'\r':
            mb_logger.info("_stop_process: успешно")
            return True
    return False


def _clean_stdout():
    sys.stdout.write('\r')
    sys.stdout.flush()

def main():
    """Основная функция программы"""
    mb_logger.info("Программа запущена")
    print("\n" + "=" * 60)
    print(" === Программа для работы по протоколам Modbus TCP/RTU === ")
    print("=" * 60)

    try:
        read_all_system_info()
        mb_logger.info("Вызов функции read_all_system_info")

        read_all_devices()
        mb_logger.info("Вызов функции read_all_devices")
    except Exception as e:
        print(e)
        mb_logger.error(e)
    except KeyboardInterrupt:
        print(f"\n\nЧтение прервано (Ctrl+C)")
        mb_logger.info(f"Чтение прервано (Ctrl+C)")

    print("\n == Программа успешно завершилась == ")
    mb_logger.info("Программа завершена")


if __name__ == "__main__":
    main()