import html


def build_default_install_page_html(url: str) -> str:
    return f"""<html>
<head>
<link rel="icon" href="data:,">
<style>
body {{
  padding: 0px 0px;
  font-family: verdana;
  text-align: center;
}}
</style>
</head>
<body>
<p><a href="{html.escape(url)}" target="_blank"><img alt=""Add to Slack"" height="40" width="139" src="https://platform.slack-edge.com/img/add_to_slack.png" srcset="https://platform.slack-edge.com/img/add_to_slack.png 1x, https://platform.slack-edge.com/img/add_to_slack@2x.png 2x" /></a></p>
</body>
</html>
"""
