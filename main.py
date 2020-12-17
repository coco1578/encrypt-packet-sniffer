import os
import time
import argparse
import configparser
import numpy as np

from log import logger
from sniffer import Sniffer
from tordriver import TorBrowser
from utils import make_batch_dir
from utils import make_sequence_dir


def parse_args():

    parser = argparse.ArgumentParser()
    parser.add_argument('--url', '-u', type=str, help='url list want to get a encrypted packet')
    parser.add_argument('--batch', '-b', type=bool, help='If true sniff url list using batch size else just loop num argument')
    parser.add_argument('--num', '-n', type=int, help='If batch is false, this argument must need to sniff website')

    args = parser.parse_args()

    # check num argument exists when batch args is False
    if args.batch is False and args.num is None:
        parser.print_help()
        exit(1)

    return args


def run(config, args):

    url_list = np.loadtxt(args.url, delimiter='\n', dtype=str)
    url_list = np.random.permutation(url_list).tolist() # Shuffle url list
    sniff_done_dict = {url: 0 for url in url_list} # Record sniff result

    browser_path = config['TorBrowser']['browser_path']
    socks_port = int(config['TorBrowser']['socks_port'])
    control_port = int(config['TorBrowser']['control_port'])
    headless = config['TorBrowser'].getboolean('headless')
    executable_path = config['TorBrowser']['executable_path']
    capture_screen = config['TorBrowser']['capture_screen']

    # default save_path is current_directory/result
    # batch directory save_path/url/epoch/batch
    # sequence directory save_path/url/epoch
    save_path = config['CaptureProgram']['save_path']
    save_path = os.path.join(os.getcwd(), save_path)

    batch_size = int(config['Batch']['batch_size'])
    total_size = int(config['Batch']['total_size'])
    sleep_batch = int(config['Batch']['sleep_batch'])
    sleep_url = int(config['Batch']['sleep_url'])
    sleep_epoch = int(config['Batch']['sleep_epoch'])

    tor_driver = TorBrowser(browser_path=browser_path, socks_port=socks_port, executable_path=executable_path, control_port=control_port, headless=headless)
    sniffer = Sniffer(tbb_driver=tor_driver, config=config, capture_screen=capture_screen, sniff_done_dict=sniff_done_dict)

    if args.batch:
        run_batch(sniffer, batch_size, total_size, url_list, save_path, sleep_batch, sleep_url, sleep_epoch)
    else:
        num_of_repeat = args.num
        run_sequence(sniffer, url_list, num_of_repeat, save_path, sleep_batch, sleep_epoch)


def run_batch(sniffer, batch_size, total_size, url_list, save_path, sleep_batch, sleep_url, sleep_epoch):

    logger.info('Sniff using batch')
    for epoch in range(total_size // batch_size): # epoch
        for url in url_list:
            for batch in range(batch_size):
                directory_name = make_batch_dir(save_path, url, epoch, batch)
                logger.info('Batch - [%d/%d] - Epoch - [%d/%d] - URL - %s' % (batch, batch_size, epoch, total_size // batch_size, url))
                sniffer.sniff(url, directory_name)
                time.sleep(sleep_batch)
            time.sleep(sleep_url)
        time.sleep(sleep_epoch)


def run_sequence(sniffer, url_list, num_of_repeat, save_path, sleep_batch, sleep_epoch):

    logger.info('Sniff using sequence')
    for epoch in range(num_of_repeat):
        for url in url_list:
            directory_name = make_sequence_dir(save_path, url, epoch)
            logger.info('Epoch - [%d/%d] - URL - %s' % (epoch, num_of_repeat, url))
            sniffer.sniff(url, directory_name)
            time.sleep(sleep_batch)
        time.sleep(sleep_epoch)

    return 0


def main():

    logger.info("Sniffing Program start")

    config = configparser.ConfigParser()
    config.read('config.ini')
    logger.info('Parse config.ini')

    args = parse_args()
    logger.info('Parse argument')
    run(config, args)


if __name__ == '__main__':

    main()
