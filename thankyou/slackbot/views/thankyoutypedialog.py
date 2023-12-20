from typing import Optional

from slack_sdk.models.blocks import InputBlock, PlainTextInputElement, ActionsBlock, ButtonElement, HeaderBlock, \
    SectionBlock, TextObject
from slack_sdk.models.views import View

from thankyou.core.models import ThankYouType
from thankyou.slackbot.utils.privatemetadata import PrivateMetadata


def thank_you_type_dialog(state: Optional[ThankYouType] = None):
    delete_type_blocks = []
    if state:
        delete_type_blocks.append(
            ActionsBlock(
                elements=[
                    ButtonElement(
                        text="Delete this value...",
                        action_id="thank_you_type_dialog_delete_value_button_clicked",
                        value=state.uuid,
                        style="danger"
                    )
                ]
            )
        )

    return View(
        type="modal",
        callback_id="thank_you_type_dialog_save_button_clicked",
        title="Update a company value" if state else "Add a new company value",
        submit="Save" if state else "Add",
        close="Cancel",
        private_metadata=str(PrivateMetadata(thank_you_type_uuid=None if state is None else state.uuid)),
        blocks=[
            InputBlock(
                label="Name",
                block_id="thank_you_type_dialog_value_name_block",
                element=PlainTextInputElement(
                    action_id="thank_you_type_dialog_value_name_action",
                    initial_value=None if not state else state.name
                )
            ),
            SectionBlock(
                text="You can copy emojis from <https://emojipedia.org/|Emojipedia>"
            ),
            *delete_type_blocks
        ]
    )


def thank_you_type_deletion_confirmation_dialog(thank_you_type: ThankYouType):
    return View(
        type="modal",
        callback_id="thank_you_type_deletion_dialog_confirm_deletion_button_clicked",
        title="Are you sure?",
        submit="Delete",
        close="Cancel",
        private_metadata=str(PrivateMetadata(thank_you_type_uuid=thank_you_type.uuid)),
        blocks=[
            HeaderBlock(text=f"Are you sure you want to delete _{thank_you_type.name}_ company value?")
        ]
    )


def thank_you_type_deletion_completion_dialog(thank_you_type_name: str):
    return View(
        type="modal",
        callback_id="thank_you_type_deletion_completion_dialog",
        title="Deleted",
        close="OK",
        blocks=[
            HeaderBlock(text=f"A company value {thank_you_type_name} was successfully deleted")
        ]
    )
