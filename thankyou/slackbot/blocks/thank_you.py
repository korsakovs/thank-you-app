from typing import List

from slack_sdk.models.blocks import SectionBlock, TextObject, PlainTextObject, ContextBlock, Option, \
    StaticSelectElement, InputBlock, PlainTextInputElement, UserMultiSelectElement, ImageElement

from thankyou.core.models import ThankYouMessage, ThankYouType
from thankyou.slackbot.utils.string import es


def thank_you_message_blocks(thank_you_message: ThankYouMessage) -> List[SectionBlock]:
    result = []
    title = ""
    if thank_you_message.type:
        title += f" *{thank_you_message.type.name}*! "
    title = es(title)

    title += "Thank you, " + ", ".join(f"<@{receiver.slack_user_id}>" for receiver in thank_you_message.receivers) + "!"

    text = thank_you_message.text
    # text = es(thank_you_message.text)

    if title:
        result.append(SectionBlock(
            text=TextObject(
                type="mrkdwn",
                text=title,
                # emoji=True
            )
        ))

    if not thank_you_message.images:
        result.append(SectionBlock(
            text=TextObject(
                type="mrkdwn",
                text=text,
                # emoji=True
            )
        ))
    else:
        images = sorted(thank_you_message.images, key=lambda i: i.ordering_key)
        result.append(SectionBlock(
            text=TextObject(
                type="mrkdwn",
                text=text + "\n---\n" + "\n".join([f"<{image.url}|{image.filename}>" for image in images])
            ),
            accessory=ImageElement(
                image_url=images[0].url,
                alt_text=images[0].filename
            )
        ))

    published_by_text = ""
    if thank_you_message.author_slack_user_id:
        published_by_text += f"Shared by <@{es(thank_you_message.author_slack_user_id)}>"

    if published_by_text:
        result.append(ContextBlock(
            elements=[
                TextObject(
                    type="mrkdwn",
                    text=published_by_text
                )
            ]
        ))

    return result


def thank_you_type_block(thank_you_types: List[ThankYouType],
                         label: str = "Thank You Type", select_text="Select a thank you type...",
                         selected_value: ThankYouType = None, block_id: str = None,
                         action_id: str = None) -> InputBlock:
    def type_as_option(thank_you_type: ThankYouType) -> Option:
        return Option(value=thank_you_type.uuid, text=thank_you_type.name)

    initial_option = None
    if selected_value and not selected_value.deleted:
        initial_option = type_as_option(selected_value)

    return InputBlock(
        block_id=block_id,
        label=label,
        element=StaticSelectElement(
            action_id=action_id,
            placeholder=select_text,
            options=[
                type_as_option(thank_you_type)
                for thank_you_type in sorted(thank_you_types, key=lambda s: str(s.name).lower())
                if not thank_you_type.deleted
            ],
            initial_option=initial_option,
            focus_on_load=False
        )
    )


def thank_you_receivers_block(label: str = "Receivers", block_id: str = None, action_id: str = None) -> InputBlock:
    return InputBlock(
        block_id=block_id,
        label=label,
        optional=False,
        element=UserMultiSelectElement(
            action_id=action_id,
            initial_users=None,
            max_selected_items=10
        )
    )


def thank_you_text_block(label: str = "Thank You", initial_value: str = None, block_id: str = None,
                         action_id: str = None) -> InputBlock:
    return InputBlock(
        block_id=block_id,
        label=label,
        optional=False,
        element=PlainTextInputElement(
            action_id=action_id,
            multiline=True,
            initial_value=initial_value,
            max_length=256,
            focus_on_load=True
        )
    )
