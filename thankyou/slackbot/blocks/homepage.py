from datetime import date
from typing import List, Optional, Tuple

from slack_sdk.models.blocks import ButtonElement, ActionsBlock, SectionBlock, HeaderBlock, DividerBlock

from thankyou.core.models import ThankYouMessage, ThankYouType, Slack_User_ID_Type
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


def home_page_show_leaders_button_block() -> ActionsBlock:
    return ActionsBlock(
        elements=[
            ButtonElement(text="🥇 Show leaders!", action_id="home_page_show_leaders_button_clicked"),
        ]
    )


def home_page_leaders_block(sender_leaders: List[Tuple[ThankYouType, List[Tuple[Slack_User_ID_Type, int]]]],
                            receiver_leaders: List[Tuple[ThankYouType, List[Tuple[Slack_User_ID_Type, int]]]],
                            from_date: date = None, until_date: date = None) \
        -> SectionBlock:
    sender_leaders_field = "_*Sent the most \"thank yous\"*_\n\n"
    receiver_leaders_field = "_*Received the most \"thank yous\"*_\n\n"

    for thank_you_type, category_leaders in sender_leaders:
        sender_leaders_field += f"\n\n*{thank_you_type.name}*\n"
        if category_leaders:
            sender_leaders_field += "\n".join(f"{position + 1}. <@{slack_user_id}>: {thank_you_messages_num} messages"
                                              for position, (slack_user_id, thank_you_messages_num)
                                              in enumerate(category_leaders))
        else:
            sender_leaders_field += "_There are no leaders in this category yet_"

    for thank_you_type, category_leaders in receiver_leaders:
        receiver_leaders_field += f"\n\n*{thank_you_type.name}*\n"
        if category_leaders:
            receiver_leaders_field += "\n".join(f"{position + 1}. <@{slack_user_id}>: {thank_you_messages_num} messages"
                                                for position, (slack_user_id, thank_you_messages_num)
                                                in enumerate(category_leaders))
        else:
            receiver_leaders_field += "_There are no leaders in this category yet_"

    from_until_text = None
    if from_date and until_date:
        from_until_text = f"\n\n_These statistics only count messages sent from {from_date} to {until_date}_"

    return SectionBlock(fields=[
        sender_leaders_field, receiver_leaders_field, from_until_text
    ])


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
