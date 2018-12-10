# Importing base64 library because we'll need it ONLY in case if the proxy we are going to use requires authentication
import base64
from scrapy.spiders import CrawlSpider, Rule
from scrapy.selector import Selector
from scrapy.conf import settings
from scrapy import http
from scrapy.shell import inspect_response  # for debugging
import re
import json
import time
from log import log
from copy import deepcopy
import requests
import os

# Start your middleware class
class ProxyMiddleware(object):
    # overwrite process request
    def __init__(self):
        self.name = 'ProxyProcess'
        self.proxy_url = settings['PROXY_URL']
        self.MAX_RETRY = 30
        self.log = log(self.name, os.path.join(settings['LOG_DIR'], 'proxy.log'))

    def process_request(self, request, spider):
        if 'change_proxy' in request.meta and request.meta['change_proxy']:
            new_proxy = self.handleProxy(request.meta['proxy'], 1)
            if new_proxy:
                request.meta.update({
                    'proxy': new_proxy
                })
                self.log.info('[Proxy Change] name:{} proxy:{}'.format(request.meta['name'], new_proxy))
                # proxy_user_pass = "USERNAME:PASSWORD"
                # # setup basic authentication for the proxy
                # encoded_user_pass = base64.encodestring(proxy_user_pass)
                # request.headers['Proxy-Authorization'] = 'Basic ' + encoded_user_pass
            request.meta['change_proxy'] = False


    def handleProxy(self, old_proxy, retry_times):
        if retry_times > self.MAX_RETRY:
            return None
        resp = requests.get(url=self.proxy_url, timeout=30)
        if resp.status_code >=200 and resp.status_code <300:
            new_proxy = resp.text
            if not old_proxy in new_proxy:
                return 'http://'+new_proxy
            else:
                self.log.info('[Proxy Duplicate] time:{} old_proxy:{} result:{}'.format(retry_times, old_proxy, resp))
                return self.handleProxy(old_proxy, retry_times+1)
        else:
            self.log.info('[Proxy Retry] time:{} result:{}'.format(retry_times, resp))
            return self.handleProxy(old_proxy, retry_times + 1)