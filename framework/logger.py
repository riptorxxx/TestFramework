import logging


#Создаём логер
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# обработчик для вывода в консоль
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)

# Форматирование
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
console_handler.setFormatter(formatter)

# Добавляем обработчик к логеру
logger.addHandler(console_handler)