import json
from json import JSONDecodeError
from typing import Optional, List, Dict

from thankyou.slackbot.utils.stringhelpers import es


def rich_text_block_as_markdown(text: str) -> Optional[str]:
    try:
        elements = json.loads(text)["elements"]
    except (TypeError, JSONDecodeError, KeyError):
        return None

    def _rich_text_section(sub_elements: List[Dict]) -> Optional[str]:
        _result = ""
        for sub_element in sub_elements:
            if sub_element["type"] == "text":
                line = es(sub_element["text"])
                if "style" in sub_element:
                    for style, enabled in sub_element["style"].items():
                        if style == "italic":
                            line = f"_{line}_"
                        elif style == "bold":
                            line = f"*{line}*"
                        elif style == "strike":
                            line = f"~{line}~"
                        elif style == "code":
                            return None
                            # line = f"`{line}`"
                        else:
                            return None
                _result += line + "‎"
            else:
                return None
        return _result[0:-1]

    def _rich_text_preformatted(sub_elements: List[Dict]) -> Optional[str]:
        _result = ""
        for sub_element in sub_elements:
            if sub_element["type"] == "text":
                line = sub_element["text"]
                _result += f"```{line}```\n"
        return _result

    result = ""
    for element in elements:
        try:
            if element["type"] == "rich_text_section":
                parse_result = _rich_text_section(element["elements"])
            elif element["type"] == "rich_text_preformatted":
                parse_result = _rich_text_preformatted(element["elements"])
            else:
                return None
            if parse_result is None:
                return None
            result += parse_result
        except (TypeError, KeyError):
            return None

    return result
