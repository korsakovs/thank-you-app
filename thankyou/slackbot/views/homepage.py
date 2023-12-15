from typing import List

from slack_sdk.models.blocks import DividerBlock
from slack_sdk.models.views import View

from thankyou.core.models import ThankYouMessage
from thankyou.slackbot.blocks.homepage import home_page_actions_block, thank_you_list_blocks


def home_page_my_thank_yous_view(thank_you_messages: List[ThankYouMessage], is_admin: bool = False):
    return View(
        type="home",
        title="Welcome to Chirik Bot!",
        blocks=[
            home_page_actions_block(selected="my_thank_yous", show_configuration=is_admin),
            DividerBlock(),
            *thank_you_list_blocks(thank_you_messages)
        ]
    )


def home_page_company_thank_yous_view(thank_you_messages: List[ThankYouMessage],
                                      is_admin: bool = False, current_user_slack_id: str = None):
    return View(
        type="home",
        title="Say Thank You :)",
        blocks=[
            home_page_actions_block(selected="company_thank_yous", show_configuration=is_admin),
            DividerBlock(),
            *thank_you_list_blocks(thank_you_messages,
                                   current_user_slack_id=current_user_slack_id,
                                   accessory_action_id="company_thank_yous_message_menu_button_clicked")
        ]
    )
