# La instrucció per a crear l´instal·lable és, des del directori on hi hagi el
# programa, el setup.py, etc. serà: "python setup.py bdist_msi".

import _thread, os, csv
from tkinter import *
from tkinter.filedialog import askopenfilename, askdirectory
from tkinter.messagebox import askokcancel
from win32com.client import Dispatch
from time import localtime as hr

# Font...
fonts = {'font_petit':('Arial', 16)}
# i un diccionari que contindrà els valors introduïts per l´usuari.
dades_usuari = {'arxiu_orig_logisdoc':0, 'arxiu_orig_fresenius':0,
                'directori_destí':0}

# Pantalla principal.
class Pant_ppal(Tk):
    def __init__(self):
        Tk.__init__(self)

        self.title('Logisdoc-Fresenius')
        self.config(bd=2)
        self.resizable(width=FALSE, height=FALSE)

        Label(self, text="Arxiu origen Logisdoc:",
                       font=fonts['font_petit']).grid(row=1,
                        column=1, sticky=W, padx=5, pady=5)
        Imatge_origen1 = PhotoImage(file='icones/Document.gif')
        orig1 = Button(self, image=Imatge_origen1, command=self.obrir_1)
        orig1.image = Imatge_origen1
        orig1.grid(row=1, column=2, sticky=W, padx=5, pady=5)

        Label(self, text="Arxiu origen Fresenius:",
                       font=fonts['font_petit']).grid(row=2,
                        column=1, sticky=W, padx=5)
        Imatge_origen2 = PhotoImage(file='icones/Document2.gif')
        orig2 = Button(self, image=Imatge_origen2, command=self.obrir_2)
        orig2.image = Imatge_origen2
        orig2.grid(row=2, column=2, sticky=W, padx=5)
      
        Label(self, text="Directori de destinació:",
                       font=fonts['font_petit']).grid(row=3,
                        column=1, sticky=W, padx=5, pady=5)
        Imatge_destí = PhotoImage(file='icones/Folder.gif')
        destí = Button(self, image=Imatge_destí, command=self.sel_directori)
        destí.image = Imatge_destí
        destí.grid(row=3, column=2, sticky=W, padx=5, pady=5)

        Imatge_exec = PhotoImage(file='icones/Start.gif')
        executa = Button(self, image=Imatge_exec, command=self.executa)
        executa.image = Imatge_exec
        executa.grid(row=4, column=1, sticky=W, padx=5, pady=5)
        Imatge_exit = PhotoImage(file='icones/Cancel.gif')
        surt = Button(self, image=Imatge_exit, command=self.surt)
        surt.image = Imatge_exit
        surt.grid(row=4, column=2, sticky=W, padx=5, pady=5)

    def obrir_1(self):
        nom_arxiu_1 = askopenfilename(title='Obrir')
        if nom_arxiu_1:
            dades_usuari['arxiu_orig_logisdoc'] = nom_arxiu_1
            
    def obrir_2(self):
        nom_arxiu_2 = askopenfilename()
        if nom_arxiu_2:
            dades_usuari['arxiu_orig_fresenius'] = nom_arxiu_2

    def sel_directori(self):
        dir_destí = askdirectory()
        if dir_destí:
            dades_usuari['directori_destí'] = dir_destí

    def surt(self):
        resposta = askokcancel('Verificant', '¿Segur que voleu sortir?')
        if resposta: Frame.quit(self)

    def executa(self):
        _thread.start_new_thread(processa, ())


def processa():
    # Aquestes dues línies han d´afegir-se en obrir un nou thread en
    # estar utilizant win32com.client. En cas contrari es rep un error
    # de CoInitialize...
    import pythoncom
    pythoncom.CoInitialize()
    
    ARXIU_ORIGEN_1 = dades_usuari['arxiu_orig_logisdoc']
    ARXIU_ORIGEN_2 = dades_usuari['arxiu_orig_fresenius']
    DIRECTORI_DEST = dades_usuari['directori_destí']
    SEPARADOR_CSV = ';'

    with open(ARXIU_ORIGEN_1, mode='r') as infile_1:
        reader_1 = csv.reader(infile_1, delimiter=SEPARADOR_CSV)
        llista_inicial_1 = [row for row in reader_1 if row]

    with open(ARXIU_ORIGEN_2, mode='r') as infile_2:
        reader_2 = csv.reader(infile_2, delimiter=SEPARADOR_CSV)
        llista_inicial_2 = [row for row in reader_2 if row]

    # Comptem el nº total de registres.
    TOTAL = len(llista_inicial_1)+len(llista_inicial_2)-1
    
    # Eliminem la capçalera de Logisdoc. Només conté nº albarà.
    llista_inicial_1 = llista_inicial_1[1:]

    # Prenem les capçaleres de l´arxiu de Fresenius i eliminem les
    # capçaleres de la llista.
    CAPÇALERES = llista_inicial_2[0]
    CAPÇALERES.append('¿Duplicado?')
    llista_inicial_2 = llista_inicial_2[1:]

    # Transformem una llista de llistes en una llista "simple".
    llista_inicial_1_mod = [int(item[0]) for item in llista_inicial_1]

    # Validem els nº d´albarà de Fresenius contra Logisdoc.
    for item in llista_inicial_2:
        if int(item[0]) in llista_inicial_1_mod:
            item.append('Sí')
            TOTAL -= 1
        else:
            item.append('Fresenius')

    # Els nº d'albarà de l'arxiu de Fresenius.
    llista_inicial_2_mod = [int(item[0]) for item in llista_inicial_2]

    # Identifiquem els albarans de logisdoc i els afegim a llista_inicial_2.
    for item in llista_inicial_1_mod:
        if item in llista_inicial_2_mod:
            pass
        else:
            llista_inicial_2.append([str(item),'n.a.','n.a.','n.a.','n.a.',
                                     'n.a.','n.a.','Logisdoc'])

    ARXIU_SORTIDA = str(hr()[0])+'-'+str(hr()[1])+'-'+str(hr()[2])+'_'+ \
                    str(hr()[3])+'.'+'{0:02}'.format(hr()[4])+'_'+os.getlogin()+'.xlsx'

    # Volcat a Excel.
    def excel():
        xl = Dispatch('Excel.Application')
        wb = xl.Workbooks.Add()
        xl.Visible = True
        ws = wb.Worksheets.Add()

        comptador_1 = 1
        for item in CAPÇALERES:
            ws.Cells(1,comptador_1).Value = item
            comptador_1 += 1
        ws.Range(ws.Cells(1, 1), ws.Cells(1, len(CAPÇALERES))).Font.Bold = True

        fila = 2
        comptador_2 = 1
        for k in llista_inicial_2:
            for j in k:
                ws.Cells(fila, comptador_2).Value = j
                comptador_2 += 1
            comptador_2 = 1
            fila += 1

        ws.Range("A2:A{0}".format(TOTAL)).NumberFormat = "0"
        ws.Columns.AutoFit()

        wb.SaveAs(os.path.normpath(os.path.join(DIRECTORI_DEST, ARXIU_SORTIDA)))

    excel()

Pant_ppal().mainloop()
