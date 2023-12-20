from typing import List

from slack_sdk.models.blocks import SectionBlock, ButtonElement, HeaderBlock, ContextBlock, TextObject, \
    ChannelSelectElement, StaticSelectElement, Option, UserMultiSelectElement, ActionsBlock, CheckboxesElement
from slack_sdk.models.views import View

from thankyou.core.models import ThankYouType, Slack_User_ID_Type, Slack_Channel_ID_Type, LeaderbordTimeSettings
from thankyou.slackbot.blocks.homepage import home_page_actions_block


def configuration_view(admin_slack_user_ids: List[Slack_User_ID_Type],
                       share_messages_in_slack_channel: Slack_Channel_ID_Type, thank_you_types: List[ThankYouType],
                       leaderbord_time_settings: LeaderbordTimeSettings, weekly_thank_you_limit: int,
                       enable_rich_text_in_thank_you_messages: bool):
    stats_time_period_to_use_options = []
    stats_time_period_to_use_selected_option = None
    for enum, option in (
            (LeaderbordTimeSettings.LAST_30_DAYS, Option(value="LAST_30_DAYS", label="Last 30 days")),
            (LeaderbordTimeSettings.CURRENT_FULL_MONTH, Option(value="CURRENT_FULL_MONTH", label="Current full month")),
            (LeaderbordTimeSettings.LAST_FULL_MONTH, Option(value="LAST_FULL_MONTH", label="Last full month")),
            (LeaderbordTimeSettings.LAST_7_DAYS, Option(value="LAST_7_DAYS", label="Last 7 days")),
            (LeaderbordTimeSettings.LAST_FULL_WEEK, Option(value="LAST_FULL_WEEK", label="Last full week")),
    ):
        stats_time_period_to_use_options.append(option)
        if enum == leaderbord_time_settings:
            stats_time_period_to_use_selected_option = option

    weekly_limit_options = sorted(list(set(list(range(1, 6)) + [weekly_thank_you_limit])))

    return View(
        type="home",
        title="Configuration",
        blocks=[
            home_page_actions_block(selected="configuration", show_configuration=True),
            HeaderBlock(
                text="Configuration"
            ),
            ContextBlock(
                elements=[TextObject(text="This page is only accessible by Slack Workspace Admins and other people "
                                          "they have granted access to",
                                     type="mrkdwn")]
            ),
            HeaderBlock(
                text="Access to the configuration page"
            ),
            SectionBlock(
                text="Select users that will have an access to this Configuration page",
                accessory=UserMultiSelectElement(
                    initial_users=admin_slack_user_ids,
                    action_id="home_page_configuration_admin_slack_user_ids_value_changed"
                )
            ),
            HeaderBlock(
                text="Notification Settings"
            ),
            SectionBlock(
                text="Share all thank yous in a Slack channel",
                accessory=ChannelSelectElement(
                    initial_channel=share_messages_in_slack_channel,
                    action_id="home_page_configuration_notification_slack_channel_value_changed"
                )
            ),
            HeaderBlock(
                text="Leaderboards Settings"
            ),
            SectionBlock(
                text="Time period to use",
                accessory=StaticSelectElement(
                    options=stats_time_period_to_use_options,
                    initial_option=stats_time_period_to_use_selected_option,
                    action_id="home_page_configuration_stats_time_period_value_changed"
                )
            ),
            HeaderBlock(
                text="Weekly limits"
            ),
            SectionBlock(
                text="How many thank yous a user can send in one week",
                accessory=StaticSelectElement(
                    options=[Option(value=str(num), label=str(num)) for num in weekly_limit_options],
                    initial_option=Option(value=str(weekly_thank_you_limit), label=str(weekly_thank_you_limit)),
                    action_id="home_page_configuration_max_number_of_messages_per_week_value_changed"
                )
            ),
            HeaderBlock(
                text="Rich Text Editing"
            ),
            ActionsBlock(
                elements=[
                    CheckboxesElement(
                        action_id="home_page_configuration_enable_rich_text_in_thank_you_messages_value_changed",
                        initial_options=[] if not enable_rich_text_in_thank_you_messages else [
                            Option(value="enable_rich_text_in_thank_you_messages",
                                   label="Enable Rich Text editing in the \"Say Thank You!\" dialog")
                        ],
                        options=[
                            Option(value="enable_rich_text_in_thank_you_messages",
                                   label="Enable Rich Text editing in the \"Say Thank You!\" dialog")
                        ]
                    )
                ]
            ),
            HeaderBlock(
                text="Company values"
            ),
            *[
                SectionBlock(
                    text=f"*{thank_you_type.name}*",
                    accessory=ButtonElement(
                        text="Edit...",
                        action_id="home_page_configuration_edit_company_value_clicked",
                        value=thank_you_type.uuid
                    ),
                ) for thank_you_type in thank_you_types
            ],
            ActionsBlock(
                elements=[
                    ButtonElement(
                        text="Add a new value...",
                        action_id="home_page_configuration_add_new_company_value_clicked"
                    )
                ]
            )
        ]
    )
