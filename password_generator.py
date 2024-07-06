from random import choice
from xkcdpass import xkcd_password


class XKCD:
    # Весь список разделителей, отдельно цифры, отдельно – спецсимволы
    delimiters_numbers = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"]
    delimiters_full = ["!", "$", "%", "^", "&", "*", "-", "_", "+", "=", ":", "|", "~", "?", "/", ".",
                       ";"] + delimiters_numbers

    def __init__(self, filename: str):
        # Загрузка словаря в память
        self.wordlist = xkcd_password.generate_wordlist(
            wordfile=filename, valid_chars="[a-z]",
            min_length=4, max_length=10,
        )

    def weak(self):
        # Слабый пароль: 2 слова без раздетилей
        return xkcd_password.generate_xkcdpassword(
            self.wordlist, numwords=2,
            delimiter="", )

    def normal(self):
        # Средний пароль: 3 слова, разделитель
        # в виде случайной цифры
        return xkcd_password.generate_xkcdpassword(
            self.wordlist, numwords=3, case="random", random_delimiters=True,
            valid_delimiters=self.delimiters_numbers
        )

    def strong(self):
        # Сильный пароль: 4 слова и большой выбор разделителей
        return xkcd_password.generate_xkcdpassword(
            self.wordlist, numwords=4, case="random", random_delimiters=True,
            valid_delimiters=self.delimiters_full
        )

    def custom(self, count: int, separators: bool, prefixes: bool):
        # Произвольный пароль:
        # сложность зависит от настроек пользователя
        pwd = xkcd_password.generate_xkcdpassword(
            self.wordlist, numwords=count, case="random",
            delimiter="", random_delimiters=separators,
            valid_delimiters=self.delimiters_full
        )
        if prefixes == separators:
            return pwd
        elif separators and not prefixes:
            return pwd[1:-1]
        elif prefixes and not separators:
            return f"{choice(self.delimiters_full)}{pwd}{choice(self.delimiters_full)}"
