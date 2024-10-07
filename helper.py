import re
import subprocess
import requests
from ping3 import ping
from telethon.tl.functions.channels import GetParticipantsRequest
from telethon.tl.types import ChannelParticipantsSearch, InputChannel
from config import *
import secrets
import string


def generate_random_token(length=24):
    characters = string.ascii_letters + string.digits
    return ''.join(secrets.choice(characters) for _ in range(length))


async def join_check(user_id, cli):
    entity = await cli.get_entity(JOIN_CHANNEL_ID)
    access_hash = entity.access_hash
    channel_id = entity.id
    participants = await cli(GetParticipantsRequest(
        channel=InputChannel(channel_id, access_hash),
        filter=ChannelParticipantsSearch(''),
        offset=0,
        limit=1000000000,
        hash=0
    ))
    result = False
    for p in participants.participants:
        if user_id == p.user_id:
            result = True
    return result, entity

def extract_host_port(config_url):
    dot = config_url.index(":")
    type_conf = config_url[:dot]
    pattern = re.compile(rf'{type_conf}://([^@]+)@([^:]+):(\d+)')
    match = pattern.match(config_url)
    if match:
        user_info, host, port = match.groups()
        return host, int(port)
    return None, None

def measure_ping(host):
    delay = ping(host)
    if delay is not None:
        return delay * 1000  # Convert to milliseconds
    return None

def measure_http_delay(host, path):
    url = f"http://{host}{path}"
    try:
        response = requests.get(url, timeout=5)
        return response.elapsed.total_seconds() * 1000  # Convert to milliseconds
    except requests.RequestException:
        return None

def get_ping(config_url):    
    host, port = extract_host_port(config_url)
    if host and port:
        # Measure HTTP request delay
        path = "/"
        http_delay = measure_http_delay(host, path)
        if http_delay is not None:
            return http_delay
        else:
            return -1
    else:
        print("Invalid configuration URL")
