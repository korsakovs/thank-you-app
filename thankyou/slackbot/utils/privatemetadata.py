import json

from thankyou.core.models import ThankYouMessage, ThankYouReceiver, ThankYouMessageImage
from thankyou.dao import dao
from thankyou.slackbot.utils.company import get_or_create_company_by_body


class PrivateMetadata:
    def __init__(self, thank_you_message_uuid: str = None, thank_you_type_uuid: str = None,
                 slash_command_slack_channel_id: str = None):
        self.thank_you_message_uuid = thank_you_message_uuid
        self.thank_you_type_uuid = thank_you_type_uuid
        self.slash_command_slack_channel_id = slash_command_slack_channel_id

    def __str__(self):
        return self.as_str()

    def as_str(self):
        result = dict()
        for key, value in {
            "thank_you_message_uuid": self.thank_you_message_uuid,
            "thank_you_type_uuid": self.thank_you_type_uuid,
            "slash_command_slack_channel_id": self.slash_command_slack_channel_id,
        }.items():
            if value is not None:
                result[key] = value
        return json.dumps(result)

    @classmethod
    def from_str(cls, s: str):
        if not s:
            return PrivateMetadata()
        d = json.loads(s)
        return PrivateMetadata(
            thank_you_message_uuid=d.get("thank_you_message_uuid"),
            thank_you_type_uuid=d.get("thank_you_type_uuid"),
            slash_command_slack_channel_id=d.get("slash_command_slack_channel_id")
        )


def retrieve_private_metadata_from_view(body) -> PrivateMetadata:
    return PrivateMetadata.from_str(body["view"]["private_metadata"])


def retrieve_thank_you_message_from_body(body) -> ThankYouMessage:
    values = body["view"]["state"]["values"]
    user_id = body["user"]["id"]
    private_metadata = retrieve_private_metadata_from_view(body)
    company_uuid = get_or_create_company_by_body(body).uuid

    try:
        selected_type = values["thank_you_dialog_thank_you_type_block"]["thank_you_dialog_thank_you_type_action_id"][
            "selected_option"]
        if selected_type is not None:
            selected_type = dao.read_thank_you_type(company_uuid=company_uuid,
                                                    thank_you_type_uuid=selected_type["value"])
    except (TypeError, KeyError):
        selected_type = None

    try:
        is_private = bool(len(values["thank_you_dialog_is_private_block"][
                                  "thank_you_dialog_send_privately_action"]["selected_options"]))
    except (TypeError, KeyError):
        is_private = False

    """
    try:
        link = values[STATUS_UPDATE_LINK_BLOCK][
            STATUS_UPDATE_MODAL_STATUS_UPDATE_LINK_ACTION_ID]["value"]
    except (KeyError, TypeError):
        link = None 
    """

    kwargs = dict()
    if private_metadata and private_metadata.thank_you_message_uuid:
        kwargs["uuid"] = private_metadata.thank_you_message_uuid

    if private_metadata and private_metadata.slash_command_slack_channel_id:
        kwargs["slash_command_slack_channel_id"] = private_metadata.slash_command_slack_channel_id

    slack_team_id = body["team"]["id"]
    try:
        company = dao.read_companies(slack_team_id=slack_team_id)[0]
    except IndexError:
        raise IndexError(f"Can not find company with slack_team_id = {slack_team_id}")

    receivers = [ThankYouReceiver(slack_user_id=receiver_slack_id)
                 for receiver_slack_id in values["thank_you_dialog_receivers_block"][
                     "thank_you_dialog_receivers_action_id"]["selected_users"]]

    try:
        images = [ThankYouMessageImage(url=image["url_private"], filename=image["name"], ordering_key=ordering_key)
                  for ordering_key, image in enumerate(values["thank_you_dialog_attached_files_block"][
                                                           "thank_you_dialog_attached_files_action_id"]["files"])]
    except (TypeError, KeyError):
        images = []

    text_element = values["thank_you_dialog_text_block"]["thank_you_dialog_text_action_id"]
    if text_element["type"] == "rich_text_input":
        text = json.dumps(text_element["rich_text_value"])
        is_rich_text = True
    else:
        text = text_element["value"]
        is_rich_text = False

    return ThankYouMessage(
        type=selected_type,
        text=text,
        is_rich_text=is_rich_text,
        author_slack_user_id=user_id,
        receivers=receivers,
        images=images,
        company=company,
        is_private=is_private,
        **kwargs
    )
