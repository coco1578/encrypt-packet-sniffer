# encrypt-packet-sniffer 

## Description

---

Sniffer for sniffing network packets from the anonymous network **`Tor browser`**

## Requirement Program and Package

---

Support OS (Ubuntu 16.04, 18.04, 20.04) *not test other linux distrubution*

Tor==0.4.2.7

Tor Browser Bundle==10.0.5 [Download Link](https://archive.torproject.org/tor-package-archive/torbrowser/10.0.5/tor-browser-linux64-10.0.5_en-US.tar.xz)

geckodriver==0.28.0 [Download Link]([https://github.com/mozilla/geckodriver/releases/download/v0.28.0/geckodriver-v0.28.0-linux64.tar.gz](https://github.com/mozilla/geckodriver/releases/download/v0.28.0/geckodriver-v0.28.0-linux64.tar.gz))

python3.6
- selenium==3.141.0
- tld==0.12.3
- numpy==1.19.4

Wireshark

## Setup

---
1. Install Wireshark
    - In terminal, enter this code to chagne wireshark rule `sudo dpkg-reconfigure wireshark-common`
    - Select Yes.
    - ![Wireshark Image](https://user-images.githubusercontent.com/25210326/102443317-c07b9380-4069-11eb-9922-d7597df00e9e.png)
    - In terminal, enter this code `sudo usermod -a -G wireshark $USER`
    - Reboot Ubuntu Desktop

2. Download Tor
    - `sudo apt-get install tor`
    - Uncomment SocksPort, ControlPort in /etc/tor/torrc file.
    - <u>**This SocksPort and ControlPort should be matched with config.ini socks_port, control_port**</u>

3. Download the Tor Browser Bundle
    - extract it whatever you want
    - remember the path of the Tor Browser Bundle
    - In my case, `$HOME/tor-browser_en-US`

4. Download the geckodriver to control Tor Browser Bundle
    - After extract it, you can see there is a `geckodriver` file.
    - In terminal enter this code to use it everywhere. `mv geckodriver /usr/local/bin`

5. clone `SnifferyEncryptedPacket` repository
    - `git clone https://github.com/coco1578/SnifferEncryptedPacket`

6. Configure Ubuntu environment
    - **To capture pure encyrpted packet** we need to remove background network traffic.
    - [how to disable ubuntu background network traffic](https://help.ubuntu.com/community/AutomaticConnections)
    - Recommend to change MTU size 1500 `sudo ifconfig <network interface> mut 1500`

**Important Setup (Only works on remote session)**
- When you are using remote session, Add `export DISPLAY=:0` in `bashrc`.


## Usage

---
1. Before we start to capture encrypted packets, We should change `config.ini` in the repository.
2. `config.ini` looks like this.
~~~ini
[TorBrowser]
browser_path=path of tor_browser bundle. In my case /user/home/administrator/tor-browser_en-US
binary_path=you can skip this one. This is not necessary option if you insert browser_path above.
profile_path=you can skip this one. This is not necessary option if you insert browser_path above.
executable_path=geckodriver path. If you do not mv geckodriver to /usr/local/bin then insert the path of geckodriver


[CaptureProgram]
filter=dumpcap filter when capture the network traffic 
save_path=directory name when the captured file saved.
duration=maximum duration when capture the network traffic
adaptor=network adaptor

[Batch]
batch_size=number of batches connecting url
total_size=total size per url
sleep_batch=sleep between batch
sleep_url=sleep between url
sleep_epoch=sleep between epoch

[Logger]
file_name=log file name if log type is file or both 
log_type=logging type (console, file, both)
log_level=log level(debug, info, error, etc..)
~~~

3. Prepare URL list text file. For instance, example.txt
~~~
https://check.torproject.org
https://www.google.com
~~~

4. Run the `main.py`
Batch mode: `python3 main.py -u example.txt -b True`
Sequence mode: `python3 main.py -u example.txt -b False`

5. See the captured packet in the `save_path` folder


## Known Issue
---
When you run the program. **You need to enter root password to start tor service**

## Will be updated

---
* Make a shell scrpit to setup this sniffer program.
* <del>Support headless mode.<del/>
* Support continuation sniffing if exeception occur.
