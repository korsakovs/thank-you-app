from typing import List, Optional

from slack_sdk.models.blocks import InputBlock, SectionBlock, TextObject
from slack_sdk.models.blocks.block_elements import UrlInputElement
from slack_sdk.models.views import View

from thankyou.core.models import ThankYouType, ThankYouMessage
from thankyou.slackbot.blocks.common import checkbox_action_block
from thankyou.slackbot.blocks.thank_you import thank_you_type_block, thank_you_text_block, thank_you_receivers_block
from thankyou.slackbot.utils.privatemetadata import PrivateMetadata


def thank_you_dialog_view(thank_you_types: List[ThankYouType], state: ThankYouMessage = None,
                          enable_rich_text: bool = False, enable_company_values: bool = True,
                          max_receivers_num: int = 10, enable_attaching_files: bool = True,
                          max_attached_files_num: int = 10,
                          num_of_messages_a_user_can_send: Optional[int] = None,
                          slash_command_slack_channel_id: str = None,
                          display_private_message_option: bool = True) -> View:
    extra_blocks = []

    if enable_attaching_files or (state and state.images):
        initial_value = None
        if state and state.images:
            initial_value = state.sorted_images[0].url
        extra_blocks.append(
            InputBlock(
                label="Add an image",
                block_id="thank_you_dialog_image_url_block",
                dispatch_action=True,
                element=UrlInputElement(
                    action_id="thank_you_dialog_image_url_action_id",
                    initial_value=initial_value
                ),
                optional=True,
            ),
        )

    if not state and (num_of_messages_a_user_can_send is not None and num_of_messages_a_user_can_send <= 0):
        submit = None
        blocks = [
            SectionBlock(
                text="You have already sent many thank you messages! Next week you will be able to send more :)"
            )
        ]
    else:
        submit = "Say!" if not state else "Save"
        blocks = [
            *([] if not slash_command_slack_channel_id else [
                SectionBlock(text=TextObject(
                    text=f"This Thank you message will be posted in <#{slash_command_slack_channel_id}> slack channel. "
                         f"*Do not forget to invite Merci! application to this channel if this channel is private!*",
                    type="mrkdwn"
                ))
            ]),
            *([] if (num_of_messages_a_user_can_send is None or num_of_messages_a_user_can_send > 3 or state) else [
                SectionBlock(
                    text=f"You can send {num_of_messages_a_user_can_send} more thank you(s) this week."
                )
            ]),
            *([] if not (enable_company_values and thank_you_types) else [
                thank_you_type_block(thank_you_types,
                                     selected_value=None if state is None or state.type is None else state.type,
                                     block_id="thank_you_dialog_thank_you_type_block",
                                     action_id="thank_you_dialog_thank_you_type_action_id"),
            ]),
            thank_you_receivers_block(block_id="thank_you_dialog_receivers_block",
                                      action_id="thank_you_dialog_receivers_action_id",
                                      max_selected_items=max_receivers_num,
                                      initial_receivers=None if not state else state.receivers),
            # thank_you_link_block(initial_value=None if state is None else state.link,
            #                      block_id=STATUS_UPDATE_LINK_BLOCK,
            #                      action_id=STATUS_UPDATE_MODAL_STATUS_UPDATE_LINK_ACTION_ID),
            thank_you_text_block(initial_value=None if state is None else state.text,
                                 initial_is_rich_text=None if not state else state.is_rich_text,
                                 block_id="thank_you_dialog_text_block",
                                 action_id="thank_you_dialog_text_action_id",
                                 enable_rich_text=enable_rich_text),
            *([] if not display_private_message_option or state else [
                checkbox_action_block(
                    block_id="thank_you_dialog_is_private_block",
                    element_action_id="thank_you_dialog_send_privately_action",
                    checkbox_value="is_private",
                    checkbox_label="Send this message privately",
                    enabled=False if not state else state.is_private
                ),
            ]),
            *extra_blocks
        ]

    return View(
        type="modal",
        callback_id="thank_you_dialog_save_button_clicked",
        title="Update Thank You!" if state else "Say Thank you!",
        submit=submit,
        close="Cancel",
        private_metadata=str(PrivateMetadata(thank_you_message_uuid=None if state is None else state.uuid,
                                             slash_command_slack_channel_id=slash_command_slack_channel_id)),
        blocks=blocks
    )
