import threading
import socket
from tkinter import messagebox
import tkinter
import pickle
from turtle import left


def load_images(card_images):
    suits = ['heart', 'club', 'diamond', 'spade']
    face_cards = ['jack', 'queen', 'king']

    if tkinter.TkVersion >= 8.6:
        extension = 'png'
    else:
        extension = 'ppm'

    # for each suit, retrieve the image for the cards
    for suit in suits:
        # first the number cards 1 to 10
        for card in range(1, 11):
            name = 'cards/{}_{}.{}'.format(str(card), suit, extension)
            image = tkinter.PhotoImage(file=name)
            card_images.update({f"{str(card)}_{suit}": (card, image, )})

        # next the face cards
        for card in face_cards:
            name = 'cards/{}_{}.{}'.format(str(card), suit, extension)
            image = tkinter.PhotoImage(file=name)
            card_images.update({f"{str(card)}_{suit}": (10, image, )})

# manage player in game contains card


class Game:
    name = None
    frame = None
    hand = []
    hand_count = 0

    def __init__(self, initialize):
        self.name = initialize[0]
        self.hand = initialize[1]
        print(self.hand)
        self.hand_count = len(initialize[1]) - 1

        self.frame = card_frame = tkinter.Frame(
            mainWindow, relief="sunken", borderwidth=1, bg="black")
        self.frame.pack(ipadx=1,
                        ipady=1, fill='x', side="left")

        score_label = tkinter.IntVar()
        tkinter.Label(card_frame, text=self.name, bg="black",
                      fg="white").pack(side="left")
        tkinter.Label(card_frame, textvariable=score_label,
                      bg="black", fg="white").pack(side="left")
        score_label.set(self.hand[-1])
        frame = tkinter.Frame(card_frame, bg="black")
        frame.pack(side="left")
        for i in range(self.hand_count):
            self.add_card(self.hand[i])

    def update(self, data):
        self.hand = data
        self.hand_count = len(data) - 1
        print(self.hand)
        frame = self.frame

        frame.pack_forget()
        frame.destroy()

        self.frame = card_frame = tkinter.Frame(
            mainWindow, relief="sunken", borderwidth=1, bg="black")
        self.frame.pack(ipadx=1,
                        ipady=1, fill='x', side="left")

        score_label = tkinter.IntVar()
        tkinter.Label(card_frame, text=self.name, bg="black",
                      fg="white").pack(side="left")
        tkinter.Label(card_frame, textvariable=score_label,
                      bg="black", fg="white").pack(side="left")
        score_label.set(self.hand[-1])

        frame = tkinter.Frame(card_frame, bg="black")
        frame.pack(side="left")
        for i in range(self.hand_count):
            self.add_card(self.hand[i])

    def add_card(self, img):
        global cards
        tkinter.Label(self.frame, image=cards[img][1],
                      relief="raised").pack(side="left")


def connect():
    global username, client
    if len(entName.get()) < 1:
        tkinter.messagebox.showerror(
            title="ERROR!!!", message="You MUST enter your first name <e.g. John>")
    else:
        username = entName.get()
        connect_to_server(username)


# network client
client = None
HOST_ADDR = "127.0.0.1"
HOST_PORT = 8080


def connect_to_server(name):
    global client, HOST_PORT, HOST_ADDR
    try:
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect((HOST_ADDR, HOST_PORT))
        client.send(name.encode())  # Send name to server after connecting

        entName.config(state=tkinter.DISABLED)
        btnConnect.config(state=tkinter.DISABLED)
        threading._start_new_thread(receive_data_from_server, (client, " "))

    except Exception as e:
        None


def disconnect():
    global client
    exit_msg = "exit"
    client.send(exit_msg.encode())
    client.close()
    mainWindow.destroy()


player = {}


def receive_data_from_server(sck, m):
    global player
    while True:
        data = pickle.loads(sck.recv(4096))
        print(f"Log {data[0]}")
        if data[0] == "init":
            gameData = [username, data[1]]
            play = Game(gameData)
            player.update({username: play})
        elif data[0] == "hit":
            play = player[username]
            play.update(data[1])
        if not data:
            break

# Legacy Code, I wrote it and I wanna keep it by Jj


def updateData():
    global data
    data = [[]]
    dataTest = []
    count = len(dataHand)

    for i in dataHand:
        dataTest.append(i)
        if count != 1:
            data.append([])
        count = count - 1
    for i in range(len(dataTest)):
        # print(dataTest[i]) #playerName
        data[i].append(dataTest[i])

    for i in range(len(dataTest)):
        playerHand = []
        cardData = []
        for j in range(len(dataHand[dataTest[i]])):
            cardData.append(dataHand[dataTest[i]][j])
            # print(dataHand[dataTest[i]][j])

        for k in range(len(cardData)):
            playerHand.append(cards[cardData[k]])
            # data[i].append(cards[cardData[k]])
        data[i].append(playerHand)

    # print(data)


def ready():
    global client
    msg = "ready"
    client.send(msg.encode())


def hit():
    global client
    msg = "hit"
    client.send(msg.encode())


def stay():
    global client
    msg = "stay"
    client.send(msg.encode())


# initialize tkinter application
mainWindow = tkinter.Tk()
mainWindow.title("Black Jack")
mainWindow.geometry("640x480")
mainWindow.configure(bg="green")

username = " "

topFrame = tkinter.Frame(mainWindow)
lblName = tkinter.Label(topFrame, text="Name:").pack(side=tkinter.LEFT)
entName = tkinter.Entry(topFrame)
entName.pack(side=tkinter.LEFT)
btnConnect = tkinter.Button(
    topFrame, text="Connect", command=lambda: connect())
btnConnect.pack(side=tkinter.LEFT)
btnLeave = tkinter.Button(topFrame, text="Leave", command=lambda: disconnect())
btnLeave.pack(side=tkinter.LEFT)
topFrame.pack(side=tkinter.TOP)

# load card images
cards = {}
load_images(cards)

# print(cards)


botFrame = tkinter.Frame(mainWindow)
btnReady = tkinter.Button(botFrame, text="Ready", command=lambda: ready())
btnReady.pack(side=tkinter.LEFT)
btnHit = tkinter.Button(botFrame, text="Hit", command=lambda: hit())
btnHit.pack(side=tkinter.LEFT)
btnStay = tkinter.Button(botFrame, text="Stay", command=lambda: stay())
btnStay.pack(side=tkinter.LEFT)
botFrame.pack(side=tkinter.BOTTOM)
displayFrame = tkinter.Frame(mainWindow)

mainWindow.mainloop()
