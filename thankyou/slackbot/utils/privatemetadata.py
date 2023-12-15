import json

from thankyou.core.models import ThankYouMessage, ThankYouReceiver
from thankyou.dao import dao
from thankyou.slackbot.utils.company import get_or_create_company_by_body


class PrivateMetadata:
    def __init__(self, thank_you_message_uuid: str = None):
        self.thank_you_message_uuid = thank_you_message_uuid

    def __str__(self):
        return self.as_str()

    def as_str(self):
        return json.dumps({
            "thank_you_message_uuid": self.thank_you_message_uuid
        })

    @classmethod
    def from_str(cls, s: str):
        if not s:
            return PrivateMetadata()
        d = json.loads(s)
        return PrivateMetadata(
            thank_you_message_uuid=d.get("thank_you_message_uuid")
        )


def retrieve_private_metadata_from_view(body) -> PrivateMetadata:
    return PrivateMetadata.from_str(body["view"]["private_metadata"])


def retrieve_thank_you_message_from_body(body) -> ThankYouMessage:
    values = body["view"]["state"]["values"]
    user_id = body["user"]["id"]
    user_name = body["user"]["name"]
    private_metadata = retrieve_private_metadata_from_view(body)
    company_uuid = get_or_create_company_by_body(body).uuid

    selected_type = values["thank_you_dialog_thank_you_type_block"]["thank_you_dialog_thank_you_type_action_id"][
        "selected_option"]
    if selected_type is not None:
        selected_type = dao.read_thank_you_type(company_uuid=company_uuid, thank_you_type_uuid=selected_type["value"])

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

    slack_team_id = body["team"]["id"]
    try:
        company = dao.read_companies(slack_team_id=slack_team_id)[0]
    except IndexError:
        raise IndexError(f"Can not find company with slack_team_id = {slack_team_id}")

    receivers = [ThankYouReceiver(slack_user_id=receiver_slack_id)
                 for receiver_slack_id in values["thank_you_dialog_receivers_block"][
                     "thank_you_dialog_receivers_action_id"]["selected_users"]]

    return ThankYouMessage(
        type=selected_type,
        text=values["thank_you_dialog_text_block"]["thank_you_dialog_text_action_id"]["value"],
        author_slack_user_id=user_id,
        author_slack_user_name=user_name,
        receivers=receivers,
        company=company,
        **kwargs
    )
