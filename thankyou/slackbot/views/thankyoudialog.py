from typing import List

from slack_sdk.models.views import View

from thankyou.core.models import ThankYouType, ThankYouMessage
from thankyou.slackbot.blocks.thank_you import thank_you_type_block, thank_you_text_block, thank_you_receivers_block
from thankyou.slackbot.utils.privatemetadata import PrivateMetadata


def thank_you_dialog_view(thank_you_types: List[ThankYouType], state: ThankYouMessage = None) -> View:
    return View(
        type="modal",
        callback_id="thank_you_dialog_save_button_clicked",
        title="Update Thank You!" if state else "Say Thank you!",
        submit="Save",
        close="Cancel",
        private_metadata=str(PrivateMetadata(thank_you_message_uuid=None if state is None else state.uuid)),
        blocks=[
            thank_you_type_block(thank_you_types,
                                 selected_value=None if state is None or state.type is None else state.type,
                                 block_id="thank_you_dialog_thank_you_type_block",
                                 action_id="thank_you_dialog_thank_you_type_action_id"),
            thank_you_receivers_block(block_id="thank_you_dialog_receivers_block",
                                      action_id="thank_you_dialog_receivers_action_id"),
            # thank_you_link_block(initial_value=None if state is None else state.link,
            #                      block_id=STATUS_UPDATE_LINK_BLOCK,
            #                      action_id=STATUS_UPDATE_MODAL_STATUS_UPDATE_LINK_ACTION_ID),
            thank_you_text_block(initial_value=None if state is None else state.text,
                                 block_id="thank_you_dialog_text_block",
                                 action_id="thank_you_dialog_text_action_id"),
        ]
    )
