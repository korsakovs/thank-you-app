from thankyou.core.models import ThankYouType
from thankyou.dao import dao
from thankyou.slackbot.handlers.common import publish_configuration_view
from thankyou.slackbot.utils.company import get_or_create_company_by_body
from thankyou.slackbot.utils.privatemetadata import PrivateMetadata
from thankyou.slackbot.views.thankyoutypedialog import thank_you_type_deletion_confirmation_dialog, \
    thank_you_type_deletion_completion_dialog


def thank_you_type_dialog_save_button_clicked_action_handler(body, client, logger):
    user_id = body["user"]["id"]
    company = get_or_create_company_by_body(body)

    new_value_name = body["view"]["state"]["values"]["thank_you_type_dialog_value_name_block"][
        "thank_you_type_dialog_value_name_action"]["value"]

    thank_you_type_uuid = PrivateMetadata.from_str(body["view"]["private_metadata"]).thank_you_type_uuid

    if thank_you_type_uuid:
        thank_you_type = dao.read_thank_you_type(company_uuid=company.uuid, thank_you_type_uuid=thank_you_type_uuid)
        thank_you_type.name = new_value_name
    else:
        dao.create_thank_you_type(thank_you_type=ThankYouType(
            company_uuid=company.uuid,
            name=new_value_name
        ))

    publish_configuration_view(
        client=client,
        company=get_or_create_company_by_body(body),
        user_id=user_id
    )


def thank_you_type_dialog_delete_value_button_clicked_action_handler(body, client, logger):
    company = get_or_create_company_by_body(body)
    thank_you_type_uuid = body["actions"][0]["value"]

    client.views_update(
        view_id=body["view"]["id"],
        view=thank_you_type_deletion_confirmation_dialog(thank_you_type=dao.read_thank_you_type(
            company_uuid=company.uuid,
            thank_you_type_uuid=thank_you_type_uuid
        ))
    )


def thank_you_type_deletion_dialog_confirm_deletion_button_clicked_action_handler(body, client, logger):
    user_id = body["user"]["id"]
    company = get_or_create_company_by_body(body)

    thank_you_type_uuid = PrivateMetadata.from_str(body["view"]["private_metadata"]).thank_you_type_uuid
    thank_you_type_name = dao.read_thank_you_type(
        company_uuid=company.uuid, thank_you_type_uuid=thank_you_type_uuid).name

    dao.delete_thank_you_type(company_uuid=company.uuid, thank_you_type_uuid=thank_you_type_uuid)

    client.views_open(
        trigger_id=body["trigger_id"],
        view=thank_you_type_deletion_completion_dialog(thank_you_type_name=thank_you_type_name)
    )

    publish_configuration_view(
        client=client,
        company=get_or_create_company_by_body(body),
        user_id=user_id
    )
