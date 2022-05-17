from concurrent.futures import wait
import tkinter as tk
import socket
import threading
import random
import pickle
import datetime
import time

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
    deck = list(cards)
    random.shuffle(deck)
    # Do this cause we want that server can do other things when it waiting for clients to be connected
    threading._start_new_thread(accept_clients, (server,))

    lblHost["text"] = "Host: " + HOST_ADDR
    lblPort["text"] = "Port: " + str(HOST_PORT)


# Stop server function
def stop_server():
    global server
    btnStart.config(state=tk.NORMAL)
    btnStop.config(state=tk.DISABLED)
    window.destroy()


def accept_clients(server):
    while True:
        client, addr = server.accept()
        clients.append(client)

        threading._start_new_thread(blackjack, (client, addr))


stay = []
ready = []
cards = []
player_hand = {}
deck = []
dealer_hand = []


def blackjack(client_connection, client_ip_addr):
    global server, clients_names, client_name, clients, ready, stay

    client_name = client_connection.recv(4096).decode()

    clients_names.append(client_name)
    print(client_name + " connected")
    update_client_names_display(clients_names)  # update client names display

    status = True
    deal_count = 0
    new_game_status = True
    while True:
        data = client_connection.recv(4096).decode()
        if not data:
            break
        if data == "exit":
            break

        print(f"recieve data: {data} -- {client_name}")

        # check in any client that they're all ready to play then initial deal to any client and broadcast to them
        if data == "ready":
            ready.append(1)
            if len(ready) == len(clients):
                initial_deal()
                for idx, c in enumerate(clients):
                    print()
                    c.send(pickle.dumps(
                        ["init", player_hand[clients_names[idx]]]))

        count = 0
        if len(stay) != 0:
            if len(clients) == len(stay):

                # you need to sent all player data back to you also the result who win
                this_client_name = get_name_client(clients, client_connection)

                for c in clients:
                    if c != client_connection:
                        # c.send()
                        None

        if status != False:
            if data == "stay":
                stay.append(1)
                status = False

            if data == "hit":
                this_client_name = get_name_client(clients, client_connection)
                deal_player(this_client_name)

                if player_hand[client_name][-1] > 21:
                    client_connection.send(pickle.dumps(
                        ["busted", player_hand[this_client_name]]))

                print(
                    f" player {this_client_name} hand : {player_hand[this_client_name]}")

                # send your own hand back to you
                client_connection.send(pickle.dumps(
                    ["hit", player_hand[this_client_name]]))

    # find the client index then remove from both lists(client name list and connection list)
    idx = get_client_index(clients, client_connection)
    del clients_names[idx]
    del clients[idx]
    del ready[-1]
    client_connection.close()

    update_client_names_display(clients_names)  # update client names display


# Return the name of the current client in the list of name

def get_name_client(client_list, curr_client):
    idx = get_client_index(client_list, curr_client)
    return clients_names[idx]


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
            data = f"{str(card)}_{suit}"
            cards.append([data, card])

        for card in face_cards:
            data = f"{str(card)}_{suit}"
            cards.append([data, 10])
    # print(cards)
# deal card


def deal_card():
    return deck.pop(0)

# initial card for player


def initial_deal():
    # global client_name, clients, player_hand
    # idx = get_client_index(clients, client_connection)
    # hand_client_name = clients_names[idx]
    # player_hand.update({hand_client_name: []})
    # deal_player(client_connection)
    # deal_player(client_connection)
    # print(
    # f" player {hand_client_name} inital hand : {player_hand[hand_client_name]}")
    for i in range(2):
        for client in clients_names:
            deal_player(client)


# deal more card to player
def deal_player(hand_client_name):
    try:
        list_cards = player_hand[hand_client_name]
    except KeyError:
        list_cards = []
        player_hand[hand_client_name] = list_cards
    card = deal_card()
    pScore = score(hand_client_name, card)
    if list_cards != []:
        del list_cards[-1]
    list_cards.append(card[0])
    list_cards.append(pScore)
    player_hand[hand_client_name] = list_cards


def score(user, card):
    global player_hand
    score = 0
    if player_hand[user] != []:
        score = player_hand[user][-1]
        score += card[1]
    else:
        score = card[1]
    return score


window.mainloop()
