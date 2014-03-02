import string,cgi,time, json, random, copy, os, copy, urllib, go, urllib2
import pybitcointools as pt
import state_library
try:
    from jsonrpc import ServiceProxy
except:
    from bitcoinrpc import AuthServiceProxy as ServiceProxy       
#bitcoin = ServiceProxy("http://user:HkTlSzJkY7@127.0.0.1:8332/")
bitcoin=ServiceProxy("http://:hfjkdahflkjsdfa@127.0.0.1:8331/")#actually litecoin
genesis={'zack':'zack', 'length':-1, 'nonce':'22', 'sha':'00000000000'}
genesisbitcoin=523218-1220
#genesisbitcoin=516070#lazy, only wait 6 seconds per block.
chain=[genesis]
chain_db='chain.db'
transactions_database='transactions.db'

#I call my database appendDB because this type of database is very fast to append data to.
def load_appendDB(file):
    out=[]
    try:
        with open(file, 'rb') as myfile:
            a=myfile.readlines()
            for i in a:
                if i.__contains__('"'):
                    out.append(json.loads(i.strip('\n')))
    except:
        pass
    return out
def load_transactions():
    return load_appendDB(transactions_database)
def load_chain():
    current=load_appendDB(chain_db)
    if len(current)<1:
        return [genesis]
    if current[0]!=genesis:
        current=[genesis]+current
    return current
def reset_appendDB(file):
    open(file, 'w').close()
def reset_transactions():
    return reset_appendDB(transactions_database)
def reset_chain():
    return reset_appendDB(chain_db)
def push_appendDB(file, tx):
    with open(file, 'a') as myfile:
        myfile.write(json.dumps(tx)+'\n')
def add_transaction(tx):#to local pool
    print("ADDING A TRANSACTION")
    transactions=load_transactions()
#    print('tx: ' +str(tx))
    state=state_library.current_state()
    if verify_transactions(transactions+[tx], state)['bool']:
        if len(transactions)>3:
            error('here')
        push_appendDB(transactions_database, tx)
def chain_push(block):
    statee=state_library.current_state()    
    if new_block_check(block, statee):
        state=verify_transactions(block['transactions'], statee)
#        print('state: ' +str(state))
#        if statee['length']>=state['newstate']['length']:
#            error('hrer')
        state=state['newstate']
        state['length']+=1
        state['recent_hash']=block['sha']
        state_library.save_state(state)
        txs=load_transactions()
        reset_transactions()
        for tx in txs:
            add_transaction(tx)
        return push_appendDB(chain_db, block)
    else:
        return 'bad'
def chain_unpush():
    chain=load_chain()
    chain=chain[:-1]
    reset_chain()
    state=state_library.empty_state
    state_library.save_state(state)
    for i in chain:
        if i['length']>=0:
            chain_push(i)
    if len(chain)>len(load_chain()):
        print('chain: ' + str(chain))
        print('lchain: ' + str(load_chain()))
#        error('here')
def package(dic):
    return json.dumps(dic).encode('hex')
def unpackage(dic):
    try:
        return json.loads(dic.decode('hex'))
    except:
        print(dic)
        error('here')
def message2signObject(tx, keys):
    out=''
    for key in sorted(keys):
        if type(tx[key])==type([1,2]):
            string=str(key)+':'
            for i in tx[key]:
                string+=str(i)+','
        else:
            string=str(key)+':'+str(tx[key])+','
        out+=string
    return out
def difficulty(bitcoin_count, leng):
    def buffer(s, n):
        while len(s)<n:
            s='0'+s
        return s
#    hashes_required=int((10**60)*((2.0/3)**(float(bitcoin_count)-float(genesisbitcoin)-(float(leng)/10)))+1)#for bitcoin
    hashes_required=int((10**60)*((9.0/10)**(float(bitcoin_count)-float(genesisbitcoin)-(float(leng)/2.5)))+1)#for litcoin
#    hashes_required=int((10**60)*((9.0/10)**(float(bitcoin_count)-float(genesisbitcoin)-(float(leng)/25)))+1)#for laziness, every 6 seconds??
    out=buffer(hex(int('f'*64, 16)/hashes_required)[2:], 64)
    return out
