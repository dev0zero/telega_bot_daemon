import psutil
import time
from tabulate import tabulate


class Status:
    def __init__(self):
        pass

    def answer(self):
        return f"👀 everything OK!" #{self.get_memory_usage()}"

    def get_cpu_usage(self):
        return psutil.cpu_percent(interval=1)

    def get_memory_usage(self):
        memory = psutil.virtual_memory()
        return {
            'Всего': f'{memory.total / (1024 ** 3):.2f} ГБ',
            'Используется': f'{memory.used / (1024 ** 3):.2f} ГБ',
            'Свободно': f'{memory.available / (1024 ** 3):.2f} ГБ',
            'Процент использования': f'{memory.percent}%'
        }

