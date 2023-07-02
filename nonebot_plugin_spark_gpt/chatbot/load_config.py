from typing import Literal
from .bard import load_config as load_bard_config
from .chatgpt_web import load_config as load_chat_gpt_web_config
from .newbing import load_config as load_newbing_config
from .Poe import load_config as load_poe_config
from .slack_claude import load_config as load_slack_claude_config
from .bard import load_config as load_bard_config
from .spark_desk import load_config as load_spark_desk_config
from .tongyiqianwen import load_config as load_tongyiqianwen_config
from ..platforms.nonebot.utils import load_config as load_common_config
from ..common.config import CONFIG_SOURCE
from ..platforms.nonebot.main import load_config as load_command_config

def get_able_source():
    from .bard import ABLE as BARD_ABLE
    from .chatgpt_web import ABLE as CHATGPTWEB_ABLE
    from .newbing import ABLE as NEWBING_ABLE
    from .Poe import ABLE as POE_ABLE
    from .slack_claude import ABLE as SLACKCLAUDE_ABLE
    from .bard import ABLE as BARD_ABLE
    from .spark_desk import ABLE as SPARKDESK_ABLE
    from .tongyiqianwen import ABLE as TongYiQianWen_ABLE

    able_dict = {
        "poe chatgpt": POE_ABLE,
        "poe claude": POE_ABLE,
        "chatgpt web": CHATGPTWEB_ABLE,
        "slack claude": SLACKCLAUDE_ABLE,
        "spark desk": SPARKDESK_ABLE,
        "bing": NEWBING_ABLE,
        "bard": BARD_ABLE,
        "通义千问": TongYiQianWen_ABLE,
    }
    source_dict = {}
    source_dict_str = ""
    i = 0
    for source, ABLE in able_dict.items():
        if ABLE:
            i += 1
            key = str(i)
            source_dict[key] = source
            source_dict_str += f"{key}: {source}\n"

    return source_dict, source_dict_str


def load_all_config():
    load_common_config()
    load_command_config()
    load_bard_config()
    load_newbing_config()
    load_poe_config()
    load_slack_claude_config()
    load_chat_gpt_web_config()
    load_spark_desk_config()
    load_tongyiqianwen_config()


def load_config(source: CONFIG_SOURCE):
    if source == "总控配置":
        load_all_config()
        load_command_config()
    elif source == "Newbing配置":
        load_newbing_config()
    elif source == "Spark Desk配置":
        load_spark_desk_config()
    elif source == "Chat GPT web配置":
        load_chat_gpt_web_config()
    elif source == "Claude Slack配置":
        load_slack_claude_config()
    elif source == "Poe配置":
        load_poe_config()
    elif source == "Bard配置":
        load_bard_config()
    elif source == "通义千问配置":
        load_tongyiqianwen_config()
