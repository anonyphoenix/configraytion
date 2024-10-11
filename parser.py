import logging

def parse_configshub(msg):
    xray_config = msg.split('\n')[0]
    country_emoji = xray_config[-xray_config[::-1].index('#'):xray_config.index('t.me/')]\
        .replace('[', '').replace(']', '')
    logging.debug('country emoji extracted.')
    xray_config = xray_config[0:-xray_config[::-1].rindex('#')-1]
    logging.debug('config rewritten.')
    i = msg.index('ᴄᴏᴜɴᴛʀʏ: #')
    j = msg.index('\nᴄᴏɴғɪɢsʜᴜʙ')
    country = msg[i + 10:j]
    logging.debug('country extracted.')
    country_abbreviation = country[country.rindex('(')+1:country.rindex(')')]
    logging.debug('country abbreviation extracted.')
    country = country.replace(f'({country_abbreviation})', '')
    logging.debug('country fixed.')
    return xray_config, country, country_abbreviation, country_emoji