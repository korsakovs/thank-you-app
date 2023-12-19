from thankyou.dao import dao
from thankyou.slackbot.app import app
from thankyou.slackbot.utils.company import get_or_create_company_by_body
from thankyou.slackbot.views.configuration import configuration_view


def home_page_configuration_button_clicked_action_handler(body, logger):
    logger.info(body)
    user_id = body["user"]["id"]
    company = get_or_create_company_by_body(body)

    app.client.views_publish(
        user_id=user_id,
        view=configuration_view(thank_you_types=dao.read_thank_you_types(company_uuid=company.uuid))
    )
