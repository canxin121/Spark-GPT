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

## 最新版本号1.2.3
# 详细教程-> [![残心文档库](source/doc.png)](https://canxin121.github.io/docs/docs/Spark_GPT.html)  
  
---
# 介绍部分

## 功能特性

- 汇聚众多来源的gpt(poe(chatgpt+claude),chatgpt网页版,Newbing,Sdyney bing,slack claude,claude ai,讯飞星火,通义千问),支持多平台(tg,kook(
  原开黑啦),qq(gocq),discord)使用且不同平台用户数据绑定互通
- 支持人格预设和前缀系统,支持文转图文转链接,支持每个用户创建不同来源不同人格的bot,同时支持公用共同的bot
- 注重提示词工程,通过提示词工程可以实现角色扮演,要求回复格式,如实现EitherChoice的对比功能
- 支持webui配置各来源的配置项以及管理预设和人格
- 性能和效率优秀,使用便捷方便,功能实用
- 便捷的代码方式,全api统一调用,方便新增来源
- 借助nonebot框架实现多平台统一消息处理,增加代码复用

## TodoList

1. 适配更多平台~~discord~~,飞书,微信,qq频道等
2. 增加英文版本文档及代码提示内容
3. 增加各来源chatbot的负载均衡  
4. ~~补全一些不同来源的gpt的功能~~

## 简要的搭建说明

### 1.env配置项
只有两个配置项,用以配置webui的地址  

> 注意如果你使用的是云服务器,请将host改为你的公网IP,并在防火墙开放相应端口 

| 配置项     | 配置含义          |
| ---------- | ----------------- |
| spark_host | 本插件webui的host |
| spark_port | 本插件webui的port |

### 2.其他配置项
访问webui进行填写,若使用的云服务器,建议再配置完成后关闭webui,防止其他人访问

### 3.配置不同平台
只需要使用nb-cli添加相应适配器并且填写相关信息即可完成配置,具体方法请查询对应的适配器或者查看[残心文档库](https://canxin121.github.io/docs/docs/Spark_GPT.html#_4-%E9%85%8D%E7%BD%AE%E5%A5%BD%E4%B8%8D%E5%90%8C%E5%B9%B3%E5%8F%B0%E7%9A%84%E5%AF%B9%E6%8E%A5-%E4%BB%A5%E5%9C%A8%E5%AF%B9%E5%BA%94%E5%B9%B3%E5%8F%B0%E4%BD%BF%E7%94%A8%E6%9C%AC%E6%8F%92%E4%BB%B6)
### 4.命令文档
命令前缀均可修改,

以下介绍中,以前缀/表示使用自己的bot,前缀.表示公用的bot,这两个前缀可以在webui中进行修改
以/表示nonebot的默认命令前缀,这个前缀可以在env中修改nonebot的响应命令前缀来进行修改

#### 1.使用bot方式
##### (1).使用命令:先查询可用的bot或创建新的bot,然后使用“前缀+bot名称+你所询问的内容 或 刷新指令”。这里前缀 "/" 使用自己的bot,前缀 "." 使用公用的bot.
> 当询问内容为 刷新指令 也就是 "清除对话" 或 "清空对话" 或"刷新对话" 时,将清除和bot的聊天记录,即重新开始对话   
 
 一个可能的私有的bot使用示例为 “/chat 在吗?” 这里的chat就是我自己的bot,是我创建的,并且可以通过 “/所有bot” 查询
 一个可能的公用的bot使用示例为 “.chat 在吗?” 这里的chat是公用的bot,可以通过 “.所有bot” 查询,但只有本插件管理员可以创建  
 一个可能的清除某个bot的聊天记录的示例为 “/chat 刷新对话”  
##### (2).无需命令:直接回复某个bot的最后一条消息来继续对话
> 注意公用的bot可能也在和别人对话,所以最后一条消息不一定是发给你的最后一条

#### 2.以下是bot管理命令列表,这里有两种不同前缀代表不用含义
##### 使用**/**前缀表示管理自己的bot

##### 使用**.** 前缀表示管理公用用户的bot

| 命令    | 命令含义            | 命令可用用户                                |
| ------- | ------------------- | ------------------------------------------- |
| 所有bot | 查询所有的可用的bot | 所有用户可用                                |
| 创建bot | 创建新的bot         | .开头仅SparkGPT管理员可用,/开头所有用户可用 |
| 改名bot | 更改bot的名称       | .开头仅SparkGPT管理员可用,/开头所有用户可用 |
| 删除bot | 删除指定bot         | .开头仅SparkGPT管理员可用,/开头所有用户可用 |

#### 3.以下是用户信息命令列表,所有命令前需要加上前缀/才能触发。

| 命令     | 命令含义                                            | 命令可用用户 |
| -------- | --------------------------------------------------- | ------------ |
| 用户信息 | 查询当前用户的通用用户的用户名和密钥.建议私聊使用   | 所有用户可用 |
| 更改绑定 | 将当前平台账户绑定到指定通用账户,实现跨平台数据互通 | 所有用户可用 |


#### 4.以下是预设管理命令列表,所有命令前需要加上前缀/才能触发。

> 预设是指在创建某个bot时,第一条发向这个bot的人格设定,并且刷新时也会一并发送

| 命令     | 命令含义                       | 命令可用用户       |
| -------- | ------------------------------ | ------------------ |
| 所有预设 | 给出所有预设的名称             | 所有用户可用       |
| 查询预设 | 查询指定预设的内容             | 所有用户可用       |
| 添加预设 | 添加新的预设(可覆盖同名预设)   | SparkGPT管理员可用 |
| 改名预设 | 修改预设的名字(可覆盖同名预设) | SparkGPT管理员可用 |
| 删除预设 | 删除指定预设                   | SparkGPT管理员可用 |

#### 5.以下是前缀管理命令列表,所有命令前需要加上前缀/才能触发。

> 前缀是指创建的bot在每次对话时,都将在你的消息前面加上这个前缀,可以使bot的回复的格式和内容满足前缀要求

| 命令     | 命令含义                       | 命令可用用户       |
| -------- | ------------------------------ | ------------------ |
| 所有前缀 | 给出所有前缀的名称             | 所有用户可用       |
| 查询前缀 | 查询指定前缀的内容             | 所有用户可用       |
| 添加前缀 | 添加新的前缀(可覆盖同名前缀)   | SparkGPT管理员可用 |
| 改名前缀 | 修改前缀的名字(可覆盖同名前缀) | SparkGPT管理员可用 |
| 删除前缀 | 删除指定前缀                   | SparkGPT管理员可用 |

#### 6.以下是webui管理命令列表,所有命令前需要加上前缀/才能触发

| 命令      | 命令含义                                             | 命令可用用户       |
| --------- | ---------------------------------------------------- | ------------------ |
| 开启webui | 默认开启,打开webui,并返回webui开启的端口(管理员可用) | SparkGPT管理员可用 |
| 关闭webui | 请在使用webui后关闭(管理员可用)                      | SparkGPT管理员可用 |
