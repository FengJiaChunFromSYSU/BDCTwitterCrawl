# -*- encoding: utf-8 -*-
import re
import json
import time
import logging
# from scrapy.conf import settings
import os

def getData():
    # read input data from input dir, and reduplicate, then feed to spiders
    input_data_dir = settings['INPUT_DATA_DIR']
    log_dir = settings['HIT_LOG_DIR']
    process_dir = settings['PROVESS_DATA_DIR']
    p = ''
    input_files_list = []
    file_batch_size = settings['FILE_BATCH_SIZE']

    # read input data files
    for root, dir, files in os.walk(input_data_dir):
        for f in files:
            input_files_list.append(f)
    # get input data
    input_data = {}
    for f in input_files_list[:file_batch_size]:
        # read input data
        with open(os.join(input_data_dir, f)) as reader:
            for line in reader:
                input_data.update({line.strip(): ''})
        # remove input file after reading
        os.remove(os.join(input_data_dir, f))

        # remove those data that has been search and hit
        with open(os.join(log_dir, f)) as reader:
            for line in reader:
                if line in input_data:
                    del input_data[line]

    return input_data.keys()

def test():
    A = ['donate', 'donates', 'donation', 'donating', 'donated']
    B = ['organ', 'organs', 'body', 'bodies', 'kidney', 'kidneys', 'liver', 'livers', 'heart', 'hearts', 'lung', 'lungs', 'pancreas', 'cornea']
    start = 'since:2018-10-10'
    end = 'until:2018-10-11'
    indir = 'D:\冯佳纯\实验室\任务\项目\数据爬取\\TweetScraper-master\\TweetScraper\\Input\\'
    with open (indir+'data1', mode='w', encoding='utf-8') as writer:
        for a in A:
            for b in B:
                writer.write('\'{} {} {} {}\',\n'.format(a, b, start, end))



if __name__ == "__main__":
    test()






