##INSTALL=======

You need to have python installed: (linux and mac probably already have python)

http://www.python.org/download/

##RUN======

you need this running:

python cryptgo.py


To look at the gui, send you browser to: 

http://localhost:8090

You own at least 1/4 of one block reward in order to play go. Black is the one who pays this, and black gets it back when the game is over. 


####You can play go now. You don't have to read below this line. It is only for people who want to make money.====

##Mining go-coins===

####miner optimizations

You could delete print statements in the code, or you could re-organize the steps I do things in.
someone needs to port cgminer for our situation.

##External IP will allow you to route transactions around the network====

*An easy way to do this is by creating a TOR .onion url. 

*Otherwise, you can use a static or dynamic IP which is accessible from the internet. Any port should be fine.

*To start doing it: 

     python quick_listen.py

*Tell zack-bitcoin about your (IP or .onion) and port, and he will hard-code it into CryptGo

*You should be able to control relevent ports from in the config file.

*Large amounts of CryptGo will be awarded on a donation basis according to the percentage of the network that you support.

Warning for TOR users! sometimes TOR's default IPs are 9050/9051, other times they are 9150/9151

##Windows TOR configuration, if you don't want to use your external IP=====

Be sure to get a version of TOR which includes vidalia. The vidalia gui interface is used to configure ports and create your .onion url.

You will need:

https://www.torproject.org/projects/torbrowser.html.en

http://www.privoxy.org/

privoxy config file needs a line uncommented. In my config file, the line was at about line number 1300 or so, it says:

        forward-socks5   /               127.0.0.1:9050 .

##Linux TOR configuration, if you don't want to use your external IP=====

You will need:

https://www.torproject.org/projects/torbrowser.html.en

http://www.privoxy.org/

torrc needs to be configured so that you have an onion url.

The onion url is used to share blocks between the miners.
        SocksListenAddress 127.0.0.1
        SocksPort 9050
        ControlPort 9051
        HiddenServiceDir /location/of/file/that/contains/this/readme
        HiddenServicePort 80 127.0.0.1:8071

privoxy config file needs a line uncommented. In my config file, the line was at about line number 1300 or so, it says:

        forward-socks5   /               127.0.0.1:9050 .


##Aspects of the program I especially want advice on=====

If you have ideas about these things, or if you want me to hurry up with one of them, or if you want to add an idea to this list, please email me zack.bitcoin at gmail dot com.

####javascript html style

*a web wallet so that we don't have to install python

*an easy way to start a game with a handicap. CryptGo already supports this, we just need a user-interface. This interface should also allow betting money against the other person.

####alt-coin issues

*port cgminer for CryptGo, to protect the system from 51%

*maybe we should merge-mine against a bigger currency.

*NatPNP/UPNP for automatic port forwarding so that more people can help connect the network together.

*automagically rank peers, so that you don't waste time talking to poorly connected peers. Also for filtering out adversaries.

*automagically share .onion or IP with peers.

####go 

*the ability to bet on games.

*the ability to re-play old games

*experation date (opposite of nlocktime) so that your partner wont start the game hours later than you had expected.

*nlocktime, to schedule a game in the future.
