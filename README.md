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
最新版本1.1.0  
# > 注意本插件使用了一个第三方程序进行文转图，所以不管你是否熟悉nonebot，请务必看教程2.(2)

# 介绍部分

## 功能特性

- 汇聚众多来源的gpt(poe(chatgpt+claude),chatgpt网页版,Newbing,slack claude,讯飞星火,通义千问),支持多平台(tg,kook(
  原开黑啦),qq(gocq))使用且不同平台用户数据绑定互通
- 支持人格预设和前缀系统,支持文转图文转链接,支持每个用户创建不同来源不同人格的bot,同时支持公用共同的bot
- 注重提示词工程,通过提示词工程可以实现角色扮演,要求回复格式,如实现EitherChoice的对比功能
- 支持webui配置各来源的配置项以及管理预设和人格
- 性能和效率优秀,使用便捷方便,功能实用
- 便捷的代码方式,全api统一调用,方便新增来源
- 借助nonebot框架实现多平台统一消息处理,增加代码复用

## TodoList

1. 适配更多平台discord,飞书,微信,qq频道等
2. 增加英文版本文档及代码提示内容
3. 增加各来源chatbot的负载均衡
4. 补全一些不同来源的gpt的功能
5. 兼容py38

# 使用说明

## 一. 从零开始的安装教程

### 1.安装nonebot框架,并创建nonebot项目

#### (1).需要确保本机已安装python3.8及以上版本(推荐py3.11)并配置了正确的系统环境变量 (如果没有安装py,可以参考这个教程进行安装 => [Python初学者在不同系统上安装Python的保姆级指引](https://blog.csdn.net/qq_20288327/article/details/124387986))

#### (2).使用pipx安装nb-cli

首先安装pipx  
如果在此步骤的输出中出现了“open a new terminal”或者“re-login”字样，那么请关闭当前终端并重新打开一个新的终端。

```
python -m pip install --user pipx
python -m pipx ensurepath
```

然后使用pipx安装nb-cli

```
pipx install nb-cli
```

#### (3).使用nb-cli创建nb项目目录

先找到一个目录,用来存放nb项目文件夹  
比如我这里可以在win桌面按住shift再点击右键,打开一个powershell,就相当于吧nb项目文件夹创建在桌面上
![打开powershell](/source/1.png)  
在命令行工具如powershell中输入

```
nb
```

此时应该出现了交互式的面板用以创建nb项目,交互方式是鼠标点击选中或者上下键切换空格键选中，然后按enter提交并进入下一个界面  
这里我们选择创建一个Nonebot项目并回车，而后提示输入一个名称，这里我们自己想一个名字输入就可以，这个名字是创建完成后文件夹的名字  
![nb-cli](/source/2.png)  
然后选择bootstrap按enter  
![nb-cli](/source/3.png)  
然后选中如图绿色驱动器的并enter  
![nb-cli](/source/4.png)  
然后选中如图绿色的适配器并enter  
![nb-cli](/source/5.png)  
然后选中如图连续输入两次Y来创建项目  
![nb-cli](/source/6.png)  
最后提示我们选择内置插件，这里可以选择echo并回车，也可以不选，但是不要选择singlesession  
![nb-cli](/source/7.png)
至此nb项目文件夹已经创建完毕

### 2.安装本插件及依赖软件

#### (1).使用nb命令一键安装插件，其他nb插件安装同理，可以去商店看看，有众多实用和有趣插件

完成上一步(3)后，我们关闭powershell，并且打开这个新创建的nb项目的文件夹，在文件夹里面重新打开powershell  
![nb-cli](/source/8.png)  
在命令行中输入

```
nb plugin install spark_gpt
```

然后等待插件安装完毕

#### (2).安装 wkhtmltopdf用以高效的文转图:

1. Debian/Ubuntu系统 使用apt命令一键安装即可:

```
sudo apt-get install wkhtmltopdf
```

2. MacOSX系统 使用brew命令安装:

```
brew install --cask wkhtmltopdf
```

3. Windows 和其他系统:

