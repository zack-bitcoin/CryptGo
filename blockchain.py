import string,cgi,time, json, random, copy, os, copy, urllib, go, urllib2, time, config
import pybitcointools as pt
import state_library
genesis={'zack':'zack', 'length':-1, 'nonce':'22', 'sha':'00000000000'}
genesisbitcoin=290800-1224#1220
chain=[genesis]
chain_db='chain.db'
transactions_database='transactions.db'

#I call my database appendDB because this type of database is very fast to append data to.
def line2dic(line):
    return json.loads(line.strip('\n'))
def load_appendDB(file):
    out=[]
    try:
        with open(file, 'rb') as myfile:
            a=myfile.readlines()
            for i in a:
                if i.__contains__('"'):
                    out.append(line2dic(i))
    except:
        pass
    return out
def load_transactions():
    return load_appendDB(transactions_database)
def load_chain():
    open(chain_db, 'a').close()
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
def add_transactions(txs):#to local pool
    #This function is order txs**2, that is risky
    txs_orig=copy.deepcopy(txs)
    count=0
    for tx in sorted(txs_orig, key=lambda x: x['count']):
        if add_transaction(tx):
            count+=1
            txs.remove(tx)
    if count>0:
        add_transactions(txs)
def add_transaction(tx):#to local pool
    if tx['type']=='mint':
        return False
    transactions=load_transactions()
    state=state_library.current_state()
    if verify_transactions(transactions+[tx], state)['bool']:
        push_appendDB(transactions_database, tx)
        return True
    return False
def chain_push(block):
    statee=state_library.current_state()    
    print('CHAIN PUSH')
    if new_block_check(block, statee):
        print('PASSED TESTS')
        state=verify_transactions(block['transactions'], statee)
        state=state['newstate']
        state['length']+=1
        state['recent_hash']=block['sha']
        state_library.save_state(state)
        if block['length']%10==0:
            state_library.backup_state(state)
        txs=load_transactions()
        reset_transactions()
        add_transactions(txs)
        return push_appendDB(chain_db, block)
    else:
        print('FAILED TESTS')
        return 'bad'
def shorten_chain_db(new_length):
    f=open(chain_db, 'r')
    lines = f.readlines()
    f.close()
    f = open(chain_db,"w")
    i=0
    for line in lines:
        a=line2dic(line)
        if a['length']<=new_length and a['length']>new_length-1500:
            f.write(line)
    f.close()
def chain_unpush():
    chain=load_chain()
    orphaned_txs=[]
    txs=load_transactions()
    state=state_library.current_state()
    length=state['length']
    state=state_library.recent_backup()
    for i in range(length-state['length']):
        orphaned_txs+=chain[-1-i]['transactions']
#    chain=chain[:-1]
    #reset_chain() instead, just back up to the nearest save.
    shorten_chain_db(state['length'])
    state_library.save_state(state)
    reset_transactions()
#    for i in chain[-100:]:
#        chain_push(i)
    add_transactions(orphaned_txs)
    add_transactions(txs)
count_value=0
count_timer=time.time()-60
def probability(p, func):
    if random.random()<p:
        return func
def getblockcount():
    global count_value
    if time.time()-count_timer<60:
        return count_value
    try:
        peer='http://blockexplorer.com/q/getblockcount'
        URL=urllib.urlopen(peer)
        URL=URL.read()
        count_value=int(URL)
    except:
        peer='http://blockchain.info/q/getblockcount'
        URL=urllib.urlopen(peer)
        URL=URL.read()
        count_value=int(URL)
    count_timer=time.time()
    return count_value
hash_dic={}
def getblockhash(count):
    global hash_dic
    if str(count) in hash_dic:
        return hash_dic[str(count)]
    try:
        peer='http://blockexplorer.com/q/getblockhash/'+str(count)
        URL=urllib.urlopen(peer)
        URL=URL.read()
        int(URL, 16)
        hash_dic[str(count)]=URL
        return URL
    except:
        peer='http://blockchain.info/q/getblockhash/'+str(count)
        URL=urllib.urlopen(peer)
        URL=URL.read()
        int(URL, 16)
        hash_dic[str(count)]=URL
        return URL

def package(dic):
    return json.dumps(dic).encode('hex')
def unpackage(dic):
    try:
        return json.loads(dic.decode('hex'))
    except:
#        print('in unpackage: '+str(dic))
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
    try:
        hashes_required=int((10**60)*((9.0/10)**(float(bitcoin_count)-float(genesisbitcoin)-(float(leng)/10)))+1)#for bitcoin
