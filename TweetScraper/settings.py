# -*- coding: utf-8 -*-

# !!! # Crawl responsibly by identifying yourself (and your website/e-mail) on the user-agent
USER_AGENT = 'TweetScraper'

# settings for spiders
BOT_NAME = 'TweetScraper'

################################################# Log Config ###########################################################
LOG_LEVEL = 'INFO'
# 日志文件         # (最好为爬虫名称，例如：qiushi.log)
LOG_FILE = 'run.log'
# 是否启用日志（创建日志后，不需开启，进行配置）
LOG_ENABLED = False  # （默认为True，启用日志）
# 日志编码
LOG_ENCODING = 'utf-8'

# 如果是True ，进程当中，所有标准输出（包括错误）将会被重定向到log中
# 例如：在爬虫代码中的 print（）
LOG_STDOUT = True  # (默认为False)


################################################# Log Config ###########################################################

DOWNLOAD_HANDLERS = {'s3': None,} # from http://stackoverflow.com/a/31233576/2297751, TODO

SPIDER_MODULES = ['TweetScraper.spiders']
NEWSPIDER_MODULE = 'TweetScraper.spiders'
ITEM_PIPELINES = {
    'TweetScraper.pipelines.SaveToFilePipeline':100,
    #'TweetScraper.pipelines.SaveToMongoPipeline':100, # replace `SaveToFilePipeline` with this to use MongoDB
    #'TweetScraper.pipelines.SavetoMySQLPipeline':100, # replace `SaveToFilePipeline` with this to use MySQL
}

DOWNLOADER_MIDDLEWARES = {
    'scrapy.contrib.downloadermiddleware.httpproxy.HttpProxyMiddleware': 110,
    'project_name.middlewares.ProxyMiddleware': 100,
    'scrapy.contrib.downloadermiddleware.retry.RetryMiddleware': 80,
}


RETRY_HTTP_CODES = [500, 503, 504, 400, 403, 404, 408]
RETRY_TIMES = 10


# settings for where to save data on disk
SAVE_TWEET_PATH = './Data/tweet/'
SAVE_USER_PATH = './Data/user/'
SAVE_ERROR_PATH ='./Data/error/'

# settings for mongodb
MONGODB_SERVER = "127.0.0.1"
MONGODB_PORT = 27017
MONGODB_DB = "TweetScraper"        # database name to save the crawled data
MONGODB_TWEET_COLLECTION = "tweet" # collection name to save tweets
MONGODB_USER_COLLECTION = "user"   # collection name to save users

# input data dir
INPUT_DATA_DIR = './Input/'
PROVESS_DATA_LIST_FILE = './Process/'
LOG_DIR = './Log/'
FILE_BATCH_SIZE = 2
QUERY_BATCH_SIZE = 10
BATCH_SLEEP_TIME = 60

PROXY_URL = 'heep://127.0.0.1:5010/get/'




