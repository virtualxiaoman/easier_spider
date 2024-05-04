import time
import numpy as np

class Timer:
    """
    [功能] 记录多次运行时间。
    [使用示例]
        timer = Timer()
          要测试时间的代码块1
        print(f'{timer.stop():.5f} sec')
          其他代码
        timer.start()
          要测试时间的代码块2
        print(f'{timer.stop():.5f} sec')
    """
    def __init__(self):
        self.times = []
        self.start()

    def start(self):
        """启动计时器"""
        self.tik = time.time()

    def stop(self):
        """停止计时器并将时间记录在列表中"""
        self.times.append(time.time() - self.tik)
        return self.times[-1]

    def avg(self):
        """返回平均时间"""
        return sum(self.times) / len(self.times)

    def sum(self):
        """返回时间总和"""
        return sum(self.times)

    def cumsum(self):
        """返回累计时间"""
        return np.array(self.times).cumsum().tolist()