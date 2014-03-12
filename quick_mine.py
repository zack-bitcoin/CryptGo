import blockchain
import pybitcointools as pt
my_privkey=pt.sha256("0")
my_pubkey=pt.privtopub(my_privkey)
peers_list=['http://zycr7u4ykb7kox7p.onion/info?{}',
            'http://gpvn7naihr4jk6dd.onion/info?{}',
            'http://fnsxouwikizbpqtq.onion/info?{}']#add friends!!
if __name__ == '__main__':
    blockchain.mine(my_pubkey, peers_list)
#out=blockchain.peer_check_all(peers, state)
