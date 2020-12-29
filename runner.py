import os
import time

from log import logger
from utils import make_batch_dir
from utils import make_sequence_dir


class Runner:

    def __init__(self, sniffer, config, url_list):

        self.sniffer = sniffer
        self.url_list = url_list

        self.browser_path = config['TorBrowser']['browser_path']
        self.socks_port = int(config['TorBrowser']['socks_port'])
        self.control_port = int(config['TorBrowser']['control_port'])
        self.headless = config['TorBrowser'].getboolean('headless')
        self.executable_path = config['TorBrowser']['executable_path']
        self.capture_screen = config['TorBrowser']['capture_screen']

        # default save_path is current_directory/result
        # batch directory save_path/url/epoch/batch
        # sequence directory save_path/url/epoch
        save_path = config['CaptureProgram']['save_path']
        self.save_path = os.path.join(os.getcwd(), save_path)

        self.batch_size = int(config['Batch']['batch_size'])
        self.total_size = int(config['Batch']['total_size'])
        self.sleep_between_batch = int(config['Batch']['sleep_batch'])
        self.sleep_between_url = int(config['Batch']['sleep_url'])
        self.sleep_between_epoch = int(config['Batch']['sleep_epoch'])

    def batch(self):

        logger.info('Sniff using batch')
        for epoch in range(self.total_size // self.batch_size):  # epoch
            for url in self.url_list:
                for batch in range(self.batch_size):
                    directory_name = make_batch_dir(self.save_path, url, epoch, batch)
                    logger.info('Batch - [%d/%d] - Epoch - [%d/%d] - URL - %s' % (batch, self.batch_size, epoch, self.total_size // self.batch_size, url))
                    self.sniffer.sniff(url, directory_name)
                    time.sleep(self.sleep_between_batch)
                time.sleep(self.sleep_between_url)
            time.sleep(self.sleep_between_epoch)

    def sequence(self, num_of_repeat):

        logger.info('Sniff using sequence')
        for epoch in range(num_of_repeat):
            for url in self.url_list:
                directory_name = make_sequence_dir(self.save_path, url, epoch)
                logger.info('Epoch - [%d/%d] - URL - %s' % (epoch, num_of_repeat, url))
                self.sniffer.sniff(url, directory_name)
                time.sleep(self.sleep_between_batch)
            time.sleep(self.sleep_between_epoch)

    def remain(self, remain_json):

        logger.info('Sniff remain.')
        keys = remain_json.keys()
        for epoch in range(self.total_size // self.batch_size):
            for key in keys:  # url
                for batch in range(self.batch_size):
                    if remain_json[key] == 100:
                        break
                    directory_name = make_batch_dir(self.save_path, key, epoch, batch)
                    logger.info('Batch - [%d/%d] - Epoch - [%d/%d] - URL - %s' % (batch, self.batch_size, epoch, self.total_size // self.batch_size, key))
                    self.sniffer.sniff(key, directory_name)
                    remain_json[key] += 1
                    time.sleep(self.sleep_between_batch)
                time.sleep(self.sleep_between_url)
            time.sleep(self.sleep_between_epoch)