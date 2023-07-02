from .config import config

PRIVATE_COMMAND = "/"
PUBLIC_COMMAND = "."


def load_command_config():
    global PRIVATE_COMMAND, PUBLIC_COMMAND
    try:
        PRIVATE_COMMAND = config.get_config("总控配置", "private_command")
    except:
        pass
    try:
        PUBLIC_COMMAND = config.get_config("总控配置", "public_command")
    except:
        pass


load_command_config()
