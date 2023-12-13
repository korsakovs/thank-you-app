import string
from random import choices

import pytest

from thankyou.core.models import Company, ThankYouMessage
from thankyou.dao import dao, create_initial_data


@pytest.fixture
def non_existing_company_slack_team_id() -> str:
    slack_team_id = "test_slack_team_id_" + "".join(choices(string.ascii_letters, k=16))
    if dao.read_companies(slack_team_id=slack_team_id):
        raise AssertionError("Can not create non-existing test_slack_team_id")
    yield slack_team_id


@pytest.fixture
def non_existing_company(non_existing_company_slack_team_id) -> Company:
    company = Company("test_company_" + "".join(choices(string.ascii_letters, k=16)),
                      slack_team_id=non_existing_company_slack_team_id)
    for c_ in dao.read_companies():
        if c_.uuid == company.uuid:
            raise AssertionError("Can not create non-existing company")
    yield company


@pytest.fixture
def existing_company(non_existing_company) -> Company:
    dao.create_company(non_existing_company)
    create_initial_data(non_existing_company)
    for d_ in dao.read_companies():
        if d_.uuid == non_existing_company.uuid:
            break
    else:
        raise AssertionError("Can not create existing company")
    yield non_existing_company


def test_thank_you_message_insertion(existing_company):
    thank_you_message = ThankYouMessage(
        text="Some Text",
        type=dao.read_thank_you_types(company_uuid=existing_company.uuid)[0],
        company=existing_company
    )
    dao.create_thank_you_message(thank_you_message)
    assert thank_you_message.uuid not in [su.uuid for su in dao.read_thank_you_messages(
        company_uuid=existing_company.uuid)]
    assert thank_you_message.uuid not in [su.uuid for su in dao.read_thank_you_messages(
        company_uuid=existing_company.uuid, published=True)]
    assert thank_you_message.uuid in [su.uuid for su in dao.read_thank_you_messages(
        company_uuid=existing_company.uuid, published=None)]
    assert thank_you_message.uuid in [su.uuid for su in dao.read_thank_you_messages(
        company_uuid=existing_company.uuid, published=False)]
