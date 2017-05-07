# Interfície gràfica del "SendIt!". Versió OOP.

# Resol els items ... de "ToDo List".
# 18/09/2016: Punt 9. L´indicador funciona(al servidor, de moment), però s´actualitza
# molt més lentament del que es transfereix l´arxiu!!! La fórmula està malament...


import _thread, queue, time, pickle, os, lzma
from tkinter import *
from socket import *
from tkinter.filedialog import askopenfilename, askdirectory
from tkinter.scrolledtext import ScrolledText
from tkinter.messagebox import askokcancel


# Fonts diverses...
fonts = {'font_notes':('Courier', 10),
         'font_text':('Courier', 12),
         'font_petit':('Courier', 16),
         'font_gran':('Courier', 22, 'bold')}
# i un diccionari que contindrà els valors introduïts per l´usuari.
dades_usuari = {'ip':0, 'arxiu_origen':0, 'directori_destí':0,
                'arxius_comprimits':0, 'arxiu_final':0, 'path_replica':0}
               
# Diverses dades generals i variables.

ip_actual = [(s.connect(('8.8.8.8', 80)), s.getsockname()[0], s.close())
               for s in [socket(AF_INET, SOCK_DGRAM)]][0][1]

text_ip = '(Intentarem connectar amb aquesta "ip")'
text_dir = 'El directori per defecte serà "/SendIt/Descarregues"'

percentatge_rebut = 0
percentatge_enviat = 0
mida_arxiu_rebut = 0
mida_arxiu_enviat = 0


# Cues de missatges dels Productors i lock.
cua_Enviar = queue.Queue()
cua_Rebre = queue.Queue()

lock = _thread.allocate_lock()

# Botó de Sortida.
class Exit(Frame):
    def __init__(self, parent=None):
        Frame.__init__(self, parent)
        self.grid()
        Boto_Exit = Button(self, text='Sortir', font=fonts['font_petit'],
                            command=self.surt)
        Boto_Exit.grid(row=1, column=1)

    def surt(self):
        resposta = askokcancel('Verificant', '¿Segur que voleu sortir?')
        if resposta: Frame.quit(self)
        

## CONSUMIDORS ##

# PANTALLA INICIAL.
class Pant_inicial(Tk):
    def __init__(self):
        Tk.__init__(self)

        self.geometry('350x160')
        self.title('SendIt! 1.0')
        self.config(bd=2)

        Label(self, text="¿Què voleu fer?",
              font=fonts['font_petit']).grid(row=1, column=1, sticky=N)
        self.var = StringVar()
        Radiobutton(self, text='Enviar un arxiu', font=fonts['font_gran'],
                    variable=self.var, value=1).grid(row=2, column=1, sticky=N)
        Radiobutton(self, text='Rebre un arxiu', font=fonts['font_gran'],
                    variable=self.var, value=2).grid(row=3, column=1, sticky=N)
        self.var.set(1)
        Button(self, text='Endavant', font=fonts['font_petit'],
               command=self.tria).grid(row=4, column=1, sticky=N)
        Exit(self).grid(row=5, column=1, sticky=S)

    def tria(self):
        if self.var.get() == '1':
            Enviar(self)
        else:
            Rebre(self)


