import os
import uuid



import dotenv


"""

В этом файле будут храниться константы
для подключения к БД и другие технические данные настройки

"""
DOT_ENV_PATH = "./.env"
if os.path.exists(DOT_ENV_PATH):
    dotenv.load_dotenv(DOT_ENV_PATH)


class ServerSettings:
    ENVIRONMENT = os.getenv('ENVIRONMENT', 'local')
    API_PATH = os.getenv('API_PATH', "/api/v1")
    HOST = os.getenv('HOST', '127.0.0.1')
    PORT = os.getenv('PORT', 8888)
    SECRET_KEY = os.getenv('SECRET_KEY') #str(uuid.uuid4().hex)
    SUPERUSER_EMAIL = os.getenv('SUPERUSER_EMAIL')
    SUPERUSER_PASSWORD = os.getenv('SUPERUSER_PASSWORD')
    SUPERUSER_FULL_NAME = os.getenv('SUPERUSER_FULL_NAME')


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