def blockhash(chain_length, nonce, state, transactions, bitcoin_hash):
    fixed_transactions=[]
    for i in transactions:
        new=''
        for key in sorted(i.keys()):
            new=new+str(key)+':'+str(i[key])+','
        fixed_transactions.append(new)
    return {'hash':pt.sha256(str(chain_length)+str(nonce)+str(state['recent_hash'])+str(sorted(fixed_transactions))+str(bitcoin_hash)), 'exact':str(chain_length)+str(nonce)+str(state['recent_hash'])+str(sorted(fixed_transactions))+str(bitcoin_hash)}
def reverse(l):
    out=[]
    while l != []:
        out=[l[0]]+out
        l=l[1:]
    return out
def new_block_check(block, state):
    def f(x):
        return str(block[x])
    if 'length' not in block or 'bitcoin_count' not in block or 'transactions' not in block:
        return False
    diff=difficulty(f('bitcoin_count'), f('length'))
    ver=verify_transactions(block['transactions'], state)
    if not ver['bool']:
#        print('44')
        return False
    if f('sha') != blockhash(f('length'), f('nonce'), state, block['transactions'], f('bitcoin_hash'))['hash']:
        print('block invalid because blockhash was computed incorrectly')
#        error('here')
        return False
    elif f('sha')>diff:
        print('block invalid because blockhash is not of sufficient difficulty')
        print(f('sha'))
        print('difficulty: ' +str(diff))
        return False
    elif f('bitcoin_hash')!=bitcoin.getblockhash(int(f('bitcoin_count'))):
        print('block invalid because it does not contain the correct bitcoin hash')
        return False
    elif f('prev_sha')!=state['recent_hash']:
        print('block invalid because it does not contain the previous block\'s hash')
        return False
    return True
def verify_count(tx, state):
    if tx['id'] not in state.keys():
        state[tx['id']]={'count':1}
    if 'count' not in tx:
        print("invalid because we need each tx to have a count")
        return False
    if 'count' in tx and tx['count']!=state[tx['id']]['count']:
        print('tx: ' +str(tx))
        print('state: ' +str(state[tx['id']]['count']))
        print("#invalid because te count did not increment form last time.")
        return False
    return True

def verify_transactions(txs, state):
#transactions can only get verified with respect to a state, and you can only verify them as a group which is to be contained in a block together.
    txs=copy.deepcopy(txs)
    state=copy.deepcopy(state)
    already_seen=[]
    txs=sorted(txs, key=lambda x: x['count'])
    for txx in txs:
        tx=copy.deepcopy(txx)
	code=message2signObject(tx,tx.keys())
        if code in already_seen:
            print('invalid because no repeats.')
            return {'bool':False}
        already_seen.append(code)
        if not verify_count(tx, state):
            print("invalid because the tx['count'] was wrong")
            return {'bool':False}
        state[tx['id']]['count']+=1#th
        types=['spend', 'mint', 'nextTurn', 'newGame']
        if tx['type'] not in types: 
            print("invalid because tx['type'] was wrong")
            return {'bool':False}
        if tx['type']=='mint':
            if not mint_check(tx, state):
                return {'bool':False}
            if 'amount' not in state[tx['id']].keys():
                state[tx['id']]['amount']=0
            state[tx['id']]['amount']+=tx['amount']
        if tx['type']=='spend':
            if not spend_check(tx, state):
                return {'bool':False}
            state[tx['id']]['amount']-=tx['amount']
            if tx['pubkey'] not in state:
                state[tx['pubkey']]={'amount':0}
            state[tx['pubkey']]['amount']+=tx['amount']
        if tx['type']=='nextTurn':
            if not go.nextTurnCheck(tx, state):
                return {'bool':False}
            state[tx['game_name']]=go.next_board(state[tx['game_name']], tx['where'])
        if tx['type']=='newGame':
#            print("state"+str(state))
            if not go.newGameCheck(tx, state):
                return {'bool':False}
#            print('tx: ' +str(tx))
            state[tx['game_name']]=go.new_game(tx)
    return {'bool':True, 'newstate':state}

def mint_check(tx, state):
    if tx['amount']>10**5:
        return False#you can only mint up to 10**5 coins per block
    return True

