import logging

from slack_bolt import App

from thankyou.core.config import slack_bot_token, get_env, Env

logging.basicConfig(level=logging.DEBUG if get_env() == Env.DEV else logging.INFO,
                    format="%(asctime)s %(levelname)s %(module)s - %(thread)d - %(message)s")

app = App(token=slack_bot_token())
