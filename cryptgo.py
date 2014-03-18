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

kill_processes_using_ports(['8071','8090'])
kill_processes_using_ports(['8071','8090'])

if __name__ == '__main__':
    #8071 appears in another file...
    #the first miner is for finding blocks. the second miner is for playing go and for talking to the network.
#    blockchain.mine(my_pubkey, config.peers_list, 0)
#    listener.main(8071)
    todo=[[blockchain.mine, 
           (my_pubkey, ['http://localhost:8071/info?{}'], 200000, '_miner')],
          [listener.main, (8071, )],
          [blockchain.mine, (my_pubkey, config.peers_list, 0)],
          [gui.main, (8090, config.brain_wallet)]
          ]
    for i in todo:
        t = threading.Thread(target=i[0], args = i[1])
#        t.daemon = True
        t.start()

