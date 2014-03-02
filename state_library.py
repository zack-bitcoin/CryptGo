import cPickle
state_db='state.db'
empty_state={'length':0, 'recent_hash':'00000000000'}
def fs_save(database, dic):
    cPickle.dump(dic, open(database, 'wb'))
def fs_load(database, sort=[]):
    try:
        out=cPickle.load(open(database, 'rb'))
        return out
    except:
        fs_save(database, sort)#these are list-databases
        return cPickle.load(open(database, 'rb'))      
def save_state(state):#state contains the positions of every board, and who has how much money.
    return fs_save(state_db, state)
def current_state(key=''):#lets make this grab current state from a file, instead of re-computing it.
#key is for optionally initializing a new id
    current=fs_load(state_db, empty_state)
    if key!='' and key not in current:
        current[key]={'count':1, 'amount':0}
    return current
