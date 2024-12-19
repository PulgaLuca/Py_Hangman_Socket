#!/usr/bin/env python3

import socket
import os
import sys, socket, subprocess

# Python program to illustrate use of exec to
# execute a given code as string.
 ############################################################################
# function illustrating how exec() functions.
def exec_code():
    LOC = """
def factorial(num):
    fact=1
    for i in range(1,num+1):
        fact = fact*i
    return fact
print(factorial(155000))
"""
    exec(LOC)
     
# Driver Code
############################################################################



PORT = 65432        # The TCP port used by the server
completionMessage = "FINITO"
# acquisisci indirizzo IP destinazione 
HOST = input("Indirizzo IP: ")
# HOST = '10.1.0.52'  # The server's hostname or IP address
# acquisisci nickname 
nickname = input("Nickname: ")
# nickname = "gamon"
# fai mani di gioco, per sempre   
while True:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        # connessione al server 
        s.connect((HOST, PORT))
        # spedisce il nickname
        s.sendall(nickname.encode())
        # (chiamata a recv() bloccante per default)
        parola = s.recv(1024).decode()
        print(parola)  # TODO togliere alla fine


        # gioco: indovina la parola  
        nLettere = len(parola)
        mostrata = '*' * nLettere
        while parola != mostrata:
            os.system('CLS')
            print(mostrata)
            fromUser = input("Lettera: ")
            onlyOneCharacter = fromUser[0]
            for i in range(0, nLettere): 
                c = parola[i]
                if c == onlyOneCharacter:
                    mostrata = mostrata[:i] + c + mostrata[i+1:]
        print ("TROVATA la parola '" + parola + "'!")
        # spedisce la stringa di fine gioco
        s.sendall(completionMessage.encode())
        # riceve la classifica 
        classifica = s.recv(1024).decode()
        print("Classifica")
        
        print(classifica)
    # fine, prossima giocata nel while True