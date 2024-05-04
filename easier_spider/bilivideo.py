import re
import json
import time
import pandas as pd
import requests
import os
from PIL import Image
from io import BytesIO

from easier_spider.config import useragent
from easier_spider.config import bilicookies as cookies
from easier_tools.Colorful_Console import ColoredText as CT

class biliVideo:
    def __init__(self, bv, html_path=None):
        """
        [使用方法]:
            biliV = biliVideo("BV18x4y187DE")  # [必要]输入bv号
            biliV.get_html()  # [必要]获取html
            # biliV.get_content(download_mp4=True)  # [可选]下载视频
            biliV.get_content()  # [可选]不下载视频
            biliV.show_values()  # [非必要]显示视频信息
        :param bv: bv号
        :param html_path: 如不指定，则不存储。如指定，则为f"{self.html_path}{self.bv}.html"

        """
        self.bv = bv  # 你要爬取的视频的bv号
        self.html_path = html_path  # html存储路径
        self.url = f"https://www.bilibili.com/video/{self.bv}"
        self.headers = {
            "User-Agent": useragent().pcChrome,
            "Cookie": cookies().bilicookie,
            'referer': 'https://www.bilibili.com'
        }

        # cid是鉴权参数。请求https://api.bilibili.com/x/player/pagelist，参数是bv号，返回的是视频的cid
        self.cid = requests.get(url=f"https://api.bilibili.com/x/player/pagelist?bvid={self.bv}",
                                headers=self.headers).json()["data"][0]["cid"]  # 目前这个似乎只适用于单P视频，暂未验证

        self.rtext = None  # 网页的文本，也就是r.text

        self.aid = None  # 视频的av号
        self.bvid = None  # 视频的bv号，可以用来和bv号对比，看看有没有错误
        self.title = None  # 视频的标题
        self.pic = None  # 视频的封面路径
        self.desc = None  # 视频的简介
        self.stat = None  # 视频的统计数据，比如{'aid': 1003283555, 'view': 27847, 'danmaku': 76, 'reply': 143, 'favorite': 1458, 'coin': 201, 'share': 40, 'now_rank': 0, 'his_rank': 0, 'like': 1566, 'dislike': 0, 'evaluation': '', 'vt': 0, 'viewseo': 27847}
        self.view = None  # 视频的播放量
        self.dm = None  # 视频的弹幕量
        self.reply = None  # 视频的评论量
        self.time = None  # 视频的发布时间
        self.like = None  # 视频的点赞量
        self.coin = None  # 视频的投币量
        self.fav = None  # 视频的收藏量
        self.share = None  # 视频的转发量

    def get_html(self):
        biliLoginState(self.headers).get_login_state()
        r = requests.get(url=self.url, headers=self.headers)
        r.encoding = 'utf-8'
        self.rtext = r.text
        if self.html_path is not None:
            if not os.path.exists(self.html_path):
                os.makedirs(self.html_path)
            with open(f"{self.html_path}{self.bv}.html", 'w', encoding='utf-8') as f:
                f.write(self.rtext)

    def get_content(self, download_mp4=False, save_mp4_path=None):
        """
        :param download_mp4: 是否下载视频
        :param save_mp4_path: 视频保存路径，路径为f"{save_mp4_path}{self.bv}.mp4"
        """
        if self.html_path is not None:
            with open(f"{self.html_path}{self.bv}.html", 'r', encoding='utf-8') as f:
                self.rtext = f.read()

        pattern_base_data = re.compile(r'window\.__INITIAL_STATE__=(.*?);\(function\(\)')
        base_data_match = re.search(pattern_base_data, self.rtext)

        if base_data_match:
            base_data_content = base_data_match.group(1)
            base_data_content = json.loads(base_data_content)
            self.aid = base_data_content['videoData']['aid']
            self.bvid = base_data_content['videoData']['bvid']
            self.title = base_data_content['videoData']['title']
            self.pic = base_data_content["videoData"]["pic"]
            self.desc = base_data_content["videoData"]["desc"]
            self.stat = base_data_content["videoData"]["stat"]  # B站牛魔前端又改了
            self.view = self.stat["view"]
            self.dm = self.stat["danmaku"]
            self.reply = self.stat["reply"]
            self.like = self.stat["like"]
            self.coin = self.stat["coin"]
            self.fav = self.stat["favorite"]
            self.share = self.stat["share"]
        else:
            print("爬取基础数据错误，再见ヾ(￣▽￣)")

        if download_mp4:
            self.play_url = f"https://api.bilibili.com/x/player/wbi/playurl?bvid={self.bv}&cid={self.cid}&qn=80"
            play_content = requests.get(url=self.play_url, headers=self.headers).json()
            # 保存视频
            video_content = requests.get(url=play_content["data"]["durl"][0]["url"], headers=self.headers).content
            if save_mp4_path is not None:
                with open(f"{save_mp4_path}{self.bv}.mp4", 'wb') as f:
                    f.write(video_content)
            else:
                with open(f"{self.bv}.mp4", 'wb') as f:
                    f.write(video_content)

        # # <div class="view-text" data-v-aed3e268="">2.8万</div>
        # pattern_view_data = re.compile(r'<div class="view-text"[^>]*>(.*?)\s*</div>')
        # view_data_match = re.search(pattern_view_data, self.rtext)
        # if view_data_match:
        #     view_data_content = view_data_match.group(1)
        #     self.view = view_data_content
        # else:
        #     print("爬取播放量数据错误，再见ヾ(￣▽￣)")
        #
        # pattern_dm_data = re.compile(r'<div class="dm-text"[^>]*>(.*?)\s*</div>')
        # dm_data_match = re.search(pattern_dm_data, self.rtext)
        # if dm_data_match:
        #     dm_data_content = dm_data_match.group(1)
        #     self.dm = dm_data_content
        # else:
        #     print("爬取弹幕数据错误，再见ヾ(￣▽￣)")
        #
        # # <span data-v-052ae598="" class="total-reply">143</span>
        # pattern_reply_data = re.compile(r'class="total-reply[^>]*>(.*?)</span>')
        # reply_data_match = re.search(pattern_reply_data, self.rtext)
        # if reply_data_match:
        #     reply_data_content = reply_data_match.group(1)
        #     self.reply = reply_data_content
        # else:
        #     print("爬取评论数据错误，再见ヾ(￣▽￣)")

        pattern_time_data = re.compile(r'<div class="pubdate-ip-text"[^>]*>(.*?)\s*</div>')
        time_data_match = re.search(pattern_time_data, self.rtext)
        if time_data_match:
            time_data_content = time_data_match.group(1)
            self.time = time_data_content
        else:
            print("爬取发布时间数据错误，再见ヾ(￣▽￣)")

        # pattern_like_data = re.compile(r'<span class="video-like-info[^>]*>(.*?)</span>')
        # like_data_match = re.search(pattern_like_data, self.rtext)
        # if like_data_match:
        #     like_data_content = like_data_match.group(1)
        #     self.like = like_data_content
        # else:
        #     print("爬取点赞数据错误，再见ヾ(￣▽￣)")
        #
        # pattern_coin_data = re.compile(r'<span class="video-coin-info[^>]*>(.*?)</span>')
        # coin_data_match = re.search(pattern_coin_data, self.rtext)
        # if coin_data_match:
        #     coin_data_content = coin_data_match.group(1)
        #     self.coin = coin_data_content
        # else:
        #     print("爬取投币数据错误，再见ヾ(￣▽￣)")
        #
        # pattern_fav_data = re.compile(r'<span class="video-fav-info[^>]*>(.*?)</span>')
        # fav_data_match = re.search(pattern_fav_data, self.rtext)
        # if fav_data_match:
        #     fav_data_content = fav_data_match.group(1)
        #     self.fav = fav_data_content
        # else:
        #     print("爬取收藏数据错误，再见ヾ(￣▽￣)")
        #
        # pattern_share_data = re.compile(r'<span class="video-share-info[^>]*>(.*?)</span>')
        # share_data_match = re.search(pattern_share_data, self.rtext)
        # if share_data_match:
        #     share_data_content = share_data_match.group(1)
        #     self.share = share_data_content
        # else:
        #     print("爬取转发数据错误，再见ヾ(￣▽￣)")

    def to_csv(self):
        data = {
            "av": [self.aid],
            "bv": [self.bvid],
            "title": [self.title],
            "pic": [self.pic],
            "desc": [self.desc],
            "view": [self.view],
            "dm": [self.dm],
            "reply": [self.reply],
            "time": [self.time],
            "like": [self.like],
            "coin": [self.coin],
            "fav": [self.fav],
            "share": [self.share],
        }
        df = pd.DataFrame(data)
        return df

    def show_values(self):
        print(CT('av号: ').blue() + f"{self.aid}")
        print(CT('bv号: ').blue() + f"{self.bvid}")
        print(CT('标题: ').blue() + f"{self.title}")
        print(CT('图片地址: ').blue() + f"{self.pic}")
        print(CT('简介: ').blue() + f"{self.desc}")
        print(CT('播放量: ').blue() + f"{self.view}")
        print(CT('弹幕数: ').blue() + f"{self.dm}")
        print(CT('评论数: ').blue() + f"{self.reply}")
        print(CT('发布时间: ').blue() + f"{self.time}")
        print(CT('点赞数: ').blue() + f"{self.like}")
        print(CT('硬币数: ').blue() + f"{self.coin}")
        print(CT('收藏数: ').blue() + f"{self.fav}")
        print(CT('分享数: ').blue() + f"{self.share}")


