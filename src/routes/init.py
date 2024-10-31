from ..middleware.users_middleware import UserWriter
from ..settings import ServerSettings


def init_superuser():
    try:
        UserWriter(
            email=ServerSettings.SUPERUSER_EMAIL,
            password=ServerSettings.SUPERUSER_PASSWORD,
            full_name=ServerSettings.SUPERUSER_FULL_NAME,
            is_superuser=True,
            is_active=True
        ).write()
    except Exception as e:
        pass