# "ENVIAR".
class Enviar(Toplevel):
    def __init__(self, parent=None):
        Toplevel.__init__(self, parent)
        self.geometry('600x455')
        self.title('Enviar un arxiu')
        Label(self, width=10, text='Arxiu:',
              font=fonts['font_petit']).grid(row=1, column=1, sticky=W)
        Button(self, command=self.obrir).grid(row=1, column=2, sticky=W)
        Label(self, width=10, text='IP:',
              font=fonts['font_petit']).grid(row=2, column=1, sticky=W)
        self.var = StringVar()
        Entry(self, width=15, textvariable=self.var).grid(row=2, column=2,
                                                          sticky=W)
        self.var.set('1xx.xxx.xx.x..')
        Label(self, text=text_ip,
              font=fonts['font_notes']).grid(row=3, column=2, sticky=W)
        Button(self, width=10, height=3, command=self.valida_n_go_Enviar, text='Endavant',
               font=fonts['font_petit']).grid(row=4, column=1, sticky=W)
        Button(self, width=10, height=3, command=self.cancela_Enviar, text='Cancel',
               font=fonts['font_petit']).grid(row=4, column=2, sticky=W)
        Finestra_missatges(self, cua=cua_Enviar).grid(row=5, column=1, columnspan=2)
        # Fem la finestra modal.
        self.focus_set()            
        self.grab_set()
        self.wait_window()

    def obrir(self):
        nom_arxiu = askopenfilename()
        if nom_arxiu:
            dades_usuari['arxiu_origen'] = nom_arxiu

    def cancela_Enviar(self):
        dades_usuari['ip'] = 0
        dades_usuari['arxiu_origen'] = 0
        self.destroy()

    def valida_n_go_Enviar(self):
        def valida_Enviar(self):
            try:
                inet_aton(self.var.get())
                dades_usuari['ip'] = self.var.get()    
            except:
                cua_Enviar.put('ERROR: Format incorrecte per a l´adreça IP...\n')
            if dades_usuari['arxiu_origen'] == 0:
                cua_Enviar.put('ERROR: No s´ha seleccionat cap arxiu...\n')
        def go_Enviar(self):
            if dades_usuari['ip'] and dades_usuari['arxiu_origen']:
                nom_arxiu_comprimit()
                _thread.start_new_thread(comprimeix, (dades_usuari['arxiu_origen'],
                                           dades_usuari['arxius_comprimits']))
                _thread.start_new_thread(arrenca_client, ())    
            else:
                pass
        valida_Enviar(self)
        go_Enviar(self)

                        
# "REBRE".
class Rebre(Toplevel):
    def __init__(self, parent=None):
        Toplevel.__init__(self, parent)
        self.geometry('590x420')
        self.title('Rebre un arxiu')
        Label(self, width=15, text='Destinació',
              font=fonts['font_petit']).grid(row=1, column=1, sticky=W)
        Button(self, command=self.sel_directori).grid(row=1, column=2, sticky=W)
        Label(self, text=text_dir,
              font=fonts['font_notes']).grid(row=2, column=2, sticky=W)
        Button(self, width=10, height=3, command=self.valida_n_go_Rebre, text='Endavant',
               font=fonts['font_petit']).grid(row=3, column=1, sticky=W)
        Button(self, width=10, height=3, command=self.cancela_Rebre, text='Cancel',
               font=fonts['font_petit']).grid(row=3, column=2, sticky=W)
        Finestra_missatges(self, cua=cua_Rebre).grid(row=4, column=1, columnspan=2)
        # Fem la finestra modal.
        self.focus_set()            
        self.grab_set()
        self.wait_window()

    def sel_directori(self):
        dir_desti = askdirectory()
        if dir_desti:
            dades_usuari['directori_destí'] = dir_desti

    def cancela_Rebre(self):
        # En haver-hi valor per defecte, cal ressetejar en cas de "Cancel".
        dades_usuari['directori_destí'] = 0 
        self.destroy()
        
    def valida_n_go_Rebre(self):
        if dades_usuari['directori_destí'] == 0:
            cua_Rebre.put('...no s´ha seleccionat cap directori...\n'
                          '...s´utilitzarà directori per defecte...\n')
            dades_usuari['directori_destí'] = os.getcwd()
            todir = ''.join((dades_usuari['directori_destí'], r'/Descarregues/'))
            if not os.path.exists(todir):
                os.mkdir(todir)
        else:
            todir = dades_usuari['directori_destí']
        # Llancem el servidor en un nou fil per a evitar bloquejar la gui.
        _thread.start_new_thread(arrenca_servidor, ())    


