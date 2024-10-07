import config

def parse_5415792594(msg):
    xray_config = msg.split('\n')[0]
    country_emoji = xray_config[-xray_config[::-1].index('#'):xray_config.index('t.me/')]\
        .replace('[', '').replace(']', '')
    xray_config = xray_config[0:-xray_config[::-1].index('#')] + country_emoji + ' ' + config.CHANNEL_ID
    i = msg.index('ᴄᴏᴜɴᴛʀʏ: #')
    j = msg.index('\nᴄᴏɴғɪɢsʜᴜʙ')
    country = msg[i + 10:j]
    country_emoji = country[country.index('(')+1:country.index(')')]
    return xray_config, country, country_emoji