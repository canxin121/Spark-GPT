<div align="center">
  <a href="https://github.com/canxin121">
    <img src="https://socialify.git.ci/canxin121/Spark-GPT/image?font=Raleway&forks=1&issues=1&language=1&logo=https%3A%2F%2Fcanxin121.github.io%2Fdocs%2Flogo.png&name=1&owner=1&pattern=Charlie%20Brown&pulls=1&stargazers=1&theme=Auto" width="700" height="350">
  </a>
  <h1>Spark-GPT仓库</h1>
  <p><em>Spark-GPT</em></p>
</div>

<p align="center">
    <a href="https://pypi.python.org/pypi/nonebot-plugin-spark-gpt">
    <img src="https://img.shields.io/pypi/v/nonebot-plugin-spark-gpt" alt="pypi">
    </a>
    <img src="https://img.shields.io/pypi/pyversions/nonebot-plugin-spark-gpt" alt="python">
    <img src="https://img.shields.io/pypi/dm/nonebot-plugin-spark-gpt" alt="pypi">
    <br />
    <a href="https://onebot.dev/">
    <img src="https://img.shields.io/badge/OneBot-v11-black?style=social&logo=data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAEAAAABABAMAAABYR2ztAAAAIVBMVEUAAAAAAAADAwMHBwceHh4UFBQNDQ0ZGRkoKCgvLy8iIiLWSdWYAAAAAXRSTlMAQObYZgAAAQVJREFUSMftlM0RgjAQhV+0ATYK6i1Xb+iMd0qgBEqgBEuwBOxU2QDKsjvojQPvkJ/ZL5sXkgWrFirK4MibYUdE3OR2nEpuKz1/q8CdNxNQgthZCXYVLjyoDQftaKuniHHWRnPh2GCUetR2/9HsMAXyUT4/3UHwtQT2AggSCGKeSAsFnxBIOuAggdh3AKTL7pDuCyABcMb0aQP7aM4AnAbc/wHwA5D2wDHTTe56gIIOUA/4YYV2e1sg713PXdZJAuncdZMAGkAukU9OAn40O849+0ornPwT93rphWF0mgAbauUrEOthlX8Zu7P5A6kZyKCJy75hhw1Mgr9RAUvX7A3csGqZegEdniCx30c3agAAAABJRU5ErkJggg==" alt="onebot">
    <a href="https://github.com/canxin121/nonebot_poe_chat/releases/">
    <img src="https://img.shields.io/github/last-commit/canxin121/Spark-GPT" alt="github">
    </a>
</p>
<div align="left">

---
最新版本1.0.7  
# ！！！项目重构已完成，新版本将无法兼容旧版本配置文件和预设文件，请手动保存原来的配置并手动转移至新版本
#### 新版本数据位置为data/sparp_gpt，其中的common文件夹中的prompt和config是可以由旧版本手动打开替换其中的部分内容的,其余数据如创建的bot均无法转移

## 最新版本支持qq，tg，开黑啦(kook)三端互通数据同时使用(安装并配置好对应的nonebot适配器即可),支持poe（gpt+claude），chatgpt网页版，slack claude，newbing，sydney bing，bard，通义千问，讯飞星火大模型的来源。
#### 具体使用请使用/shelp命令获取帮助面板

>
## [教程-残心小站-文档库(已更新从零开始教程和)](https://canxin121.github.io/docs/docs/Spark_GPT.html )

> 用户交流群:[610948446](http://qm.qq.com/cgi-bin/qm/qr?_wv=1027&k=KHGqjjbiz6fpRr-W2X9SugTXThKFiprJ&authKey=LhpClaGtc4%2Ff3EL7f4IIIt7F94vLHJj4HSS8c2YCE55nRBRBtftzla%2Bgj7pa0fWX&noverify=0&group_code=610948446
)

---
# 项目需要依赖一个第三方的库wkhtmltopdf,需要手动安装才可正常使用文转图功能
1.  安装 wkhtmltopdf:

    - Debian/Ubuntu:

      ```bash
      sudo apt-get install wkhtmltopdf
      ```
    - MacOSX:

      ```bash
      brew install --cask wkhtmltopdf
      ```
    - Windows 和其他系统:

      在[下载页面](https://wkhtmltopdf.org/downloads.html)下载对应版本安装，并将安装的目录下的bin目录添加到系统环境变量  
# .env.*配置项：  
| 项 | 默认值 | 含义 |
| --- | --- | --- |
| spark_host | 127.0.0.1 | webui的host地址 |
| spark_port | 8666 | webui的端口地址 |

# 其余所有配置项均通过webui实时配置，热更新，
## 各来源gpt验证信息获取方式均通过注释显示在对应位置
