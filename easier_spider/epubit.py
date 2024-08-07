# 对于一本书的其中一页的网页链接：
# https://labs.epubit.com/onlineEbookReader?id=190b3825-3013-4fb9-88e4-c9c5455ddbfb&pid=27be6d78-dc2b-43fb-a9f0-cf76723af3ca&isFalls=true&src=normal
# 其中pid是projectId，书的ID。id是folderId，书的某一页的ID。
# 使用"https://labs.epubit.com/pubcloud/content/front/getContentsByFolderId"来获取书的内容，参数是folderId和projectId
# 使用"https://labs.epubit.com/pubcloud/content/front/nextNotNullSection"来获取下一页的folderId，参数是folderId和projectId
#
# 注意cookie是每日更新的，需要手动更新
#
# 右侧工具栏
# 目录：https://labs.epubit.com/pubcloud/content/front/ebookFolderTree?projectId=27be6d78-dc2b-43fb-a9f0-cf76723af3ca
# 搜索：https://labs.epubit.com/pubcloud/content/front/ebookSearch?keyword=&page=1&size=5&tag=&projectType=&projectId=27be6d78-dc2b-43fb-a9f0-cf76723af3ca
# 应该做一个目录的功能，但是我现在好懒啊

import os
import random
import re
import time
import warnings

import requests
from easier_spider.config import useragent, epubitcookies

