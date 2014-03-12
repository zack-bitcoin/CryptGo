import blockchain
import pybitcointools as pt
my_privkey=pt.sha256("0")
my_pubkey=pt.privtopub(my_privkey)
peers_list=['http://www.sbb.tc/info?{}',
            'http://162.243.13.112/info?{}',
            'http://fnsxouwikizbpqtq.onion/info?{}']#add friends!!
if __name__ == '__main__':
    blockchain.mine(my_pubkey, peers_list)
#out=blockchain.peer_check_all(peers, state)
