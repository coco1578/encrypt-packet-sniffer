import json
import argparse
import configparser
import numpy as np

from log import logger
from runner import Runner
from sniffer import Sniffer
from tordriver import TorBrowser


def parse_args():

    parser = argparse.ArgumentParser()
    parser.add_argument('--url', '-u', type=str, help='url list want to get a encrypted packet')
    parser.add_argument('--batch', '-b', type=bool, help='If true sniff url list using batch size else just loop num argument')
    parser.add_argument('--num', '-n', type=int, help='If batch is false, this argument must need to sniff website')
    parser.add_argument('--remain', '-r', type=bool, help='Recapture the remaining website.')
    parser.add_argument('--json', '-j', type=str, help='remain json path')

    args = parser.parse_args()

    # check num argument exists when batch args is False
    if args.batch is False and args.num is None:
        parser.print_help()
        exit(1)

    # check remain and json arguemnt
    if args.remain is True and args.json is None:
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

    tor_driver = TorBrowser(browser_path=browser_path, socks_port=socks_port, executable_path=executable_path, control_port=control_port, headless=headless)
    sniffer = Sniffer(tbb_driver=tor_driver, config=config, capture_screen=capture_screen, sniff_done_dict=sniff_done_dict)
    runner = Runner(snifer=sniffer, config=config, url_list=url_list)

    if args.batch is True:
        runner.batch()
    elif args.batch is False:
        num_of_repeat = args.num
        runner.sequence(num_of_repeat)
    elif args.remain is True:
        try:
            remain_json = open(args.json)
            remain_json = json.load(remain_json)
        except:
            logger.error('File not existed')
            exit(1)
        runner.remain(remain_json)
    else:
        logger.error('Wrong argument is inserted. Please read argument help.')
        exit(1)


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
