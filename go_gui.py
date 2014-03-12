from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import string,cgi,time, json, random, copy, pickle, os
PORT=8090
import blockchain, state_library, go, quick_mine
import pybitcointools as pt

#privkey=pt.sha256("Brain Wallet Here")
#pubkey=pt.privtopub(privkey)
#state=state_library.current_state()
#my_count=state[pubkey]['count']
spend_list=['type','pubkey', 'amount', 'count']
win_list=['game_name', 'id']
def spend(amount, pubkey, to_pubkey):
    tx={'type':'spend', 'id':pubkey, 'amount':amount, 'to':to_pubkey}
    easy_add_transaction(tx, spend_list, privkey)
def wingame(game_name, pubkey, privkey):
    tx={'type':'winGame', 'game_name':game_name, 'id':pubkey}
    easy_add_transaction(tx, win_list, privkey)
def newgame(opponent, name, pubkey_mine, privkey, size=19, amount=0):
    amount=int(amount)
    print('NEWGAME')
    tx={'type':'newGame', 'game_name':name, 'id':pubkey_mine, 'pubkey_white':opponent, 'pubkey_black':pubkey_mine, 'whos_turn':'black', 'time':5, 'white':[], 'black':[], 'size':size, 'amount':amount}
    easy_add_transaction(tx, go.newgame_sig_list, privkey)
def move(game_name, location, pubkey, privkey):
    state=state_library.current_state()
    board=state[game_name]
    print('location: ' +str(location))
    txs=blockchain.load_transactions()
    game_txs=filter(lambda x: x['game_name']==game_name, txs)
    tx_orig={'type':'nextTurn', 'id':pubkey, 'game_name':game_name, 'where':location, 'move_number':board['move_number']+len(game_txs)}
    easy_add_transaction(tx_orig, go.nextturn_sig_list, privkey)
def easy_add_transaction(tx_orig, sign_over, privkey):
    state=state_library.current_state()
    pubkey=pt.privtopub(privkey)
    if pubkey not in state or 'count' not in state[pubkey]:
        my_count=1
    else:
        my_count=state[pubkey]['count']
    txs=blockchain.load_transactions()
    my_txs=filter(lambda x: x['id']==pubkey, txs)
    tx=copy.deepcopy(tx_orig)
    tx['count']=len(my_txs)+my_count
    tx['signature']=pt.ecdsa_sign(blockchain.message2signObject(tx, sign_over), privkey)
    print(blockchain.add_transaction(tx))
    if 'move_number' in tx:
        for i in range(10):
            tx['move_number']+=1
            tx['signature']=pt.ecdsa_sign(blockchain.message2signObject(tx, sign_over), privkey)
            print(blockchain.add_transaction(tx))
    print('tx: ' +str(tx))
    blockchain.pushtx(tx, quick_mine.peers_list)
def fs2dic(fs):
    dic={}
    for i in fs.keys():
        a=fs.getlist(i)
        if len(a)>0:
            dic[i]=fs.getlist(i)[0]
        else:
            dic[i]=""
    return dic
submit_form='''
<form name="first" action="{}" method="{}">
<input type="submit" value="{}">{}
</form> {}
'''
active_games=[]
def easyForm(link, button_says, moreHtml='', typee='post'):
    a=submit_form.format(link, '{}', button_says, moreHtml, "{}")
    if typee=='get':
        return a.format('get', '{}')
    else:
        return a.format('post', '{}')
linkHome = easyForm('/', 'HOME', '', 'get')

def dot_spot(s, i, j):
    sp=[3,9,15]
    if s==19 and i in sp and j in sp:
        return True
    sp=[2,6]
    if s==9 and i in sp and j in sp:
        return True
    sp=[2,10]
    if s==13 and ((i in sp and j in sp) or (j==6 and i==6)):
        return True
def board_spot(j, i, not_whos_turn_pubkey, whos_turn_pubkey, pubkey, board, privkey):
    s=board['size']
    out='{}'
    if [j, i] in board['white']:
        out=out.format(hex2htmlPicture(white_txt))
    elif [j, i] in board['black']:
        out=out.format(hex2htmlPicture(black_txt))
    else:
        img=empty_txt
        if dot_spot(s, i, j):
            img=dot_txt
        if True:
            out=out.format('''<form style='display:inline;\n margin:0;\n padding:0;' name="play_a_move" action="/home" method="POST"><input type="image" src="{}" name="move" height="{}"><input type="hidden" name="move" value="{},{}"><input type="hidden" name="game" value="{}"><input type="hidden" name="privkey" value="{}"></form>{}'''.format(txt2src(img), str(piece_size), str(j), str(i), board['game_name'], privkey,'{}'))
        else:
            out=out.format(hex2htmlPicture(img))
    return out
    
