from thankyou.dao import dao
from thankyou.slackbot.app import app
from thankyou.slackbot.handlers.common import get_user_info
from thankyou.slackbot.utils.company import get_or_create_company_by_body
from thankyou.slackbot.utils.privatemetadata import retrieve_thank_you_message_from_body
from thankyou.slackbot.views.homepage import home_page_company_thank_yous_view


def thank_you_dialog_save_button_clicked_action_handler(body, logger):
    thank_you_message = retrieve_thank_you_message_from_body(body)
    dao.create_thank_you_message(thank_you_message)

    user_id = body["user"]["id"]
    user_info = get_user_info(user_id)
    company = get_or_create_company_by_body(body)

    app.client.views_publish(
        user_id=user_id,
        view=home_page_company_thank_yous_view(
            thank_you_messages=dao.read_thank_you_messages(company_uuid=company.uuid, last_n=20),
            is_admin=user_info.is_admin,
            current_user_slack_id=user_id,
            enable_leaderboard=company.enable_leaderboard
        )
    )
