import blockchain, config, threading, gui, listener, os, subprocess, re
import pybitcointools as pt
my_privkey=pt.sha256(config.brain_wallet)
my_pubkey=pt.privtopub(my_privkey)

def kill_processes_using_ports(ports):
    popen = subprocess.Popen(['netstat', '-lpn'],
                             shell=False,
                             stdout=subprocess.PIPE)
    (data, err) = popen.communicate()
    pattern = "^tcp.*((?:{0})).* (?P<pid>[0-9]*)/.*$"
    pattern = pattern.format(')|(?:'.join(ports))
    prog = re.compile(pattern)
    for line in data.split('\n'):
        match = re.match(prog, line)
        if match:
            pid = match.group('pid')
            subprocess.Popen(['kill', '-9', pid])
try:
    kill_processes_using_ports([str(config.listen_port), str(config.gui_port)])
    kill_processes_using_ports([str(config.listen_port), str(config.gui_port)])
except:
    #so windows doesn't die
    pass
if __name__ == '__main__':
    #the first miner is for finding blocks. the second miner is for playing go and for talking to the network.
    todo=[[blockchain.mine, 
           (my_pubkey, ['http://localhost:'+str(config.listen_port)+'/info?{}'], config.hashes_till_check, '_miner')],
          [listener.main, (config.listen_port, )],
          [blockchain.mine, (my_pubkey, config.peers_list, 0)],
          [gui.main, (config.gui_port, config.brain_wallet)]
          ]
    for i in todo:
        t = threading.Thread(target=i[0], args = i[1])
#        t.daemon = True
        t.start()