在[下载页面](https://wkhtmltopdf.org/downloads.html)下载对应版本安装，并将安装的目录下的bin目录添加到系统环境变量  
例如windows操作如下  
![nb-cli](/source/9.png)  
打开上面超链接，下载所指软件并安装，注意在安装时要注意记住你安装的路径是什么  
![nb-cli](/source/10.png)    
根据上如的安装路径，我们来添加系统环境变量  
首先搜索打开编辑系统环境变量界面  
![nb-cli](/source/11.png)  
点击编辑系统环境变量  
![nb-cli](/source/12.png)  
双击编辑系统变量中的Path变量  
![nb-cli](/source/13.png)  
点击新建，并且在新的编辑框中输入你刚才记下的安装路径，后面在加上 /bin  ,比如我的安装路径是C:\Program Files\wkhtmltopdf，我就填写C:\Program Files\wkhtmltopdf\bin  
![nb-cli](/source/14.png)  
最后记得一直点确定并关闭，确保保存成功
### 3.配置本插件的env设置
只有两个配置项,用以配置webui的地址  

| 配置项     | 配置含义          |
| ---------- | ----------------- |
| spark_host | 本插件webui的host |
| spark_port | 本插件webui的port |

配置示例,如下填写到nonebot项目文件夹的.env文件后，就可以打开http://127.0.0.1:8666/来访问webui控制面板
```
spark_host = 127.0.0.1
spark_port = 6666
```

### 4.配置好不同平台的对接,以在对应平台使用本插件
1. qq平台:   使用gocq进行链接，把机器人的qq和你的nonebot框架对接起来  
   这里只做简单描述，具体操作请看[gcoq及签名服务器部署](https://www.bilibili.com/video/BV1nu411h7bS/?spm_id_from=333.337.search-card.all.click&vd_source=8dd506c36e6670647607bab36d681869)  

   简单描述:
   首先我们在github[下载gocq](https://github.com/Mrs4s/go-cqhttp/releases),注意下载对应平台和架构的  
   然后找一个文件夹用以存放gocq程序，在此处shift右击打开命令行，./gocq程序名称来初次运行，运行后生成配置文件，在config.yaml中填写对应配置，主要是qq和反代链接(注意obv11的反代地址是nonebot的env中配置的host(默认127.0.0.1)和port(默认8080)对应的 ws://host:port/onebot/v11/ws)以及签名服务器链接  
   最后运行gocq并按提示登录你的机器人小号即可
2. telegram平台:   使用nonebot的适配器一键链接  
   如果你没有tg的bot，先申请一个bot:  
   首先你需要有一个 Telegram 帐号，添加 BotFather 为好友。  
   接着，向它发送 /newbot 指令，按要求回答问题。  
   如果你成功创建了一个机器人，BotFather 会发给你机器人的 token,格式如下：    
```
1234567890:ABCDEFGHIJKLMNOPQRSTUVWXYZABCDEFGHI
```

   然后你需要向 BotFather 发送 /setprivacy 并选择 Disable。  
   并且你还需要向 BotFather 发送 /setinline。  
   
   最后将tgbot的token添加到nonebot项目文件夹的.env文件(如果你看不见,请开启显示隐藏的文件)中，格式如下：  
   
```
telegram_bots = [{"token": "1234567890:ABCDEFGHIJKLMNOPQRSTUVWXYZABCDEFGHI"}]
```
3.kook(原开黑啦)平台: 使用nonebot适配器一键链接  
   首先如果你还没有kook的应用，请打开[KOOK开发者平台](https://developer.kookapp.cn/app/index)点击新建应用,并在创建后点击机器人的图标，选中左侧机器人一项，复制右侧token
填写到nonebot项目文件夹的.env文件中，格式如下：  
``` 
kaiheila_bots =[{"token": "1/MTA2MjE=/DnbsqfmN6/IfVCrdOiGXKcQ=="}]
```

## 二. Webui配置介绍

首页可以选择进入配置和预设两个配置面板  
![webui首页](/source/15.png)  
配置界面可以配置各个来源的gpt所需的内容，各项均有小字注释来解释  
![webui配置界面](/source/16.png)  
预设界面可以删除添加改名预设以及修改预设对应内容，点击左侧对应预设才会在右侧显示并可以显示对应预设  
![webui预设界面](/source/17.png)  

## 三. 控制命令介绍
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

#### 3.以下是用户信息命令列表,所有命令前需要加上前缀{command_start}才能触发。

| 命令     | 命令含义                                            | 命令可用用户 |
| -------- | --------------------------------------------------- | ------------ |
| 用户信息 | 查询当前用户的通用用户的用户名和密钥.建议私聊使用   | 所有用户可用 |
| 更改绑定 | 将当前平台账户绑定到指定通用账户,实现跨平台数据互通 | 所有用户可用 |


#### 4.以下是预设管理命令列表,所有命令前需要加上前缀{command_start}才能触发。

> 预设是指在创建某个bot时,第一条发向这个bot的人格设定,并且刷新时也会一并发送

| 命令     | 命令含义                       | 命令可用用户       |
| -------- | ------------------------------ | ------------------ |
| 所有预设 | 给出所有预设的名称             | 所有用户可用       |
| 查询预设 | 查询指定预设的内容             | 所有用户可用       |
| 添加预设 | 添加新的预设(可覆盖同名预设)   | SparkGPT管理员可用 |
| 改名预设 | 修改预设的名字(可覆盖同名预设) | SparkGPT管理员可用 |
| 删除预设 | 删除指定预设                   | SparkGPT管理员可用 |

#### 5.以下是前缀管理命令列表,所有命令前需要加上前缀{command_start}才能触发。

> 前缀是指创建的bot在每次对话时,都将在你的消息前面加上这个前缀,可以使bot的回复的格式和内容满足前缀要求

| 命令     | 命令含义                       | 命令可用用户       |
| -------- | ------------------------------ | ------------------ |
| 所有前缀 | 给出所有前缀的名称             | 所有用户可用       |
| 查询前缀 | 查询指定前缀的内容             | 所有用户可用       |
| 添加前缀 | 添加新的前缀(可覆盖同名前缀)   | SparkGPT管理员可用 |
| 改名前缀 | 修改前缀的名字(可覆盖同名前缀) | SparkGPT管理员可用 |
| 删除前缀 | 删除指定前缀                   | SparkGPT管理员可用 |

#### 6.以下是webui管理命令列表,所有命令前需要加上前缀{command_start}才能触发

| 命令      | 命令含义                                             | 命令可用用户       |
| --------- | ---------------------------------------------------- | ------------------ |
| 开启webui | 默认开启,打开webui,并返回webui开启的端口(管理员可用) | SparkGPT管理员可用 |
| 关闭webui | 请在使用webui后关闭(管理员可用)                      | SparkGPT管理员可用 |