class biliReply:
    """暂时只支持视频评论"""
    def __init__(self, bv=None, av=None):
        """
        :param bv: bv号(bv号和av号有且只能有一个不为None)
        :param av: av号(bv号和av号有且只能有一个不为None)
        """
        self.bv = bv
        self.headers = {
            "User-Agent": useragent().pcChrome,
            "Cookie": cookies().bilicookie,
            'referer': f'https://www.bilibili.com/video/{self.bv}'
        }
        if av is None:
            if self.bv is None:
                raise ValueError("bv和av不能同时为None")
            else:
                self.av = BV2AV().bv2av(self.bv)
        else:
            self.av = av

    def send_reply(self, message):
        """
        [使用方法]:
            biliR = biliReply(bv="BV141421X7TZ")
            biliR.send_reply("对着香奶妹就是一个冲刺😋")
        :param message: 评论内容
        """
        # 对https://api.bilibili.com/x/v2/reply/add发送POST请求，参数是type=1，oid=self.av，message=评论内容，plat=1
        post_url = "https://api.bilibili.com/x/v2/reply/add"
        post_data = {
            "type": 1,
            "oid": self.av,
            "message": message,
            "plat": 1,
            "csrf": cookies().bili_jct
        }
        r = requests.post(url=post_url, headers=self.headers, data=post_data)
        reply_data = r.json()
        if reply_data["code"] != 0:
            print(f"评论失败，错误码{reply_data['code']}，"
                  f"请查看'https://socialsisteryi.github.io/bilibili-API-collect/docs/comment/action.html'获取错误码信息")
            biliLoginState(self.headers).get_login_state()
        else:
            print("评论成功")
            print("评论rpid：", reply_data["data"]["rpid"])
            print("评论内容：", reply_data["data"]["reply"]["content"]["message"])