def board(out, state, game, privkey):
#    state=copy.deepcopy(state)
#    transactions=blockchain.load_transactions()
#    a=blockchain.verify_transactions(transactions, state)
#    if a['bool']:
#        state=a['newstate']
#    else:
#        pass
#        print('ERROR')
#    print('state: ' +str(state))
    board=state[game]
    s=board['size']
    '''
    transactions=filter(lambda x: x['game_name']==board['game_name'], transactions)
    black_tx=filter(lambda x: x['id']==board['pubkey_black'], transactions)
    white_tx=filter(lambda x: x['id']==board['pubkey_white'], transactions)
    black_txs=[]
    white_txs=[]
    print('black: ' +str(black_tx))
    for i in black_tx:
        if 'where' in i:
            black_txs.append(i['where'])
        else:
            out=out.format('<p>You are attempting to win this game</p>{}')
    for i in white_tx:
        if 'where' in i:
            white_txs.append(i['where'])
        else:
            out=out.format('<p>You are attempting to win this game</p>{}')
'''
    pubkey=pt.privtopub(privkey)
    #instead of putting more stones on the board, we should be trying to calculate what the next board will look like.
    if board['whos_turn']=='white':
        whos_turn_pubkey=board['pubkey_white']
        not_whos_turn_pubkey=board['pubkey_black']
    else:
        whos_turn_pubkey=board['pubkey_black']
        not_whos_turn_pubkey=board['pubkey_white']
    for j in range(s):
        out=out.format('<br>{}')
        for i in range(s):
#            out=out.format(board_spot(j, i, moves_played, not_whos_turn_pubkey, whos_turn_pubkey, pubkey, board, white_txs, black_txs, privkey))
            out=out.format(board_spot(j, i, not_whos_turn_pubkey, whos_turn_pubkey, pubkey, board, privkey))
    return out
def page1():
    out=empty_page
    out=out.format(easyForm('/home', 'Play Go!', '<input type="text" name="BrainWallet" value="">'))
    return out.format('')
def home(dic):
    print(dic)
    if 'BrainWallet' in dic:
        dic['privkey']=pt.sha256(dic['BrainWallet'])
    privkey=dic['privkey']
    print('priv: ' +str(dic['privkey']))
    pubkey=pt.privtopub(dic['privkey'])
    if 'do' in dic.keys():
        if dic['do']=='newGame':
            try:
                a=newgame(dic['partner'], dic['game'], pubkey, privkey, int(dic['size']), dic['amount'])
            except:
                a=newgame(dic['partner'], dic['game'], pubkey, privkey, 19, dic['amount'])
            active_games.append(dic['game'])
        if dic['do']=='winGame':
            wingame(dic['game'], pubkey, privkey)
        if dic['do']=='joinGame':
            active_games.append(dic['game'])
        if dic['do']=='deleteGame':
            active_games.remove(dic['game'])
    if 'move' in dic.keys():
        string=dic['move'].split(',')
        i=int(string[0])
        j=int(string[1])
        move(dic['game'], [i, j], pubkey, privkey)
    fs=fs_load()
    out=empty_page
    out=out.format('<p>your address is: ' +str(pubkey)+'</p>{}')
    state=state_library.current_state()
    out=out.format('<p>current block is: ' +str(state['length'])+'</p>{}')
    transactions=blockchain.load_transactions()
    a=blockchain.verify_transactions(transactions, state)
    if a['bool']:
        state=a['newstate']
    else:
        pass
        print(a)
        print(transactions)
        print('ERROR')
    if pubkey not in state:
        state[pubkey]={'amount':0}
    if 'amount' not in state[pubkey]:
        state[pubkey]['amount']=0
    out=out.format('<p>current balance is: ' +str(state[pubkey]['amount']/100000.0)+'</p>{}')        
    for game in active_games:
        out=out.format("<h1>"+str(game)+"</h1>{}")
        if game in state:
            out=out.format('<h1>Timer: ' + str(state[game]['last_move_time']+state[game]['time']-state['length'])+' </h1>{}')
        if game in state.keys():
            in_last_block=state[game]
            out=board(out, state, game, privkey)
            out=out.format(easyForm('/home', 'win this game', '''
            <input type="hidden" name="do" value="winGame">
            <input type="hidden" name="privkey" value="{}">
            <input type="hidden" name="game"  value="{}">'''.format(privkey, game)))
            out=out.format(easyForm('/home', 'leave this game', '''
            <input type="hidden" name="do" value="deleteGame">
            <input type="hidden" name="privkey" value="{}">
            <input type="hidden" name="game"  value="{}">'''.format(privkey, game)))
        else:
            out=out.format("<p>this game does not yet exist</p>{}")
            out=out.format(easyForm('/home', 'delete this game', '''
            <input type="hidden" name="do" value="deleteGame">
            <input type="hidden" name="privkey" value="{}">
            <input type="hidden" name="game"  value="{}">'''.format(privkey,game)))
    out=out.format(easyForm('/home', 'Refresh boards', '''
    <input type="hidden" name="privkey" value="{}">
    '''.format(privkey)))    
    out=out.format(easyForm('/home', 'Join Game', '''
    <input type="hidden" name="do" value="joinGame">
    <input type="hidden" name="privkey" value="{}">
    <input type="text" name="game" value="unique game name">
    '''.format(privkey)))
    out=out.format(easyForm('/home', 'New Game', '''
    <input type="hidden" name="do" value="newGame">
    <input type="hidden" name="privkey" value="{}">
    <input type="text" name="game" value="unique game name">
    <input type="text" name="partner" value="put your partners address here.">
    <input type="text" name="size" value="board size (9, 13, 19 are popular)">
    <input type="text" name="amount" value="0">
    '''.format(privkey)))
    return out
