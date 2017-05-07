from datetime import datetime, timedelta
import os


# Definim els valors d´ajustament dels temps originals. Valors positius o negatius.
offset_hores = 0
offset_mins = 0
offset_secs = 0

arxius_subs = []

for arxiu in os.listdir(os.getcwd()):
    if arxiu.endswith('.srt'):
        arxius_subs.append(arxiu)

def offsrt(subtitol, secs=0, mins=0, hores=0):
    arxiu_in = subtitol
    arxiu_out = arxiu_in + '_mod'

    fileres = [line for line in open(arxiu_in)]
    blocs = dict()
    ordinal = 0

    # Es genera el diccionari "blocs", que té com a keys els valors de les capçaleres dels subs (1, 2,...)
    # i com a valors els blocs de subtítol corresponents a cada capçalera (temps amb "->" i textos).
    for item in fileres:
        try:
            blocs[int(item)] = []
            ordinal += 1
        except:
            blocs[ordinal].append(item)

    # Verifiquem que l´offset definit no ens deixi els temps en negatiu.
    primer_temps = datetime(100,1,1,int(blocs[1][0][:2]),int(blocs[1][0][3:5]),int(blocs[1][0][6:8]))
    offset_aux = datetime(100,1,1,abs(offset_hores),abs(offset_mins),abs(offset_secs))
    if (offset_hores or offset_mins or offset_secs) < 0:
        assert primer_temps.time() >= offset_aux.time(), "El temps no pot ser negatiu"

    # Prenem seqüència per seqüència, corregim els valors de temps i escrivim els valors
    # corregits i la resta de informació a l´arxiu de sortida.
    with open(arxiu_out, 'a') as sortida:
        for seq in range(1, len(blocs)+1):
            sortida.write(str(seq)+'\n')

            hor_ppi_ini = int(blocs[seq][0][:2])
            min_ppi_ini = int(blocs[seq][0][3:5])
            sec_ppi_ini = int(blocs[seq][0][6:8])
            hor_fi_ini = int(blocs[seq][0][17:19])
            min_fi_ini = int(blocs[seq][0][20:22])
            sec_fi_ini = int(blocs[seq][0][23:25])
            
            temps_ppi_inicial = datetime(100, 1, 1, hor_ppi_ini, min_ppi_ini, sec_ppi_ini)
            temps_fin_inicial = datetime(100, 1, 1, hor_fi_ini, min_fi_ini, sec_fi_ini)

            offset = timedelta(seconds = offset_secs, minutes = offset_mins, hours = offset_hores)

            temps_ppi_final = temps_ppi_inicial + offset
            temps_fin_final = temps_fin_inicial + offset

            blocs[seq][0] = str(temps_ppi_final.time())+blocs[seq][0][8:17]\
                            +str(temps_fin_final.time())+blocs[seq][0][25:]

            for item in blocs[seq]:
                sortida.write(item)

for item in arxius_subs:
    offsrt(item, offset_secs, offset_mins, offset_hores)

