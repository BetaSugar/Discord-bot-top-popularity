import configparser
import os


def create_config(path: str):
    """
    Create a config file
    """
    config = configparser.ConfigParser(allow_no_value=True)
    config.add_section('discord')
    config.add_section('wasd.tv')
    config.add_section('twitch.tv')
    config.set('discord', 'token', '')
    config.set('discord', '#ID like and dislike emojis')
    config.set('discord', 'emoji_like_id', '')
    config.set('discord', 'emoji_dislike_id', '')
    config.set('discord',
               '#ID of the channel and the message-top that is stored in this channel')
    config.set('discord', 'channel_top_id', '')
    config.set('discord', 'message_top_id', '')
    config.set('discord', '#ID role for notifications')
    config.set('discord', 'notif_role_id', '')

    with open(path, "w") as config_file:
        config.write(config_file)


def get_config(path: str):
    """
    Returns the config object
    """
    if not os.path.exists(path):
        create_config(path)

    config = configparser.ConfigParser()
    config.read(path)
    return config


def get_setting(path: str, section: str, setting: str, type: str):
    """
    Print out a setting
    """
    config = get_config(path)
    if type == 'str':
        return config.get(section, setting)
    elif type == 'int':
        return config.getint(section, setting)
    elif type == 'bool':
        return config.getboolean(section, setting)
    elif type == 'float':
        return config.getfloat(section, setting)


def update_setting(path: str, section: str, setting: str, value: str):
    """
    Update a setting
    """
    config = get_config(path)
    config.set(section, setting, value)
    with open(path, "w") as config_file:
        config.write(config_file)


def delete_setting(path: str, section: str, setting: str):
    """
    Delete a setting
    """
    config = get_config(path)
    config.remove_option(section, setting)
    with open(path, "w") as config_file:
        config.write(config_file)
