import random
import string


class Generates:
    """
        Класс для генерации данных.
    """

    # Функция генерирует рандомную латинскую строку
    @staticmethod
    def random_string(length=None):
        """
            Генерирует случайную латинскую строку.

            Если длина не указана, генерируется случайная длина от 2 до 100.
            Если длина указана, она должна быть в пределах от 2 до 100.

            Args:
                length (int, optional): Длина генерируемой строки.
                                        Должна быть между 2 и 100.

            Returns:
                str: Случайная строка, состоящая из латинских букв (верхнего и нижнего регистра).

            Raises:
                ValueError: Если указанная длина меньше 2 или больше 100.
        """
        if length is None:
            length = random.randint(2, 100)  # Генерируем случайную длину от 2 до 100
        else:
            if length < 2 or length > 100:
                raise ValueError("Length must be between 2 and 100")

        # Генерируем строку из латинских букв (как верхнего, так и нижнего регистра)
        letters = string.ascii_letters  # 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
        return ''.join(random.choice(letters) for _ in range(length))

# Пример использования
if __name__ == "__main__":
    print(Generates.random_string())  # Случайная строка длиной от 2 до 100
    print(Generates.random_string(10))  # Случайная строка длиной 10