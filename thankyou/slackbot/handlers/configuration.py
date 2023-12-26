from thankyou.core.models import CompanyAdmin, LeaderbordTimeSettings
from thankyou.dao import dao
from thankyou.slackbot.app import app
from thankyou.slackbot.handlers.common import publish_configuration_view
from thankyou.slackbot.utils.company import get_or_create_company_by_body
from thankyou.slackbot.views.thankyoutypedialog import thank_you_type_dialog


def home_page_configuration_button_clicked_action_handler(body, logger):
    logger.info(body)
    publish_configuration_view(
        company=get_or_create_company_by_body(body),
        user_id=body["user"]["id"]
    )


def home_page_configuration_admin_slack_user_ids_value_changed_action_handler(body, logger):
    logger.info(body)
    user_id = body["user"]["id"]
    company = get_or_create_company_by_body(body)

    selected_slack_user_ids = body["actions"][0]["selected_users"]

    admins_to_remove = [admin for admin in company.admins if admin.slack_user_id not in selected_slack_user_ids]
    admins_to_add = [CompanyAdmin(slack_user_id=slack_user_id, company_uuid=company.uuid)
                     for slack_user_id in selected_slack_user_ids
                     if slack_user_id not in [admin.slack_user_id for admin in company.admins]]

    for admin in admins_to_remove:
        dao.delete_company_admin(company_uuid=company.uuid, slack_user_id=admin.slack_user_id)
    for admin in admins_to_add:
        dao.create_company_admin(admin)

    company = dao.read_company(company_uuid=company.uuid)

    publish_configuration_view(
        company=company,
        user_id=user_id
    )


def home_page_configuration_notification_slack_channel_value_changed_action_handler(body, logger):
    logger.info(body)
    user_id = body["user"]["id"]
    company = get_or_create_company_by_body(body)

    channel_slack_id = body["actions"][0]["selected_channel"]
    if company.share_messages_in_slack_channel != channel_slack_id:
        # ORM_WARNING: the following statement works because we use SQL Alchemy
        company.share_messages_in_slack_channel = channel_slack_id

    publish_configuration_view(
        company=company,
        user_id=user_id
    )


def home_page_configuration_enable_leaderboard_value_changed_action_handler(body, logger):
    logger.info(body)
    user_id = body["user"]["id"]
    company = get_or_create_company_by_body(body)

    new_enable_leaderboard = ("enable_leaderboard"
                              in [option["value"] for option in body["actions"][0]["selected_options"]])

    if company.enable_leaderboard != new_enable_leaderboard:
        # ORM_WARNING: the following statement works because we use SQL Alchemy
        company.enable_leaderboard = new_enable_leaderboard

    publish_configuration_view(
        company=company,
        user_id=user_id
    )


def home_page_configuration_stats_time_period_value_changed_action_handler(body, logger):
    logger.info(body)
    user_id = body["user"]["id"]
    company = get_or_create_company_by_body(body)

    try:
        new_time_period = LeaderbordTimeSettings[body["actions"][0]["selected_option"]["value"]]
    except (KeyError, TypeError):
        new_time_period = LeaderbordTimeSettings.LAST_30_DAYS

    if company.leaderbord_time_settings != new_time_period:
        # ORM_WARNING: the following statement works because we use SQL Alchemy
        company.leaderbord_time_settings = new_time_period

    publish_configuration_view(
        company=company,
        user_id=user_id
    )


def home_page_configuration_max_number_of_thank_you_receivers_value_changed_action_handler(body, logger):
    logger.info(body)
    user_id = body["user"]["id"]
    company = get_or_create_company_by_body(body)

    try:
        new_limit = int(body["actions"][0]["selected_option"]["value"])
        new_limit = max(1, new_limit)
        new_limit = min(10, new_limit)
    except (TypeError, ValueError):
        new_limit = 10

    if company.receivers_number_limit != new_limit:
        # ORM_WARNING: the following statement works because we use SQL Alchemy
        company.receivers_number_limit = new_limit

    publish_configuration_view(
        company=company,
        user_id=user_id
    )


