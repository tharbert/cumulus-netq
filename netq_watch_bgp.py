#!/usr/bin/python

import sys
import time

from slacker import Slacker
from netq.lib.netq import NetQ
from netq.orm.redisdb.models import BgpSession
from netq.orm.redisdb.query import RedisQuery

REDIS_SERVER_IP_ADDR = 'x.x.x.x'
SLACK_API_KEY = 'slack_api_key'
SLACK_CHANNEL = '#slack_channel'

def connect_to_redis():
    netq = NetQ(REDIS_SERVER_IP_ADDR, None, None)
    if not netq:
        print 'Error: Unable to establish connection with DB'
        sys.exit(1)

def post_to_slack(slack_message):
    slack = Slacker(SLACK_API_KEY)
    slack.chat.post_message(SLACK_CHANNEL, slack_message)

def main():
    down_peer_set = set()
    connect_to_redis()
    while True:
        time.sleep(60)
        for entry in BgpSession.query.filter():
            peer_summary = '%s:%s(%s)' % (entry.hostname, entry.peer_name, entry.peer_hostname)
            if (entry.state == 'Established') and (peer_summary in down_peer_set):
                down_peer_set.remove(peer_summary)
                post_to_slack('BGP neighbor recovered: ' +peer_summary)
            elif (entry.state != 'Established') and (peer_summary not in down_peer_set):
                down_peer_set.add(peer_summary)
                post_to_slack('BGP neighbor down: ' +peer_summary)

if __name__ == '__main__':
    main()
