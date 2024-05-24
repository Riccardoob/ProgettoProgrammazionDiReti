#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Apr 20 14:48:56 2024

@author: Riccardo Bartolini
0001068901
"""


import threading
import socket
import time
import sys
import tkinter as tkt


MAX_ATTEMPTS = 3
DELAY = 0.1
BUFFERSIZE = 1024   
HOST = 'localhost'
PORT = 8080
SERVER_CLOSED= "Server: Server disconnected type exit to quit..."

server_address = (HOST, PORT)

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)   # Inizialize  the socket


# global variable gui
root = tkt.Tk()
message = tkt.StringVar()
messages_frame = tkt.Frame(root)
scrollbar = tkt.Scrollbar(messages_frame)
message_list = tkt.Listbox(messages_frame, height=15, width=50, yscrollcommand=scrollbar.set)

first_message = True    #first message is the name
kill_thread = False     #stop the thread

receiving_thread_lock = threading.Lock()  
kill_thread_lock = threading.Lock()     

# Receive the message
def receive_message(event=None):
    while True:
        with kill_thread_lock:
            if kill_thread: 
                break
        try:
            message_received = client_socket.recv(BUFFERSIZE).decode("utf8")
            
            with receiving_thread_lock:
                message_list.insert(tkt.END, message_received)  
            
            if(message_received == SERVER_CLOSED):
                break
                
            else:
                print(message_received)
                
            with kill_thread_lock:
                if kill_thread: # the program is finish
                    break
                
        except OSError:
            break
        
        except Exception as e:  # exception of receivment of message
            print("\nError receiving message: ", e)
            
            with kill_thread_lock:
                if not kill_thread:
                    close_client()
                    
            break
        
        
# send the message to the server
def send_message(event=None):
    attempts = 0    
    global first_message
    
    while attempts <= MAX_ATTEMPTS:    
        attempts += 1
        
        with kill_thread_lock:
            if kill_thread:
                break
            
        try:
           message_to_send = message.get()  
           message.set("")
           
           if message_to_send == 'exit':    # client close
               close_client()
               break
           
           if first_message:
               if message_to_send.lower() == 'server':  
                   with receiving_thread_lock:
                       message_list.insert(tkt.END, "Change your name...")
                       
                   break
               
               else:
                   with receiving_thread_lock:
                       message_list.insert(tkt.END, "Welcome " + message_to_send + " :)")   
                
                   first_message = False
                    
           client_socket.send(message_to_send.encode()) 
           break 
       
        except BrokenPipeError as b:   
            print("\nError sending message: ", b)
            
            with kill_thread_lock:
                if not kill_thread:
                    close_client()
                    
            break
        
        except Exception as e:  # generic exception
            print("\nError sending message: ", e)
            
            if attempts >= MAX_ATTEMPTS:
                print("\nMax attempts reached...")
                
                with kill_thread_lock:
                    if not kill_thread:
                        close_client()
                        
                break
            
            else:
                wait() 

            
# starting the gui
def start_gui():
    root.title("Chat")
    
    scrollbar.pack(side=tkt.RIGHT, fill=tkt.Y) 
    
  
    message_list.pack(side=tkt.LEFT, fill=tkt.BOTH)
    message_list.pack()
    messages_frame.pack()
     
    
    entry_field = tkt.Entry(root, textvariable=message)
    entry_field.bind("<Return>", send_message)
    entry_field.pack()
    
    
    send_button = tkt.Button(root, text="Invio", command=send_message)
    send_button.pack()
    
    root.protocol("WM_DELETE_WINDOW", close_client)
    
   
    with receiving_thread_lock:
        message_list.insert(tkt.END, "Insert your name in the text box...")
        message_list.insert(tkt.END, "Type exit to quit...")
    
    root.mainloop() 
    

def wait():
    print("\nNew attempt...")
    time.sleep(DELAY)
    
# client close
def close_client(event=None):
    try: 
        root.after(1000, root.destroy())
    except Exception:
        print("\nGui closed")
    
    global kill_thread
    with kill_thread_lock:
        if not kill_thread:
            kill_thread = True
    
    client_socket.close()
    
    print("\nDisconnected from the server...")
    
    root.quit()
    sys.exit()
   
   
    
    
receiving_thread = threading.Thread(target=receive_message)


# main 
def main():
    con_attempts = 0
    global kill_thread
    
    while con_attempts <= MAX_ATTEMPTS:
        con_attempts += 1    
        
        with kill_thread_lock:
            if kill_thread:
                break
        
        try:
            client_socket.connect(server_address)   
            receiving_thread.start()   
            start_gui()    
            
        except ConnectionRefusedError as r:     
            print("\nServer is full. Connection rejected.")
            
            if con_attempts >= MAX_ATTEMPTS:    # max number of attempts reached
                print("\nMax attempts reached...")
                print("\nErrore connecting to server: ", r)
                
                with kill_thread_lock:
                    if not kill_thread:
                        close_client()
                        
                break
            
            else:
                con_attempts += 1
                wait()  # attempt of reconection
                
        except Exception as e:
            print("\nError:", e)
            with kill_thread_lock:
                if not kill_thread:
                    close_client()
            break
        
    
if __name__ == "__main__":
    main()

