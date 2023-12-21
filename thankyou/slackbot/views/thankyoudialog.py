from typing import List

from slack_sdk.models.blocks import InputBlock
from slack_sdk.models.blocks.block_elements import FileInputElement
from slack_sdk.models.views import View

from thankyou.core.models import ThankYouType, ThankYouMessage
from thankyou.slackbot.blocks.thank_you import thank_you_type_block, thank_you_text_block, thank_you_receivers_block
from thankyou.slackbot.utils.privatemetadata import PrivateMetadata


def thank_you_dialog_view(thank_you_types: List[ThankYouType], state: ThankYouMessage = None,
                          enable_rich_text: bool = False, enable_company_values: bool = True,
                          max_receivers_num: int = 10, enable_attaching_files: bool = True,
                          max_attached_files_num: int = 10) -> View:
    extra_blocks = []

    if enable_attaching_files and max_attached_files_num > 0:
        extra_blocks.append(
            InputBlock(
                label="Attach an image" + ("" if max_attached_files_num == 1 else "(s)"),
                block_id="thank_you_dialog_attached_files_block",
                dispatch_action=True,
                element=FileInputElement(
                    action_id="thank_you_dialog_attached_files_action_id",
                    filetypes=["jpg", "jpeg", "png", "gif"],
                    max_files=max_attached_files_num,
                ),
                optional=True,
            ),
        )

    return View(
        type="modal",
        callback_id="thank_you_dialog_save_button_clicked",
        title="Update Thank You!" if state else "Say Thank you!",
        submit="Save",
        close="Cancel",
        private_metadata=str(PrivateMetadata(thank_you_message_uuid=None if state is None else state.uuid)),
        blocks=[
            *([] if not (enable_company_values and thank_you_types) else [
                thank_you_type_block(thank_you_types,
                                     selected_value=None if state is None or state.type is None else state.type,
                                     block_id="thank_you_dialog_thank_you_type_block",
                                     action_id="thank_you_dialog_thank_you_type_action_id"),
            ]),
            thank_you_receivers_block(block_id="thank_you_dialog_receivers_block",
                                      action_id="thank_you_dialog_receivers_action_id",
                                      max_selected_items=max_receivers_num),
            # thank_you_link_block(initial_value=None if state is None else state.link,
            #                      block_id=STATUS_UPDATE_LINK_BLOCK,
            #                      action_id=STATUS_UPDATE_MODAL_STATUS_UPDATE_LINK_ACTION_ID),
            thank_you_text_block(initial_value=None if state is None else state.text,
                                 block_id="thank_you_dialog_text_block",
                                 action_id="thank_you_dialog_text_action_id",
                                 enable_rich_text=enable_rich_text),
            *extra_blocks
        ]
    )
