from slack_sdk.models.blocks import HeaderBlock, DividerBlock, SectionBlock, TextObject
from slack_sdk.models.views import View

from thankyou.slackbot.blocks.homepage import home_page_actions_block


def home_page_help_view():
    return View(
        type="home",
        title="Welcome to Chirik Bot!",
        blocks=[
            home_page_actions_block(selected="help"),
            DividerBlock(),
            HeaderBlock(text="Help"),
            SectionBlock(
                text=TextObject(
                    type="mrkdwn",
                    text="We will add more useful information to this page soon. In the meantime, "
                         "feel free to visit our website: https://merci.emgbook.com",
                )
            )
        ]
    )
