from slack_sdk.models.blocks import InputBlock, PlainTextInputElement, ContextBlock, TextObject
from slack_sdk.models.views import View

from thankyou.slackbot.utils.privatemetadata import PrivateMetadata


def thanks_back_dialog_view(thank_you_message_uuid: str, author_slack_user_id: str) -> View:
    return View(
        type="modal",
        callback_id="thanks_back_dialog_send_button_clicked",
        title="Thanks back!",
        submit="Thanks back!",
        close="Cancel",
        private_metadata=str(PrivateMetadata(thank_you_message_uuid=thank_you_message_uuid)),
        blocks=[
            InputBlock(
                label="Add a message",
                block_id="thanks_back_dialog_input_block",
                element=PlainTextInputElement(
                    placeholder="Write something...",
                    action_id="thanks_back_dialog_input_block_action",
                    multiline=True,
                    max_length=2000
                )
            ),
            ContextBlock(
                elements=[
                    TextObject(f"Only <@{author_slack_user_id}> will see this message", type="mrkdwn"),
                ]
            ),
        ]
    )
