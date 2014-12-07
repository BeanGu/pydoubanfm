#!/usr/bin/env python
# coding: utf-8
import threading
import json
from twisted.internet.protocol import Protocol, ClientFactory
from twisted.internet import reactor
from utils import json_dumps, setting


class DoubanFmClientProtocol(Protocol):
    def connectionMade(self):
        threading.Thread(target=self.input).start()
        self.transport.write('user_info\nsong')

    def input(self):
        while True:
            self.transport.write(raw_input())

    def dataReceived(self, data):
        for row in data.split('\n'):
            if row:
                try:
                    data = json.loads(row)
                    if len(data) == 1:
                        getattr(self, 'on_' + data[0])()
                    else:
                        getattr(self, 'on_' + data[0])(data[1])
                except Exception as e:
                    print('error: ' + e.message)

    @staticmethod
    def on_error(message):
        print('error: ' + message)

    @staticmethod
    def on_user_info(user_info):
        print('当前用户：' + json_dumps(user_info))

    @staticmethod
    def on_song(song):
        print('当前播放：' + json_dumps(song))

    @staticmethod
    def on_play(song):
        print('当前播放：' + json_dumps(song))

    @staticmethod
    def on_skip():
        print('跳过')

    @staticmethod
    def on_like():
        print('喜欢')

    @staticmethod
    def on_unlike():
        print('不再喜欢')

    @staticmethod
    def on_remove():
        print('不再播放')

    @staticmethod
    def on_pause():
        print('暂停播放')

    @staticmethod
    def on_resume():
        print('恢复播放')

    @staticmethod
    def on_login_success(user_info):
        print('登录成功：' + json_dumps(user_info))

    @staticmethod
    def on_kbps(kbps):
        print('当前码率：' + kbps + 'kbps')

    @staticmethod
    def on_channel(channel_id):
        print('当前频道：' + channel_id)

    @staticmethod
    def on_channels(channels):
        print('频道列表：' + json_dumps(channels))

    @staticmethod
    def on_playlist(playlist):
        print('播放列表：' + json_dumps(playlist))


class DoubanFmFactory(ClientFactory):
    def __init__(self):
        self.protocol = DoubanFmClientProtocol()

    def buildProtocol(self, addr):
        return self.protocol

if __name__ == '__main__':
    import sys
    reload(sys)
    sys.setdefaultencoding('utf-8')

    reactor.connectTCP('127.0.0.1', setting.get('port'), DoubanFmFactory())
    reactor.run()
