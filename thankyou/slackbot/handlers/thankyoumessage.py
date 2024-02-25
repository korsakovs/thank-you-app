from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from slack_sdk.models.blocks import SectionBlock
from slack_sdk.models.views import View

from thankyou.dao import dao
from thankyou.slackbot.utils.company import get_or_create_company_by_body
from thankyou.slackbot.utils.privatemetadata import PrivateMetadata
from thankyou.slackbot.views.thanksbackdialog import thanks_back_dialog_view


def thank_you_message_say_thanks_button_clicked_handler(body, client, logger):
    company = get_or_create_company_by_body(body)
    user_id = body["user"]["id"]

    message_uuid = body["actions"][0]["value"]
    message = dao.read_thank_you_message(company_uuid=company.uuid, thank_you_message_uuid=message_uuid)

    if not message:
        logger.error(f"Could not find message {message.uuid} of company id {company.uuid}")
        return

    if user_id not in [r.slack_user_id for r in message.receivers]:
        logger.error(f"USER ID {user_id} not in message receivers. Message id = {message.uuid} "
                     f"Receivers = {[r.slack_user_id for r in message.receivers]} Company ID = {company.uuid}")
        return

    client.views_open(
        trigger_id=body["trigger_id"],
        view=thanks_back_dialog_view(
            thank_you_message_uuid=message.uuid,
            author_slack_user_id=message.author_slack_user_id
        )
    )


def thanks_back_dialog_send_button_clicked_handler(body, client: WebClient, logger):
    company = get_or_create_company_by_body(body)
    user_id = body["user"]["id"]

    thank_you_message_uuid = PrivateMetadata.from_str(body["view"]["private_metadata"]).thank_you_message_uuid
    thank_you_message = dao.read_thank_you_message(company_uuid=company.uuid,
                                                   thank_you_message_uuid=thank_you_message_uuid)

    try:
        thanks_back_text = body["view"]["state"]["values"]["thanks_back_dialog_input_block"][
            "thanks_back_dialog_input_block_action"]["value"]
    except (TypeError, KeyError):
        logger.error(f"Could not find a text in the text back dialog data: {body}")
        return

    if not thank_you_message:
        logger.error(f"Could not find message {thank_you_message_uuid} for company {company.uuid}")
        return

    client.chat_postMessage(
        channel=thank_you_message.author_slack_user_id,
        text=f"<@{user_id}> thanks you for a thank you message you previously sent to them. "
             f"This is what they say:\n\n"
             f"{thanks_back_text}"
    )

    try:
        client.views_open(
            trigger_id=body["trigger_id"],
            view=View(
                title="Done!",
                type="modal",
                blocks=[
                    SectionBlock(
                        text=f"Your message (_{thanks_back_text[0:20]}_...) was successfully sent! Thank you!"
                    )
                ]
            )
        )
    except SlackApiError as e:
        if e.response["error"] != "expired_trigger_id":
            logger.warning(f"Could not notify user {user_id} (Company id = {company.uuid}) about the fact that their "
                           f"thank you back message was sent - can't open a dialog view: {e}")
        try:
            client.chat_postMessage(
                channel=user_id,
                text=f"Your message (_{thanks_back_text[0:20]}_...) was successfully sent! Thank you!"
            )
        except SlackApiError as e:
            logger.error(f"Could not notify user {user_id} (Company id = {company.uuid}) about the fact that their "
                         f"thank you back message was sent - can't send a private message: {e}")
