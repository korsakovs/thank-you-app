from typing import Optional

from slack_sdk.models.blocks import ActionsBlock, CheckboxesElement, Option


def checkbox_action_block(
        element_action_id: str,
        checkbox_value: str,
        checkbox_label: str,
        enabled: bool,
        block_id: str = None,
):
    return ActionsBlock(
        block_id=block_id,
        elements=[
            CheckboxesElement(
                action_id=element_action_id,
                initial_options=[] if not enabled else [
                    Option(value=checkbox_value, label=checkbox_label)
                ],
                options=[
                    Option(value=checkbox_value, label=checkbox_label)
                ]
            )
        ]
    )
