import os
import time
import subprocess

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver import DesiredCapabilities
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary
from selenium.webdriver.firefox.firefox_profile import FirefoxProfile

from http.client import CannotSendRequest

from log import logger


class TorController:

    def __init__(self):

        self.service = 'tor'

        self._init_tor()

    def _init_tor(self):

        result = self._check_tor_is_run()
        if result == 'active':
            self.restart()
        elif result == 'inactive':
            self.start()

    def _check_tor_is_run(self):

        process = subprocess.Popen(['systemctl', 'is-active', self.service], stdout=subprocess.PIPE)
        output, error = process.communicate()
        output = output.decode('utf-8').strip()

        if output == 'inactive':
            return 'inactive'
        elif output == 'active':
            return 'active'
        elif error is not None:
            return 'error'
        else: # unknown error
            return 'error'

    def start(self):

        process = subprocess.Popen(['systemctl', 'start', self.service], stdout=subprocess.PIPE)
        output, error = process.communicate()
        if output == b'':
            logger.info('Tor process start')
            return True
        else:
            logger.warning('Tor process cannot stop. Program will be Exit.')
            # return False
            exit(1)

    def stop(self):

        process = subprocess.Popen(['systemctl', 'stop', self.service], stdout=subprocess.PIPE)
        output, error = process.communicate()
        if output == b'':
            logger.info('Tor process stop')
            return True
        else:
            logger.warning('Tor process cannot stop')
            return False

    def restart(self):

        process = subprocess.Popen(['systemctl', 'restart', self.service], stdout=subprocess.PIPE)
        output, error = process.communicate()
        if output == b'':
            logger.info('Tor process restart')
            return True
        else:
            logger.warning('Tor process cannot restart. Program will be Exit.')
            # return False
            exit(1)


