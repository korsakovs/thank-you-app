from datetime import datetime, timedelta

from thankyou.dao import dao
from thankyou.slackbot.utils.company import get_or_create_company_by_body
from thankyou.slackbot.views.thankyoudialog import thank_you_dialog_view


def merci_slash_command_action_handler(body, client, logger):
    company = get_or_create_company_by_body(body)
    user_id = body["user_id"]

    logger.debug(f"Received a new slash command. Channel ID: {body.get('channel_id')} Body: {body}")
    try:
        channel_id = body["channel_id"]
        if channel_id[0] != "C":
            logger.warning(f"The channel id received as a result of sending a slash command is weird: {channel_id}")
            # channel_id = None
    except (TypeError, KeyError):
        logger.warning("Could not find channel id in the message body received as a result of sending a slash command")
        channel_id = None

    if company.enable_weekly_thank_you_limit:
        beginning_of_the_week = (datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
                                 - timedelta(days=datetime.utcnow().weekday()))
        end_of_the_week = beginning_of_the_week + timedelta(days=7)
        sent_messages_num = len(dao.read_thank_you_messages(
            company_uuid=company.uuid,
            author_slack_user_id=user_id,
            created_after=beginning_of_the_week,
            created_before=end_of_the_week
        ))
        num_of_messages_a_user_can_send = max(0, company.weekly_thank_you_limit - sent_messages_num)
    else:
        num_of_messages_a_user_can_send = None

    try:
        client.views_open(
            trigger_id=body["trigger_id"],
            view=thank_you_dialog_view(
                app_name=company.merci_app_name,
                thank_you_types=dao.read_thank_you_types(company_uuid=company.uuid),
                enable_rich_text=company.enable_rich_text_in_thank_you_messages,
                enable_company_values=company.enable_company_values,
                max_receivers_num=company.receivers_number_limit,
                enable_attaching_files=company.enable_attaching_files,
                max_attached_files_num=company.max_attached_files_num,
                num_of_messages_a_user_can_send=num_of_messages_a_user_can_send,
                slash_command_slack_channel_id=channel_id,
                display_private_message_option=company.enable_private_messages,
            ),
        )
    except Exception as e:
        logger.error(f"Error publishing home tab: {e}")
