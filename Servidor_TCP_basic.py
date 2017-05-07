#!/usr/bin/env python3.4

# Sembla funcionar perfectament!!!

import pickle
from socket import *

HOST = ''    # Indica a "bind()" que pot utiltzar qualsevol adreça disponible.
PORT = 27061
BUFSIZ = 4096
ADDR = (HOST, PORT)

tcpSerSock = socket(AF_INET, SOCK_STREAM)
tcpSerSock.bind(ADDR)
tcpSerSock.listen(5)

path_desti = r'/Users/tonipe/Desktop/'
arxiu_desti = []

print('esperant connexions...')
NomArxiuSocket_server, addr = tcpSerSock.accept()
print('...connectat des de:', addr)

def captura_arxiu():
    nom_arxiu_bytes = NomArxiuSocket_server.recv(BUFSIZ)
    nom_arxiu = pickle.loads(nom_arxiu_bytes)
    arxiu_desti.append(path_desti+nom_arxiu)
    print('...nom arxiu rebut: {0}'.format(arxiu_desti[0]))

captura_arxiu()
NomArxiuSocket_server.close()
print('...Esperant dades...')

DadesSocket_server, addr = tcpSerSock.accept()

def rep_arxiu():
    while True:
        with open(arxiu_desti[0], 'a+b') as arxiu_out:
            data = DadesSocket_server.recv(BUFSIZ)
            if not data:
                break
            arxiu_out.write(data)
    DadesSocket_server.close()
    print('...dades rebudes, arxiu creat...')
    
rep_arxiu()
tcpSerSock.close()

