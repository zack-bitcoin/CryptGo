======INSTALL======
You need to have python installed: (linux and mac probably already have python)
http://www.python.org/download/

======RUN======
to download the chain, and to broadcast your moves, you need this running:
python gocoin.py

To play go, you need the gui:
python gui.py

To look at the gui, send you browser to: 
http://localhost:8090
It does not cost gocoin to play, but you can only play if you own at least 25000 gocoins. (1/4 of the block reward given out every 60 seconds) 
You can get them for free by emailing zack.bitcoin at gmail dot com and he will send you some to test it out.
You can play with zack-bitcoin for free.

=====You can play go now. You don't have to read below this line. It is only for people who want to make money.====

===Mining go-coins===
In the config file, change the number "hashes_till_check" to a positive integer. For my computer, numbers between 60 and 300 seem to work pretty well. Optimal number depends a lot on connection speed, and the power of your CPU.

===External IP will allow you to route transactions around the network====
*An easy way to do this is by creating a TOR .onion url. 
*Otherwise, you can use a static or dynamic IP which is accessible from the internet. Any port should be fine.
*To start doing it: 
     python quick_listen.py
*Tell zack-bitcoin about your (IP or .onion) and port, and he will hard-code it into the gocoin program.
*You should be able to control relevent ports from in the config file.
*Large amounts of gocoin will be awarded on a donation basis according to the percentage of the network that you support.

===Using external IP===
port numbers are controlled by the config.py file.

##Warning for TOR users! sometimes TOR's default IPs are 9050/9051, other times they are 9150/9151
=====Windows TOR configuration, if you don't want to use your external IP=====
Be sure to get a version of TOR which includes vidalia. The vidalia gui interface is used to configure ports and create your .onion url.
You will need:
https://www.torproject.org/projects/torbrowser.html.en
http://www.privoxy.org/
privoxy config file needs a line uncommented. In my config file, the line was at about line number 1300 or so, it says:
        forward-socks5   /               127.0.0.1:9050 .

=====Linux TOR configuration, if you don't want to use your external IP=====
You will need:
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
privoxy config file needs a line uncommented. In my config file, the line was at about line number 1300 or so, it says:
        forward-socks5   /               127.0.0.1:9050 .


