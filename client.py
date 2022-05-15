
import threading
import socket
from tkinter import messagebox
import tkinter


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
            

row_num = 2


class Game:
    name = None
    hand = []

    def __init__(self, card_frame, initialize):
        global row_num
        self.name = initialize[0]
        self.hand = initialize[1]
        score_label = tkinter.IntVar()
        tkinter.Label(card_frame, text=self.name, bg="black",
                      fg="white").grid(row=row_num, column=0)
        tkinter.Label(card_frame, textvariable=score_label,
                      bg="black", fg="white").grid(row=row_num+1, column=0)
        row_num += 2

    def update():
        None


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
displayFrame = tkinter.Frame(mainWindow)

# load card images
cards = {}
load_images(cards)

print(cards)

card_frame = tkinter.Frame(
    mainWindow, relief="sunken", borderwidth=1, bg="black")
card_frame.pack(side=tkinter.LEFT)

# load initial player data
data = [["jack", [1, 2, 3]], ["black", [3, 2, 1]]]
player = []
for i in range(len(data)):
    play = Game(card_frame, data[i])
    player.append(play)

mainWindow.mainloop()
