import os
import time
import subprocess

from log import logger


class Capture:

    def __init__(self, config):

        assert config is not None

        self.config = config

        self.packet_capture_process = None # subprocess.Popen()
        self.packet_capture_program = None
        self.packet_capture_filter = None
        self.save_path = None
        self.duration = None
        self.file_size = None
        self.network_adaptor = None
        self.command = None

        self.process = None

        self._init_capture_setup()

    def _init_capture_setup(self):

        self.packet_capture_program = self.config['CaptureProgram']['program']
        self.packet_capture_filter = self.config['CaptureProgram']['filter']
        self.save_path = self.config['CaptureProgram']['save_path']
        self.duration = self.config['CaptureProgram']['duration']
        self.file_size = self.config['CaptureProgram']['file_size']
        self.network_adaptor = self.config['CaptureProgram']['adaptor']

    def init_capture_program(self, save_path):

        # Will be support tcpdump & tshark
        if save_path is not None:
            self.save_path = os.path.join(save_path, time.strftime('%Y-%m-%d_%H_%M_%S'))

        self.command = '{} -a duration:{} -a filesize:{} -i {} -s 0 -f \'{}\' -w {}'.format(self.packet_capture_program, self.duration, self.file_size, self.network_adaptor, self.packet_capture_filter, self.save_path) # dumpcap
        logger.info('Packet Capture command %s' % self.command)

    def start(self):

        try:
            self.process = subprocess.Popen(self.command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
            logger.info('Dumpcap process start')
        except subprocess.SubprocessError:
            self.stop()
            logger.error('Subprocess error')
        except subprocess.CalledProcessError:
            self.stop()
            logger.error('Call dumpcap error')

    def stop(self):

        self.process.kill()
        logger.info('Dumpcap process stop')

    def remove(self):

        remove_command = 'rm -rf %s' % self.save_path
        remove_process = subprocess.Popen(remove_command, stdout=subprocess.PIPE)
