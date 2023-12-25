from datetime import datetime, timedelta

from thankyou.dao import dao
from thankyou.slackbot.app import app
from thankyou.slackbot.utils.company import get_or_create_company_by_body
from thankyou.slackbot.views.thankyoudialog import thank_you_dialog_view


def merci_slash_command_action_handler(body, logger):
    company = get_or_create_company_by_body(body)
    user_id = body["user_id"]

    beginning_of_the_week = (datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
                             - timedelta(days=datetime.utcnow().weekday()))
    end_of_the_week = beginning_of_the_week + timedelta(days=7)
    sent_messages_num = len(dao.read_thank_you_messages(
        company_uuid=company.uuid,
        author_slack_user_id=user_id,
        created_after=beginning_of_the_week,
        created_before=end_of_the_week
    ))

    if company.enable_weekly_thank_you_limit:
        num_of_messages_a_user_can_send = max(0, company.weekly_thank_you_limit - sent_messages_num)
    else:
        num_of_messages_a_user_can_send = None

    try:
        app.client.views_open(
            trigger_id=body["trigger_id"],
            view=thank_you_dialog_view(
                thank_you_types=dao.read_thank_you_types(company_uuid=company.uuid),
                enable_rich_text=company.enable_rich_text_in_thank_you_messages,
                enable_company_values=company.enable_company_values,
                max_receivers_num=company.receivers_number_limit,
                enable_attaching_files=company.enable_attaching_files,
                max_attached_files_num=company.max_attached_files_num,
                num_of_messages_a_user_can_send=num_of_messages_a_user_can_send,
            ),
        )
    except Exception as e:
        logger.error(f"Error publishing home tab: {e}")
