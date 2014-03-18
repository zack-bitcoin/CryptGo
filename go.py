import pybitcointools as pt
import copy, state_library
newgame_sig_list=['id', 'type', 'game_name', 'pubkey_white', 'pubkey_black', 'count', 'whos_turn', 'white', 'time', 'black', 'size', 'amount']
nextturn_sig_list=['id', 'game_name', 'type', 'count', 'where']
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
        if not nextTurnCheck(tx, state):
            print('NEXT TURN ERROR')
            return (state_orig, False)
        state[tx['game_name']]=next_board(state[tx['game_name']], tx['where'], state['length'])

#    print('tx: ' +str(tx))
    if tx['type']=='newGame':
        if not newGameCheck(tx, state):
            print('FAILED NEW GAME CHECK')
            return (state_orig, False)
        state[tx['game_name']]=new_game(copy.deepcopy(tx))
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
        if not winGameCheck(tx, state):
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
        #    try:
    if not pt.ecdsa_verify(message2signObject(tx, spend_list), tx['signature'], tx['id'] ):
        print("bad signature")
        return False
#    except:
#        print('Weird error when checking the signature of a transaction')
#        return False
    return True
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
def valid_board(board, move):
    #tells whether this is a valid move to make on this board.
    color=board['whos_turn']
    if color=='white':
        other_color='black'
    else:
        other_color='white'
#    print('move: ' +str(move))
    where=move['where']
    return alive(where, copy.deepcopy(board[color]+[where]), copy.deepcopy(board[other_color]), board['size'])
def alive(loc, mine, yours, size):#is my piece at loc still alive?
    if loc[0]<0 or loc[1]<0 or loc[0]>=size or loc[1]>=size:#off the edge
        return False
    if loc in yours:
        return False
    if loc not in mine+yours:
        return True#Found a liberty!!
    if loc in mine:
        yours.append(loc)
        return alive([loc[0]+1, loc[1]], mine, yours, size) or alive([loc[0]-1, loc[1]], mine, yours, size) or alive([loc[0], loc[1]+1], mine, yours, size) or alive([loc[0], loc[1]-1], mine, yours, size)
def next_board(board, move, count):
#how does dictionary "board" change between moves?
    if board['whos_turn']=='black':
        color='black'
        other_color='white'
    else:
        color='white'
        other_color='black'
    board['move_number']+=1
    board[color]+=[move]
    board['whos_turn']=other_color
    board=remove_dead_stones(board, move)
    board['last_move_time']=count
    return board
def new_game(tx):
    print('tx: ' +str(tx))
    state=state_library.current_state()
    tx['last_move_time']=state['length']
    tx.pop('signature')
    tx.pop('id')
    tx.pop('count')
    tx.pop('type')
    tx['move_number']=1
    return tx
def remove_dead_stones(board, move):
#    print('board: ' +str(board))
    color=board['whos_turn']
    if color=='white':
        other_color='black'
    else:
        other_color='white'
    def group(pt, color, board):
        if color=='black':
            other_color='white'
        else:
            other_color='black'
        if pt[0]<0 or pt[1]<0 or pt[0]>=board['size'] or pt[1]>=board['size']:
            return []
        if pt in board[other_color]:
            return []
        if pt not in board[other_color]+board[color]:
            return []
        if pt in board[color]:
            board[color].remove(pt)
            board[other_color].append(pt)
            return [pt]+group([pt[0]+1,pt[1]], color, board)+group([pt[0]-1,pt[1]], color, board)+group([pt[0],pt[1]+1], color, board)+group([pt[0],pt[1]-1], color, board)
    def set_minus(l1, l2):#l1-l2
        out=[]
#        print('l1: ' +str(l1))
#        print('l2: ' +str(l2))
        for i in l1:
            if i not in l2:
                out.append(i)
        return out
#    print('move: ' +str(move))
    around=[[move[0]+1, move[1]],[move[0]-1, move[1]],[move[0], move[1]+1],[move[0], move[1]-1]]
    around
    for pt in around:
        if not alive(pt, copy.deepcopy(board[color]), copy.deepcopy(board[other_color]), copy.deepcopy(board['size'])):
            board[color]=set_minus(board[color], group(pt, color, copy.deepcopy(board)))
    return board

def nextTurnCheck(i, state):
    if i['game_name'] not in state:
        print('19')
        return False
    board=state[i['game_name']]
    if len(state.keys())==0:
        print('2')
        return False
#    print('state: ' +str(state))
#    print('board: ' +str(board))
    if board['whos_turn']=='white':
        pubkey=board['pubkey_white']
    else:
        pubkey=board['pubkey_black']
    if board['move_number'] != i['move_number']:
        return False
    try:#so that invalid pubkeys don't break anything.
        if not pt.ecdsa_verify(message2signObject(i, nextturn_sig_list), i['signature'], pubkey):
            print('i: ' +str(i))
            print('state: ' +str(state))
            print('14')
            return False
    except:
        print('invalid pubkey error')
        return False
    n=next_board(copy.deepcopy(board), i['where'], state['length'])
    if (len(n['black'])+len(n['white']))<=(len(board['black'])+len(board['white'])):#if it kills, then it lives
#        error('here')
        return True
    return valid_board(board, i)
def winGameCheck(tx, state):
    game=state[tx['game_name']]
    print('game: ' +str(game))
    if game['last_move_time']+game['time']>=state['length']:
        return False
    return True
def newGameCheck(i, state):
    if 'pubkey_black' not in i.keys():
        i['pubkey_black']=i['id']
    if 'pubkey_white' not in i.keys() or type(i['pubkey_white']) not in [type('string'), type(u'unicode')] or len(i['pubkey_white'])!=130:
        print('type: ' +str(type(i['pubkey_white'])))
        print('badly formated newgame white pubkey')
        return False
    if not enough_funds(state, i['pubkey_black'], 25000):
        print('you need at least 1/4 of a CryptGo coin in order to play.')
        return False
    if 'game_name' not in i.keys():
        print('the game needs a name')
        return False
    if len(i['game_name'])>129:
        print('name too long')
        return False
    if not 'pubkey_white' in i or not 'pubkey_black' in i:
        print('13')
        return False
    if 'whose_turn' not in i:
        i['whos_turn']='black'
    if i['whos_turn'] not in ['white', 'black']:
        print('4')
        return False
    if type(i['white']) != type([1,2]):
        return False
    if type(i['black']) != type([1,2]):
        return False
    for j in i['white']+i['black']:
        #            print('j: ' +str(j))
        if type(j)!=type([1,2]) or len(j)!=2:
            print('5')
            return False
    if 'time' not in i:
        i['time']=5
    if 'size' not in i:
        i['size']=13
    if 'white' not in i:
        i['white']=[]
    if 'black' not in i:
        i['black']=[]
    if (type(i['time']) != type(3)):
        print('7')
        return False
    if type(i['size']) != type(3) or i['size']<3 or i['size']>30:
        print('8')
        return False
    if type(i['white']) != type([1,2]) or type(['black']) != type([1,2]):
        print('6')
        return False
    if 'amount' not in i:
        i['amount']=0
    if type(i['amount'])!=type(10):
        print('bet error')
        return False
    sign=message2signObject(i, newgame_sig_list)
    if not pt.ecdsa_verify(sign, i['signature'], i['pubkey_black']):
        print('i: ' +str(i))
        print('signature error')
        return False
    if i['amount']>0 and 'signature_white' not in i:
        print('both people need to consent, if you want to bet')
        return False
    if i['amount']>0 and not pt.ecdsa_verify(sign, i['signature_white'], pubkey_white):
        print('signature error 2')
        return False
    return True