def spend_check(tx, state):
    if tx['id'] not in state.keys():
        print("you can't spend money from a non-existant account")
        return False
    if tx['amount']>=state[tx['id']]['amount']:
        print("you don't have that much money to spend")
        return False
    if 'signature' not in tx:
        print("spend transactions must be signed")
        return False
    signed_properties=['type','pubkey','amount', 'count']
    if not pt.ecdsa_verify(message2signObject(tx, ['type','pubkey','amount', 'count']), tx['signature'], tx['id'] ):
        print("bad signature")
        return False
    return True
def send_command(peer, command):
    proxy_support = urllib2.ProxyHandler({"http" : "127.0.0.1:8118"})
    opener = urllib2.build_opener(proxy_support) 
#    opener.addheaders = [('User-agent', 'Mozilla/5.0')]
    url=peer.format(package(command))
    try:
        out=opener.open(url)
        out=out.read()
    except:
        out={'error':'cannot connect to peer'}
    try:
        return unpackage(out)
    except:
        return out


'''
def send_command(peer, command):
    try:
        URL=urllib.urlopen(peer.format(package(command)))
    except:
        return {'error':'peer disconnected'}
    URL=URL.read()
    try:
        return unpackage(URL)
    except:
        return URL
'''
def mine_1(reward_pubkey):
    sha={'hash':100}
    diff=0
    hashes_limit=1000
    hash_count=0
    while sha['hash']>diff:
        hash_count+=1
        if hash_count>=hashes_limit:
            return False
        state=state_library.current_state(reward_pubkey)
        bitcoin_count=bitcoin.getblockcount()
        bitcoin_hash=bitcoin.getblockhash(bitcoin_count)
        diff=difficulty(bitcoin_count, state['length']+1)
        nonce=random.randint(0,10000000000000000)
        time.sleep(0.01)
        transactions=load_transactions()
        extra=0
        for tx in transactions:
            if tx['id']==reward_pubkey:
                extra+=1
        count=state[reward_pubkey]['count']+extra
        transactions.append({'type':'mint', 'amount':10**5, 'id':reward_pubkey, 'count':count})
        try:
#            state=verify_transactions(transactions, state)['newstate']
            pass
        except:
            print('transactions: ' +str(transactions))
            print('state: ' +str(state))
            error('here')
        length=state['length']
        sha=blockhash(length, nonce, state, transactions, bitcoin_hash)
    block={'nonce':nonce, 'length':length, 'sha':sha['hash'], 'transactions':transactions, 'bitcoin_hash':bitcoin_hash, 'bitcoin_count':bitcoin_count, 'exact':sha['exact'], 'prev_sha':state['recent_hash']}
    print('new link: ' +str(block))
    chain_push(block)
    
def mine(reward_pubkey, peers):
    while True:
        peer_check_all(peers)
        mine_1(reward_pubkey)
def fork_check(newblocks, state):#while we are mining on a forked chain, this check returns True. once we are back onto main chain, it returns false.
    try:
#        hashes=filter(lambda x: 'prev_sha' in x and x['prev_sha']==state['recent_hash'], newblocks)
        hashes=filter(lambda x: 'sha' in x and x['sha']==state['recent_hash'], newblocks)
    except:
#        print('state: ' +str(state))
        error('here')
    return len(hashes)==0

def peer_check_all(peers):
    blocks=[]
    for peer in peers:
        blocks+=peer_check(peer)
    for block in blocks:
#        print('block: ' +str(block))
#       error('hrer')
        chain_push(block)

def peer_check(peer):
    state=state_library.current_state()
    cmd=(lambda x: send_command(peer, x))
    block_count=cmd({'type':'blockCount'})
    if type(block_count)!=type({'a':1}):
        return []
    if 'error' in block_count.keys():
        return []        
    ahead=int(block_count['length'])-int(state['length'])
    if ahead < 0:
        return []
    if ahead == 0:#if we are on the same block, ask for any new txs
        if state['recent_hash']!=block_count['recent_hash']:
            chain_unpush()
            print('peer_check 3')
            return []
        txs=cmd({'type':'transactions'})
        for tx in txs:
            add_transaction(tx)#skips bad transactions
        return []
    start=int(state['length'])-20
    if start<0:
        start=0
    if ahead>500:
        end=int(state['length'])+499
    else:
        end=block_count['length']
    blocks= cmd({'type':'rangeRequest', 
                 'range':[start, end]})
    if type(blocks)!=type([1,2]):
        return []
    times=1
    while fork_check(blocks, state) and times>0:
        times-=1
        chain_unpush()
    return blocks

