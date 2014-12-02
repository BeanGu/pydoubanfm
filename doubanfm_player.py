# encoding: utf-8
import os
import json
import cookielib
from gi.repository import Gtk, Notify
from doubanfm import Doubanfm, LoginError
from hook import Hook
from player import Player
import utils
import setting


class DoubanfmPlayer(Hook):
    def __init__(self):
        Hook.__init__(self)
        self.init_notify()
        self.init_doubanfm()
        self.init_channels()
        self.init_player()

    def init_doubanfm(self):
        self.doubanfm = Doubanfm()
        self.doubanfm.session.cookies = \
            cookielib.LWPCookieJar(setting.cookies_file)

        try:
            self.doubanfm.session.cookies.load()
            self.user_info = json.load(open(setting.user_file))
            self.doubanfm.set_token(self.user_info)
        except:
            pass

        self.doubanfm.set_kbps(setting.get('kbps'))
        self.playlist_count = 0
        self.song = {'sid': -1}

    def init_player(self):
        self.player = Player()
        self.player.on('eos', self.on_player_eos)

    def init_notify(self):
        """初始化桌面通知"""
        Notify.init(__name__)
        self.notify = Notify.Notification.new('', '', '')

    def init_channels(self):
        """创建频道选择菜单"""
        if os.path.isfile(setting.channels_file):
            self.channels = json.load(open(setting.channels_file))
        else:
            self.update_channels()

    def update_notify(self, title='', content='', picture=''):
        """更新桌面通知显示当前歌曲信息"""
        if not title:
            title = self.song['title']
            content = self.song['artist']
            picture = self.song['picture_file']

        self.notify.update(title, content, picture)
        self.notify.show()

    def update_channels(self):
        self.channels = self.doubanfm.get_channels()
        self.channels.insert(0, {'name': '红心兆赫', 'channel_id': -3})
        utils.json_dump(self.channels, setting.channels_file)

    def update_playlist(self, operation_type):
        self.playlist = self.doubanfm.get_playlist(
            setting.get('channel'), operation_type, self.song['sid'])['song']
        self.doubanfm.session.cookies.save()

    def set_kbps(self, kbps):
        self.doubanfm.set_kbps(kbps)
        setting.put('kbps', kbps)
        self.dispatch('kbps_change')

    def login(self, email, password):
        try:
            self.user_info = self.doubanfm.login(email, password)
            self.doubanfm.session.cookies.save()
            self.dispatch('login_success')
            utils.json_dump(self.user_info, setting.user_file)
            return self.user_info
        except LoginError as e:
            return e

    def play(self):
        self.song = self.playlist[self.playlist_count]
        self.save_album_cover()
        self.player.set_uri(self.song['url'])
        self.player.play()
        self.update_notify()
        self.dispatch('play_new')

    def next(self, operation_type='n'):
        """播放下一首
        :param operation_type: 操作类型，详情请参考 https://github.com/qiuxiang/pydoubanfm/wiki/%E8%B1%86%E7%93%A3FM-API
        """
        self.update_playlist(operation_type)
        self.playlist_count = 0
        self.player.stop()
        self.play()

    def select_channel(self, channel_id):
        """设置收听频道
        :param channel_id: 频道ID
        """
        setting.put('channel', channel_id)
        self.next('n')
        self.dispatch('channel_change')

    def pause(self):
        """播放/暂停"""
        if self.player.get_state() == 'playing':
            self.player.pause()
            self.dispatch('pause')
        else:
            self.player.play()
            self.dispatch('play')

    def rate(self):
        """喜欢/取消喜欢"""
        if self.song['like'] == 0:
            self.update_playlist('r')
            self.song['like'] = True
        else:
            self.update_playlist('u')
            self.song['like'] = False

        self.playlist_count = 0
        self.dispatch('rate')

    def on_player_eos(self):
        """一首歌曲播放完毕的处理"""
        if len(self.playlist) == self.playlist_count + 1:
            self.update_playlist('p')
            self.playlist_count = 0
        else:
            self.playlist_count += 1

        self.doubanfm.get_playlist(setting.get('channel'), 'e', self.song['sid'])
        self.play()

    def run(self):
        self.update_playlist('n')
        self.play()

    def no_longer_play(self):
        """不再播放当前的歌曲"""
        self.next('b')
        self.dispatch('no_longer_play')

    def skip(self):
        """跳过当前的歌曲"""
        self.next('s')
        self.dispatch('skip')

    def set_volume(self, value):
        self.player.set_volume(value)
        self.dispatch('volume_change')

    def save_album_cover(self):
        """保存并更新专辑封面"""
        self.song['picture_file'] = \
            setting.albumcover_dir + self.song['picture'].split('/')[-1]
        if not os.path.isfile(self.song['picture_file']):
            utils.download(self.song['picture'], self.song['picture_file'])

if __name__ == '__main__':
    doubanfm_player = DoubanfmPlayer()
    doubanfm_player.run()
    Gtk.main()
