from datetime import date
from typing import List, Optional, Tuple

from slack_sdk.models.blocks import ButtonElement, ActionsBlock, SectionBlock, HeaderBlock, DividerBlock, TextObject, \
    ContextBlock, Block, ConfirmObject

from thankyou.core.models import ThankYouMessage, ThankYouType, Slack_User_ID_Type
from thankyou.slackbot.blocks.thank_you import thank_you_message_blocks


def home_page_actions_block(selected: str = "my_updates") -> ActionsBlock:
    elements = [
        ButtonElement(
            text="Say Thank you!",
            style="danger",
            action_id="home_page_say_thank_you_button_clicked"
        ),
        ButtonElement(
            text="All Thank yous",
            style="primary" if selected == "company_thank_yous" else None,
            action_id="home_page_company_thank_you_button_clicked"
        ),
        ButtonElement(
            text="Your Thank yous",
            style="primary" if selected == "my_thank_yous" else None,
            action_id="home_page_my_thank_you_button_clicked"
        ),
        ButtonElement(
            text="Help",
            style="primary" if selected == "help" else None,
            action_id="home_page_help_button_clicked"
        ),
        ButtonElement(
            text="Configuration",
            style="primary" if selected == "configuration" else None,
            action_id="home_page_configuration_button_clicked"
        )
    ]

    return ActionsBlock(elements=elements)


def home_page_welcome_blocks() -> List[Block]:
    return [
        HeaderBlock(text="Welcome to the Merci! application"),
        SectionBlock(
            text="Recognizing and appreciating your team is a cornerstone of a motivated workforce. "
                 "The Merci! Slack application provides a seamless way for you and your colleagues to express "
                 "gratitude and foster a positive workplace culture."
        ),
        SectionBlock(
            text="Have you already tried sending a thank you message? If not, click on the \"Say Thank you!\" button "
                 "and send a couple of warm words to your colleague(s)!"
        ),
        SectionBlock(
            text=TextObject(
                type="mrkdwn",
                text="In case you want your message to appear in a a specific team channel, open this channel and "
                     "simpy send a `/thanks` or `/merci` command"
            ),
        ),
        ActionsBlock(
            elements=[
                ButtonElement(
                    text="Hide this message",
                    action_id="home_page_hide_welcome_message_button_clicked",
                    confirm=ConfirmObject(
                        title="Are you sure?",
                        text="Are you sure you want to hide this text? "
                             "If you need help, you can check the \"Help\" tab"
                    )
                )
            ]
        ),
    ]


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
        if thank_you_type:
            sender_leaders_field += f"\n\n*{thank_you_type.name}*\n"
        if category_leaders:
            sender_leaders_field += "\n".join(f"{position + 1}. <@{slack_user_id}>: {thank_you_messages_num} messages"
                                              for position, (slack_user_id, thank_you_messages_num)
                                              in enumerate(category_leaders))
        else:
            sender_leaders_field += "_There are no leaders in this category yet_"

    for thank_you_type, category_leaders in receiver_leaders:
        if thank_you_type:
            receiver_leaders_field += f"\n\n*{thank_you_type.name}*\n"
        if category_leaders:
            receiver_leaders_field += "\n".join(f"{position + 1}. <@{slack_user_id}>: {thank_you_messages_num} messages"
                                                for position, (slack_user_id, thank_you_messages_num)
                                                in enumerate(category_leaders))
        else:
            receiver_leaders_field += "_There are no leaders in this category yet_"

    def _format_date(d: date):
        return d.strftime("%b, %d")

    from_until_text = None
    if from_date and until_date:
        from_until_text = f"\n\n_These statistics only count messages sent between {_format_date(from_date)} " \
                          f"and {_format_date(until_date)}_"

    return SectionBlock(fields=[
        sender_leaders_field, receiver_leaders_field, from_until_text
    ])


def home_page_hidden_messages_warn_block(slack_channel_with_all_messages: str = None, hidden_messages_num: int = None) \
        -> Optional[ContextBlock]:
    if slack_channel_with_all_messages:
        if hidden_messages_num and hidden_messages_num > 0:
            text = (f"Only the latest messages are shown below. To read all the Thank You messages, "
                    f"please go to the <#{slack_channel_with_all_messages}> channel.")
        else:
            text = (f"Don't forget to join the <#{slack_channel_with_all_messages}> slack channel so "
                    f"you don't miss out on the Thank You messages your colleagues send to each other!")
    else:
        if hidden_messages_num and hidden_messages_num > 0:
            text = (f"Only the latest messages are shown below. To read all the Thank You messages, "
                    f"please ask your Slack administrator to configure the Merci! application, so the all "
                    f"Thank You messages are forwarded to a public slack channel.")
        else:
            text = None

    if text:
        return ContextBlock(
            elements=[
                TextObject(
                    text=text,
                    type="mrkdwn"
                )
            ]
        )


def thank_you_list_blocks(thank_you_messages: List[ThankYouMessage], current_user_slack_id: str = None,
                          accessory_action_id: str = None, blocks_num_limit: int = None) -> List[SectionBlock]:
    result = []
    last_date: Optional[date] = None
    for thank_you_message in thank_you_messages:
        blocks_to_append = []

        if last_date is None or thank_you_message.created_at.date() != last_date:
            last_date = thank_you_message.created_at.date()
            blocks_to_append.append(HeaderBlock(
                text=last_date.strftime("%A, %B %-d")
            ))
            blocks_to_append.append(DividerBlock())

        blocks_to_append.extend(
            thank_you_message_blocks(
                thank_you_message,
                show_say_thank_you_button=current_user_slack_id in [
                    r.slack_user_id for r in thank_you_message.receivers]
            )
        )

        blocks_to_append.append(DividerBlock())

        if blocks_num_limit is not None and len(result) + len(blocks_to_append) > blocks_num_limit:
            break

        result.extend(blocks_to_append)

    return result
