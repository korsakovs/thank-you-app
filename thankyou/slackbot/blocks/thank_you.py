import json
from typing import List

from slack_sdk.models.blocks import SectionBlock, TextObject, ContextBlock, Option, \
    StaticSelectElement, InputBlock, PlainTextInputElement, UserMultiSelectElement, ImageElement, \
    RichTextInputElement, RichTextBlock

from thankyou.core.models import ThankYouMessage, ThankYouType
from thankyou.slackbot.blocks.utils import rich_text_block_as_markdown
from thankyou.slackbot.utils.string import es


def thank_you_message_blocks(thank_you_message: ThankYouMessage) -> List[SectionBlock]:
    result = []
    title = ""
    if thank_you_message.type:
        title += f" *{thank_you_message.type.name}*! "
    title = es(title)

    title += "Thank you, " + ", ".join(f"<@{receiver.slack_user_id}>" for receiver in thank_you_message.receivers) + "!"

    # text = es(thank_you_message.text)

    is_rich_text = thank_you_message.is_rich_text
    text = thank_you_message.text
    if is_rich_text and thank_you_message.images:
        markdown_text = rich_text_block_as_markdown(text)
        if markdown_text is not None:
            is_rich_text = False
            text = markdown_text

    if title:
        title_accessory = None
        if is_rich_text and thank_you_message.images:
            image = sorted(thank_you_message.images, key=lambda i: i.ordering_key)[0]
            title_accessory = ImageElement(
                image_url=image.url,
                alt_text=image.filename
            )
        result.append(SectionBlock(
            text=TextObject(
                type="mrkdwn",
                text=title,
                # emoji=True
            ),
            accessory=title_accessory
        ))

    if is_rich_text:
        result.append(RichTextBlock(
            elements=json.loads(thank_you_message.text)["elements"]
        ))
        if thank_you_message.images:
            images = sorted(thank_you_message.images, key=lambda i: i.ordering_key)
            result.append(SectionBlock(
                text=TextObject(
                    type="mrkdwn",
                    text="---\n" + "\n".join([f"<{image.url}|{image.filename}>" for image in images])
                ),
            ))
    else:
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
                    text=text + "\n---\n"
                         + "\n".join([f"<{image.url}|{image.filename}>" for image in images])
                ),
                accessory=ImageElement(
                    image_url=images[0].url,
                    alt_text=images[0].filename
                )
            ))

    published_by_text = ""
    if thank_you_message.author_slack_user_id:
        published_by_text += f"_This Thank You message was sent by <@{es(thank_you_message.author_slack_user_id)}>!_"

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
                         label: str = "Select a company value", select_text="Select a company value...",
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


def thank_you_receivers_block(label: str = "Who do you want to thank?", block_id: str = None, action_id: str = None,
                              max_selected_items: int = 10) -> InputBlock:
    return InputBlock(
        block_id=block_id,
        label=label,
        optional=False,
        element=UserMultiSelectElement(
            action_id=action_id,
            initial_users=None,
            max_selected_items=max_selected_items
        )
    )


def thank_you_text_block(label: str = "Add a message", initial_value: str = None, block_id: str = None,
                         action_id: str = None, enable_rich_text: bool = False) -> InputBlock:
    if enable_rich_text:
        element = RichTextInputElement(
            action_id=action_id,
            initial_value=initial_value,
            focus_on_load=True
        )
    else:
        element = PlainTextInputElement(
            action_id=action_id,
            multiline=True,
            initial_value=initial_value,
            max_length=1000,
            focus_on_load=True
        )

    return InputBlock(
        block_id=block_id,
        label=label,
        optional=False,
        element=element
    )