#    hashes_required=int((10**60)*((9.0/10)**(float(bitcoin_count)-float(genesisbitcoin)-(float(leng)/2.5)))+1)#for litcoin
#    hashes_required=int((10**60)*((9.0/10)**(float(bitcoin_count)-float(genesisbitcoin)-(float(leng)/25)))+1)#for laziness, every 6 seconds??
    except:
        hashes_required=999999999999999999999999999999999999999999999999999999999999
    out=buffer(hex(int('f'*64, 16)/hashes_required)[2:], 64)
    return out
def blockhash(chain_length, nonce, state, transactions, bitcoin_hash):
    fixed_transactions=[]
    if len(transactions)==0:
        error('here')
    for i in transactions:
        new=''
        for key in sorted(i.keys()):
            new=new+str(key)+':'+str(i[key])+','
        fixed_transactions.append(new)
    exact=str(chain_length)+str(nonce)+str(state['recent_hash'])+str(sorted(fixed_transactions))+str(bitcoin_hash)
#    return {'hash':pt.sha256(exact), 'exact':exact}
    return {'hash':pt.sha256(exact)}
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
        print('ERRROR !')
        return False
    diff=difficulty(f('bitcoin_count'), f('length'))
    ver=verify_transactions(block['transactions'], state)
    if not ver['bool']:
        print('44')
        return False
#    print('new_ block: ' +str(block))
    if f('sha') != blockhash(f('length'), f('nonce'), state, block['transactions'], f('bitcoin_hash'))['hash']:
        print('blockhash: ' +str(blockhash(f('length'), f('nonce'), state, block['transactions'], f('bitcoin_hash'))))
        print('block invalid because blockhash was computed incorrectly')
#        error('here')
        return False
    a=getblockcount()
    if int(f('bitcoin_count'))>int(a):
        print('website: ' + str(type(a)))
        print('f: ' +str(type(f('bitcoin_count'))))
        print('COUNT ERROR')
        return False
    elif f('sha')>diff:
        print('block invalid because blockhash is not of sufficient difficulty')
        return False
    elif f('bitcoin_hash')!=getblockhash(int(f('bitcoin_count'))):
        print('block invalid because it does not contain the correct bitcoin hash')
        return False
    elif f('prev_sha')!=state['recent_hash']:
        print('block invalid because it does not contain the previous block\'s hash')
        return False
    return True
def verify_count(tx, state):
    if 'id' not in tx:
        print('bad input error in verify count')
        error('here')
        return False
    if tx['id'] not in state.keys():
        state[tx['id']]={'count':1}
    if 'count' not in tx:
        print("invalid because we need each tx to have a count")
        return False
    if 'count' not in state[tx['id']]:
        state[tx['id']]['count']=1
    if 'count' in tx and tx['count']!=state[tx['id']]['count']:
        return False
    return True

def verify_transactions(txs, state):
    txs=copy.deepcopy(txs)
    if len(txs)==0:
        return {'bool':True, 'newstate':state}
    print('txs: ' +str(txs))
    length=len(txs)
    state=copy.deepcopy(state)
    remove_list=[]
    for i in txs:
        (state, booll) = attempt_absorb(i, state)
        if booll:
            remove_list.append(i)
    for i in remove_list:
        txs.remove(i)
    if len(txs)>=length:
        print('HERE')
        print(txs)
        return {'bool':False}
    if len(txs)==0:
        return {'bool':True, 'newstate':state}
    else:
        return verify_transactions(txs, state)
def attempt_absorb(tx, state):
    state=copy.deepcopy(state)
    state_orig=copy.deepcopy(state)
    if not verify_count(tx, state):
       print("invalid because the tx['count'] was wrong")
       return (state, False)
    state[tx['id']]['count']+=1
    types=['spend', 'mint', 'nextTurn', 'newGame', 'winGame']
    if tx['type'] not in types: 
        print('tx: ' +str(tx))
        print("invalid because tx['type'] was wrong")
        return (state_orig, False)
    if tx['type']=='mint':
        if not mint_check(tx, state):
            print('MINT ERROR')
            return (state_orig, False)
        if 'amount' not in state[tx['id']].keys():
            state[tx['id']]['amount']=0
        state[tx['id']]['amount']+=tx['amount']
    if tx['type']=='spend':
        if not spend_check(tx, state):
            print('SPEND ERROR')
            return (state_orig, False)
        if tx['to'] not in state:
            print('PUBKEY ERROR')
            state[tx['to']]={'amount':0}
        if 'amount' not in state[tx['to']]:
            state[tx['to']]['amount']=0
        state[tx['id']]['amount']-=tx['amount']
        state[tx['to']]['amount']+=tx['amount']
    if tx['type']=='nextTurn':
        if not go.nextTurnCheck(tx, state):
            print('NEXT TURN ERROR')
            return (state_orig, False)
        state[tx['game_name']]=go.next_board(state[tx['game_name']], tx['where'], state['length'])