class TorBrowser:
    '''
    Refactoring for 2020 12 version of Tor Browser Bundle
    '''
    def __init__(self, browser_path, binary_path=None, profile_path=None, executable_path=None, socks_port=9050, control_port=9051, extensions=None, capabilities=None, headless=False, capture_screen=False, url=None):

        assert browser_path is not None

        self.browser_path = browser_path
        self.binary_path = binary_path
        self.profile_path = profile_path
        self.executable_path = executable_path

        self.socks_port = socks_port
        self.control_port = control_port
        self.extensions = extensions
        self.capabilities = capabilities
        self.headless = headless
        self.capture_screen = capture_screen
        self.url = url

        self.profile = None
        self.binary = None # firefox
        self.options = None
        self.webdriver = None
        self.tor_controller = TorController() # Start tor process..

        self._initialize()

    def _initialize(self):

        self._init_browser()
        self.profile = FirefoxProfile(self.profile_path)
        self._init_profile()
        self._init_extensions()
        self._init_capabilities()
        self._init_binary()
        self._init_options()
        self._init_webdriver()

    def _init_browser(self):

        if self.binary_path is None:
            # tor-browser_en-US/Browser/firefox
            self.binary_path = os.path.join(self.browser_path, os.path.join('Browser', 'firefox'))
        if self.profile_path is None:
            # tor-browser_en-US/Browser/TorBrowser/Data/Browser/profile.default
            self.profile_path = os.path.join(self.browser_path, os.path.join('Browser', os.path.join('TorBrowser', os.path.join('Data', os.path.join('Browser', 'profile.default')))))

    def _init_profile(self):

        self.profile.set_preference('browser.startup.page', '0')
        self.profile.set_preference('browser.startup.homepage', 'about:newtab')
        self.profile.set_preference('network.proxy.type', 1)
        self.profile.set_preference('network.proxy.socks', '127.0.0.1')
        self.profile.set_preference('network.proxy.socks_port', self.socks_port)
        self.profile.set_preference('extensions.torlauncher.promp_at_startup', 0)
        self.profile.set_preference('network.http.use-cache', False)
        self.profile.set_preference('webdriver.load.strategy', 'conservative')
        self.profile.set_preference('extensions.torlauncher.start_tor', False)
        self.profile.set_preference('extensions.torbutton.versioncheck_enabled', False)
        self.profile.set_preference('permissions.memory_only', False)
        # update_preference('webdriver.load.strategy', 'normal')
        # update_preference('app.update.enabled', False)
        # update_preference('extensions.torbutton.versioncheck_enabled', False)
        # update_preference('extensions.torbutton.prompted_language', True)
        # update_preference('extensions.torbutton.socks_port', self.socks_port)
        # update_preference('extensions.torlauncher.control_port', self.control_port)
        # update_preference('extensions.torlauncher.start_tor', True)
        # update_preference('extensions.torbutton.block_dis', False)
        # update_preference('extensions.torbutton.custom.socks_host', '127.0.0.1')
        # update_preference('extensions.torbutton.custom.socks_port', self.socks_port)
        # update_preference('extensions.torbutton.inserted_button', True)
        # update_preference('extensions.torbutton.launch_warning', False)
        # update_preference('privacy.spoof_english', 2)
        # update_preference('extensions.torbutton.loglevel', 2)
        # update_preference('extensions.torbutton.logmethod', 0)
        # update_preference('extensions.torbutton.settings_method', 'custom')
        # update_preference('extensions.torbutton.use_privoxy', False)
        # update_preference('extensions.torlauncher.control_port', self.control_port)
        # update_preference('extensions.torlauncher.loglevel', 2)
        # update_preference('extensions.torlauncher.logmethod', 0)
        # update_preference('extensions.torlauncher.prompt_at_startup', False)

        self.profile.update_preferences()

    def _init_extensions(self):

        if self.extensions is not None:
            for extension in self.extensions:
                self.profile.add_extension(extension)

    def _init_capabilities(self):

        if self.capabilities is None:
            self.capabilities = DesiredCapabilities.FIREFOX
            self.capabilities.update({'handlesAlerts': True, 'databaseEnabled': True, 'javascriptEnabled': True, 'browserConnectionEnabled': True})

    def _init_binary(self):

        self.binary = FirefoxBinary(firefox_path=self.binary_path)
        self.binary.add_command_line_options('--class', '"Tor Browser"')

    def _init_options(self):

        if self.headless is True:
            self.options = Options()
            self.options.headless = self.headless

    def _init_webdriver(self):

        self.webdriver = webdriver.Firefox(firefox_profile=self.profile, firefox_binary=self.binary, timeout=60, capabilities=self.capabilities, executable_path=self.executable_path, options=self.options)

    def connect_url(self, url):

        self.webdriver.get(url)
        WebDriverWait(self.webdriver, timeout=30).until(expected_conditions.presence_of_element_located((By.TAG_NAME, 'body')))

    def close(self):
        try:
            self.tor_controller.stop()
            self.webdriver.quit()
        except CannotSendRequest:
            logger.error('CannotSendRequest while quitting TorBrowserDriver')
            self.binary.kill()
        except Exception as e:
            logger.error('Exception while quitting TorBrowserDriver', e)

    def init_canvas_permission(self, url):
        '''
        Create a permission DB and add exception for the canvas image extraction.
        Otherwise screenshots taken by Selenium will be just blank images due to
        canvas fingerprinting defense in Tor Browser Bundle.
        '''
        import sqlite3
        from tld import get_tld

        connection = sqlite3.connect
        permission_db = connection(os.path.join(self.profile_path, 'permissions.sqlite'))
        cursor = permission_db.cursor()

        # http://mxr.mozilla.org/mozilla-esr31/source/build/automation.py.in
        cursor.execute("PRAGMA user_version=3")
        cursor.execute("""CREATE TABLE IF NOT EXISTS moz_hosts (
            id INTEGER PRIMARY KEY,
            host TEXT,
            type TEXT,
            permission INTEGER,
            expireType INTEGER,
            expireTime INTEGER,
            appId INTEGER,
            isInBrowserElement INTEGER)""")

        domain = get_tld(url)
        logger.debug('Adding canvas/extractData permission for %s' % domain)
        query = """INSERT INTO 'moz_hosts' VALUES (NULL, '%s', 'canvas/extractData', 1, 0, 0, 0, 0);""" % domain
        cursor.execute(query)
        permission_db.commit()
        cursor.close()

    def take_screenshot(self, save_path):

        if save_path is not None:
            save_path = os.path.join(save_path, 'screenshot.png')
        else:
            save_path = 'screenshot.png'

        self.webdriver.get_screenshot_as_file(save_path)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


# For testing
if __name__ == '__main__':

    test_url = 'https://check.torproject.org'
    tor_browser = TorBrowser(browser_path='/home/parallels/tor-browser_en-US', executable_path='./geckodriver')
    tor_browser.connect_url(test_url)