# "FINESTRA MISSATGES". Prendrà dades d´una Queue de missatges d´error
# i els mostrarà a l´ScrolledText.
class Finestra_missatges(ScrolledText):
    def __init__(self, parent=None, cua=None):
        ScrolledText.__init__(self, parent)
        self.cua = cua
        self.config(relief=SUNKEN, bg= 'BLACK', fg='WHITE',
                     font=fonts['font_text'])
        self.config(state=NORMAL)
        self.insert(INSERT, '...\n')
        self.config(state=DISABLED)
        self.consumidor_info()

    def consumidor_info(self):
        try:
            missatges = self.cua.get(block=False)
        except queue.Empty:
            pass
        else:
            if missatges.startswith('Progrés'):
                Inici = self.index("insert linestart")
                Final = self.index("insert lineend")
                self.config(state=NORMAL)
                self.delete(Inici, Final)
                self.insert(Inici, str(missatges))
                self.config(state=DISABLED)
            else:
                on_som = self.index(INSERT)
                if on_som.endswith('.0'):
                    self.config(state=NORMAL)
                    self.insert(INSERT, str(missatges))
                    self.config(state=DISABLED)
                else:
                    self.config(state=NORMAL)
                    self.insert(INSERT, '\n')
                    self.insert(INSERT, str(missatges))
                    self.config(state=DISABLED)
        self.after(100, self.consumidor_info)


## PRODUCTORS ##

# RECEPTOR TCP. 
PORT = 27061
BUFSIZ = 4096

def arrenca_servidor():
    HOST_Rebre = ''
    ADDR_Rebre = (HOST_Rebre, PORT)

    tcpSerSock = socket(AF_INET, SOCK_STREAM)
    tcpSerSock.bind(ADDR_Rebre)
    tcpSerSock.listen(5)

    path_desti = dades_usuari['directori_destí']+'/'
    arxiu_desti_TCP = []

    cua_Rebre.put('...esperant connexions...\n')
    NomArxiuSocket_server, addr_server1 = tcpSerSock.accept()
    cua_Rebre.put('...connectat des de:', addr_server1,'\n')

    def captura_arxiu():
        nom_arxiu_bytes = NomArxiuSocket_server.recv(BUFSIZ)
        nom_arxiu_desti = pickle.loads(nom_arxiu_bytes)
        dades_usuari['arxiu_final'] = nom_arxiu_desti
        arxiu_desti_TCP.append(path_desti+nom_arxiu_desti)
        cua_Rebre.put('...nom arxiu rebut: {0}\n'.format(arxiu_desti_TCP[0]))

    captura_arxiu()
    NomArxiuSocket_server.close()
    cua_Rebre.put('...esperant dades...\n')

    ######

    MidaSocket_server, addr = tcpSerSock.accept()

    def rep_mida_arxiu():
        mida_arxiu_bytes = MidaSocket_server.recv(BUFSIZ)
        global mida_arxiu
        mida_arxiu = pickle.loads(mida_arxiu_bytes)

    rep_mida_arxiu()
    MidaSocket_server.close()

    ######

    DadesSocket_server, addr_server2 = tcpSerSock.accept()

    nom_arxiu_descomprimir()

    def rep_arxiu():
        while True:
            with open(dades_usuari['path_replica'], 'a+b') as arxiu_out:
                dades_rep_arxiu = DadesSocket_server.recv(BUFSIZ)
                if not dades_rep_arxiu:
                    break
                arxiu_out.write(dades_rep_arxiu)
                global percentatge_rebut
                percentatge_rebut += (BUFSIZ/mida_arxiu) * 100
                cua_Rebre.put('Progrés: {0:02}%'.format(int(percentatge_rebut)))
                
        DadesSocket_server.close()
        cua_Rebre.put('...dades rebudes, descomprimint...\n')
        _thread.start_new_thread(descomprimeix, (dades_usuari['path_replica'],
                                dades_usuari['directori_destí']+dades_usuari['arxiu_final']))
        
    rep_arxiu()
    tcpSerSock.close()


