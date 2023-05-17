from pathlib import Path
import nonebot

from .common.render.render import md_to_pic

from .newbing import main
from .chatgpt_web import main
from .common import main
from .common.config import spark_persistor

if spark_persistor.poe_api_mode == 0:
    from .poe_http import main
elif spark_persistor.poe_api_mode == 1:
    from .poe_pw import main

from .claude_slack import main
from .Spark_desk import main
from .bard import main
from nonebot.matcher import Matcher
from nonebot.plugin import PluginMetadata
from nonebot.adapters.onebot.v11 import (
    Event,
    Bot,
    MessageSegment,
)
sourcepath = str(Path(__file__).parent / "source")

__version__ = "0.1.9"
__plugin_meta__ = PluginMetadata(
    "Spark-GPT",
    "将多来源的gpt接入qq及更多平台(todo)，使用便捷，管理完善，功能强大",
    "通过/help /帮助 /说明 /使用说明  命令来获取详细使用说明",
    {"Author": "canxin121"},
)


poe_help = nonebot.on_command(
    "help", aliases={"帮助", "使用说明", "说明"}, priority=4, block=False
)


@poe_help.handle()
async def __poe_help__(bot: Bot, matcher: Matcher, event: Event):
    user_id = str(event.user_id)
    msg = """
# Spark-GPT 帮助说明

- 以下命令前面全部要加 '/'。

## Poe帮助命令

| 命令 | 描述 |
| --- | --- |
| `/poehelp / ph` | 获取Poe帮助说明。 |

## Newbing帮助命令

| 命令 | 描述 |
| --- | --- |
| `/binghelp / bh` | 获取Newbing帮助说明。 |

## GPT_Web帮助命令

| 命令 | 描述 |
| --- | --- |
| `/gwhelp / gwh` | 获取GPT_Web帮助说明。 |

## Claude_Slack帮助命令

| 命令 | 描述 |
| --- | --- |
| `/chelp / ch` | 获取Claude_Slack帮助说明。 |

## Spark_desk帮助命令

| 命令 | 描述 |
| --- | --- |
| `/shelp / sh` | 获取Spark_desk帮助说明。 |

## Bard帮助命令

| 命令 | 描述 |
| --- | --- |
| `/bardhelp / gbh` | 获取Spark_desk帮助说明。 |

# 通用命令

- 所有用户均可使用

| 命令 | 描述 |
| --- | --- |
| `/bot列表 / botlist / bl` | 获取你的所有机器人的列表。 |
| `/bot信息 / botinfo / bi + 名字` | 获取你的机器人的详细信息。 |
| `/bot更改 / botchange / bc + 名字` | 更改你的机器人的信息。 |
| `/共享bot列表 / sharebotlist / sbl` | 获取所有共享机器人的列表。 |

- 只有spark管理员可以使用

| 命令 | 描述 |
| --- | --- |
| `/添加预设 / ap` | 添加通用预设 |
| `/删除预设 / rp` | 删除通用预设 |
| `/sbr / sharebotremove + 名字` | 删除共享机器人 |
| `/sbc / sharebotchange + 名字` | 更改共享机器人 |



"""
    # pic = await md_to_pic(msg)
    # await matcher.send(MessageSegment.image(pic))
    await poe_help.send(MessageSegment.image(Path(sourcepath / Path("demo(1).png")).absolute()))
    await poe_help.finish()
