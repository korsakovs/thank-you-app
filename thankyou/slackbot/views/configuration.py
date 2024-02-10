from typing import List

from slack_sdk.models.blocks import SectionBlock, ButtonElement, HeaderBlock, ContextBlock, TextObject, \
    ChannelSelectElement, StaticSelectElement, Option, UserMultiSelectElement, ActionsBlock, DividerBlock
from slack_sdk.models.views import View

from thankyou.core.models import ThankYouType, Slack_User_ID_Type, Slack_Channel_ID_Type, LeaderbordTimeSettings
from thankyou.slackbot.blocks.common import checkbox_action_block
from thankyou.slackbot.blocks.homepage import home_page_actions_block


def configuration_no_access_view(admin_slack_ids: List[str] = None):
    admins_str = ""
    if admin_slack_ids:
        admins_str = (" You can also ask " + ", ".join(f"<@{admin_slack_id}>" for admin_slack_id in admin_slack_ids)
                      + ", as they also have access to the configuration settings, and can give you permissions.")

    return View(
        type="home",
        title="Configuration",
        blocks=[
            home_page_actions_block(selected="configuration"),
            HeaderBlock(
                text="Configuration"
            ),
            ContextBlock(
                elements=[TextObject(text="This page is only accessible by Slack Workspace Admins and other people "
                                          "they have granted access to",
                                     type="mrkdwn")]
            ),
            DividerBlock(),
            SectionBlock(
                text="Unfortunately, you don't have access to the app configuration. Are you sure you need "
                     "to configure the \"Merci!\" application? If so, ask you Slack admins to add you "
                     "to the list of administrators." + admins_str
            ),
        ],
    )


