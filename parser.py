import config
import logging

def parse_configshub(msg):
    xray_config = msg.split('\n')[0]
    country_emoji = xray_config[-xray_config[::-1].index('#'):xray_config.index('t.me/')]\
        .replace('[', '').replace(']', '')
    logging.debug('initial country emoji extracted.')
    xray_config = xray_config[0:-xray_config[::-1].index('#')] + country_emoji + ' ' + config.CHANNEL_ID
    logging.debug('config rewritten.')
    i = msg.index('ᴄᴏᴜɴᴛʀʏ: #')
    j = msg.index('\nᴄᴏɴғɪɢsʜᴜʙ')
    country = msg[i + 10:j]
    logging.debug('country extracted.')
    country_emoji = country[country.index('(')+1:country.index(')')]
    logging.debug('final country emoji extracted.')
    return xray_config, country, country_emoji