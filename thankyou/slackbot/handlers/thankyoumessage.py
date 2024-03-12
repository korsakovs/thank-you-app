import validators
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from slack_sdk.models.blocks import SectionBlock
from slack_sdk.models.views import View

from thankyou.dao import dao
from thankyou.slackbot.utils.company import get_or_create_company_by_body
from thankyou.slackbot.utils.employee import get_or_create_employee_by_slack_user_id
from thankyou.slackbot.utils.privatemetadata import PrivateMetadata
from thankyou.slackbot.views.homepage import home_page_company_thank_yous_view
from thankyou.slackbot.views.thanksbackdialog import thanks_back_dialog_view
from thankyou.slackbot.views.thankyoudialog import thank_you_dialog_view


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


def thank_you_message_overflow_menu_clicked_handler(client, body, logger):
    company = get_or_create_company_by_body(body)
    user_id = body["user"]["id"]

    action, message_id = str(body["actions"][0]["selected_option"]["value"]).split(":", 1)
    message = dao.read_thank_you_message(company.uuid, message_id)

    if not message:
        logger.error(f"Could not find a message {message_id} for company {company.uuid}")
        return

    can_edit = (user_id == message.author_slack_user_id) \
        or (user_id in [admin.slack_user_id for admin in company.admins])
    can_delete = (user_id == message.author_slack_user_id) \
        or (user_id in [admin.slack_user_id for admin in company.admins])

    if action == "edit":
        if can_edit:
            if message.images:
                if not validators.url(message.sorted_images[0].url):
                    for image in message.images:
                        dao.delete_thank_you_image(image)
                    message.images = []
            try:
                client.views_open(trigger_id=body["trigger_id"], view=thank_you_dialog_view(
                    app_name=company.merci_app_name,
                    state=message,
                    thank_you_types=dao.read_thank_you_types(company_uuid=company.uuid),
                    enable_rich_text=company.enable_rich_text_in_thank_you_messages,
                    enable_company_values=company.enable_company_values,
                    max_receivers_num=company.receivers_number_limit,
                    enable_attaching_files=company.enable_attaching_files,
                    max_attached_files_num=company.max_attached_files_num,
                    display_private_message_option=company.enable_private_messages,
                ))
            except Exception as e:
                logger.error(f"Error publishing home tab: {e}")
        else:
            client.views_open(
                trigger_id=body["trigger_id"],
                view=View(
                    type="modal",
                    title="Permission denied",
                    blocks=[
                        SectionBlock(
                            text=f"You cannot edit this message. Only the author and administrators can do it."
                        )
                    ]
                ),
            )
    elif action == "delete":
        if can_delete:
            client.views_open(
                trigger_id=body["trigger_id"],
                view=View(
                    type="modal",
                    callback_id="thank_you_deletion_dialog_delete_button_clicked",
                    title="Are you sure?",
                    submit="Delete",
                    close="Cancel",
                    private_metadata=PrivateMetadata(thank_you_message_uuid=message.uuid).as_str(),
                    blocks=[
                        SectionBlock(
                            text=f"Are you sure you want to delete this message? This operation can not be undone"
                        )
                    ]
                ),
            )
        else:
            client.views_open(
                trigger_id=body["trigger_id"],
                view=View(
                    type="modal",
                    title="Permission denied",
                    blocks=[
                        SectionBlock(
                            text=f"You cannot delete this message. Only the author and administrators can do it."
                        )
                    ]
                ),
            )
    else:
        logger.error(f"Unknown message action: {action}")


def thank_you_deletion_dialog_delete_button_clicked(client: WebClient, body, logger):
    company = get_or_create_company_by_body(body)
    user_id = body["user"]["id"]
    employee = get_or_create_employee_by_slack_user_id(company_uuid=company.uuid, slack_user_id=user_id)

    message_uuid = PrivateMetadata.from_str(body["view"]["private_metadata"]).thank_you_message_uuid
    message = dao.read_thank_you_message(company_uuid=company.uuid, thank_you_message_uuid=message_uuid)

    if not message:
        logger.error(f"Can not find message {message_uuid} from company {company.uuid}")
        return

    if message.deleted:
        client.views_open(
            trigger_id=body["trigger_id"],
            view=View(
                type="modal",
                title="Deleted",
                blocks=[
                    SectionBlock(text="The message you're trying to delete doesn't exist. Maybe you've already "
                                      "deleted it?")
                ]
            ),
        )
        return

    try:
        for slack_delivery in message.slack_deliveries:
            if not slack_delivery.deleted:
                try:
                    client.chat_delete(
                        channel=slack_delivery.slack_channel_id,
                        ts=slack_delivery.message_ts,
                    )
                except SlackApiError as api_error:
                    if api_error.response["error"] != "message_not_found":
                        raise
                slack_delivery.deleted = True
        dao.delete_thank_you_message(thank_you_message_uuid=message_uuid)
    except Exception as e:
        logger.error(f"Could not delete a message {message.uuid} for company {company.uuid}: {e}")
        deleted = False
    else:
        deleted = True

    if deleted:
        text = "The message was successfully deleted"
    else:
        text = "The message was not deleted due to an internal error. Please, try again later"

    client.views_open(
        trigger_id=body["trigger_id"],
        view=View(
            type="modal",
            title="Deleted",
            blocks=[
                SectionBlock(text=text)
            ]
        ),
    )

    client.views_publish(
        user_id=user_id,
        view=home_page_company_thank_yous_view(
            thank_you_messages=dao.read_thank_you_messages(company_uuid=company.uuid, last_n=20, private=False),
            app_name=company.merci_app_name,
            current_user_slack_id=user_id,
            enable_leaderboard=company.enable_leaderboard,
            show_welcome_message=not employee.closed_welcome_message
        )
    )
