from .bard import load_config as load_bard_config
from .chatgpt_web import load_config as load_chat_gpt_web_config
from .newbing import load_config as load_newbing_config
from .poe import load_config as load_poe_config
from .slack_claude import load_config as load_slack_claude_config
from .spark_desk import load_config as load_spark_desk_config
from .tongyiqianwen import load_config as load_tongyiqianwen_config
from ..common.config import CONFIG_SOURCE
from ..common.load_config import load_command_config


def get_able_source():
    from .chatgpt_web import ABLE as CHATGPTWEB_ABLE
    from .newbing import ABLE as NEWBING_ABLE
    from .poe import ABLE as POE_ABLE
    from .slack_claude import ABLE as SLACKCLAUDE_ABLE
    from .bard import ABLE as BARD_ABLE
    from .spark_desk import ABLE as SPARKDESK_ABLE
    from .tongyiqianwen import ABLE as TongYiQianWen_ABLE

    # 用一个列表来存储所有的来源和介绍
    sources = [
        ("poe chatgpt", POE_ABLE, "poe网站的chatgpt,支持预设最长约2000字,支持前缀但字数不宜过多"),
        ("poe claude", POE_ABLE, "poe网站的claude,支持预设最长约2000字,支持前缀但字数不宜过多"),
        (
            "chatgpt web",
            CHATGPTWEB_ABLE,
            "openai官网的chatgpt网页版,支持预设最长约5400字,支持前缀但字数不宜过多",
        ),
        ("slack claude", SLACKCLAUDE_ABLE, "slack网站的claude,支持非常长的预设,支持前缀但字数不宜过多"),
        ("sydneybing", NEWBING_ABLE, "微软的Newbing越狱版,支持长度约4000的预设,支持前缀但字数不宜过多"),
        ("spark desk", SPARKDESK_ABLE, "讯飞的讯飞星火语言模型,支持少数短预设和前缀"),
        ("通义千问", TongYiQianWen_ABLE, "阿里的通义千问,不支持预设"),
        ("bing", NEWBING_ABLE, "微软的Newbing,不支持预设"),
        ("bard", BARD_ABLE, "谷歌的Bard,不支持预设"),
    ]

    # 用一个推导式来生成字典和表格
    source_dict = {
        str(i + 1): source for i, (source, able, des) in enumerate(sources) if able
    }
    source_dict_str = (
            "\n\n| 序号 | 来源名称 | 来源介绍 |\n| --- | --- | --- |\n"
            + "\n".join(
        f"| {i + 1} | {source} | {des} |"
        for i, (source, able, des) in enumerate(sources)
        if able
    )
            + "\n"
    )

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


# 定义一个字典，把配置源和配置函数对应起来
CONFIG_DICT = {
    "总控配置": load_all_config,
    "Newbing配置": load_newbing_config,
    "Spark Desk配置": load_spark_desk_config,
    "Chat GPT web配置": load_chat_gpt_web_config,
    "Claude Slack配置": load_slack_claude_config,
    "Poe配置": load_poe_config,
    "Bard配置": load_bard_config,
    "通义千问配置": load_tongyiqianwen_config
}


def load_config(source: CONFIG_SOURCE):
    config_func = CONFIG_DICT.get(source)
    if config_func:
        config_func()
    else:
        raise Exception(f"load_config时error: 无效的配置源: {source}")
