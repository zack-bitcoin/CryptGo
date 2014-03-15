import blockchain, config
import pybitcointools as pt
my_privkey=pt.sha256(config.brain_wallet)
my_pubkey=pt.privtopub(my_privkey)
if __name__ == '__main__':
    blockchain.mine(my_pubkey, config.peers_list)
#out=blockchain.peer_check_all(peers, state)
