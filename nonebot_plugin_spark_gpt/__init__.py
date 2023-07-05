from nonebot.plugin import PluginMetadata

from . import platforms
from .common.web import app

__plugin_meta__ = PluginMetadata(
    name="Spark_GPT",
    description="将poe,chatgpt,slack claude,Newbing,SydneyBing,google bard,讯飞星火模型(SparkDesk),通义千问等接入qq,tg,kook(原开黑啦)多平台用户绑定实现数据互通,并提供webui进行便捷配置,自适应文转图,实现预设人格化bot的便捷创建,使用和管理",
    usage="查看/shelp命令",
    extra={},
    supported_adapters=[
        "nonebot.adapters.kaiheila",
        "nonebot.adapters.telegram",
        "nonebot.adapters.onebot.v11",
    ],
    type="application",
    homepage="https://github.com/canxin121/Spark-GPT",
)
