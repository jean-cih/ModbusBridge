'''
Регистры обмена по протоколу ModBus

У меня тип датчика 35 - Pt1000 (α = 0,00385 °С-1)

Регистры приведены для первого канала
'''
registers_sensor_MB210_101 = [
    {
        "name": "Значение (float) на входе",
        "description": "—",
        "access": "Только чтение",
        "data_type": "FLOAT 32",
        "address": 4000
    },
    {
        "name": "Циклическое время измерения входа",
        "description": "0...65535 (миллисекунд)",
        "access": "Только чтение",
        "data_type": "UINT 16",
        "address": 4002
    },
    {
        "name": "Значение (integer) на входе",
        "description": "—",
        "access": "Только чтение",
        "data_type": "INT 16",
        "address": 4064
    },
    {
        "name": "Тип датчика входа",
        "description": "см. таблицу 6.4",
        "access": "Чтение и запись",
        "data_type": "UINT 32",
        "address": 4100
    },
    {
        "name": "Полоса фильтра входа",
        "description": "0…100",
        "access": "Чтение и запись",
        "data_type": "UINT 16",
        "address": 4102
    },
    {
        "name": "Положение десятичной точки входа",
        "description": "0…7",
        "access": "Чтение и запись",
        "data_type": "UINT 16",
        "address": 4103
    },
    {
        "name": "Сдвиг характеристики входа",
        "description": "–10000…10000",
        "access": "Чтение и запись",
        "data_type": "FLOAT 32",
        "address": 4104
    },
    {
        "name": "Наклон характеристики входа",
        "description": "–1…10",
        "access": "Чтение и запись",
        "data_type": "FLOAT 32",
        "address": 4106
    },
    {
        "name": "AIN.H верхняя граница входа",
        "description": "–10000…10000",
        "access": "Чтение и запись",
        "data_type": "FLOAT 32",
        "address": 4108
    },
    {
        "name": "AIN.L нижняя граница входа",
        "description": "–10000…10000",
        "access": "Чтение и запись",
        "data_type": "FLOAT 32",
        "address": 4110
    },
    {
        "name": "Постоянная времени фильтра входа",
        "description": "0…65535",
        "access": "Чтение и запись",
        "data_type": "UINT 16",
        "address": 4112
    },
    {
        "name": "Период измерения входа",
        "description": "600…10000 (миллисекунд)",
        "access": "Чтение и запись",
        "data_type": "UINT 16",
        "address": 4113
    }
]

registers_sensor_TPM10 = [
    {
        "name": "Измеренная величина",
        "description": "—",
        "access": "Только чтение",
        "data_type": "FLOAT 32",
        "address": 0
    },
    {
        "name": "Входная величина",
        "description": "—",
        "access": "Только чтение",
        "data_type": "FLOAT 32",
        "address": 2
    },
    {
        "name": "Тип датчика на входе",
        "description": "см. таблицу значений",
        "access": "Чтение и запись",
        "data_type": "UINT 16",
        "address": 4
    },
    {
        "name": "Полоса фильтра входа",
        "description": "—",
        "access": "Чтение и запись",
        "data_type": "FLOAT 32",
        "address": 5
    },
    {
        "name": "Постоянная времени фильтра",
        "description": "0...65535",
        "access": "Чтение и запись",
        "data_type": "UINT 16",
        "address": 7
    },
    {
        "name": "Положение десятичной точки",
        "description": "см. таблицу значений",
        "access": "Чтение и запись",
        "data_type": "UINT 16",
        "address": 8
    },
    {
        "name": "Нижний порог предупреждения",
        "description": "—",
        "access": "Чтение и запись",
        "data_type": "FLOAT 32",
        "address": 9
    },
    {
        "name": "Верхний порог предупреждения",
        "description": "—",
        "access": "Чтение и запись",
        "data_type": "FLOAT 32",
        "address": 11
    },
    {
        "name": "Тип функции для входа",
        "description": "см. таблицу значений",
        "access": "Чтение и запись",
        "data_type": "UINT 16",
        "address": 13
    },
    {
        "name": "Период выборки",
        "description": "0...65535",
        "access": "Чтение и запись",
        "data_type": "UINT 16",
        "address": 18
    },
    {
        "name": "Динамический диапазон",
        "description": "—",
        "access": "Чтение и запись",
        "data_type": "FLOAT 32",
        "address": 19
    },
    {
        "name": "Подключение источника",
        "description": "см. таблицу значений",
        "access": "Чтение и запись",
        "data_type": "UINT 16",
        "address": 21
    }
]