#    print('tx: ' +str(tx))
    if tx['type']=='newGame':
        if not go.newGameCheck(tx, state):
            print('FAILED NEW GAME CHECK')
            return (state_orig, False)
        state[tx['game_name']]=go.new_game(copy.deepcopy(tx))
        pubkey_black=state[tx['game_name']]['pubkey_black']        
        print('state: ' +str(state))
        if pubkey_black not in state:
            print('newgame error 1')
            return (state_orig, False)
        state[pubkey_black]['amount']-=25000#1/4 of mining reward
	if tx['amount']>0:
            state[pubkey_black]['amount']-=tx['amount']
            state[pubkey_white]['amount']-=tx['amount']
#    print('tx: ' +str(tx))
    if tx['type']=='winGame':
        if not go.winGameCheck(tx, state):
            print('FAILED WIN GAME CHECK')
            return (state_orig, False)
        pubkey_black=state[tx['game_name']]['pubkey_black']
        state[pubkey_black]['amount']+=25000
#        print('tx: ' +str(tx))
        a=state[tx['game_name']]['amount']
        if a>0:
            state[tx['id']]['amount']+=a*2
        state.pop(tx['game_name'])
    return (state, True)
def mint_check(tx, state):
    if tx['amount']>10**5:
        return False#you can only mint up to 10**5 coins per block
    return True
spend_list=['id', 'amount', 'count', 'to']
def enough_funds(state, pubkey, enough):
    if enough==0:
        return True
    if pubkey not in state:
        print('nonexistant people have no money')
        return False
    if 'amount' not in state[pubkey]:
        print('this person has no money')
        return False
    funds=state[pubkey]['amount']
    return funds>=enough

def spend_check(tx, state):
    if tx['id'] not in state.keys():
        print("you can't spend money from a non-existant account")
        return False
    if 'amount' not in tx:
        print('how much did you want to spend?')
        return False
    if type(tx['amount']) != type(5):
        print('you can only spend integer amounts of money')
        return False
    if tx['amount']<=1000:
        print('the minimum amount to spend is 1000 base units = 0.01 CryptGo coin.')
        return False
    if not enough_funds(state, tx['id'], tx['amount']):
        print('not enough money to spend in this account')
        return False
    if 'signature' not in tx:
        print("spend transactions must be signed")
        return False
    try:
        if not pt.ecdsa_verify(message2signObject(tx, spend_list), tx['signature'], tx['id'] ):
            print("bad signature")
            return False
    except:
        print('Weird error when checking the signature of a transaction')
        return False
    return True
def send_command(peer, command):
#    opener.addheaders = [('User-agent', 'Mozilla/5.0')]
    command['version']=3
    url=peer.format(package(command))
    print('in send command')
    time.sleep(1)#so we don't DDOS the networking computers which we all depend on.
    if 'onion' in url:
        try:
            print('trying privoxy method')
            proxy_support = urllib2.ProxyHandler({"http" : "127.0.0.1:8118"})
            opener = urllib2.build_opener(proxy_support) 
            out=opener.open(url)
            out=out.read()
            print('privoxy succeeded')
        except:
            print('url: ' +str(url))
            out={'error':'cannot connect to peer'}
    else:
        try:
            print('attempt to open: ' +str(url))
            URL=urllib.urlopen(url)
            out=URL.read()
        except:
            print('url: ' +str(url))
            out={'error':'cannot connect to peer'}
    try:
        return unpackage(out)
    except:
        return out
def mine_1(reward_pubkey, peers, times):
    sha={'hash':100}
    diff=0
    hash_count=0
    print('start mining ' +str(times)+ ' times')
    while sha['hash']>diff:
#        print(str(hash_count))
        if hash_count>=times:
#            time.sleep(2)#otherwise you send requests WAY TOO FAST and the networking miners shutdown.
            print('was unable to find blocks')
            return False
        state=state_library.current_state(reward_pubkey)
        bitcoin_count=getblockcount()
        bitcoin_hash=getblockhash(bitcoin_count)
        diff=difficulty(bitcoin_count, state['length']+1)
        nonce=random.randint(0,10000000000000000)
#        time.sleep(0.01)
        transactions=load_transactions()
        extra=0
        for tx in transactions:
            if tx['id']==reward_pubkey:
                extra+=1
        count=state[reward_pubkey]['count']+extra
        transactions.append({'type':'mint', 'amount':10**5, 'id':reward_pubkey, 'count':count})
        length=state['length']
        sha=blockhash(length, nonce, state, transactions, bitcoin_hash)
        hash_count+=1
#    block={'nonce':nonce, 'length':length, 'sha':sha['hash'], 'transactions':transactions, 'bitcoin_hash':bitcoin_hash, 'bitcoin_count':bitcoin_count, 'exact':sha['exact'], 'prev_sha':state['recent_hash']}
    block={'nonce':nonce, 'length':length, 'sha':sha['hash'], 'transactions':transactions, 'bitcoin_hash':bitcoin_hash, 'bitcoin_count':bitcoin_count, 'prev_sha':state['recent_hash']}
    print('new link: ' +str(block))
    chain_push(block)
#    pushblock(block, peers)
def mine(reward_pubkey, peers):
    while True:
        peer_check_all(peers)
        mine_1(reward_pubkey, peers, config.hashes_till_check)
        a=load_appendDB('suggested_transactions.db')
        add_transactions(a)
        reset_appendDB('suggested_transactions.db')
        a=load_appendDB('suggested_blocks.db')
        for block in a:
            chain_push(block)
        reset_appendDB('suggested_blocks.db')
        #if there are suggested transactions, try to add them.
        #if there are suggested blocks. try to add them.
def fork_check(newblocks, state):#while we are mining on a forked chain, this check returns True. once we are back onto main chain, it returns false.
    try:
#        hashes=filter(lambda x: 'prev_sha' in x and x['prev_sha']==state['recent_hash'], newblocks)
        hashes=filter(lambda x: 'sha' in x and x['sha']==state['recent_hash'], newblocks)
    except:
        error('here')
    return len(hashes)==0

def peer_check_all(peers):
    blocks=[]
    for peer in peers:
        blocks+=peer_check(peer)
    for block in blocks:
        chain_push(block)

def pushtx(tx, peers):
    for p in peers:
        send_command(p, {'type':'pushtx', 'tx':tx})

def pushblock(block, peers):
    for p in peers:
        send_command(p, {'type':'pushblock', 'block':block})    
def set_minus(l1, l2, ids):#l1-l2
    out=[]
    def member_of(a, l, ids):
        for i in l:
            if a[ids[0]]==i[ids[0]] and a[ids[1]]==i[ids[1]]:
                return True
        return False
    for i in l1:
        if not member_of(i, l2, ids):
            out.append(i)
    return out

def peer_check(peer):
    print('checking peer')
    state=state_library.current_state()
    cmd=(lambda x: send_command(peer, x))
    block_count=cmd({'type':'blockCount'})
    print('block count: ' +str(block_count))
    if type(block_count)!=type({'a':1}):
        return []
    if 'error' in block_count.keys():
        return []        
    print('state: ' +str(state))
    ahead=int(block_count['length'])-int(state['length'])
    if ahead < 0:
        chain=copy.deepcopy(load_chain())
        pushblock(chain[int(block_count['length'])+1],[peer])
        probability(0.2, chain_unpush())
        return []
    if ahead == 0:#if we are on the same block, ask for any new txs
        print('ON SAME BLOCK')
        if state['recent_hash']!=block_count['recent_hash']:
            chain_unpush()
            print('WE WERE ON A FORK. time to back up.')
            return []
        my_txs=load_transactions()
        txs=cmd({'type':'transactions'})
        add_transactions(txs)
        pushers=set_minus(my_txs, txs, ['count', 'id'])
        for push in pushers:
            pushtx(push, [peer])
        return []
    if ahead>1001:
        try_state=cmd({'type':'backup_states',
                   'start': block_count['length']-1000})
        if type(try_state)==type({'a':'1'}) and 'error' not in state:
            print('state: ' +str(state))
            state=try_state
            state_library.save_state(state)
        return []
    print("############################## ahead: "+str(ahead))
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
