import logging

from slack_bolt.oauth.oauth_settings import OAuthSettings
from slack_sdk.oauth.installation_store.sqlalchemy import SQLAlchemyInstallationStore
from slack_sdk.oauth.state_store.sqlalchemy import SQLAlchemyOAuthStateStore

from thankyou.core.config import slack_client_id, slack_client_secret, required_slack_app_permissions
from thankyou.dao import dao
from thankyou.dao.sqlalchemy import SQLAlchemyDao


def get_installation_store(client_id: str):
    if isinstance(dao, SQLAlchemyDao):
        return SQLAlchemyInstallationStore(
            engine=dao.engine,
            client_id=client_id
        )
    else:
        raise TypeError(f"An installation store for the Dao type {type(dao)} can not be created")


def get_oauth_state_store():
    if isinstance(dao, SQLAlchemyDao):
        return SQLAlchemyOAuthStateStore(
            expiration_seconds=600,
            engine=dao.engine,
        )
    else:
        raise TypeError(f"An OAuth state store for the Dao type {type(dao)} can not be created")


oauth_settings = None

if slack_client_id() and slack_client_secret():
    oauth_settings = OAuthSettings(
        client_id=slack_client_id(),
        client_secret=slack_client_secret(),
        scopes=required_slack_app_permissions(),
        installation_store=get_installation_store(slack_client_id()),
        state_store=get_oauth_state_store()
    )