def home_page_configuration_enable_weekly_thank_you_limit_value_changed_action_handler(body, logger):
    logger.info(body)
    user_id = body["user"]["id"]
    company = get_or_create_company_by_body(body)

    new_enable_weekly_thank_you_limit = "enable_weekly_thank_you_limit" \
                                        in [option["value"] for option in body["actions"][0]["selected_options"]]

    if company.enable_weekly_thank_you_limit != new_enable_weekly_thank_you_limit:
        # ORM_WARNING: the following statement works because we use SQL Alchemy
        company.enable_weekly_thank_you_limit = new_enable_weekly_thank_you_limit

    publish_configuration_view(
        company=company,
        user_id=user_id
    )


def home_page_configuration_max_number_of_messages_per_week_value_changed_action_handler(body, logger):
    logger.info(body)
    user_id = body["user"]["id"]
    company = get_or_create_company_by_body(body)

    try:
        new_limit = int(body["actions"][0]["selected_option"]["value"])
        new_limit = max(1, new_limit)
        new_limit = min(10, new_limit)
    except (TypeError, ValueError):
        new_limit = 5

    if company.weekly_thank_you_limit != new_limit:
        # ORM_WARNING: the following statement works because we use SQL Alchemy
        company.weekly_thank_you_limit = new_limit

    publish_configuration_view(
        company=company,
        user_id=user_id
    )


def home_page_configuration_enable_rich_text_in_thank_you_messages_value_changed_action_handler(body, logger):
    logger.info(body)
    user_id = body["user"]["id"]
    company = get_or_create_company_by_body(body)

    new_enable_rich_text_value = "enable_rich_text_in_thank_you_messages" \
                                 in [option["value"] for option in body["actions"][0]["selected_options"]]

    if company.enable_rich_text_in_thank_you_messages != new_enable_rich_text_value:
        # ORM_WARNING: the following statement works because we use SQL Alchemy
        company.enable_rich_text_in_thank_you_messages = new_enable_rich_text_value

    publish_configuration_view(
        company=company,
        user_id=user_id
    )


def home_page_configuration_enable_attaching_files_value_changed_action_handler(body, logger):
    logger.info(body)
    user_id = body["user"]["id"]
    company = get_or_create_company_by_body(body)

    new_enable_attaching_files = "enable_attaching_files" \
                                 in [option["value"] for option in body["actions"][0]["selected_options"]]

    if company.enable_attaching_files != new_enable_attaching_files:
        # ORM_WARNING: the following statement works because we use SQL Alchemy
        company.enable_attaching_files = new_enable_attaching_files

    publish_configuration_view(
        company=company,
        user_id=user_id
    )


def home_page_configuration_max_attached_files_num_value_changed_action_handler(body, logger):
    logger.info(body)
    user_id = body["user"]["id"]
    company = get_or_create_company_by_body(body)

    try:
        new_limit = int(body["actions"][0]["selected_option"]["value"])
        new_limit = max(1, new_limit)
        new_limit = min(10, new_limit)
    except (TypeError, ValueError):
        new_limit = 5

    if company.max_attached_files_num != new_limit:
        # ORM_WARNING: the following statement works because we use SQL Alchemy
        company.max_attached_files_num = new_limit

    publish_configuration_view(
        company=company,
        user_id=user_id
    )


def home_page_configuration_enable_company_values_value_changed_action_handler(body, logger):
    logger.info(body)
    user_id = body["user"]["id"]
    company = get_or_create_company_by_body(body)

    new_enable_company_values = ("enable_company_values"
                                 in [option["value"] for option in body["actions"][0]["selected_options"]])

    if company.enable_company_values != new_enable_company_values:
        # ORM_WARNING: the following statement works because we use SQL Alchemy
        company.enable_company_values = new_enable_company_values

    publish_configuration_view(
        company=company,
        user_id=user_id
    )


def home_page_configuration_edit_company_value_clicked_action_handler(body, logger):
    logger.info(body)
    # user_id = body["user"]["id"]
    company = get_or_create_company_by_body(body)

    thank_you_type_uuid = body["actions"][0]["value"]
    thank_you_type = dao.read_thank_you_type(company_uuid=company.uuid, thank_you_type_uuid=thank_you_type_uuid)

    app.client.views_open(
        trigger_id=body["trigger_id"],
        view=thank_you_type_dialog(
            state=thank_you_type
        )
    )


def home_page_configuration_add_new_company_value_clicked_action_handler(body, logger):
    app.client.views_open(
        trigger_id=body["trigger_id"],
        view=thank_you_type_dialog()
    )
