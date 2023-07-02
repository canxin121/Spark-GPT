from . import platforms
from .common.web import app
from nonebot.plugin import PluginMetadata

__plugin_meta__ = PluginMetadata(
    name="Spark_GPT",
    description="提供多平台数据互通的多来源人格化gpt语言模型便捷使用,提供webui用以配置和管理预设人格",
    usage="查看/help命令",
    extra={},
)
