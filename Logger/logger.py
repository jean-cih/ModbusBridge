import logging


def logged(cls=None, *, name="", level=logging.INFO):
    def wrap(cls):
        cls.log = logging.getLogger(name or cls.__name__)
        cls.log.setLevel(level)

        log_handler = logging.FileHandler(f"log_status/{name or cls.__name__}.log",
                                          mode="w", encoding="utf-8")
        log_formatter = logging.Formatter("%(name)s %(asctime)s %(levelname)s %(message)s")

        log_handler.setFormatter(log_formatter)
        cls.log.addHandler(log_handler)
        return cls
    return wrap if cls is None else wrap(cls)

