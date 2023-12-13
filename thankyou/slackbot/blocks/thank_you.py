from typing import List

from slack_sdk.models.blocks import SectionBlock, TextObject, PlainTextObject, ContextBlock

from thankyou.core.models import ThankYouMessage
from thankyou.slackbot.utils import es


def thank_you_message_blocks(thank_you_message: ThankYouMessage) -> List[SectionBlock]:
    result = []
    title = ""
    if thank_you_message.type:
        title += f" *{thank_you_message.type.name}*"
    title = es(title)

    text = " • "
    text += thank_you_message.text

    if title:
        result.append(SectionBlock(
            text=TextObject(
                type="mrkdwn",
                text=title,
                # emoji=True
            )
        ))

    result.append(SectionBlock(
        text=PlainTextObject(text=text),
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