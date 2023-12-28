import logging
import os
from enum import Enum


def _demand_env_variable(name: str) -> str:
    result = os.getenv(name)
    if result is None:
        raise EnvironmentError(f"{name} env variable is not set. Please, set it and relaunch this app.")
    return result


def slack_bot_token() -> str:
    return _demand_env_variable("SLACK_BOT_TOKEN")


def slack_app_token() -> str:
    return _demand_env_variable("SLACK_APP_TOKEN")


class Env(Enum):
    DEV = 1
    PROD = 2


def get_env(default=Env.DEV) -> Env:
    try:
        return Env[os.getenv("THANK_YOU_ENV", "").upper().strip()]
    except KeyError:
        return default


class DaoType(Enum):
    SQLITE = 1
    POSTGRES = 2


def get_active_dao_type(default=DaoType.POSTGRES) -> DaoType:
    logging.info("THANK_YOU_DAO ENV = " + os.getenv("THANK_YOU_DAO", ""))
    try:
        return DaoType[os.getenv("THANK_YOU_DAO", "").upper().strip()]
    except KeyError:
        return default


INITIAL_THANK_YOU_TYPES = [
    "🎉 Release",
    "🚀 Launch",
    "📄 RFC",
]
