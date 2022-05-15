import tkinter as tk
import socket
import threading
import random
import pickle

window = tk.Tk()
window.title("Sever")

# Top frame consisting of two buttons widgets (i.e. btnStart, btnStop)
topFrame = tk.Frame(window)
btnStart = tk.Button(topFrame, text="Start", command=lambda: start_server())
btnStart.pack(side=tk.LEFT)
btnStop = tk.Button(topFrame, text="Stop",
                    command=lambda: stop_server(), state=tk.DISABLED)
btnStop.pack(side=tk.LEFT)
topFrame.pack(side=tk.TOP, pady=(5, 0))

# Middle frame consisting of two labels for displaying the host and port info
middleFrame = tk.Frame(window)
lblHost = tk.Label(middleFrame, text="Host: X.X.X.X")
lblHost.pack(side=tk.LEFT)
lblPort = tk.Label(middleFrame, text="Port:XXXX")
lblPort.pack(side=tk.LEFT)
middleFrame.pack(side=tk.TOP, pady=(5, 0))

# The client frame shows the client area
clientFrame = tk.Frame(window)
lblLine = tk.Label(clientFrame, text="**********Client List**********").pack()
scrollBar = tk.Scrollbar(clientFrame)
scrollBar.pack(side=tk.RIGHT, fill=tk.Y)
tkDisplay = tk.Text(clientFrame, height=15, width=30)
tkDisplay.pack(side=tk.LEFT, fill=tk.Y, padx=(5, 0))
scrollBar.config(command=tkDisplay.yview)
tkDisplay.config(yscrollcommand=scrollBar.set, background="#F4F6F7",
                 highlightbackground="grey", state="disabled")
clientFrame.pack(side=tk.BOTTOM, pady=(5, 10))


server = None
HOST_ADDR = "127.0.0.1"
HOST_PORT = 8080
client_name = " "
clients = []
clients_names = []


# Start server function
def start_server():
    global server, HOST_ADDR, HOST_PORT, cards, deck
    btnStart.config(state=tk.DISABLED)
    btnStop.config(state=tk.NORMAL)

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    server.bind((HOST_ADDR, HOST_PORT))
    server.listen(5)  # server is listening for client connection
    load_card(cards)
    deck = list(cards) + list(cards) + list(cards)
    random.shuffle(deck)
    threading._start_new_thread(accept_clients, (server, " "))

    lblHost["text"] = "Host: " + HOST_ADDR
    lblPort["text"] = "Port: " + str(HOST_PORT)

# Stop server function

def stop_server():
    global server
    btnStart.config(state=tk.NORMAL)
    btnStop.config(state=tk.DISABLED)
    window.destroy()


def accept_clients(the_server, y):
    while True:
        client, addr = the_server.accept()
        clients.append(client)

        threading._start_new_thread(blackjack, (client, addr))


stay = []
cards = []
player_hand = {}
deck = []

def blackjack(client_connection, client_ip_addr):
    global server, client_name, clients, stay

    client_name = client_connection.recv(4096).decode()

    clients_names.append(client_name)

    update_client_names_display(clients_names)  # update client names display

    status = True
    count_hit = 0
    while True:
        data = client_connection.recv(4096).decode()
        if not data:
            break
        if data == "exit":
            break

        count = 0
        if len(stay) != 0:
            if len(clients) == len(stay):
                # you need to sent all player data back to you also the result who win
                idx = get_client_index(clients, client_connection)
                sending_client_name = clients_names[idx]

                for c in clients:
                    if c != client_connection:
                        #c.send()
                        None
                        
        if status != False:
            if data == "stay":
                print(f"player {client_name}: Stay!")
                stay.append(1)
                status = False
                         
            if data == "hit" and count_hit < 5:
                count_hit += 1
                print(f"player {client_name}: Hit!")
                #deal_player(client_connection)
                # you need to sent your data that have already been update back to yours
                # client_connection.send()
            

    # find the client index then remove from both lists(client name list and connection list)
    idx = get_client_index(clients, client_connection)
    del clients_names[idx]
    del clients[idx]
    server_msg = "BYE!"
    client_connection.send(server_msg.encode())
    client_connection.close()

    update_client_names_display(clients_names)  # update client names display


# Return the index of the current client in the list of clients
def get_client_index(client_list, curr_client):
    idx = 0
    for conn in client_list:
        if conn == curr_client:
            break
        idx = idx + 1

    return idx


# Update client name display when a new client connects OR
# When a connected client disconnects
def update_client_names_display(name_list):
    tkDisplay.config(state=tk.NORMAL)
    tkDisplay.delete('1.0', tk.END)

    for c in name_list:
        tkDisplay.insert(tk.END, c+"\n")
    tkDisplay.config(state=tk.DISABLED)


def load_card(cards):
    suits = ['heart', 'club', 'diamond', 'spade']
    face_cards = ['jack', 'queen', 'king']
    for suit in suits:
        for card in range(1, 11):
            cards.append(f"{str(card)}_{suit}")

        for card in face_cards:
            cards.append(f"{str(card)}_{suit}")

# deal card
def deal_card():
    return deck.pop(0)

# initial card for player 
def initial_deal(client_connection):
    global client_name, clients, player_hand
    idx = get_client_index(clients, client_connection)
    hand_client_name = clients_names[idx]
    player_hand.update({hand_client_name: []})
    deal_player(client_connection)
    deal_player(client_connection)
    print(f" player {hand_client_name} inital hand : {player_hand[hand_client_name]}")

# deal more card to player
def deal_player(client_connection):
    global client_name, clients, player_hand
    idx = get_client_index(clients, client_connection)
    hand_client_name = clients_names[idx]
    list_cards = player_hand[hand_client_name]
    card = deal_card()
    list_cards.append(card)
    player_hand[hand_client_name] = list_cards


window.mainloop()
