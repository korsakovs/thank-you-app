from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from slack_sdk.models.blocks import SectionBlock
from slack_sdk.models.views import View
from slack_sdk.web import SlackResponse

from thankyou.core.models import ThankYouReceiver, ThankYouMessageImage, ThankYouMessageSlackDelivery
from thankyou.dao import dao
from thankyou.slackbot.blocks.thank_you import thank_you_message_blocks
from thankyou.slackbot.handlers.common import already_invited_to_a_channel
from thankyou.slackbot.utils.company import get_or_create_company_by_body
from thankyou.slackbot.utils.employee import get_or_create_employee_by_slack_user_id
from thankyou.slackbot.utils.privatemetadata import retrieve_thank_you_message_from_body
from thankyou.slackbot.views.homepage import home_page_company_thank_yous_view


def thank_you_dialog_save_button_clicked_action_handler(body, client: WebClient, logger):
    def message_ts(response_: SlackResponse):
        if "ts" in response_.data:
            return response_.data["ts"]
        return response_.data["message_ts"]

    user_id = body["user"]["id"]
    company = get_or_create_company_by_body(body)
    employee = get_or_create_employee_by_slack_user_id(company_uuid=company.uuid, slack_user_id=user_id)

    thank_you_message = retrieve_thank_you_message_from_body(body)
    initial_message = dao.read_thank_you_message(company_uuid=company.uuid,
                                                 thank_you_message_uuid=thank_you_message.uuid)
    if not initial_message:
        dao.create_thank_you_message(thank_you_message)
    else:
        initial_message.text = thank_you_message.text
        initial_message.is_rich_text = thank_you_message.is_rich_text
        for receiver_to_add in thank_you_message.receivers:
            if receiver_to_add.slack_user_id not in (r.slack_user_id for r in initial_message.receivers):
                initial_message.receivers.append(ThankYouReceiver(receiver_to_add.slack_user_id))
        for receiver_to_delete in initial_message.receivers:
            if receiver_to_delete.slack_user_id not in (r.slack_user_id for r in thank_you_message.receivers):
                dao.delete_receiver(receiver_to_delete)
        for image in initial_message.images:
            dao.delete_thank_you_image(image)
        for image in thank_you_message.images:
            initial_message.images.append(image)
        if initial_message.type != thank_you_message.type:
            initial_message.type = thank_you_message.type
        # initial_message.receivers = thank_you_message.receivers

    if initial_message:
        try:
            for slack_delivery in initial_message.slack_deliveries:
                if not slack_delivery.deleted:
                    try:
                        client.chat_update(
                            channel=slack_delivery.slack_channel_id,
                            ts=slack_delivery.message_ts,
                            blocks=thank_you_message_blocks(
                                thank_you_message,
                                show_say_thank_you_button=(slack_delivery.is_direct_message
                                                           or slack_delivery.is_ephemeral_message)
                            ),
                        )
                    except SlackApiError as api_error:
                        if api_error.response["error"] != "message_not_found":
                            raise
        except Exception as e:
            logger.error(f"Could not update a message {initial_message.uuid} for company {company.uuid}: {e}")
    else:
        should_send_directly_to_user = False
        could_not_send_ephemeral_messages_to = []

        if thank_you_message.slash_command_slack_channel_id:
            try:
                if thank_you_message.is_private:
                    for receiver in set([r.slack_user_id for r in thank_you_message.receivers]
                                        + [thank_you_message.author_slack_user_id]):
                        try:
                            response = client.chat_postEphemeral(
                                user=receiver,
                                channel=thank_you_message.slash_command_slack_channel_id,
                                blocks=thank_you_message_blocks(
                                    thank_you_message,
                                    show_say_thank_you_button=user_id in [
                                        r.slack_user_id for r in thank_you_message.receivers]
                                ),
                                unfurl_links=False,
                                unfurl_media=False,
                            )
                            dao.create_thank_you_message_slack_delivery(ThankYouMessageSlackDelivery(
                                thank_you_message_uuid=thank_you_message.uuid,
                                slack_channel_id=thank_you_message.slash_command_slack_channel_id,
                                message_ts=message_ts(response),
                                is_direct_message=False,
                                is_ephemeral_message=True,
                            ))
                        except SlackApiError as err:
                            response: SlackResponse = err.response
                            data: dict = response.data
                            if not data["ok"] and data["error"] == "user_not_in_channel":
                                could_not_send_ephemeral_messages_to.append(receiver)
                            else:
                                raise

                else:
                    response = client.chat_postMessage(
                        channel=thank_you_message.slash_command_slack_channel_id,
                        blocks=thank_you_message_blocks(thank_you_message),
                        unfurl_links=False,
                        unfurl_media=False,
                    )
                    dao.create_thank_you_message_slack_delivery(ThankYouMessageSlackDelivery(
                        thank_you_message_uuid=thank_you_message.uuid,
                        slack_channel_id=thank_you_message.slash_command_slack_channel_id,
                        message_ts=message_ts(response),
                        is_direct_message=False,
                        is_ephemeral_message=False,
                    ))
            except SlackApiError as e:
                if e.response.data["error"] == "channel_not_found":
                    should_send_directly_to_user = True
                    try:
                        response = client.chat_postMessage(
                            text=f"Your thank you message could not be "
                                 f"delivered to the Slack channel "
                                 f"<#{thank_you_message.slash_command_slack_channel_id}>. "
                                 f"Are you sure that the {company.merci_app_name} application was invited "
                                 f"to this channel? "
                                 f"We will deliver your message directly to the receivers",
                            channel=thank_you_message.author_slack_user_id,
                            unfurl_links=False,
                            unfurl_media=False,
                        )
                        dao.create_thank_you_message_slack_delivery(ThankYouMessageSlackDelivery(
                            thank_you_message_uuid=thank_you_message.uuid,
                            slack_channel_id=thank_you_message.author_slack_user_id,
                            message_ts=message_ts(response),
                            is_direct_message=True,
                            is_ephemeral_message=False,
                        ))
                    except SlackApiError as e2:
                        logger.error("Couldn't inform a user about the fact that their message had not been delivered "
                                     f"to a slack channel there they typed a /thanks or /merci command. Error: {e2}")
                else:
                    logger.error("A thank you message was not delivered to the slack channel in which the slash command"
                                 f" was typed. Channel: {thank_you_message.slash_command_slack_channel_id}. Error: {e}")

        elif company.enable_sharing_in_a_slack_channel and company.share_messages_in_slack_channel:
            def invite_users():
                slack_user_ids = [_receiver.slack_user_id for _receiver in thank_you_message.receivers
                                  if not already_invited_to_a_channel(
                                    company_id=company.uuid,
                                    channel=company.share_messages_in_slack_channel,
                                    user_id=_receiver.slack_user_id
                                  )]
                if not slack_user_ids:
                    return
                try:
                    client.conversations_invite(
                        channel=company.share_messages_in_slack_channel,
                        users=slack_user_ids,
                        force=True
                    )
                except SlackApiError as e:
                    logger.warning(f"Can not invite users {slack_user_ids} to a slack channel "
                                   f"{company.share_messages_in_slack_channel}. Error: {e}")
                    raise

            try:
                invite_users()
            except SlackApiError as err:
                response: SlackResponse = err.response
                data: dict = response.data
                if not data["ok"] and data["error"] == "not_in_channel":
                    try:
                        client.conversations_join(
                            channel=company.share_messages_in_slack_channel,
                        )
                        invite_users()
                    except SlackApiError as err2:
                        logger.error(f"Could not join the {company.share_messages_in_slack_channel} slack channel. "
                                     f"Or couldn't invite users to it: {err2}")
                else:
                    logger.warning(f"Could not invite users to the {company.share_messages_in_slack_channel} "
                                   f"slack channel. Error: {err}")

            try:
                if thank_you_message.is_private:
                    for receiver in set([r.slack_user_id for r in thank_you_message.receivers]
                                        + [thank_you_message.author_slack_user_id]):
                        try:
                            response = client.chat_postEphemeral(
                                channel=company.share_messages_in_slack_channel,
                                blocks=thank_you_message_blocks(
                                    thank_you_message,
                                    show_say_thank_you_button=user_id in [
                                        r.slack_user_id for r in thank_you_message.receivers]
                                ),
                                user=receiver,
                                unfurl_links=False,
                                unfurl_media=False,
                            )
                            dao.create_thank_you_message_slack_delivery(ThankYouMessageSlackDelivery(
                                thank_you_message_uuid=thank_you_message.uuid,
                                slack_channel_id=company.share_messages_in_slack_channel,
                                message_ts=message_ts(response),
                                is_direct_message=False,
                                is_ephemeral_message=True,
                            ))
                        except SlackApiError as err:
                            response: SlackResponse = err.response
                            data: dict = response.data
                            if not data["ok"] and data["error"] == "user_not_in_channel":
                                could_not_send_ephemeral_messages_to.append(receiver)
                            else:
                                raise
                else:
                    response = client.chat_postMessage(
                        channel=company.share_messages_in_slack_channel,
                        blocks=thank_you_message_blocks(thank_you_message),
                        unfurl_links=False,
                        unfurl_media=False,
                    )
                    dao.create_thank_you_message_slack_delivery(ThankYouMessageSlackDelivery(
                        thank_you_message_uuid=thank_you_message.uuid,
                        slack_channel_id=company.share_messages_in_slack_channel,
                        message_ts=message_ts(response),
                        is_direct_message=False,
                        is_ephemeral_message=False,
                    ))
            except SlackApiError as e:
                logger.error(f"Can not deliver a thank you message to a slack channel "
                             f"{company.share_messages_in_slack_channel}. Error: {e}")

        else:
            should_send_directly_to_user = True

        if should_send_directly_to_user or could_not_send_ephemeral_messages_to:
            slack_ids = set([r.slack_user_id for r in thank_you_message.receivers]
                            + could_not_send_ephemeral_messages_to)
            for receiver in slack_ids:
                try:
                    response = client.chat_postMessage(
                        text="You received a Thank You message!",
                        channel=receiver,
                        blocks=thank_you_message_blocks(
                            thank_you_message,
                            show_say_thank_you_button=user_id in [
                                r.slack_user_id for r in thank_you_message.receivers]
                        ),
                        unfurl_links=False,
                        unfurl_media=False,
                    )
                    dao.create_thank_you_message_slack_delivery(ThankYouMessageSlackDelivery(
                        thank_you_message_uuid=thank_you_message.uuid,
                        slack_channel_id=receiver,
                        message_ts=message_ts(response),
                        is_direct_message=True,
                        is_ephemeral_message=True,
                    ))
                except SlackApiError as e:
                    logger.error(f"Can not sent a thank you message directly to user {receiver}. Error: {e}")

    client.views_publish(
        user_id=user_id,
        view=home_page_company_thank_yous_view(
            thank_you_messages=dao.read_thank_you_messages(company_uuid=company.uuid, last_n=20, private=False),
            app_name=company.merci_app_name,
            current_user_slack_id=user_id,
            enable_leaderboard=company.enable_leaderboard,
            show_welcome_message=not employee.closed_welcome_message
        )
    )

    try:
        text = "Your thank you message was successfully sent! The receivers were successfully notified. Thank you!"
        if initial_message:
            text = "Your thank you message was successfully updated!"

        client.views_open(
            trigger_id=body["trigger_id"],
            view=View(
                title="Done!",
                type="modal",
                blocks=[
                    SectionBlock(text=text)
                ]
            )
        )
    except SlackApiError as e:
        if e.response["error"] != "expired_trigger_id":
            logger.warning(f"Could not notify user {user_id} (Company id = {company.uuid}) about the fact that their "
                           f"thank you message was sent - can't open a dialog view: {e}")
        try:
            client.chat_postMessage(
                channel=user_id,
                text="Your thank you message was successfully sent! The receivers were successfully notified. "
                     "Thank you!"
            )
        except SlackApiError as e:
            logger.error(f"Could not notify user {user_id} (Company id = {company.uuid}) about the fact that their "
                         f"thank you message was sent - can't send a private message: {e}")

