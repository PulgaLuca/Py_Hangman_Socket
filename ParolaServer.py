#!/usr/bin/env python3

from inspect import classify_class_attrs
import os
import socket
import threading
from asyncio.windows_events import NULL
import datetime
from gettext import NullTranslations
import random
from tkinter.tix import Tree
from unicodedata import name 

# parametri generali
#HOST = '127.0.0.1'  # Standard loopback interface address (localhost)

HOST = ''           # stringa vuota per accettare connessioni da ogni
                    # interfaccia di rete del PC
PORT = 65432        # Port to listen on (non-privileged ports are > 1023)

tempoMaxAttesaIscrizioni = 15   # in s
tempoMaxAttesaGioco = 15    # in s

# dati comuni
# lista vuota di parole
parole = []  # verrà riempita dal codice

# classe che contiene le info sul client che si collega 
class clientInfo:
    socket = None
    nickname = None
    finishTime = None

gameStatus = "PrimaDiInizio"

# creazione dell'array di clientInfo, per tenerci i socket ed il resto
# lista vuota di clientInfo
infoAboutClients = []

completionMessage = "FINITO"

nParole = 0

programmaFinito = False

# Thread che gestisce il collegamento dei nuovi client 
def AttesaConnessioni():
    # creazione di nuovo socket listener
    listenerSocket = None
    listenerSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # associazione al socket della sua identificazione
    listenerSocket.bind((HOST, PORT))
    # timeout per chiudere l'attesa dopo la fine del tempo di iscrizione  
    #listenerSocket.settimeout(tempoMaxAttesaIscrizioni + 1)
    listenerSocket.settimeout(0.5)
    # ascolto sul port definito
    listenerSocket.listen()
    # per chiamate non bloccanti, mettere la seguente a (1)
    # (ed accettare che il programma vada male..)
    #listenerSocket.setblocking(0)
    

    # attesa della sottoscrizione dei giocatori
    while gameStatus == "Iscrizioni":
        # accetta le richieste di connessione dai socket client 
        # la connessione è accettata in un NUOVO socket: clientSocket
        # che viene messo nella lista  

        # socket.accept() restituisce DUE parametri: 
        # 1 - un nuovo socket da usare per le comunicazioni
        # 2 - l'indirizzo del client che si è connesso 
        try:
            clientSocket, clientSocketIdentification = listenerSocket.accept()    
            print('Collegato un client: (''indirizzo IP client'', port client) =', clientSocketIdentification)
            clientSocket.settimeout(tempoMaxAttesaGioco + 1)
            newClient = clientInfo() 
            newClient.socket = clientSocket

            # lettura del nickname proveniente dal client
            nick = clientSocket.recv(1024).decode()
            newClient.nickname = nick
            print("Giocatore: " + nick)
            # aggiunta delle info sul client alla lista di clientInfo 
            infoAboutClients.append(newClient)  
            # lancio del thread sul quale si faranno le comunicazioni 
            # con il client appena accettato
            threading.Thread(target=AscoltoDiUnClient, 
            args=(clientSocket, newClient), daemon=True).start()
        except socket.timeout:
            pass 
    # quando il tempo delle iscrizioni è finito, si può chiudere
    # il socket ed il thread 
    listenerSocket.close()
    
    # ora nessuno ascolta più sulla porta 
    # function finita = thread finito

# Thread che gestisce le comunicazioni con UN client durante il gioco
def AscoltoDiUnClient(socketGiocatore, infoGiocatore):
    # attende la fine delle iscrizioni
    while gameStatus == "Iscrizioni":
        pass           
    # attesa della comunicazione del completamento del gioco
    # da parte del client
    try:
        received = socketGiocatore.recv(1024).decode()  # bloccante! 
        # mi ricordo del tempo di arrivo
        if received == completionMessage:
            infoGiocatore.finishTime = datetime.datetime.now()
    except:
        pass
    # non serve più ascoltare, il thread di ascolto può finire

def nuovaParola(): 
    # sorteggio di una nuova parola
    abbastanzaLunga = False
    parola = ''
    # scarta le parole lunghe 5 caratteri o meno   
    while(not abbastanzaLunga): 
        numeroCasuale = random.randrange(0, nParole)
        print (numeroCasuale)
        parola = parole[numeroCasuale]
        # print("Parola: " + parola) 
        abbastanzaLunga = (len(parola) > 5)
    print("Parola: " + parola) 
    return parola