class biliQRLogin:
    """B站扫码登录，目前该功能没有实现
    [示例代码]:
        QRL = biliQRLogin()
        QRL.require()
        QRL.generate()
        while True:
            status, cookie = QRL.scan_qr()
            match status:
                case 86090:
                    print("扫码成功但未确认")
                case 0:
                    print("登录成功")
                case 86101:
                    print("未扫码")
                case 86038:
                    print("二维码失效")
                    break
    """
    def __init__(self):
        self.headers = {"User-Agent": useragent().pcChrome}
        self.url = 'https://passport.bilibili.com/x/passport-login/web/qrcode/generate'

    def require(self):
        r = requests.get(self.url, headers=self.headers)
        print(r.text)
        data = r.json()
        self.token = data['data']['qrcode_key']
        self.qrcode_url = data['data']['url']

    def generate(self):
        r = requests.get(self.qrcode_url, headers=self.headers)
        img = Image.open(BytesIO(r.content))
        img.show()
        print("请使用手机客户端扫描二维码登录...")

    def scan_qr(self):
        status = ''
        cookie = ''
        while True:
            url = f'https://passport.bilibili.com/x/passport-login/web/qrcode/poll?key={self.token}'
            response = requests.get(url)
            data = response.json().get('data', {})
            status = data.get('status')
            if status in ['ScanSuccess', 'Success']:
                cookie = response.headers.get('set-cookie')
            if status in ['ScanSuccess', 'Success', 'Timeout', 'Invalid']:
                break
            time.sleep(1)
        return status, cookie


