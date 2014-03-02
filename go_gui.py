from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import string,cgi,time, json, random, copy, pickle, os
PORT=8090
import blockchain, state_library, go
import pybitcointools as pt

#privkey=pt.sha256("Brain Wallet Here")
#pubkey=pt.privtopub(privkey)
#state=state_library.current_state()
#my_count=state[pubkey]['count']
def spend(amount, pubkey):
    state=state_library.current_state()
    my_count=state[pubkey]['count']
#    tx={'type':'spend', 'id':pubkey, 'amount':2, 'count':my_count, 'pubkey':'0424823507306d62690158d76a55c060a5c36e51a6ae569681aee69291d09e4bed942e41fb8574f80e3b55a0dc8605a62223a1102e83210200593ba84c7b2eb677'}  
    tx={'type':'spend', 'id':pubkey, 'amount':amount, 'count':my_count, 'pubkey':pubkey}
    tx['signature']=pt.ecdsa_sign(blockchain.message2signObject(tx,['type','pubkey', 'amount', 'count']), privkey)
    print(blockchain.add_transaction(tx))
def newgame(opponent, name, pubkey_mine, privkey, size=19):
    state=state_library.current_state()
    if pubkey_mine not in state or 'count' not in state[pubkey_mine]:
        my_count=1
    else:
        my_count=state[pubkey_mine]['count']
    tx={'type':'newGame', 'id':pubkey_mine, 'game_name':name, 'pubkey_white':pubkey_mine, 'count':my_count, 'pubkey_black':opponent, 'whos_turn':'white', 'time':0, 'white':[], 'black':[], 'size':size}
    tx['signature']=pt.ecdsa_sign(blockchain.message2signObject(tx, go.newgame_sig_list), privkey)
    print(blockchain.add_transaction(tx))
    return name
def move(game_name, location, pubkey, privkey):#this function is way wrong
    state=state_library.current_state()
    board=state[game_name]
#    print('state: ' +str(state))
    if pubkey not in state:
        state[pubkey]={'count':1}
    if 'count' not in state[pubkey]:
        state[pubkey]['count']=1
    my_count=state[pubkey]['count']
    tx={'type':'nextTurn', 'id':pubkey, 'game_name':game_name, 'count':my_count, 'where':location, 'move_number':board['move_number']}
    tx['signature']=pt.ecdsa_sign(blockchain.message2signObject(tx, go.nextturn_sig_list), privkey)
    print(blockchain.add_transaction(tx))
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
def board(out, board, privkey):
    s=board['size']
    for j in range(s):
        out=out.format('<br>{}')
        for i in range(s):
            if [j, i] in board['white']:
                out=out.format(white)
            elif [j, i] in board['black']:
                out=out.format(black)
            else:
                img=empty_txt
                sp=[3,9,15]
                if s==19 and i in sp and j in sp:
                    img=dot_txt
                sp=[2,6]
                if s==9 and i in sp and j in sp:
                    img=dot_txt
                sp=[2,10]
                if s==13 and ((i in sp and j in sp) or (j==6 and i==6)):
                    img=dot_txt
                out=out.format('''<form style='display:inline;\n margin:0;\n padding:0;' name="play_a_move" action="/home" method="POST"><input type="image" src="{}" name="move" height="{}"><input type="hidden" name="move" value="{},{}"><input type="hidden" name="game" value="{}"><input type="hidden" name="privkey" value="{}"></form>{}'''.format(txt2src(img), str(piece_size), str(j), str(i), board['game_name'], privkey,'{}'))
#                    out=out.format(empty)
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
                a=newgame(dic['partner'], dic['game'], pubkey, privkey, int(dic['size']))
            except:
                a=newgame(dic['partner'], dic['game'], pubkey, privkey)
            active_games.append(a)
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
    for game in active_games:
        out=out.format("<h1>"+str(game)+"</h1>{}")
        print('state: ' +str(state))
        if game in state.keys():
            out=board(out, state[game], privkey)
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
    '''.format(privkey)))
    return out.format('')
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
def txt2src(txt):
    return "data:image/png;base64,"+txt
white=hex2htmlPicture(white_txt)
dot=hex2htmlPicture(dot_txt)
empty=hex2htmlPicture(empty_txt)
black=hex2htmlPicture(black_txt)
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




