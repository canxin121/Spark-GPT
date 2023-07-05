from .Poe import load_config as load_poe_config
from .bard import load_config as load_bard_config
from .chatgpt_web import load_config as load_chat_gpt_web_config
from .newbing import load_config as load_newbing_config
from .slack_claude import load_config as load_slack_claude_config
from .spark_desk import load_config as load_spark_desk_config
from .tongyiqianwen import load_config as load_tongyiqianwen_config
from ..common.config import CONFIG_SOURCE
from ..common.load_config import load_command_config


def get_able_source():
    from .chatgpt_web import ABLE as CHATGPTWEB_ABLE
    from .newbing import ABLE as NEWBING_ABLE
    from .Poe import ABLE as POE_ABLE
    from .slack_claude import ABLE as SLACKCLAUDE_ABLE
    from .bard import ABLE as BARD_ABLE
    from .spark_desk import ABLE as SPARKDESK_ABLE
    from .tongyiqianwen import ABLE as TongYiQianWen_ABLE

    able_dict = {
        "poe chatgpt": {"able": POE_ABLE, "des": "poe网站的chatgpt,支持预设最长约830字,支持前缀但字数不宜过多"},
        "poe claude": {"able": POE_ABLE, "des": "poe网站的claude,支持预设最长约830字,支持前缀但字数不宜过多"},
        "chatgpt web": {
            "able": CHATGPTWEB_ABLE,
            "des": "openai官网的chatgpt网页版,支持预设最长约5400字,支持前缀但字数不宜过多",
        },
        "slack claude": {
            "able": SLACKCLAUDE_ABLE,
            "des": "slack网站的claude,支持非常长的预设,支持前缀但字数不宜过多",
        },
        "sydneybing": {
            "able": NEWBING_ABLE,
            "des": "微软的Newbing越狱版,支持长度约4000的预设,支持前缀但字数不宜过多",
        },
        "spark desk": {
            "able": SPARKDESK_ABLE,
            "des": "讯飞的讯飞星火语言模型,支持少数短预设和前缀",
        },
        "通义千问": {
            "able": TongYiQianWen_ABLE,
            "des": "阿里的通义千问,不支持预设",
        },
        "bing": {
            "able": NEWBING_ABLE,
            "des": "微软的Newbing,不支持预设",
        },
        "bard": {
            "able": BARD_ABLE,
            "des": "谷歌的Bard,不支持预设",
        },
    }
    
    source_dict = {}
    source_dict_str = "\n\n| 序号 | 来源名称 | 来源介绍 |\n| --- | --- | --- |\n"
    i = 0
    for source, dict in able_dict.items():
        if dict["able"]:
            i += 1
            order = str(i)
            des = dict["des"]
            source_dict[order] = source
            source_dict_str += f"| {order} | {source} | {des} |\n"
    source_dict_str += "\n"

    return source_dict, source_dict_str


def load_all_config():
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
