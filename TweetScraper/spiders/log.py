# -*- encoding: utf-8 -*-
import logging  # 引入logging模块
import os.path
import time
from scrapy.conf import settings

class log:

    def __init__(self, domain, file_path):
        # 第一步，创建一个logger
        self.logger = logging.getLogger(domain)
        self.logger.setLevel(logging.INFO)  # Log等级总开关
        # 第二步，创建一个handler，用于写入日志文件
        # rq = time.strftime('%Y%-m%-%d %H:%M:%S', time.localtime(time.time()))
        self.log_path = file_path
        self.fh = logging.FileHandler(self.log_path, mode='a')
        self.fh.setLevel(logging.DEBUG)  # 输出到file的log等级的开关
        # 第三步，定义handler的输出格式
        self.formatter = logging.Formatter("[%(asctime)s] - [%(levelname)s] %(message)s")
        self.fh.setFormatter(self.formatter)
        # 第四步，将logger添加到handler里面
        self.logger.addHandler(self.fh)


    def debug(self, message):
        self.logger.debug(message)

    def info(self, message):
        self.logger.info(message)

    def warning(self, message):
        self.logger.warning(message)

    def error(self, message):
        self.logger.error(message)

    def critical(self, message):
        self.logger.critical(message)
