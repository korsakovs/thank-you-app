from typing import List

from slack_sdk.models.blocks import SectionBlock, ButtonElement, HeaderBlock, ContextBlock, TextObject, \
    ChannelSelectElement, StaticSelectElement, Option, UserMultiSelectElement, ActionsBlock
from slack_sdk.models.views import View

from thankyou.core.models import ThankYouType
from thankyou.slackbot.blocks.homepage import home_page_actions_block


def configuration_view(thank_you_types: List[ThankYouType]):
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
                accessory=UserMultiSelectElement()
            ),
            HeaderBlock(
                text="Notification Settings"
            ),
            SectionBlock(
                text="Share all thank yous in a Slack channel",
                accessory=ChannelSelectElement()
            ),
            HeaderBlock(
                text="Leaderboards Settings"
            ),
            SectionBlock(
                text="Time period to use",
                accessory=StaticSelectElement(options=[
                    Option(value="last_30_days", label="Last 30 days"),
                    Option(value="last_full_month", label="Last full month"),
                    Option(value="last_7_days", label="Last 7 days"),
                    Option(value="last_full_week", label="Last full week"),
                ])
            ),
            HeaderBlock(
                text="Weekly limits"
            ),
            SectionBlock(
                text="How many thank yous a user can send in one week",
                accessory=StaticSelectElement(options=[
                    Option(value=str(num), label=str(num)) for num in range(1, 6)
                ])
            ),
            HeaderBlock(
                text="Company values"
            ),
            *[
                SectionBlock(
                    text=f"*{thank_you_type.name}*",
                    accessory=ButtonElement(text="Edit..."),
                ) for thank_you_type in thank_you_types
            ],
            ActionsBlock(
                elements=[ButtonElement(text="Add a new value...")]
            ),
        ]
    )
