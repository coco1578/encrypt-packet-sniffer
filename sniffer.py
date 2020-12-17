import os
import time
import json

from log import logger
from packet_capture import Capture


class Sniffer:

    def __init__(self, tbb_driver, config, capture_screen, sniff_done_dict):
        assert tbb_driver is not None

        self.tbb_driver = tbb_driver
        self.config = config
        self.capture_screen = capture_screen
        self.packet_capture_process = Capture(config)
        self.json_save_path = config['CaptureProgram']['save_path']
        self.sniff_done_dict = sniff_done_dict
        self.json_file_name = os.path.join(self.json_save_path, time.strftime('%Y-%m-%d_%H_%M_%S') + '.json')

    def sniff(self, url, save_path): # sniff just one website

        logger.info('Sniffing starts')

        try:
            self.packet_capture_process.init_capture_program(save_path)

            # start sniff encrypted packet from browser
            start_time = time.time()
            self.packet_capture_process.start()
            self.tbb_driver.connect_url(url)
            self.packet_capture_process.stop()
            end_time = time.time()

            elasped_time = end_time - start_time
            logger.info('Capture packet %s times' % elasped_time)

            # Is this best way to save sniff done website..?
            self.sniff_done_dict[url] += 1
            with open(self.json_file_name, 'w') as fd:
                json.dump(self.sniff_done_dict, fd)

            if self.capture_screen is True:
                self.tbb_driver.init_canvas_permission(url)
                self.tbb_driver.take_screenshot(save_path)

        except KeyboardInterrupt:
            logger.info('Program stop')
            self.packet_capture_process.stop()
            self.packet_capture_process.remove()
            exit(1)

        except Exception as e:
            logger.error('Exception while sniffing. Remove captured packet')
            self.packet_capture_process.stop()
            self.packet_capture_process.remove()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.packet_capture_process.stop()