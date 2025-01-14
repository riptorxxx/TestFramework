import functools
import testit


class TestErrorHandler:
    """
    Класс для обработки ошибок в тестовых и вспомогательных методах.

    Предоставляет декоратор для автоматической обработки исключений
    и логирования ошибок в TestIT.

    Обрабатывает:
        - Тестовые методы (начинающиеся с `test_`)
        - Вспомогательные методы (начинающиеся с `_`)
    """

    @staticmethod
    def handle_test_errors(cls):
        """
        Декоратор класса для обработки ошибок во всех тестовых методах.

        Этот декоратор оборачивает все методы класса, начинающиеся с
        `test_`, и применяет обработчик тестовых ошибок. Также обрабатываются
        вспомогательные методы, начинающиеся с `_`.

        Args:
            cls: Тестовый класс, к которому применяется декоратор.

        Returns:
            type: Модифицированный класс с обработкой ошибок во всех тестовых методах.
        """

        for attr_name, attr_value in cls.__dict__.items():
            if callable(attr_value):  # Handle all callable methods
                if attr_name.startswith('test_'):
                    # For test methods
                    setattr(cls, attr_name, TestErrorHandler._wrap_test_method(attr_value))
                elif attr_name.startswith('_'):
                    # For helper methods
                    setattr(cls, attr_name, TestErrorHandler._wrap_helper_method(attr_value))
        return cls


    @staticmethod
    def _wrap_test_method(method):
        """
        Оборачивает тестовый метод в обработчик ошибок.

        Обрабатываемые исключения:
            - ValueError: ошибки валидации.
            - AssertionError: ошибки проверок.
            - Exception: все остальные ошибки.

        Все ошибки логируются в TestIT и затем пробрасываются дальше.

        Args:
            method (callable): Тестовый метод для обработки.

        Returns:
            callable: Обёрнутый метод с обработкой ошибок.
        """

        @functools.wraps(method)
        def wrapper(*args, **kwargs):
            try:
                return method(*args, **kwargs)
            except ValueError as ve:
                testit.addMessage(f"Ошибка валидации: {str(ve)}")
                raise
            except AssertionError as ae:
                testit.addMessage(f"Ошибка проверки: {str(ae)}")
                raise
            except Exception as e:
                testit.addMessage(f"Непредвиденная ошибка: {str(e)}")
                raise

        return wrapper


    @staticmethod
    def _wrap_helper_method(method):
        """
        Оборачивает вспомогательный метод в обработчик ошибок.

        Обрабатываемые исключения:
            - ValueError: ошибки валидации.
            - AttributeError: ошибки доступа к атрибутам.
            - KeyError: ошибки отсутствующих ключей.
            - Exception: все остальные ошибки.

        Особенности:
            - Добавляет имя метода в сообщение об ошибке.
            - Предоставляет детальную информацию для отладки.

        Args:
            method (callable): Вспомогательный метод для обработки.

        Returns:
            callable: Обёрнутый метод с обработкой ошибок.
        """

        @functools.wraps(method)
        def wrapper(*args, **kwargs):
            try:
                return method(*args, **kwargs)
            except ValueError as ve:
                testit.addMessage(f"Ошибка валидации в методе {method.__name__}: {str(ve)}")
                raise
            except AttributeError as ae:
                testit.addMessage(f"Ошибка доступа к атрибутам в методе {method.__name__}: {str(ae)}")
                raise
            except KeyError as ke:
                testit.addMessage(f"Отсутствует обязательный параметр в методе {method.__name__}: {str(ke)}")
                raise
            except Exception as e:
                testit.addMessage(f"Непредвиденная ошибка в методе {method.__name__}: {str(e)}")
                raise

        return wrapper
