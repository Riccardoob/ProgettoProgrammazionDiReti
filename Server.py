#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Apr 20 14:49:46 2024

@author: Riccardo Bartolini
0001068901
"""


import socket
import threading
import time
import sys


MAX_ATTEMPTS = 3    
DELAY = 0.1     
BACKLOG = 5     
BUFFERSIZE = 1024  
HOST = 'localhost'
PORT = 8080
SERVER_CLOSED = "Server: Server disconnected type exit to quit..."   

server_address = (HOST, PORT)

# manage of client list 
client_list = []
client_list_lock = threading.Lock()

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)   


# manage of  client
def handle_client(client):
    name = None
    
    while True:
        try:
            if not name:    
                name = client.recv(BUFFERSIZE).decode("utf8")
                if name:
                    print('\n' + name + " is ", client.getpeername())
                
            else:
                message = client.recv(BUFFERSIZE).decode("utf8")   
                if message == 'exit':
                    disconnect_client(client)
                    
                if message:
                    message = name + ": " +  message    
                    print('\n' + message)
                
                    send_to_all_clients(message)    
                
        except Exception as e:  
            print("\nError receiving message: ", e)
            
            with client_list_lock:  # mutex for the list
                disconnect_client(client)
            break


# send message to all the client connected
def send_to_all_clients(message):
    with client_list_lock:
        for client in client_list:
            attempts = 0
            
            while True:
                attempts += 1
                
                try:
                    client.send(message.encode())  
                    break
                
                except BrokenPipeError as b:    
                    print("\nError sending message to: ", str(client.getpeername()))
                    print("\nError type: ", b)
                    
                    with client_list_lock:
                        disconnect_client(client)
                    break
                    
                except Exception as e:  
                    print("\nError sending message to: ", e)
                    print("\nError type: ", e)
                    
                    if attempts >= MAX_ATTEMPTS:   
                        
                        with client_list_lock:
                            disconnect_client(client)
                        break
                    
                    else:
                        wait()  


# disconnection of client
def disconnect_client(client):
    if client.fileno() != -1:   # check the connection
        client.close()
    
    if client in client_list:   # check the client in the client list
        client_list.remove(client)



def wait():
    print("\nNew attempt...")
    time.sleep(DELAY)


# server close
def close_server(event=None):
    close = ''
    
    time.sleep(5)
    
    while not close == 'close':     
        close = input("\n")
        
    
    send_to_all_clients(SERVER_CLOSED)  
    
    
    with client_list_lock:      
        for client in client_list:
            disconnect_client(client)
            
    
    server_socket.close()   
    print("\nServer has been closed...")
    
    sys.exit()
    #server close


# main 
def main():
    server_socket.bind(server_address)
    server_socket.listen(BACKLOG)
    
    threading.Thread(target=close_server).start()  
    
    print("\nServer created...")
    
    while True:
        print("\nWaiting for connections...")
        try:
            connections_socket, client_address = server_socket.accept()    

            with client_list_lock:
                client_list.append(connections_socket)  
                
            threading.Thread(target=handle_client, args=(connections_socket, )).start()    
            
            print("\nClient connected: ", client_address)
            
        except Exception as e:
            print("\nError during server execution: ", e)
            break
    
    
if __name__ == "__main__":
    main()
                   
