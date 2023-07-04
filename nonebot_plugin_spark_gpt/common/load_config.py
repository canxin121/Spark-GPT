from .config import config

PRIVATE_COMMAND = "/"
PUBLIC_COMMAND = "."
Generated_Help_Msg_Pic = False
PICABLE = "Auto"
NUMLIMIT = 850
URLABLE = "True"
PIC_WIDTH = 1800
SPECIALPIC_WIDTH = 600


def load_command_config():
    global PRIVATE_COMMAND, PUBLIC_COMMAND, Generated_Help_Msg_Pic, PICABLE, NUMLIMIT, URLABLE, PIC_WIDTH, SPECIALPIC_WIDTH

    try:
        PRIVATE_COMMAND = config.get_config("总控配置", "private_command")
    except:
        pass
    try:
        PUBLIC_COMMAND = config.get_config("总控配置", "public_command")
    except:
        pass
    try:
        PICABLE = config.get_config("总控配置", "pic_able")
    except:
        PICABLE = "Auto"
    try:
        PIC_WIDTH = int(config.get_config("总控配置", "pic_width"))
    except:
        PIC_WIDTH = 1800
    try:
        SPECIALPIC_WIDTH = int(config.get_config("总控配置", "specialpic_width"))
    except:
        SPECIALPIC_WIDTH = 600
    if PICABLE == "Auto":
        try:
            NUMLIMIT = int(config.get_config("总控配置", "num_limit"))
        except:
            NUMLIMIT = 800
        try:
            URLABLE = config.get_config("总控配置", "url_able")
        except:
            URLABLE = False
    if PICABLE == "True":
        try:
            URLABLE = config.get_config("总控配置", "url_able")
        except:
            URLABLE = False
    Generated_Help_Msg_Pic = False


load_command_config()


def get_help_pic():
    global Generated_Help_Msg_Pic
    Generated_Help_Msg_Pic = True
