import os

"""

В этом файле будут храниться константы
для подключения к БД и другие технические данные настройки

"""

class ServerSettings:
    ENVIRONMENT = os.getenv('ENVIRONMENT', 'local')
    API_TAIL = os.getenv('API_TAIL', "/api/v1")

class DBSettings:
    """
    Данный класс хранит данные для подключения к БД
    """
    DB_PORT: str = os.getenv("DB_PORT", "5432") # порт
    DB_HOST: str = os.getenv("DB_HOST", "localhost") # хост базы данных
    DB_PASSWORD: str = os.getenv("DB_PASSWORD", "12345678") # пароль
    DB_USER: str = os.getenv("DB_USER", "postgres") # пользователь
    DB_NAME: str = os.getenv("DB_NAME", "postgres") # название базы
    DB_KIND: str = os.getenv("DB_KIND", "sqlite") # вид базы данных: Postgres | SQLite

    @classmethod
    @property
    def uri(cls) -> str:
        """
        Данный метод возвращает uri для подключения
        к БД PostgreSQL
        :return: uri: str
        """
        uri: str = f"postgresql+psycopg://{cls.DB_USER}:{cls.DB_PASSWORD}"\
               f"@{cls.DB_HOST}:{cls.DB_PORT}/{cls.DB_NAME}"
        if ServerSettings.ENVIRONMENT != 'local':
            uri += "?sslmode=require"
        return uri