class epubit:
    def __init__(self, pid, book_name="temp"):
        """
        初始化
        :param pid: 这个是书的ID，也就是下文参数里的projectId
        :param book_name: 书名，可选参数，默认为temp，以后有空再做自动获取书名的功能
        """
        self.url_content = "https://labs.epubit.com/pubcloud/content/front/getContentsByFolderId"
        self.pid = pid
        self.book_name = book_name
        self.book_path = None

        self.headers = {
            "Cookie": epubitcookies().cookie,
            "User-Agent": useragent().pcChrome,
            "origin-domain": "labs.epubit.com",  # 这个不加就直接寄
            "host": "labs.epubit.com",  # 该参数似乎可以不加，但是先留着吧
        }

        self._init_book_path()

    def _init_book_path(self):
        self.book_path = f"output/epubit/{self.book_name}"
        if not os.path.exists(self.book_path):
            os.makedirs(self.book_path)
            os.makedirs(f"{self.book_path}/img")

    def get_content(self, folderId):
        """
        获取pid书的folderId页面
        :param folderId: 页面id
        :return: list，书的内容，list的元素是html格式
        """
        img_list = []  # 图
        content_list = []  # 书

        params = {
            "folderId": folderId,
            "projectId": self.pid,
            "src": "normal"
        }
        response = requests.get(self.url_content, headers=self.headers, params=params)
        # print(response.json())
        try:
            r_json = response.json()
        except Exception as e:
            warnings.warn(f"获取{folderId}的内容失败，错误信息{e}，返回值{response.text}")
            # 等待一段时间再继续
            time.sleep(66)
            return self.get_content(folderId)
        if r_json["code"] == '0':
            # print("获取成功")
            r_data = r_json["data"]
            r_contents = r_data["contents"]
            for content in r_contents:
                editingContent = content["editingContent"]
                # 如果contet以pubcloud开头，以图片格式(png,jpg,jpeg,gif,webp)结尾(这个暂时不知道有多少格式，先不写)，那么就是图片。
                # 保存图片到img文件夹，然后将图片的路径加入到content_list中
                if editingContent.startswith("pubcloud"):
                    img_name = editingContent.split("/")[-1]
                    img_local = f"{self.book_path}/img/{img_name}"
                    img_response = requests.get(f"https://cdn.ptpress.cn/{editingContent}")
                    # print(img_response.url)
                    with open(img_local, "wb") as f:
                        f.write(img_response.content)
                    content_list.append(f'<img src="img/{img_name}" class="img">')
                else:
                    content_list.append(editingContent)
            # r_imgs = r_data["imgUrls"]
            # for r_img in r_imgs:
            #     # 去除i在?后面的内容
            #     img_without_watermark = r_img.split('?')[0]
            #     # print(img_without_watermark)
            #     img_local = f"{self.book_path}/img/{img_without_watermark.split('/')[-1]}"
            #     img_response = requests.get(img_without_watermark)
            #     with open(img_local, "wb") as f:
            #         f.write(img_response.content)
            #     img_list.append(f"img/{img_without_watermark.split('/')[-1]}")
            # r_contents = r_data["contents"]
            # for r_content in r_contents:
            #     content = r_content["content"]
            #     gs_pattern = re.compile(r'<p class="gs".*?>.*?</p>')  # 匹配公式(因为公式有时候出现text-align: center;以及公式序号)
            #     # print(content)
            #     # 这是图片的content
            #     if content == '<p class="图"></p>':
            #         if img_list:
            #             content_list.append(f'<img src="{img_list[0]}" class="img">')  # 图片就加入url，因为content中没有其他信息了
            #             img_list.pop(0)
            #         else:
            #             warnings.warn(f"获取对应的imgUrls失败，content为{content}")
            #     elif gs_pattern.match(content):
            #         if img_list:
            #             content_list.append(f'<img src="{img_list[0]}" class="img">')  # 公式加入url，这里应该是$$ $$形式的公式
            #             img_list.pop(0)
            #         else:
            #             warnings.warn(f"获取对应的imgUrls失败，content为{content}")
            #     elif content == '<p style=\"text-align: center\"></p>':
            #         if img_list:
            #             content_list.append(f'<img src="{img_list[0]}" class="img">')
            #             img_list.pop(0)
            #         else:
            #             warnings.warn(f"获取对应的imgUrls失败，content为{content}")
            #     # 有些content为空就不需要加入了
            #     elif content:
            #         content_list.append(content)
            # if img_list:
            #     # 我猜测该warning是因为较长的公式的公式图片也可能在r_data["imgUrls"]里面，但是因为没有特殊的命名规则，所以无法判断
            #     warnings.warn(f"请注意图片未能全部填入到content_list中，缺少的图片是{img_list}")
            #     content_list.extend(img_list)  # 将剩余的图片加入到content_list中
        else:
            warnings.warn(f"获取{folderId}的内容失败，错误信息{r_json}")
            # 等待一段时间再继续
            time.sleep(22)
            return self.get_content(folderId)
        return content_list

    def get_whole_content(self, first_folderId, content=None):
        """
        获取整本书
        :param first_folderId: 第一个folderId。断点续传时应该选用被10整除的那个folderId，因为每10次保存一次
        :param content: 可选参数，断点续传时传入的content
        :return: list, content
        """
        content_list = []
        if content:
            content_list.extend(content)

        current_folderId = first_folderId
        current_iter = 0  # 当前get_content次数
        while True:
            content = self.get_content(current_folderId)
            content_list.extend(content)

            current_folderId = self._get_next_folderId(current_folderId)
            if current_folderId == -1:
                print("获取完毕")
                break

            if current_iter % 10 == 0:
                print(f"当前次数{current_iter}，当前folderId{current_folderId}")
                self.content2html(content_list)  # 防止中途寄寄
            current_iter += 1
            print(f"\r当前次数{current_iter}", end="")
            self._sleep_in_get_whole_content(current_iter)
        self.content2html(content_list)

    def _get_next_folderId(self, folderId):
        url = f"https://labs.epubit.com/pubcloud/content/front/nextNotNullSection?folderId={folderId}&projectId={self.pid}"
        response = requests.get(url, headers=self.headers)
        try:
            r_json = response.json()
        except Exception as e:
            warnings.warn(f"获取{folderId}的next_folderId失败，错误信息{e}，返回值{response.text}")
            exit(111)
        if r_json["code"] == "0":
            return r_json["data"]
        elif r_json["code"] == "6":
            return -1  # 表示结尾
        else:
            raise ValueError(f"获取{folderId}的next_folderId失败，错误信息{r_json}")

    def content2html(self, content):
        """
        将content转化成真正的html
        :param content:get_content获取到的list元素content
        """
        # 补全HTML结构
        html_content = """<!DOCTYPE html>
        <html lang="zh-CN">
        <head>
            <meta charset="UTF-8">
            <title>Document</title>
            <style>
            body {
                display: flex;
                justify-content: center;
            }
            .content_main {
                width: 80%;
            }
            p.zw {
                text-indent: 2em;
                margin: 1em 0;
                line-height: 180%;
            }
            p.footnote {
                margin: 1em 0;
                font-size: 80%;
                line-height: 180%;
                background-color: #EFF8FB;
            }
            .img {
                max-width: 80%;
                display: block;
                margin: auto;
            }
            p.图题{
                text-align: center;
            }
        </style>
        </head>
        <body>
        <div class="content_main">
        """ + "\n".join(content) + """
        </div>
        </body>
        </html>
        """
        # 将HTML内容写入文件
        with open(f"{self.book_path}/{self.book_name}.html", 'w', encoding='utf-8') as file:
            file.write(html_content)

        print(f"HTML文件已保存为{self.book_path}/{self.book_name}.html")

    def html2content(self, html_path):
        """
        将html转化成content，一般用于断点续传
        :param html_path: html文件路径
        :return: list, content
        """
        with open(html_path, 'r', encoding='utf-8') as file:
            html_content = file.read()
        # 获取<div class="content_main"></div>中的内容
        html_content = html_content.split('<div class="content_main">')[1].split('</div>')[0]
        # 将内容按行分割
        return html_content.split("\n")

    def _sleep_in_get_whole_content(self, current_iter):
        # 根据需求调整sleep时间
        time.sleep(1.2)
        if current_iter % 5 == 0:
            time.sleep(random.uniform(8, 16))
        if current_iter % 17 == 0:
            time.sleep(random.uniform(20, 50))
        if current_iter % 37 == 0:
            time.sleep(random.uniform(100, 120))
        if current_iter % 73 == 0:
            time.sleep(random.uniform(140, 165))

ep = epubit("75044a69-f2c0-451f-8ca3-96e4b4f1987a", "深度学习案例精粹")
content = ep.html2content("output/epubit/深度学习案例精粹/深度学习案例精粹.html")  # 断点续传
ep.get_whole_content("50454a93-ee9f-4190-baec-24610ae5bd29", content=content)  # 使用之前的content继续获取

