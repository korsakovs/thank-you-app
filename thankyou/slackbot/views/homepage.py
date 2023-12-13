from typing import List

from slack_sdk.models.blocks import DividerBlock
from slack_sdk.models.views import View

from thankyou.core.models import ThankYouMessage
from thankyou.slackbot.blocks.homepage import home_page_actions_block, thank_you_list_blocks


def home_page_my_updates_view(thank_you_messages: List[ThankYouMessage], is_admin: bool = False):
    return View(
        type="home",
        title="Welcome to Chirik Bot!",
        blocks=[
            home_page_actions_block(selected="my_updates", show_configuration=is_admin),
            DividerBlock(),
            *thank_you_list_blocks(thank_you_messages)
        ]
    )
