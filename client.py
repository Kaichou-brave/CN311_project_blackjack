import threading
import socket
from tkinter import messagebox
import tkinter
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


class Game:
    name = None
    frame = None
    hand = []
    hand_count = 0

    def __init__(self, initialize):
        self.name = initialize[0]
        self.hand = initialize[1]
        self.hand_count = len(initialize[1])

        card_frame = tkinter.Frame(
            mainWindow, relief="sunken", borderwidth=1, bg="black")
        card_frame.pack(ipadx=1,
                        ipady=1, fill='x', side="left")
        score_label = tkinter.IntVar()
        tkinter.Label(card_frame, text=self.name, bg="black",
                      fg="white").pack(side="left")
        tkinter.Label(card_frame, textvariable=score_label,
                      bg="black", fg="white").pack(side="left")
        frame = tkinter.Frame(card_frame, bg="black")
        frame.pack(side="left")
        for i in range(self.hand_count):
            self.add_card(self.hand[i])

    def update():
        None

    def add_card(self, img):
        tkinter.Label(self.frame, image=img[1],
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

    except Exception as e:
        None


def disconnect():
    global client
    exit_msg = "exit"
    client.send(exit_msg.encode())
    client.close()
    mainWindow.destroy()


def receive_data_from_server(sck, m):
    while True:
        from_server = sck.recv(4096).decode()

        if not from_server:
            break


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

# load data to display
data = [["jack", [cards["jack_spade"], cards["2_heart"], ]],
        ["black", [cards["5_spade"], ]],
        ["test", [cards["6_club"], cards["king_spade"], ]]
        ]
print(data)
player = []
for i in range(len(data)):
    play = Game(data[i])
    player.append(play)

botFrame = tkinter.Frame(mainWindow)
btnHit = tkinter.Button(botFrame, text="Hit", command=lambda: hit())
btnHit.pack(side=tkinter.LEFT)
btnStay = tkinter.Button(botFrame, text="Stay", command=lambda: stay())
btnStay.pack(side=tkinter.LEFT)
botFrame.pack(side=tkinter.BOTTOM)
displayFrame = tkinter.Frame(mainWindow)

mainWindow.mainloop()
