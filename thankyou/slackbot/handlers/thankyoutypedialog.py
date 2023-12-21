from thankyou.core.models import ThankYouType
from thankyou.dao import dao
from thankyou.slackbot.app import app
from thankyou.slackbot.utils.company import get_or_create_company_by_body
from thankyou.slackbot.utils.privatemetadata import PrivateMetadata
from thankyou.slackbot.views.configuration import configuration_view
from thankyou.slackbot.views.thankyoutypedialog import thank_you_type_deletion_confirmation_dialog, \
    thank_you_type_deletion_completion_dialog


def thank_you_type_dialog_save_button_clicked_action_handler(body, logger):
    user_id = body["user"]["id"]
    company = get_or_create_company_by_body(body)

    new_value_name = body["view"]["state"]["values"]["thank_you_type_dialog_value_name_block"][
        "thank_you_type_dialog_value_name_action"]["value"]

    company_value_uuid = PrivateMetadata.from_str(body["view"]["private_metadata"]).thank_you_type_uuid

    if company_value_uuid:
        company_value = dao.read_thank_you_type(company_uuid=company.uuid, thank_you_type_uuid=company_value_uuid)
        company_value.name = new_value_name
    else:
        dao.create_thank_you_type(thank_you_type=ThankYouType(
            company_uuid=company.uuid,
            name=new_value_name
        ))

    app.client.views_publish(
        user_id=user_id,
        view=configuration_view(
            thank_you_types=dao.read_thank_you_types(company_uuid=company.uuid),
            admin_slack_user_ids=[admin.slack_user_id for admin in company.admins],
            leaderbord_time_settings=company.leaderbord_time_settings,
            share_messages_in_slack_channel=company.share_messages_in_slack_channel,
            weekly_thank_you_limit=company.weekly_thank_you_limit,
            enable_rich_text_in_thank_you_messages=company.enable_rich_text_in_thank_you_messages,
            enable_leaderboard=company.enable_leaderboard,
            enable_company_values=company.enable_company_values,
            max_thank_you_receivers_num=company.receivers_number_limit,
        )
    )


def thank_you_type_dialog_delete_value_button_clicked_action_handler(body, logger):
    company = get_or_create_company_by_body(body)
    thank_you_type_uuid = body["actions"][0]["value"]

    app.client.views_update(
        view_id=body["view"]["id"],
        view=thank_you_type_deletion_confirmation_dialog(thank_you_type=dao.read_thank_you_type(
            company_uuid=company.uuid,
            thank_you_type_uuid=thank_you_type_uuid
        ))
    )


def thank_you_type_deletion_dialog_confirm_deletion_button_clicked_action_handler(body, logger):
    user_id = body["user"]["id"]
    company = get_or_create_company_by_body(body)

    thank_you_type_uuid = PrivateMetadata.from_str(body["view"]["private_metadata"]).thank_you_type_uuid
    thank_you_type_name = dao.read_thank_you_type(
        company_uuid=company.uuid, thank_you_type_uuid=thank_you_type_uuid).name

    dao.delete_thank_you_type(company_uuid=company.uuid, thank_you_type_uuid=thank_you_type_uuid)

    app.client.views_open(
        trigger_id=body["trigger_id"],
        view=thank_you_type_deletion_completion_dialog(thank_you_type_name=thank_you_type_name)
    )

    app.client.views_publish(
        user_id=user_id,
        view=configuration_view(
            thank_you_types=dao.read_thank_you_types(company_uuid=company.uuid),
            admin_slack_user_ids=[admin.slack_user_id for admin in company.admins],
            leaderbord_time_settings=company.leaderbord_time_settings,
            share_messages_in_slack_channel=company.share_messages_in_slack_channel,
            weekly_thank_you_limit=company.weekly_thank_you_limit,
            enable_rich_text_in_thank_you_messages=company.enable_rich_text_in_thank_you_messages,
            enable_leaderboard=company.enable_leaderboard,
            enable_company_values=company.enable_company_values,
            max_thank_you_receivers_num=company.receivers_number_limit,
        )
    )
