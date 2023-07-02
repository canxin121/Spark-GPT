from .config import config

PRIVATE_COMMAND = "/"
PUBLIC_COMMAND = "."
Generated_Help_Msg_Pic = False


def load_command_config():
    global PRIVATE_COMMAND, PUBLIC_COMMAND, Generated_Help_Msg_Pic
    try:
        PRIVATE_COMMAND = config.get_config("总控配置", "private_command")
    except:
        pass
    try:
        PUBLIC_COMMAND = config.get_config("总控配置", "public_command")
    except:
        pass
    Generated_Help_Msg_Pic = False


load_command_config()


def get_help_pic():
    global Generated_Help_Msg_Pic
    Generated_Help_Msg_Pic = True
