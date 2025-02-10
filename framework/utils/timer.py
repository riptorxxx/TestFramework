import time
from functools import wraps
from tests.api.api_client import logger

def timer(func):
    """Декоратор для замера времени выполнения функции"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.perf_counter_ns()  # Наносекунды для еще большей точности
        result = func(*args, **kwargs)
        end_time = time.perf_counter_ns()
        execution_time = (end_time - start_time) / 1_000_000_000  # Конвертируем в секунды
        logger.info(f"Время выполнения {func.__name__}: {execution_time:.6f} секунд")
        return result
    return wrapper