# Main program
os.system('CLS')
# inizializzazione dei dati per l'estrazione di una nuova parola
random.seed()
text_file = open(".\italian-word-list-total.csv", "r")
# vettore delle parole 
righe = text_file.read().split('\n')
# numero delle righe del file
nRighe = len(righe)
# isola la parola dalla riga, generando un array di sole  parole 
nRiga = 0
for riga in righe:
    campi = riga.split(';')
    if len(campi) > 1 and nRiga > 2:
        parola = campi[1]
        parole.append(parola)
    nRiga += 1
nParole = len(parole)

# fai mani di gioco, per sempre   
while True:   
    print("INIZIO DI UN NUOVO GIOCO")

    # lancio di un nuovo thread che gestisce il collegamento iniziale 
    # con questo server da parte di tutti i giocatori
    threading.Thread(target=AttesaConnessioni, daemon=True).start() 
    
    gameStatus = "Iscrizioni"

    # attesa che finisca il tempo per l'iscrizione  
    inizio = datetime.datetime.now() 
    datetimeDopo = inizio + datetime.timedelta(seconds=tempoMaxAttesaIscrizioni)
    print(inizio , datetimeDopo)
    print("Attesa della sottoscrizione dei giocatori")
    # mentre esegue questo ciclo il thread AttesaConnessioni() acquisisce 
    # dalla rete i nomi dei client ed i socket di collegamento e li mette in una lista.
    # per ogni client collegato crea anche un thread per le comunicazioni con esso  
    while datetime.datetime.now() < datetimeDopo: 
        pass
    gameStatus = "Sorteggio"

    # sorteggio di una nuova parola
    parola = nuovaParola()

    # visualizzazione dei nickname dei giocatori 
    # e spedizione della nuova parola a tutti i giocatori
    print("Elenco dei nickname dei giocatori")
    for info in infoAboutClients: 
        print("Giocatore: " + info.nickname)
        try:
            info.socket.sendall(parola.encode())
        except ConnectionResetError:
            pass # se l'utente chide il programma in questo momento 
    
    gameStatus = "Gioco"

    # attesa della fine del gioco
    # i thread di comunicazione con i giocatori (ComunicazioniConUnClient())
    # catturano le comunicazioni di fine gioco 
    adesso = datetime.datetime.now()
    datetimeDopo = adesso + datetime.timedelta(seconds=tempoMaxAttesaGioco)
    print("Attesa fine gioco")
    print(datetimeDopo)
    while datetime.datetime.now()  < datetimeDopo: 
        pass
            
    # fine del tempo di gioco: risultati
    gameStatus = "Fine"

    print("Gioco finito")
    # sort per generare la classifica, ammette valori None, che mette in fondo
    # l'ho trovata in Web, ma non ho capito come funziona l'espressione lambda su cui è basata  
    infoAboutClients.sort(key=lambda r: r.finishTime
        if (r and r.finishTime)
        else datetime.datetime.now())
    # produce la stringa da spedire ai client
    stringClassifica = ""
    for info in infoAboutClients:
        prompt = "Giocatore: " + str(info.nickname) + " Istante fine: " + str(info.finishTime)
        print(prompt)
        stringClassifica += prompt + "\n"

    # spedisce ai client la classifica 
    # poi chiude i loro socket e toglie le info dalla lista
    netString = ''
    for info in infoAboutClients:
        if not info.finishTime is None:
            try:    
                info.socket.sendall(stringClassifica.encode()) 
            except:
                pass
            info.socket.close()
            # infoAboutClients.remove(info)
    print ("Classifica")
    print(stringClassifica)
    # nella lista rimangono solo quelli che non hanno 
    # finito in tempo. Li avverto e chiudo anche i loro 
    # socket 
    print("Arrivati in ritardo")
    # visualizza l'elenco di tutti quelli arrivati in ritardo
    for info in infoAboutClients: 
        if info.finishTime is None:
            print(info.nickname)
    # cancellazione della lista
    infoAboutClients.clear()
    print()
    # fine del blocco while True, va alla prossima mano di gioco