class biliLoginState:
    def __init__(self, headers):
        """
        :param headers: 比如headers={"Cookie": cookies().bilicookie, "User-Agent": useragent().pcChrome}
        """
        self.headers = headers
        self.url = 'https://api.bilibili.com/x/web-interface/nav'

    def get_login_state(self):
        """
        获取登录状态
        [使用方法]:
            biliLoginState(headers).get_login_state()
        :return:
        """
        # get请求https://api.bilibili.com/x/web-interface/nav，参数是cookie，返回的是用户的信息
        r = requests.get(url=self.url, headers=self.headers)
        login_msg = r.json()
        print("登录状态：", login_msg["data"]["isLogin"])


class BV2AV:
    def __init__(self):
        """转化算法来自于https://socialsisteryi.github.io/bilibili-API-collect/docs/misc/bvid_desc.html#python"""
        self.XOR_CODE = 23442827791579
        self.MASK_CODE = 2251799813685247
        self.MAX_AID = 1 << 51
        self.ALPHABET = "FcwAPNKTMug3GV5Lj7EJnHpWsx4tb8haYeviqBz6rkCy12mUSDQX9RdoZf"
        self.ENCODE_MAP = 8, 7, 0, 5, 1, 3, 2, 4, 6
        self.DECODE_MAP = tuple(reversed(self.ENCODE_MAP))

        self.BASE = len(self.ALPHABET)
        self.PREFIX = "BV1"
        self.PREFIX_LEN = len(self.PREFIX)
        self.CODE_LEN = len(self.ENCODE_MAP)

    def av2bv(self, aid: int) -> str:
        """
        [使用方法]:
            BV2AV().av2bv(111298867365120)  # 返回"BV1L9Uoa9EUx"
        :param aid: av号
        :return: bv号
        """
        self.bvid = [""] * 9
        tmp = (self.MAX_AID | aid) ^ self.XOR_CODE
        for i in range(self.CODE_LEN):
            self.bvid[self.ENCODE_MAP[i]] = self.ALPHABET[tmp % self.BASE]
            tmp //= self.BASE
        return self.PREFIX + "".join(self.bvid)

    def bv2av(self, bvid: str) -> int:
        """
        [使用方法]:
            BV2AV().bv2av("BV1L9Uoa9EUx")  # 返回111298867365120
        :param bvid: bv号
        :return: av号
        """
        assert bvid[:3] == self.PREFIX
        bvid = bvid[3:]
        tmp = 0
        for i in range(self.CODE_LEN):
            idx = self.ALPHABET.index(bvid[self.DECODE_MAP[i]])
            tmp = tmp * self.BASE + idx
        return (tmp & self.MASK_CODE) ^ self.XOR_CODE


if __name__ == '__main__':

    bv_content_df = pd.DataFrame()
    for bvs in ["BV1dy421e7KG", "BV1DZ421J7a2"]:
        biliV = biliVideo(bvs)
        biliV.get_html()
        biliV.get_content()
        bv_content_df = pd.concat([bv_content_df, biliV.to_csv()], axis=0)
    bv_content_df.to_excel("input/xlsx_data/bv_msg.xlsx", index=False)




