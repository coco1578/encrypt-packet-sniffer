import os

from selenium import webdriver
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary
from selenium.webdriver.firefox.firefox_profile import FirefoxProfile
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions
from stem.process import launch_tor_with_config
from http.client import CannotSendRequest


class TorBrowser:
    '''
    Refactoring for 2020 12 version of Tor Browser Bundle
    '''
    def __init__(self, browser_path, binary_path=None, profile_path=None, executable_path=None, socks_port=9050, control_port=9051, extensions=None, capabilities=None, headless=False):

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

        self.profile = None
        self.binary = None # firefox
        self.tor_binary = None # tor binary
        self.options = None
        self.tor_process = None
        self.webdriver = None

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
        # tor-browser_en-US/Browser/TorBrowser/Tor/tor
        self.tor_binary = os.path.join(self.browser_path, os.path.join('Browser', os.path.join('TorBrowser', os.path.join('Tor', 'tor'))))
        # tor-browser_en-US/Browser/TorBrowser/Data/Tor/torrc-defaults
        self.torrc = os.path.join(self.browser_path, os.path.join('Browser', os.path.join('TorBrowser', os.path.join('Data', os.path.join('Tor', 'torrc-defaults')))))

    def _init_profile(self):

        update_preference = self.profile.set_preference
        update_preference('browser.startup.page', '0')
        update_preference('browser.startup.homepage', 'about:newtab')
        update_preference('extensions.torlauncher.promp_at_startup', 0)
        update_preference('webdriver.load.strategy', 'normal')
        update_preference('app.update.enabled', False)
        update_preference('extensions.torbutton.versioncheck_enabled', False)
        update_preference('extensions.torbutton.prompted_language', True)
        update_preference('network.proxy.socks_port', self.socks_port)
        update_preference('extensions.torbutton.socks_port', self.socks_port)
        update_preference('extensions.torlauncher.control_port', self.control_port)
        update_preference('extensions.torlauncher.start_tor', True)
        update_preference('extensions.torbutton.block_dis', False)
        update_preference('extensions.torbutton.custom.socks_host', '127.0.0.1')
        update_preference('extensions.torbutton.custom.socks_port', self.socks_port)
        update_preference('extensions.torbutton.inserted_button', True)
        update_preference('extensions.torbutton.launch_warning', False)
        update_preference('privacy.spoof_english', 2)
        update_preference('extensions.torbutton.loglevel', 2)
        update_preference('extensions.torbutton.logmethod', 0)
        update_preference('extensions.torbutton.settings_method', 'custom')
        update_preference('extensions.torbutton.use_privoxy', False)
        update_preference('extensions.torlauncher.control_port', self.control_port)
        update_preference('extensions.torlauncher.loglevel', 2)
        update_preference('extensions.torlauncher.logmethod', 0)
        update_preference('extensions.torlauncher.prompt_at_startup', False)

        self.profile.update_preferences()

    def _init_extensions(self):

        if self.extensions is not None:
            for extension in self.extensions:
                self.profile.add_extension(extension)

    def _init_capabilities(self):

        if self.capabilities is None:
            self.capabilities = {"marionette": True, "capabilities": {"alwaysMatch": {"moz:firefoxOptions": {"log": {"level": "info"}}}}}

    def _init_binary(self):

        self.binary = FirefoxBinary(firefox_path=self.binary_path)
        self.binary.add_command_line_options('--class', '"Tor Browser"')

    def _init_options(self):

        if self.headless is True:
            self.options = Options()
            self.options.headless = self.headless

    def _init_webdriver(self):

        self.tor_process = launch_tor_with_config(config=self.torrc, tor_cmd=self.tor_binary)
        self.webdriver = webdriver.Firefox(firefox_profile=self.profile, firefox_binary=self.binary, timeout=60, capabilities=self.capabilities, executable_path=self.executable_path, options=self.options)

    def connect_url(self, url):

        self.webdriver.get(url)
        WebDriverWait(self.webdriver, timeout=30).until(expected_conditions.presence_of_element_located((By.TAG_NAME, 'body')))

    def close(self):

        try:
            self.webdriver.quit()
        except (CannotSendRequest, AttributeError, WebDriverException):
            try:
                if self.webdriver.w3c:
                    self.webdriver.service.stop()
                if hasattr(self.webdriver, "binary"):
                    self.binary.kill()
            except Exception as e:
                print("[WARNING] Exception while close Tor Browser: %s", e)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):

        self.close()


# For testing
if __name__ == '__main__':

    test_url = 'https://check.torproject.org'
    tor_browser = TorBrowser(browser_path='/home/parallels/tor-browser_en-US')
    tor_browser.connect_url(test_url)