def hex2htmlPicture(string):
    return '<img height="{}" src="data:image/png;base64,{}">{}'.format(str(piece_size), string, '{}')
#def file2hexPicture(fil):
#    return image64.convert(fil)
#def file2htmlPicture(fil):
#    return hex2htmlPicture(file2hexPicture(fil))
def newline():
    return '''<br />
{}'''
empty_page='<html><body>{}</body></html>'
initial_db={}
database='tags.db'
board_size=500
piece_size=board_size/19
dot_txt="iVBORw0KGgoAAAANSUhEUgAAAAkAAAAJCAIAAABv85FHAAAACXBIWXMAAAsTAAALEwEAmpwYAAAAB3RJTUUH3gITFCMP6bUdsgAAABl0RVh0Q29tbWVudABDcmVhdGVkIHdpdGggR0lNUFeBDhcAAAAuSURBVAjXY/S448EAAztUdiBzmRhwA+LkdqjsgJOEASPccrgOuAjCTIgQNdwJAJ24Duf6+IShAAAAAElFTkSuQmCC"
white_txt="iVBORw0KGgoAAAANSUhEUgAAAAkAAAAJCAIAAABv85FHAAAACXBIWXMAAAsTAAALEwEAmpwYAAAAB3RJTUUH3gITDyM1P8qIkQAAABl0RVh0Q29tbWVudABDcmVhdGVkIHdpdGggR0lNUFeBDhcAAABASURBVAjXY/S448HAwMDAwLBdeTuE4XnXE8Jg8Ljj8R8b8LjjwcSAGzD+//8flxw+fXjlEK5CBZ53PfG6BY//ALQ0JoSAn9HtAAAAAElFTkSuQmCC"
empty_txt="iVBORw0KGgoAAAANSUhEUgAAAAkAAAAJCAIAAABv85FHAAAACXBIWXMAAAsTAAALEwEAmpwYAAAAB3RJTUUH3gITDyIL57CkewAAABl0RVh0Q29tbWVudABDcmVhdGVkIHdpdGggR0lNUFeBDhcAAAAfSURBVAjXY/S448EAAztUdiBzmRhwA3Ll8AFGOrsFAO/zCOeJq9qTAAAAAElFTkSuQmCC"
black_txt="iVBORw0KGgoAAAANSUhEUgAAAAkAAAAJCAIAAABv85FHAAAACXBIWXMAAAsTAAALEwEAmpwYAAAAB3RJTUUH3gITDyMEbhSIqwAAABl0RVh0Q29tbWVudABDcmVhdGVkIHdpdGggR0lNUFeBDhcAAAApSURBVAjXY/S448HAwMDAwLBDZQeEARdBYqECjzseTAx0BmS6hRGP/wCVjQ6PyfnLuwAAAABJRU5ErkJggg=="
half_black_txt='iVBORw0KGgoAAAANSUhEUgAAAAkAAAAJCAIAAABv85FHAAAACXBIWXMAAAsTAAALEwEAmpwYAAAAB3RJTUUH3gMCFQAdcKJo5gAAABl0RVh0Q29tbWVudABDcmVhdGVkIHdpdGggR0lNUFeBDhcAAABbSURBVAjXY/S448HAwMDAwLBn6p4//X9YCllcsl0gIiwQUQYkAOG6ZLswMeAGzA+YH8A5/078Y7KEqr53+h4ebQyMLIUscA7ELXAuE9xVaICAW1ggSpB9AjcJAJjWHSoSD4gAAAAAAElFTkSuQmCC'
half_white_txt='iVBORw0KGgoAAAANSUhEUgAAAAkAAAAJCAIAAABv85FHAAAACXBIWXMAAAsTAAALEwEAmpwYAAAAB3RJTUUH3gMCFDo4H80I7wAAABl0RVh0Q29tbWVudABDcmVhdGVkIHdpdGggR0lNUFeBDhcAAABTSURBVAjXY/S448HAwMDAwBAiG/Jj4Q+OeI41j9dARFggogxIAMJd83gNEwNuwISmCVk3y4+FP5CFkLksHPEcyBLIXCa4q9AAAbewQJQg+wRuEgBisR8X0r+9ngAAAABJRU5ErkJggg=='
def txt2src(txt):
    return "data:image/png;base64,"+txt
