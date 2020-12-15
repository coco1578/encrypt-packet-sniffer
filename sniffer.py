import time

from log import logger
from packet_capture import Capture


class Sniffer:

    def __init__(self, tbb_driver, config, capture_screen):
        assert tbb_driver is not None

        self.tbb_driver = tbb_driver
        self.config = config
        self.capture_screen = capture_screen
        self.packet_capture_process = Capture(config)

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

            if self.capture_screen is True:
                self.tbb_driver.init_canvas_permission(url)
                self.tbb_driver.take_screenshot(url, save_path)

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