from .config import config

PRIVATE_COMMAND = "/"
PUBLIC_COMMAND = "."
Generated_Help_Msg_Pic = False
Generated_Super_Msg_Pic = False
Generated_Source_Pic = False

PICABLE = "Auto"
NUMLIMIT = 850
URLABLE = "True"
WAIT_MSG_ABLE = "True"
PIC_WIDTH = 1800

CONFIG_DICT = {
    "private_command": None,
    "public_command": None,
    "pic_able": "Auto",
    "pic_width": 1800,
    "wait_msg_able": "True",
    "num_limit": 800,
    "url_able": False
}


def load_command_config():
    def get_config(key):
        return config.get_config("总控配置", key) or CONFIG_DICT[key]

    global PRIVATE_COMMAND, PUBLIC_COMMAND, Generated_Help_Msg_Pic, PICABLE, NUMLIMIT, URLABLE, PIC_WIDTH, SPECIALPIC_WIDTH, WAIT_MSG_ABLE, Generated_Super_Msg_Pic, Generated_Source_Pic
    PRIVATE_COMMAND = get_config("private_command")
    PUBLIC_COMMAND = get_config("public_command")
    PICABLE = get_config("pic_able")
    PIC_WIDTH = int(get_config("pic_width"))
    WAIT_MSG_ABLE = get_config("wait_msg_able")
    Generated_Help_Msg_Pic = False
    Generated_Super_Msg_Pic = False
    Generated_Source_Pic = False
    # 根据PICABLE的值来设置NUMLIMIT和URLABLE
    if PICABLE == "Auto":
        NUMLIMIT = int(get_config("num_limit"))
        URLABLE = get_config("url_able")
    elif PICABLE == "True":
        URLABLE = get_config("url_able")


load_command_config()


def get_help_pic():
    global Generated_Help_Msg_Pic
    Generated_Help_Msg_Pic = True


def get_super_pic():
    global Generated_Super_Msg_Pic
    Generated_Super_Msg_Pic = True


def get_source_pic():
    global Generated_Source_Pic
    Generated_Source_Pic = True