def configuration_view(admin_slack_user_ids: List[Slack_User_ID_Type], enable_sharing_in_a_slack_channel: bool,
                       share_messages_in_slack_channel: Slack_Channel_ID_Type, thank_you_types: List[ThankYouType],
                       leaderbord_time_settings: LeaderbordTimeSettings, enable_weekly_thank_you_limit: bool,
                       weekly_thank_you_limit: int,
                       enable_rich_text_in_thank_you_messages: bool, enable_company_values: bool,
                       enable_leaderboard: bool, max_thank_you_receivers_num: int, enable_attaching_files: bool,
                       enable_private_messages: bool, max_attached_files_num: int,
                       enable_private_message_counting_in_leaderboard: bool):
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

    weekly_limit_options = sorted(list(set(list(range(1, 11)) + [weekly_thank_you_limit])))
    max_thank_you_receivers_options = sorted(list(set(list(range(1, 11)) + [max_thank_you_receivers_num])))
    max_attached_files_num_options = sorted(list(set(list(range(1, 11)) + [max_attached_files_num])))

    return View(
        type="home",
        title="Configuration",
        blocks=[
            home_page_actions_block(selected="configuration"),
            HeaderBlock(
                text="Configuration"
            ),
            ContextBlock(
                elements=[TextObject(text="This page is only accessible by Slack Workspace Admins and other people "
                                          "they have granted access to",
                                     type="mrkdwn")]
            ),
            HeaderBlock(
                text="Buy me a coffee"
            ),
            ContextBlock(
                elements=[TextObject(text="As of today, The Merci! application is offered free of charge. "
                                          "Please, consider supporting authors of the application by "
                                          "<https://korsakov.pro/buymeacoffee|buying them> a coffee! Thank you :)",
                                     type="mrkdwn")]
            ),
            HeaderBlock(
                text="Access to the configuration page"
            ),
            SectionBlock(
                text="Select the users who will have access to this configuration page.",
                accessory=UserMultiSelectElement(
                    initial_users=admin_slack_user_ids,
                    action_id="home_page_configuration_admin_slack_user_ids_value_changed"
                )
            ),
            HeaderBlock(
                text="Notification Settings"
            ),
            checkbox_action_block(
                element_action_id="home_page_configuration_enable_sharing_in_a_slack_channel_value_changed",
                checkbox_value="enable_sharing_in_a_slack_channel",
                checkbox_label="Share all thank you messages in a public Slack channel",
                enabled=enable_sharing_in_a_slack_channel
            ),
            *([] if not enable_sharing_in_a_slack_channel else [
                SectionBlock(
                    text="Select a public Slack channel.",
                    accessory=ChannelSelectElement(
                        initial_channel=share_messages_in_slack_channel,
                        action_id="home_page_configuration_notification_slack_channel_value_changed"
                    )
                ),
            ]),
            checkbox_action_block(
                element_action_id="home_page_configuration_enable_private_messages_value_changed",
                checkbox_value="enable_private_messages",
                checkbox_label="Allow users to send messages privately",
                enabled=enable_private_messages
            ),
            HeaderBlock(
                text="Leaderboards Settings"
            ),
            checkbox_action_block(
                element_action_id="home_page_configuration_enable_leaderboard_value_changed",
                checkbox_value="enable_leaderboard",
                checkbox_label="Enable Leaderboard",
                enabled=enable_leaderboard
            ),
            *([] if not enable_leaderboard else [
                SectionBlock(
                    text="Time period for identifying leaders",
                    accessory=StaticSelectElement(
                        options=stats_time_period_to_use_options,
                        initial_option=stats_time_period_to_use_selected_option,
                        action_id="home_page_configuration_stats_time_period_value_changed"
                    )
                ),
                checkbox_action_block(
                    element_action_id=
                    "home_page_configuration_enable_private_message_counting_in_leaderboard_value_changed",
                    checkbox_value="enable_private_message_counting_in_leaderboard",
                    checkbox_label="Count private messages when counting the leaderboard",
                    enabled=enable_private_message_counting_in_leaderboard
                ),
            ]),
            HeaderBlock(
                text="Weekly limits"
            ),
            checkbox_action_block(
                element_action_id="home_page_configuration_enable_weekly_thank_you_limit_value_changed",
                checkbox_value="enable_weekly_thank_you_limit",
                checkbox_label="Enable a weekly limit on the number of thanks that one user can send.",
                enabled=enable_weekly_thank_you_limit
            ),
            *([] if not enable_weekly_thank_you_limit else [SectionBlock(
                text="How many thank you messages can a user send in a week?",
                accessory=StaticSelectElement(
                    options=[Option(value=str(num), label=str(num)) for num in weekly_limit_options],
                    initial_option=Option(value=str(weekly_thank_you_limit), label=str(weekly_thank_you_limit)),
                    action_id="home_page_configuration_max_number_of_messages_per_week_value_changed"
                )
            )]),
            HeaderBlock(
                text="Maximum number of thank you receivers"
            ),
            SectionBlock(
                text="How many people can users add as recipients of thank you messages they send?",
                accessory=StaticSelectElement(
                    options=[Option(value=str(num), label=str(num)) for num in max_thank_you_receivers_options],
                    initial_option=Option(value=str(max_thank_you_receivers_num),
                                          label=str(max_thank_you_receivers_num)),
                    action_id="home_page_configuration_max_number_of_thank_you_receivers_value_changed"
                )
            ),
            HeaderBlock(
                text="Rich Text Editing"
            ),
            checkbox_action_block(
                element_action_id="home_page_configuration_enable_rich_text_in_thank_you_messages_value_changed",
                checkbox_value="enable_rich_text_in_thank_you_messages",
                checkbox_label="Enable Rich Text editing in the \"Say Thank You!\" dialog",
                enabled=enable_rich_text_in_thank_you_messages
            ),
            HeaderBlock(
                text="Attaching images"
            ),
            checkbox_action_block(
                element_action_id="home_page_configuration_enable_attaching_files_value_changed",
                checkbox_value="enable_attaching_files",
                checkbox_label="Enable attaching images to \"Thank You!\" messages",
                enabled=enable_attaching_files
            ),
            # *([] if not enable_attaching_files else [
            #     SectionBlock(
            #         text="How many images can be attached to one thank you message?",
            #         accessory=StaticSelectElement(
            #             options=[Option(value=str(num), label=str(num)) for num in max_attached_files_num_options],
            #             initial_option=Option(value=str(max_attached_files_num),
            #                                   label=str(max_attached_files_num)),
            #             action_id="home_page_configuration_max_attached_files_num_value_changed"
            #         )
            #     ),
            # ]),
            HeaderBlock(
                text="Company values"
            ),
            checkbox_action_block(
                element_action_id="home_page_configuration_enable_company_values_value_changed",
                checkbox_value="enable_company_values",
                checkbox_label="Enable Company Values",
                enabled=enable_company_values
            ),
            *([] if not enable_company_values else [
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
            ]),
        ]
    )
