import logging
from functools import wraps
import os
import shutil

log_path = "Logger/log_status"
if os.path.exists(log_path):
    try:
        shutil.rmtree(log_path)
        print(f"Папка '{log_path}' успешно очищена (удалена).")
    except OSError as e:
        print(f"Ошибка при удалении папки '{log_path}': {e}")
else:
    print(f"Папка '{log_path}' не существует, очистка не требуется.")

os.makedirs(log_path)

def logged(cls=None, *, name="", level=logging.INFO):
    def wrap(cls):
        logger_name = name or cls.__name__
        cls.log = logging.getLogger(logger_name)

        if not cls.log.handlers:
            file_handler = logging.FileHandler(f"Logger/log_status/{logger_name}.log", encoding='utf-8')
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            file_handler.setFormatter(formatter)
            cls.log.addHandler(file_handler)
            cls.log.setLevel(level)

        return cls

    return wrap if cls is None else wrap(cls)


def log_function_call(name="", level=logging.DEBUG):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            logger_name = name or f"app.{func.__module__}.{func.__name__}"
            log = logging.getLogger(logger_name)

            if not log.handlers:
                file_handler = logging.FileHandler(f"Logger/log_status/{logger_name}.log", encoding='utf-8')
                formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
                file_handler.setFormatter(formatter)
                log.addHandler(file_handler)
                log.setLevel(level)

            log.log(level, f"Вызов функции {func.__name__} с args: {args}, kwargs: {kwargs}")
            try:
                result = func(*args, **kwargs)
                log.log(level, f"Функция {func.__name__} завершена успешно. Результат: {result}")
                return result
            except Exception as e:
                log.exception(f"Ошибка в функции {func.__name__}: {e}")
                raise

        return wrapper

    return decorator