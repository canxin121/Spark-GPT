from .bard import load_config as load_bard_config
from .chatgpt_web import load_config as load_chat_gpt_web_config
from .claude_ai import load_config as load_claude_ai_config
from .newbing import load_config as load_newbing_config
from .poe import load_config as load_poe_config
from .slack_claude import load_config as load_slack_claude_config
from .spark_desk import load_config as load_spark_desk_config
from .tongyiqianwen import load_config as load_tongyiqianwen_config
from ..common.config import CONFIG_SOURCE
from ..common.load_config import load_command_config
from ..common.prefix_data import prefixes
from ..common.prompt_data import prompts

Generated_Source_Pic = False


def get_able_source():
    from .chatgpt_web import ABLE as CHATGPTWEB_ABLE
    from .newbing import ABLE as NEWBING_ABLE
    from .poe import ABLE as POE_ABLE
    from .slack_claude import ABLE as SLACKCLAUDE_ABLE
    from .claude_ai import ABLE as CLAUDE_AI_ABLE
    from .bard import ABLE as BARD_ABLE
    from .spark_desk import ABLE as SPARKDESK_ABLE
    from .tongyiqianwen import ABLE as TongYiQianWen_ABLE
    from .poe import SUBSCRIBE_ABLE as POE_SUBSCRIBE_ABLE
    able_dict = {
        "poe chatgpt": {
            "able": POE_ABLE,
            "des": "poe网站的chatgpt,支持预设最长约2000字,支持前缀但字数不宜过多",
        },
        "poe claude": {
            "able": POE_ABLE,
            "des": "poe网站的claude,支持预设最长约2000字,支持前缀但字数不宜过多",
        },
        "poe chatgpt4": {
            "able": POE_SUBSCRIBE_ABLE,
            "des": "poe网站的chatgpt4,仅限已定阅用户使用,仅限白名单用户对话使用,支持预设最长约2000字,支持前缀但字数不宜过多",
        },
        "poe claude-2-100k": {
            "able": POE_SUBSCRIBE_ABLE,
            "des": "poe网站的claude-2-100k,仅限已定阅用户使用,仅限白名单用户对话使用,支持预设最长约2000字,支持前缀但字数不宜过多",
        },
        "chatgpt web": {
            "able": CHATGPTWEB_ABLE,
            "des": "openai官网的chatgpt网页版,支持预设最长约5400字,支持前缀但字数不宜过多",
        },
        "claude ai": {
            "able": CLAUDE_AI_ABLE,
            "des": "claude官网的claude网页版,支持超极长的预设,有内容安全审查,支持前缀字数也很长",
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
    source_des_dict = {}
    i = 0
    for source, dict in able_dict.items():
        if dict["able"]:
            i += 1
            source_dict[str(i)] = source
            source_des_dict[source] = dict["des"]

    return source_dict, source_des_dict


def load_all_config():
    prompts.Generated = False
    prefixes.Generated = False
    load_command_config()
    load_bard_config()
    load_newbing_config()
    load_poe_config()
    load_slack_claude_config()
    load_claude_ai_config()
    load_chat_gpt_web_config()
    load_spark_desk_config()
    load_tongyiqianwen_config()


# 定义一个字典，把配置源和配置函数对应起来
CONFIG_DICT = {
    "总控配置": load_all_config,
    "Newbing配置": load_newbing_config,
    "Spark Desk配置": load_spark_desk_config,
    "Chat GPT web配置": load_chat_gpt_web_config,
    "Claude Slack配置": load_slack_claude_config,
    "Claude Ai配置": load_claude_ai_config,
    "Poe配置": load_poe_config,
    "Bard配置": load_bard_config,
    "通义千问配置": load_tongyiqianwen_config,
}


def load_config(source: CONFIG_SOURCE):
    global Generated_Source_Pic
    Generated_Source_Pic = False
    config_func = CONFIG_DICT.get(source)
    if config_func:
        config_func()
    else:
        raise Exception(f"load_config时error: 无效的配置源: {source}")


def get_source_pic():
    global Generated_Source_Pic
    Generated_Source_Pic = True
