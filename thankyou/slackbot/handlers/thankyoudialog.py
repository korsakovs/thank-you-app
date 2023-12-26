from slack_sdk.errors import SlackApiError
from slack_sdk.web import SlackResponse

from thankyou.dao import dao
from thankyou.slackbot.app import app
from thankyou.slackbot.blocks.thank_you import thank_you_message_blocks
from thankyou.slackbot.handlers.common import already_invited_to_a_channel
from thankyou.slackbot.utils.company import get_or_create_company_by_body
from thankyou.slackbot.utils.privatemetadata import retrieve_thank_you_message_from_body
from thankyou.slackbot.views.homepage import home_page_company_thank_yous_view


def thank_you_dialog_save_button_clicked_action_handler(body, logger):
    user_id = body["user"]["id"]
    company = get_or_create_company_by_body(body)

    thank_you_message = retrieve_thank_you_message_from_body(body)
    dao.create_thank_you_message(thank_you_message)

    if company.share_messages_in_slack_channel:
        def invite_users():
            slack_user_ids = [_receiver.slack_user_id for _receiver in thank_you_message.receivers
                              if not already_invited_to_a_channel(
                                company_id=company.uuid,
                                channel=company.share_messages_in_slack_channel,
                                user_id=_receiver.slack_user_id
                              )]
            if not slack_user_ids:
                return
            try:
                app.client.conversations_invite(
                    channel=company.share_messages_in_slack_channel,
                    users=slack_user_ids,
                    force=True
                )
            except SlackApiError:
                pass

        try:
            invite_users()
        except SlackApiError as err:
            response: SlackResponse = err.response
            data: dict = response.data
            if not data["ok"] and data["error"] == "not_in_channel":
                try:
                    app.client.conversations_join(
                        channel=company.share_messages_in_slack_channel,
                    )
                    invite_users()
                except SlackApiError as err2:
                    logger.err(err2)
            else:
                raise

        try:
            app.client.chat_postMessage(
                channel=company.share_messages_in_slack_channel,
                blocks=thank_you_message_blocks(thank_you_message)
            )
        except SlackApiError:
            pass

    for receiver in thank_you_message.receivers:
        try:
            app.client.chat_postMessage(
                text="You received a Thank You message!",
                channel=receiver.slack_user_id,
                blocks=thank_you_message_blocks(thank_you_message)
            )
        except SlackApiError:
            pass

    app.client.views_publish(
        user_id=user_id,
        view=home_page_company_thank_yous_view(
            thank_you_messages=dao.read_thank_you_messages(company_uuid=company.uuid, last_n=20),
            current_user_slack_id=user_id,
            enable_leaderboard=company.enable_leaderboard
        )
    )
