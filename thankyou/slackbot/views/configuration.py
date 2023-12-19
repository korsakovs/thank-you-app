from slack_sdk.models.blocks import SectionBlock, ButtonElement, HeaderBlock, ContextBlock, TextObject
from slack_sdk.models.views import View

from thankyou.slackbot.blocks.homepage import home_page_actions_block


def configuration_view():
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
                text="Admins: ",
                accessory=ButtonElement(
                    text="Edit...",
                    action_id="configuration_view_edit_admins_button_clicked"
                )
            )
        ]
    )
