from datetime import date
from typing import List, Optional

from slack_sdk.models.blocks import ButtonElement, ActionsBlock, SectionBlock, HeaderBlock, DividerBlock

from thankyou.core.models import ThankYouMessage
from thankyou.slackbot.blocks.thank_you import thank_you_message_blocks


def home_page_actions_block(selected: str = "my_updates", show_configuration: bool = False) -> ActionsBlock:
    elements = [
        ButtonElement(
            text="Say Thank you!",
            style="danger",
            action_id="home_page_say_thank_you_button_clicked"
        ),
        ButtonElement(
            text="Company Thank yous",
            style="primary" if selected == "company_thank_yous" else None,
            action_id="home_page_company_thank_you_button_clicked"
        ),
        ButtonElement(
            text="Your Thank yous",
            style="primary" if selected == "my_thank_yous" else None,
            action_id="home_page_my_thank_you_button_clicked"
        ),
    ]
    if show_configuration:
        elements.append(ButtonElement(
            text="Configuration",
            style="primary" if selected == "configuration" else None,
            action_id="home_page_configuration_button_clicked"
        ))

    return ActionsBlock(elements=elements)


def thank_you_list_blocks(thank_you_messages: List[ThankYouMessage], current_user_slack_id: str = None,
                          accessory_action_id: str = None) -> List[SectionBlock]:
    result = []
    last_date: Optional[date] = None
    for thank_you_message in thank_you_messages:
        if last_date is None or thank_you_message.created_at.date() != last_date:
            last_date = thank_you_message.created_at.date()
            result.append(HeaderBlock(
                text=last_date.strftime("%A, %B %-d")
            ))
            result.append(DividerBlock())

        result.extend(
            thank_you_message_blocks(thank_you_message)
        )
        result.append(DividerBlock())
    return result
