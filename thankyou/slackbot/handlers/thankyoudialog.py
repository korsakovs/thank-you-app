from thankyou.dao import dao
from thankyou.slackbot.app import app
from thankyou.slackbot.blocks.thank_you import thank_you_message_blocks
from thankyou.slackbot.utils.company import get_or_create_company_by_body
from thankyou.slackbot.utils.privatemetadata import retrieve_thank_you_message_from_body
from thankyou.slackbot.views.homepage import home_page_company_thank_yous_view


def thank_you_dialog_save_button_clicked_action_handler(body, logger):
    user_id = body["user"]["id"]
    company = get_or_create_company_by_body(body)

    thank_you_message = retrieve_thank_you_message_from_body(body)
    dao.create_thank_you_message(thank_you_message)

    if company.share_messages_in_slack_channel:
        app.client.chat_postMessage(
            channel=company.share_messages_in_slack_channel,
            blocks=thank_you_message_blocks(thank_you_message)
        )

    for receiver in thank_you_message.receivers:
        app.client.chat_postMessage(
            text="You received a Thank You message!",
            channel=receiver.slack_user_id,
            blocks=thank_you_message_blocks(thank_you_message)
        )

    app.client.views_publish(
        user_id=user_id,
        view=home_page_company_thank_yous_view(
            thank_you_messages=dao.read_thank_you_messages(company_uuid=company.uuid, last_n=20),
            current_user_slack_id=user_id,
            enable_leaderboard=company.enable_leaderboard
        )
    )
