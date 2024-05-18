## 更便捷的爬虫操作
<p>TIP: 需要运行该项目，你应该先自行配置config.py文件。</p>
<p>本项目(easier_spider)结构如下:</p>

```
.
├── easier_spider
│   ├── config.py
│   ├── bilibvideo.py
├── easier_tools
│   ├── Colorful_Console.py
```

其余文件非必须。

config.py可以如下配置，其中需要在`self.bilicookie = `里填入你的cookie：
```python

class bilicookies:
    def __init__(self):
        self.bilicookie = """填入你的cookie"""
        self.SESSDATA = None
        self.bili_jct = None  # csrf参数
        self.get_SESSDATA()
        self.get_bili_jct()

    def get_SESSDATA(self):
        # 使用split()方法根据分号";"将字符串拆分成多个子字符串
        cookie_parts = self.bilicookie.split(";")
        # 遍历这些子字符串，找到以"SESSDATA="开头的子字符串
        SESSDATA_value = None
        for part in cookie_parts:
            if part.strip().startswith("SESSDATA="):
                key_value_pair = part.split("=")  # 使用split()方法根据等号"="将该子字符串拆分成键值对
                SESSDATA_value = key_value_pair[1]  # 提取键值对中的值，即SESSDATA的值
                break
        self.SESSDATA = SESSDATA_value
        if self.SESSDATA is None:
            print("SESSDATA not found in cookies")
            exit(1)

    def get_bili_jct(self):
        # 使用split()方法根据分号";"将字符串拆分成多个子字符串
        cookie_parts = self.bilicookie.split(";")
        # 遍历这些子字符串，找到以"bili_jct="开头的子字符串
        bili_jct_value = None
        for part in cookie_parts:
            if part.strip().startswith("bili_jct="):
                key_value_pair = part.split("=")
                bili_jct_value = key_value_pair[1]
                break
        self.bili_jct = bili_jct_value
        if self.bili_jct is None:
            print("bili_jct not found in cookies")
            exit(1)

class useragent:
    def __init__(self):
        self.pcChrome = """Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36 Edg/124.0.0.0"""

```
