# -*- coding: utf-8 -*-
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
from inputData import inputData

try:
    from urllib import quote  # Python 2.X
except ImportError:
    from urllib.parse import quote  # Python 3+

from datetime import datetime
import os

from TweetScraper.items import Tweet, User, Page, ErrorPage




class TweetScraper(CrawlSpider):
    name = 'TweetScraper'
    allowed_domains = ['twitter.com']
    custom_settings = {
        'DOWNLOADER_MIDDLEWARES': {
            'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware': None,
            'TESTSpider.middlewares.ProcessAllExceptionMiddleware': 120,
        },
        'DOWNLOAD_DELAY': 20,
        'AUTOTHROTTLE_ENABLED': True,  # 启动[自动限速]
        'AUTOTHROTTLE_DEBUG': True,  # 开启[自动限速]的debug
        'AUTOTHROTTLE_MAX_DELAY': 10,  # 设置最大下载延时
        'DOWNLOAD_TIMEOUT': 15,
        'CONCURRENT_REQUESTS_PER_DOMAIN': 4  # 限制对该网站的并发请求数
    }


    def __init__(self, crawl_user=False, top_tweet=False):
        self.start_url = 'https://twitter.com/i/search/timeline?vertical=default&q={}&src=typd&max_position={}'
        # self.start_url = 'https://twitter.com/search?l={}&q={}&src=typd'
        #
        # if not top_tweet:
        #     self.url = self.url + "&f=tweets"

        # self.url = self.url + "&q=%s&src=typed&max_position=%s"
        self.log = log(self.name, os.path.join(settings['LOG_DIR'], 'tweet.log'))
        self.crawl_user = crawl_user
        # self.query = 'donate heart love since:2018-10-07 until:2018-10-08'
        self.input_data = inputData
        self.query_batch_size = settings['QUERY_BATCH_SIZE']
        self.batch_sleep_time = settings['BATCH_SLEEP_TIME']
        self.save_name = '{date_time}_{query}_{pagenum}'
        self.proxy_url = 'http://127.0.0.1:5010/get/'
        self.Req_id = '[Req] query:{} page:{}'
        self.MAX_RETRY = 30

    def start_requests(self):
        # if not self.input_data:
        #     return
        #
        # # query in batch
        # for k, query in enumerate(self.input_data):
        #     url = self.url % ('', quote(query))
        #     yield http.Request(url, callback=self.parse_page)
        #     if k%self.query_batch_size == 0 and k !=0:
        #         time.sleep(self.batch_sleep_time)
        # url = self.start_url.format('', quote('love since:2018-10-10 until:2018-10-10'))
        for req in self.batch_request(0):
            yield req

    def batch_request(self, position):
        end = position+self.query_batch_size
        if not end < len(self.input_data):
            end = len(self.input_data)
        for pos in range(position, end):
            query = self.input_data[pos]
            url = self.start_url.format(quote(query), '')
            # print url
            yield http.Request(
                url,
                callback=self.parse_page,
                meta={
                    'name': self.Req_id.format(query, 1),
                    'page_num': 1,
                    'query': query,
                    'pos': pos,
                    'change_proxy': True,
                },
                errback=self.retry
            )
            self.log.info('[Request] query: {} page: {} url: {}'.format(1, query, url))

    def parse_page(self, response):
        # inspect_response(response, self)
        # handle current page
        # pass empty page
        data = json.loads(response.body.decode("utf-8"))
        parsed_time = time.strftime('%Y-%m-%d_%H-%M-%S', time.localtime(time.time()))
        meta = deepcopy(response.meta)

        # save error page to debug
        if 'items_html' not in data:
            page = ErrorPage()
            page['data'] = data
            page['page_num'] = meta['page_num']
            page['query'] = meta['query']
            page['save_name'] = self.save_name.format(
                date_time=parsed_time,
                query=meta['query'].replace(':', '_').replace(' ', '_'),
                pagenum=meta['page_num']
            )
            page['url'] = response.url
            yield page
            self.log.info('[ErrorPage] query: {} page: {} url:{}'.format(meta['page_num'], meta['query'], response.url))

        # pass empty page
        elif 'tweet' not in data['items_html']:
            self.log.info('[EndPage] query: {} page: {} url:{}'.format(meta['page_num'], meta['query'], response.url))

        else:
            # save page
            page = Page()
            page['data'] = data
            page['page_num'] = response.meta['page_num']
            page['query'] = meta['query']
            page['save_name'] = self.save_name.format(
                date_time = parsed_time,
                query = meta['query'].replace(':', '_').replace(' ', '_'),
                pagenum = meta['page_num']
            )
            page['url'] = response.url
            yield page
            self.log.info('[HitPage] query: {} page: {} url:{}'.format(meta['page_num'], meta['query'], response.url))

            # get next page
            min_position = data['min_position']
            url = self.start_url.format(quote(meta['query']), min_position)
            meta.update({
                'name': self.Req_id.format(meta['query'], response.meta['page_num'] + 1),
                'page_num': response.meta['page_num'] + 1
            })
            yield http.Request(
                url,
                callback=self.parse_page,
                meta=meta,
                errback=self.retry
            )
            self.log.info('[Request] query: {} page: {} url: {} '.format(meta['page_num'], meta['query'], url))

            # request new query
            if meta['pos'] % self.query_batch_size == self.query_batch_size - 1:
                for req in self.batch_request(meta['pos'] + 1):
                    yield req

    def retry(self, response):
        meta = response.request.meta
        if not 'retry_time' in meta:
            meta.update({
                'retry_time': 0
            })
        if meta['retry_time'] > self.MAX_RETRY:
            self.log.info('[RETRY_STOP] time:{} query: {} page: {} url: {} '.format(meta['retry_time'], meta['page_num'], meta['query'], response.url))
        else:
            meta['retry_time'] = meta['retry_time'] + 1
            self.log.info(
                '[RETRY] time:{} query: {} page: {} url: {} '.format(meta['retry_time'], meta['page_num'], meta['query'], response.url))
            yield response.request


    # def parse_tweets_block(self, html_page):
    #     page = Selector(text=html_page)
    #
    #     ### for text only tweets
    #     items = page.xpath('//li[@data-item-type="tweet"]/div')
    #     for item in self.parse_tweet_item(items):
    #         yield item
    #
    # def parse_tweet_item(self, items):
    #     for item in items:
    #         try:
    #             tweet = Tweet()
    #
    #             tweet['usernameTweet'] = item.xpath('.//span[@class="username u-dir u-textTruncate"]/b/text()').extract()[0]
    #
    #             ID = item.xpath('.//@data-tweet-id').extract()
    #             if not ID:
    #                 continue
    #             tweet['ID'] = ID[0]
    #
    #             ### get text content
    #             tweet['text'] = ' '.join(
    #                 item.xpath('.//div[@class="js-tweet-text-container"]/p//text()').extract()).replace(' # ',
    #                                                                                                     '#').replace(
    #                 ' @ ', '@')
    #             if tweet['text'] == '':
    #                 # If there is not text, we ignore the tweet
    #                 continue
    #
    #             ### get meta data
    #             tweet['url'] = item.xpath('.//@data-permalink-path').extract()[0]
    #
    #             nbr_retweet = item.css('span.ProfileTweet-action--retweet > span.ProfileTweet-actionCount').xpath(
    #                 '@data-tweet-stat-count').extract()
    #             if nbr_retweet:
    #                 tweet['nbr_retweet'] = int(nbr_retweet[0])
    #             else:
    #                 tweet['nbr_retweet'] = 0
    #
    #             nbr_favorite = item.css('span.ProfileTweet-action--favorite > span.ProfileTweet-actionCount').xpath(
    #                 '@data-tweet-stat-count').extract()
    #             if nbr_favorite:
    #                 tweet['nbr_favorite'] = int(nbr_favorite[0])
    #             else:
    #                 tweet['nbr_favorite'] = 0
    #
    #             nbr_reply = item.css('span.ProfileTweet-action--reply > span.ProfileTweet-actionCount').xpath(
    #                 '@data-tweet-stat-count').extract()
    #             if nbr_reply:
    #                 tweet['nbr_reply'] = int(nbr_reply[0])
    #             else:
    #                 tweet['nbr_reply'] = 0
    #
    #             tweet['datetime'] = datetime.fromtimestamp(int(
    #                 item.xpath('.//div[@class="stream-item-header"]/small[@class="time"]/a/span/@data-time').extract()[
    #                     0])).strftime('%Y-%m-%d %H:%M:%S')
    #
    #             ### get photo
    #             has_cards = item.xpath('.//@data-card-type').extract()
    #             if has_cards and has_cards[0] == 'photo':
    #                 tweet['has_image'] = True
    #                 tweet['images'] = item.xpath('.//*/div/@data-image-url').extract()
    #             elif has_cards:
    #                 logger.debug('Not handle "data-card-type":\n%s' % item.xpath('.').extract()[0])
    #
    #             ### get animated_gif
    #             has_cards = item.xpath('.//@data-card2-type').extract()
    #             if has_cards:
    #                 if has_cards[0] == 'animated_gif':
    #                     tweet['has_video'] = True
    #                     tweet['videos'] = item.xpath('.//*/source/@video-src').extract()
    #                 elif has_cards[0] == 'player':
    #                     tweet['has_media'] = True
    #                     tweet['medias'] = item.xpath('.//*/div/@data-card-url').extract()
    #                 elif has_cards[0] == 'summary_large_image':
    #                     tweet['has_media'] = True
    #                     tweet['medias'] = item.xpath('.//*/div/@data-card-url').extract()
    #                 elif has_cards[0] == 'amplify':
    #                     tweet['has_media'] = True
    #                     tweet['medias'] = item.xpath('.//*/div/@data-card-url').extract()
    #                 elif has_cards[0] == 'summary':
    #                     tweet['has_media'] = True
    #                     tweet['medias'] = item.xpath('.//*/div/@data-card-url').extract()
    #                 elif has_cards[0] == '__entity_video':
    #                     pass  # TODO
    #                     # tweet['has_media'] = True
    #                     # tweet['medias'] = item.xpath('.//*/div/@data-src').extract()
    #                 else:  # there are many other types of card2 !!!!
    #                     logger.debug('Not handle "data-card2-type":\n%s' % item.xpath('.').extract()[0])
    #
    #             is_reply = item.xpath('.//div[@class="ReplyingToContextBelowAuthor"]').extract()
    #             tweet['is_reply'] = is_reply != []
    #
    #             is_retweet = item.xpath('.//span[@class="js-retweet-text"]').extract()
    #             tweet['is_retweet'] = is_retweet != []
    #
    #             tweet['user_id'] = item.xpath('.//@data-user-id').extract()[0]
    #             yield tweet
    #
    #             if self.crawl_user:
    #                 ### get user info
    #                 user = User()
    #                 user['ID'] = tweet['user_id']
    #                 user['name'] = item.xpath('.//@data-name').extract()[0]
    #                 user['screen_name'] = item.xpath('.//@data-screen-name').extract()[0]
    #                 user['avatar'] = \
    #                     item.xpath('.//div[@class="content"]/div[@class="stream-item-header"]/a/img/@src').extract()[0]
    #                 yield user
    #         except:
    #             logger.error("Error tweet:\n%s" % item.xpath('.').extract()[0])
    #             # raise
    #
    # def extract_one(self, selector, xpath, default=None):
    #     extracted = selector.xpath(xpath).extract()
    #     if extracted:
    #         return extracted[0]
    #     return default