# EMISSOR TCP.
def arrenca_client():
    # arrenca_servidor no té lock i no veig perquè el necessito aquí...
    #lock.acquire()
    HOST_Enviar = dades_usuari['ip']
    ADDR_Enviar = (HOST_Enviar, PORT)

    try:
        NomArxiuSocket = socket(AF_INET, SOCK_STREAM)
        NomArxiuSocket.connect(ADDR_Enviar)

        arxiu_origen_TCP = dades_usuari['arxius_comprimits']

        def envia_nom_arxiu():
            nom_arxiu_origen = os.path.basename(dades_usuari['arxiu_origen'])
            dades_envianomarxiu = pickle.dumps(nom_arxiu_origen)
            NomArxiuSocket.send(dades_envianomarxiu)

        envia_nom_arxiu()
        NomArxiuSocket.close()

        ######

        MidaArxiuSocket = socket(AF_INET, SOCK_STREAM)
        MidaArxiuSocket.connect(ADDR_Enviar)

        def envia_mida_arxiu():
            global mida_arxiu_enviat
            mida_arxiu_enviat = os.path.getsize(dades_usuari['arxius_comprimits'])
            dades_mida = pickle.dumps(mida_arxiu_enviat)
            MidaArxiuSocket.send(dades_mida)

        envia_mida_arxiu()
        MidaArxiuSocket.close()

        ######

        DadesSocket = socket(AF_INET, SOCK_STREAM)
        DadesSocket.connect(ADDR_Enviar)

        def envia_arxiu():
            with open(arxiu_origen_TCP, 'rb') as arxiu_in:
                while True:
                    dades_enviaarxiu = arxiu_in.read(BUFSIZ)
                    if not dades_enviaarxiu:
                        break
                    DadesSocket.send(dades_enviaarxiu)
                cua_Enviar.put('Arxiu enviat!!!...\n')
                # Eliminem l´arxiu comprimit.
                os.remove(arxiu_origen_TCP)
        
        envia_arxiu()    
        DadesSocket.close()
    except:
        cua_Enviar.put('ERROR: Connexió rebutjada...\n')
    #lock.release()

# COMPRESSOR LZMA.
# Obtenim la versió ".xz" de l´arxiu a enviar...
def nom_arxiu_comprimit():
    nom_arxiu_a_enviar = os.path.basename(dades_usuari['arxiu_origen'])
    nom_xz = ''.join((os.path.splitext(nom_arxiu_a_enviar)[0], '.xz'))
    arxiu_origen_aux = dades_usuari['arxiu_origen'].split('/')
    arxiu_origen_aux.pop(-1)
    arxiu_origen_aux.append(nom_xz)
    dades_usuari['arxius_comprimits'] = '/'.join(arxiu_origen_aux) 

# ...i el comprimim.
def comprimeix(arxiu_original, arxiu_comprimit):
    lock.acquire()
    cua_Enviar.put('...comprimint arxiu...\n')
    with open(arxiu_original, 'rb') as llegir:
        dades_lzma = llegir.read()

    with lzma.open(arxiu_comprimit, 'w') as comprimir:
        # arxiu_comprimit tindrà extensió ".xz"
        comprimir.write(dades_lzma)
    cua_Enviar.put('...arxiu comprimit, procedim a enviar-lo...\n')
    lock.release()


# DESCOMPRESSOR LZMA.
# Obtenim la versió "normalitzada" de l´arxiu comprimit...
def nom_arxiu_descomprimir():
    nom_arxiu_a_rebre = dades_usuari['arxiu_final']
    nom_xz_rebre = ''.join((os.path.splitext(nom_arxiu_a_rebre)[0], '.xz'))
    dades_usuari['path_replica'] = dades_usuari['directori_destí'] + nom_xz_rebre
    
# ...i descomprimim l´arxiu.
def descomprimeix(arxiu_comprimit, arxiu_replica):
    lock.acquire()
    with lzma.open(arxiu_comprimit) as obrir:
        contingut_arxiu = obrir.read()

    with open(arxiu_replica, 'wb') as escriure:
        escriure.write(contingut_arxiu)
    cua_Rebre.put('Arxiu descomprimit!!!...\n')
    # Eliminem l´arxiu comprimit.
    os.remove(dades_usuari['path_replica'])
    lock.release()

Pant_inicial().mainloop()