#white=hex2htmlPicture(white_txt)
dot=hex2htmlPicture(dot_txt)
empty=hex2htmlPicture(empty_txt)
black=hex2htmlPicture(black_txt)
half_white=hex2htmlPicture(half_white_txt)
half_black=hex2htmlPicture(half_black_txt)
def fs_load():
    try:
        out=pickle.load(open(database, 'rb'))
        return out
    except:
        fs_save(initial_db)
        return pickle.load(open(database, 'rb'))      
def fs_save(dic):
    pickle.dump(dic, open(database, 'wb'))
class MyHandler(BaseHTTPRequestHandler):
   def do_GET(self):
      try:
         if self.path == '/' :    
#            page = make_index( '.' )
            self.send_response(200)
            self.send_header('Content-type',    'text/html')
            self.end_headers()
            self.wfile.write(page1())
            return    
         else : # default: just send the file    
            filepath = self.path[1:] # remove leading '/'    
            if [].count(filepath)>0:
#               f = open( os.path.join(CWD, filepath), 'rb' )
                 #note that this potentially makes every file on your computer readable bny the internet
               self.send_response(200)
               self.send_header('Content-type',    'application/octet-stream')
               self.end_headers()
               self.wfile.write(f.read())
               f.close()
            else:
               self.send_response(200)
               self.send_header('Content-type',    'text/html')
               self.end_headers()
               self.wfile.write("<h5>Don't do that</h5>")
            return
         return # be sure not to fall into "except:" clause ?      
      except IOError as e :  
             # debug    
         print e
         self.send_error(404,'File Not Found: %s' % self.path)
   def do_POST(self):
            print("path: " + str(self.path))
#         try:
            ctype, pdict = cgi.parse_header(self.headers.getheader('content-type'))    
            print(ctype)
            if ctype == 'multipart/form-data' or ctype=='application/x-www-form-urlencoded':    
               fs = cgi.FieldStorage( fp = self.rfile,
                                      headers = self.headers, # headers_,
                                      environ={ 'REQUEST_METHOD':'POST' })
            else: raise Exception("Unexpected POST request")
            self.send_response(200)
            self.end_headers()
            dic=fs2dic(fs)
            
            if self.path=='/home':
                self.wfile.write(home(dic))
            else:
                print('ERROR: path {} is not programmed'.format(str(self.path)))
def main():
   try:
      server = HTTPServer(('', PORT), MyHandler)
      print 'started httpserver...'
      server.serve_forever()
   except KeyboardInterrupt:
      print '^C received, shutting down server'
      server.socket.close()
if __name__ == '__main__':
   main()




