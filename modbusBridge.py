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


def read_all_system_info() -> None:
    """Чтение системных данных"""
    print("\n Чтение системных данных...")

    info = SystemInfo()
    info.get_ports_info()
    info.get_network_interfaces()

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
        elif name == "MeasureModuleMicroprocessor_RTU_Slave1":
            read_tpm10(device)
        elif name == "ElectroDynamometer":
            constant_read_med(device)
        else:
            print(f"Для устройства {name} логика еще не прописана")


def read_mb210_101(device: Dict[str, Any]) -> None:
    """Логика для работы с MB210-101, он работает только по tcp"""
    client = None
    try:
        client = PyModbusClientTCP(device["ip"], device["port"])
        if client.connect():
            info_reader = InfoReaderMB210101(client)
            for channel in range(1, 9):
                info_reader.get_sensor_info(channel, device["device_id"])

    except Exception as e:
        raise DeviceWorkError(f"Ошибка работы с устройством {device["name"]}") from e
    finally:
        if client:
            client.disconnect()

def read_tpm10(device: Dict[str, Any]) -> None:
    """Логика для работы с TPM10, он работает только по rtu, rs 485"""
    client = None
    try:
        client = PyModbusClientRTU(device["port"], device.get("baudrate", 9600), timeout=1)
        if client.connect():
            registers = client._read_registers(device["device_id"], 1, 2)
            print(registers)
            info_reader = InfoReaderTPM10(client)
            info_reader.get_sensor_info(device["device_id"])

    except Exception as e:
        raise DeviceWorkError(f"Ошибка работы с устройством {device["name"]}") from e
    finally:
        if client:
            client.disconnect()


def constant_read_med(device: Dict[str, Any]) -> None:
    """Логика постоянного отслеживания данных НПО 'МЭД'"""
    while True:
        if _stop_process():
            raise MonitoringStoppedError("Мониторинг остановлен по команде")

        data = _read_med(device)
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
            return data if data else None
    except serial.SerialTimeoutException:
        raise serial.SerialTimeoutException(f"Таймаут при чтении из порта {device["port"]}")
    except serial.SerialException as e:
        raise serial.SerialException(f"Ошибка при работе с портом {device["port"]}: {e}")


def _stop_process() -> bool:
    if msvcrt.kbhit():
        key = msvcrt.getch()
        if key == b'\r':
            return True
    return False


def _clean_stdout():
    sys.stdout.write('\r')
    sys.stdout.flush()

def main():
    """Основная функция программы"""
    print("\n" + "=" * 60)
    print(" === Программа для работы по протоколам Modbus TCP/RTU === ")
    print("=" * 60)

    try:
        read_all_system_info()
        read_all_devices()
    except Exception as e:
        print(e)
    except KeyboardInterrupt:
        print(f"\n\nЧтение прервано (Ctrl+C)")

    print("\n == Программа успешно завершилась == ")


if __name__ == "__main__":
    main()