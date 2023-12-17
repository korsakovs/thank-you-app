from datetime import date
from typing import List, Tuple

from slack_sdk.models.blocks import DividerBlock
from slack_sdk.models.views import View

from thankyou.core.models import ThankYouMessage, ThankYouType, Slack_User_ID_Type
from thankyou.slackbot.blocks.homepage import home_page_actions_block, thank_you_list_blocks, home_page_leaders_block


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
                                      sender_leaders: List[Tuple[ThankYouType, List[Tuple[Slack_User_ID_Type, int]]]]
                                      = None,
                                      receiver_leaders: List[Tuple[ThankYouType, List[Tuple[Slack_User_ID_Type, int]]]]
                                      = None,
                                      leaders_stats_from_date: date = None, leaders_stats_until_date: date = None,
                                      is_admin: bool = False, current_user_slack_id: str = None):
    leaders_blocks = []
    if sender_leaders and receiver_leaders:
        leaders_blocks.append(home_page_leaders_block(
            sender_leaders=sender_leaders,
            receiver_leaders=receiver_leaders,
            from_date=leaders_stats_from_date,
            until_date=leaders_stats_until_date
        ))
    return View(
        type="home",
        title="Say Thank You :)",
        blocks=[
            home_page_actions_block(selected="company_thank_yous", show_configuration=is_admin),
            DividerBlock(),
            *leaders_blocks,
            *thank_you_list_blocks(thank_you_messages,
                                   current_user_slack_id=current_user_slack_id,
                                   accessory_action_id="company_thank_yous_message_menu_button_clicked")
        ]
    )
