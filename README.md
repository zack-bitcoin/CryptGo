##INSTALL==WARNING!!! This currency will be rebooted sometime in the next 48 hours. the money is all worthless. I will put money into the brainwallet: "password" for experimentation.====

You need to have python installed: (linux and mac probably already have python)

http://www.python.org/download/

##RUN======

to download the chain, and to broadcast your moves, you need this running:

python cryptgo.py

To play go, you need the gui:

python gui.py



To look at the gui, send you browser to: 

http://localhost:8090

You own at least 1/4 of one block reward. Black is the one who pays this, and black gets it back when the game is over. 

You can get free coins by emailing zack.bitcoin at gmail dot com and he will send you some.


####You can play go now. You don't have to read below this line. It is only for people who want to make money.====

##Mining go-coins===

In the config file, change the number "hashes_till_check" to a positive integer. For my computer, numbers between 10 and 50 seem to work pretty well for mining. Optimal number depends a lot on connection speed, and the power of your CPU.
When I am playing go, I keep this number between 0 and 5. I can see moves more quickly that way.

If the number is too high, then all the blocks you mine will get orphaned. If the number is too low, then you will waste all your time talking to other miners instead of mining blocks.

When the system is stable, it should take 1 minute per block. In this situation you might want to experiment with bigger numbers like 60 for faster mining speed.

When lots of people are joining the system, block time could only take 20 seconds, or less. In this situation, you want a very low number, like 5, otherwise you will only mine orphans.

##External IP will allow you to route transactions around the network====

*An easy way to do this is by creating a TOR .onion url. 

*Otherwise, you can use a static or dynamic IP which is accessible from the internet. Any port should be fine.

*To start doing it: 

     python quick_listen.py

*Tell zack-bitcoin about your (IP or .onion) and port, and he will hard-code it into the gocoin program.

*You should be able to control relevent ports from in the config file.

*Large amounts of gocoin will be awarded on a donation basis according to the percentage of the network that you support.

##Using external IP===

port numbers are controlled by the config.py file.

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

-javascript html style

*auto-refresh the game whenever transactions.db changes, so you don't have to hit the refresh button over and over. (I think a solution to this will involve javascript.)

*a web wallet so that we don't have to install python

*an easy way to start a game with a handicap (CryptGo already supports this, we just need a user-interface.)

-alt-coin issues

*port cgminer for CryptGo, to protect the system from 51%

*NatPNP/UPNP for automatic port forwarding so that more people can help connect the network together.

-go 

*The ability to bet on other people's games.

*the ability to re-play old games

*experation date (opposite of nlocktime) so that your partner wont start the game hours later than you had expected.

*nlocktime, to schedule a game in the future.
