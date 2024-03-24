import logging
import os
from enum import Enum
from typing import Optional, List


def _demand_env_variable(name: str) -> str:
    result = os.getenv(name)
    if result is None:
        raise EnvironmentError(f"{name} env variable is not set. Please, set it and relaunch this app.")
    return result


def slack_bot_token() -> Optional[str]:
    return os.getenv("SLACK_BOT_TOKEN")


def slack_app_token() -> Optional[str]:
    return os.getenv("SLACK_APP_TOKEN")


def slack_client_id() -> Optional[str]:
    return os.getenv("SLACK_CLIENT_ID")


def slack_client_secret() -> Optional[str]:
    return os.getenv("SLACK_CLIENT_SECRET")


def slack_signing_secret() -> Optional[str]:
    return os.getenv("SLACK_SIGNING_SECRET")


def required_slack_app_permissions() -> List[str]:
    return [
        "channels:join",  # Join public channels in a workspace
        "channels:write.invites",  # Invite members to public channels
        "chat:write",  # Send messages as @Merci App
        "chat:write.public",  # Send messages to channels @Merci App isn't a member of
        "commands",  # Add shortcuts and/or slash commands that people can use
        "files:read",  # View files shared in channels and conversations that [DEV] Merci App has been added to
        "im:write",  # Start direct messages with people
        "users.profile:read",  # View profile details about people in a workspace
        "users:read",  # View people in a workspace
    ]


class Env(Enum):
    DEV = 1
    PROD = 2


def get_env(default=Env.DEV) -> Env:
    try:
        return Env[os.getenv("MERCI_ENV", "").upper().strip()]
    except KeyError:
        return default


class DaoType(Enum):
    SQLITE = 1
    POSTGRES = 2


def get_active_dao_type(default=DaoType.POSTGRES) -> DaoType:
    logging.info("THANK_YOU_DAO = " + os.getenv("THANK_YOU_DAO", ""))
    try:
        return DaoType[os.getenv("THANK_YOU_DAO", "").upper().strip()]
    except KeyError:
        return default


def database_encryption_secret_key(default=None) -> Optional[str]:
    secret_key = os.getenv("DATABASE_ENCRYPTION_SECRET_KEY", default)
    if secret_key == "":
        secret_key = default
    return secret_key


INITIAL_THANK_YOU_TYPES = [
    "🎉 Collaboration",
    "🚀 Innovation",
    "🌐 Ethical Responsibility",
]
