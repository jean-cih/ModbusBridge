devices = [
    # --- TCP-устройства на разных IP-адресах ---
    {
        "name": "AnalogInputModul_TCP_Room1",
        "ip": "192.168.1.99",      # Другой IP-адрес
        "port": 502,
        "device_id": 1,           # Slave ID на этом TCP-сервере
        "type": "tcp"
    },
    {
        "name": "HumiditySensor_TCP_Server",
        "ip": "192.168.1.11",      # Еще один IP-адрес
        "port": 502,
        "device_id": 1,
        "type": "tcp"
    },
    # --- TCP-шлюз к нескольким Modbus RTU устройствам (разные device_id на одном IP/Port) ---
    {
        "name": "GatewayRTU_Device_A",
        "ip": "192.168.1.100",
        "port": 502,
        "device_id": 1,
        "type": "tcp"
    },
    {
        "name": "GatewayRTU_Device_B",
        "ip": "192.168.1.100",
        "port": 502,
        "device_id": 2,
        "type": "tcp"
    },
    # --- Modbus RTU устройства на разных COM-портах ---
    {
        "name": "PressureSensor_RTU_COM1",
        "port": "COM1",
        "baudrate": 9600,
        "bytesize": 8,
        "parity": 'N',
        "stopbits": 1,
        "device_id": 1,
        "type": "rtu"
    },
    {
        "name": "FlowMeter_RTU_COM2",
        "port": "COM2",
        "baudrate": 19200,
        "bytesize": 8,
        "parity": 'E',
        "stopbits": 1,
        "device_id": 1,
        "type": "rtu"
    },
    # --- Modbus RTU устройства на одном COM-порту, но с разными device_id (цепь) ---
    {
        "name": "MeasureModuleMicroprocessor_RTU_Slave1",
        "port": "COM5",
        "baudrate": 9600,
        "bytesize": 8,
        "parity": 'N',
        "stopbits": 1,
        "device_id": 2,
        "type": "rtu"
    },
    {
        "name": "AnalogInput_RTU_Slave2",
        "port": "COM4",
        "baudrate": 115200,
        "bytesize": 7,
        "parity": 'E',
        "stopbits": 2,
        "device_id": 2,
        "type": "rtu"
    },
    {
        "name": "DigitalOutput_RTU_Slave3",
        "port": "COM4",
        "baudrate": 115200,
        "bytesize": 8,
        "parity": 'O',
        "stopbits": 1,
        "device_id": 3,
        "type": "rtu"
    },
    {
        "name": "SpecialDevice_TCP_Port10000",
        "ip": "192.168.1.150",
        "port": 10000,
        "device_id": 1,
        "type": "tcp"
    },
# --- Modbus RTU устройство-динамометр на COM-порту ---
    {
        "name": "ElectroDynamometer_RTU",
        "port": "COM9",
        "baudrate": 9600,
        "bytesize": 8,
        "parity": 'O',
        "stopbits": 1,
        "device_id": 1,
        "type": "rtu"
    }
]
