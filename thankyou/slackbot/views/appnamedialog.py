from slack_sdk.models.blocks import InputBlock, PlainTextInputElement
from slack_sdk.models.views import View


def app_name_dialog(app_name: str):
    return View(
        type="modal",
        callback_id="edit_merci_app_name_dialog_save_button_clicked",
        title="Edit the app name",
        submit="Save",
        close="Cancel",
        blocks=[
            InputBlock(
                label="Name",
                block_id="edit_merci_app_name_dialog_app_name_block",
                element=PlainTextInputElement(
                    action_id="edit_merci_app_name_dialog_app_name_action",
                    initial_value=app_name
                )
            ),
        ]
    )
