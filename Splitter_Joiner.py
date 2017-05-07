#!/usr/bin/python3.4

# Programa que pren un arxiu, el llegeix en binari en trossos d´una mega que desa en una
# carpeta temporal(SPLITTER), i després el recrea(JOINER) a partir d´aquests trossos.

# Caldria afegir un gzip per als trossos que es creïn(per a un eventual enviament per xarxa)
# i el seu corresponent unzip per al JOINER. El JOINER també hauria d´eliminar la carpeta
# temporal creada per a emmagatzemar les parts.


import sys, os
from time import time

# Variables a personalitzar. Respectivament: arxiu origen, dir temporal,
# arxiu destí.

fromfile = 'Gotham.mp4'
todir = 'Gotham_Temp'
tofile = 'Fuckin_gotham.mp4'

kilobytes = 1024
megabytes = kilobytes * 1000
chunksize = int(1 * megabytes)                     


# SPLITTER


def split(fromfile, todir, chunksize=chunksize):
    if not os.path.exists(todir):                  
        os.mkdir(todir)                            
    else:
        for fname in os.listdir(todir):            
            os.remove(os.path.join(todir, fname))
    partnum = 0
    input = open(fromfile, 'rb')                   
    while True:                                    
        chunk = input.read(chunksize)              
        if not chunk: break
        partnum += 1
        filename = os.path.join(todir, ('part%08d' % partnum))
        fileobj  = open(filename, 'wb')
        fileobj.write(chunk)
        fileobj.close()                            
    input.close()
    return partnum    


absfrom, absto = map(os.path.abspath, [fromfile, todir])
print('Splitting', absfrom, 'to', absto, 'by', chunksize, '\n')
temps_inicial = time()

try:
    parts = split(fromfile, todir, chunksize)
except:
    print('Error during split:')
    print(sys.exc_info()[0], sys.exc_info()[1])
else:
    temps_final = time()
    temps_total = temps_final - temps_inicial
    print('Split finished:', parts, ' parts en {0:.2} segons'.format(temps_total),
          'parts are in', absto, '\n')


# JOINER

def join(todir, tofile):
    output = open(tofile, 'wb')
    parts  = os.listdir(todir)
    parts.sort()
    for filename in parts:
        filepath = os.path.join(todir, filename)
        fileobj  = open(filepath, 'rb')
        while True:
            filebytes = fileobj.read(kilobytes)
            if not filebytes: break
            output.write(filebytes)
        fileobj.close()
    output.close()


absfrom, absto = map(os.path.abspath, [todir, tofile])
print('Joining', absfrom, 'to make', absto, '\n')
temps_inicial_2 = time()

try:
    join(todir, tofile)
except:
    print('Error joining files:')
    print(sys.exc_info()[0], sys.exc_info()[1])
else:
    temps_final_2 = time()
    temps_total_2 = temps_final_2 - temps_inicial_2
    print('Completat en {0:.2} segons'.format(temps_total_2))
    print('Join complete: see', absto)
        
