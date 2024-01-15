from threading import Lock

from thankyou.core.models import Employee
from thankyou.dao import dao

CREATE_EMPLOYEE_LOCK = Lock()


def get_or_create_employee_by_slack_user_id(company_uuid: str, slack_user_id: str) -> Employee:
    employee = dao.read_employee_by_slack_id(company_uuid=company_uuid, slack_user_id=slack_user_id)
    if employee is not None:
        return employee
    with CREATE_EMPLOYEE_LOCK:
        employee = dao.read_employee_by_slack_id(company_uuid=company_uuid, slack_user_id=slack_user_id)
        if employee is not None:
            return employee
        employee = Employee(
            company_uuid=company_uuid,
            slack_user_id=slack_user_id
        )
        dao.create_employee(employee)
        return employee
