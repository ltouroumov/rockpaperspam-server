import re
import json
import logging
from channels import Group
from channels.sessions import channel_session

log = logging.getLogger(__name__)


@channel_session
def ws_connect(message):
    pass


@channel_session
def ws_receive(message):
    pass


@channel_session
def ws_disconnect(message):
    pass
