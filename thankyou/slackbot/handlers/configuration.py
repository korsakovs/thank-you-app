from slack_sdk import WebClient

from thankyou.slackbot.app import app
from thankyou.slackbot.handlers.common import get_user_info
from thankyou.slackbot.utils.company import get_or_create_company_by_body
from thankyou.slackbot.views.configuration import configuration_view


def home_page_configuration_button_clicked_action_handler(body, logger):
    logger.info(body)
    user_id = body["user"]["id"]
    user_info = get_user_info(user_id)
    company = get_or_create_company_by_body(body)

    app.client.views_publish(
        user_id=user_id,
        view=configuration_view()
    )
