from slack_sdk.models.blocks import HeaderBlock, DividerBlock, SectionBlock, TextObject, ContextBlock
from slack_sdk.models.views import View

from thankyou.slackbot.blocks.homepage import home_page_actions_block


def home_page_help_view():
    return View(
        type="home",
        title="Welcome to Chirik Bot!",
        blocks=[
            home_page_actions_block(selected="help"),
            DividerBlock(),
            HeaderBlock(text="Help"),
            SectionBlock(
                text=TextObject(
                    type="mrkdwn",
                    text="Please refer to the following pages to find more information about this application:\n"
                         "* <https://merci.emgbook.com/faq|Frequently Asked Questions>\n"
                         "* <https://merci.emgbook.com/configuration|Configuration> - "
                         "check this page for more information on how to set up this application\n"
                         "* <https://merci.emgbook.com/contactus|Contact Us> - in case you want to reach out to us"
                )
            ),
            HeaderBlock(
                text="Buy me a coffee"
            ),
            ContextBlock(
                elements=[TextObject(text="As of today, The Merci! application is offered free of charge. "
                                          "Please, consider supporting authors of the application by "
                                          "<https://merci.emgbook.com/buymeacoffee|buying them> a coffee! Thank you :)",
                                     type="mrkdwn")]
            ),
        ]
    )
