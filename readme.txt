======INSTALL======
You need these 3rd party programs:
http://www.python.org/download/

These programs should be included in the install file, so you probably don't have to download them. here are their websites:
http://json-rpc.org/wiki/python-json-rpc (which may require http://bazaar.canonical.com/en/ )
https://github.com/vbuterin/pybitcointools


======RUN======
To send your mined blocks to the network, you need listener running:
python quick_listen.py

To mine blocks and to download the chain, you need the miner running:
python quick_mine.py

To play go, you need the gui:
python go_gui.py

To look at the gui, send you browser to: 
http://localhost:8090



===Optional: Use TOR===
You also need:
https://www.torproject.org/projects/torbrowser.html.en
http://www.privoxy.org/

torrc needs to be configured so that you have an onion url.
The onion url is used to share blocks between the miners.
---Add these lines to your torrc---
SocksListenAddress 127.0.0.1
SocksPort 9050
ControlPort 9051
HiddenServiceDir /location/of/file/that/contains/this/readme
HiddenServicePort 80 127.0.0.1:8071
-----------------------------------


privoxy config file needs a line uncommented. In my config file, the line
was at about line number 1300 or so, it says:
        forward-socks5   /               127.0.0.1:9050 .
