import threading
import socket
from tkinter import messagebox
import tkinter
import pickle


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
    image = tkinter.PhotoImage(file='cards/back.png')
    card_images.update({"back.png": (None, image)})



status = True  # if False = you lose can't do anything else


class Game:
    name = None
    frame = None
    hand = []
    hand_count = 0
    positions = "left"

    def __init__(self, initialize):
        self.name = initialize[0]
        self.hand = initialize[1]
        print(self.hand)
        self.hand_count = len(initialize[1]) - 1

        self.frame = card_frame = tkinter.Frame(
            mainWindow, relief="sunken", borderwidth=1, bg="black")
        self.frame.pack(ipadx=1,
                        ipady=1, fill='x', side="top")

        score_label = tkinter.IntVar()
        tkinter.Label(card_frame, text=self.name, bg="black",
                      fg="white").pack(side="top")
        tkinter.Label(card_frame, textvariable=score_label,
                      bg="black", fg="white").pack(side="top")
        score_label.set(self.hand[-1])
        frame = tkinter.Frame(card_frame, bg="black")
        frame.pack(side=self.positions)
        for i in range(self.hand_count):
            self.add_card(self.hand[i])

    def update(self, data):
        self.hand = data
        self.hand_count = len(data) - 1
        print(self.hand)
        print(data)
        frame = self.frame

        frame.pack_forget()
        frame.destroy()

        self.frame = card_frame = tkinter.Frame(
            mainWindow, relief="sunken", borderwidth=1, bg="black")
        self.frame.pack(ipadx=1,
                        ipady=1, fill='x', side="top")

        score_label = tkinter.IntVar()
        tkinter.Label(card_frame, text=self.name, bg="black",
                      fg="white").pack(side="top")
        tkinter.Label(card_frame, textvariable=score_label,
                      bg="black", fg="white").pack(side="top")
        score_label.set(self.hand[-1])

        frame = tkinter.Frame(card_frame, bg="black")
        frame.pack(side=self.positions)
        for i in range(self.hand_count):
            self.add_card(self.hand[i])

    def add_card(self, img):
        global cards
        tkinter.Label(self.frame, image=cards[img][1],
                      relief="raised").pack(side=self.positions)

    def destroy(self):
        frame = self.frame

        frame.pack_forget()
        frame.destroy()


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
        check = client.recv(1024)
        if check.decode() == "max":
            client.close()
            tkinter.messagebox.showerror(
                title="ERROR!!!", message="Maximum connection")
        else:
            client.send(name.encode())  # Send name to server after connecting

            entName.config(state=tkinter.DISABLED)
            btnConnect.config(state=tkinter.DISABLED)
            threading._start_new_thread(
                receive_data_from_server, (client, " "))

    except Exception as e:
        None


def disconnect():
    global client
    exit_msg = "exit"
    client.send(exit_msg.encode())
    client.close()
    mainWindow.destroy()


player = {}
dealer = None


def receive_data_from_server(sck, m):
    global player, dealer, status
    draw_before_exceed_21 = True
    while True:
        data = pickle.loads(sck.recv(4096))

        print(f"Log {data[0]}")

        if ((data[0] == "win")):
            res = str(data[1])
            result_text.set("End Game Results" + " --> " + res)
            dealer.update(data[2])
            for i in data[3]:
                if (f"{i}" == username):
                    None
                else:
                    play = player[i]
                    play.update(data[3][i])
            play = player[username]
            play.update(data[3][username])

        if ((data[0] == "init") and (status == True)):
            result_text.set("Game Start !")

            dealerData = ["Dealer", data[3]]
            dealer = Game(dealerData)

            for i in range(len(data[1])):

                data1 = f"data --> {data[1][i]}"
                data2 = f"data --> {username}"

                if (data1 == data2):
                    None
                else:
                    print(data[1][i])
                    gameData = [data[1][i], data[2][data[1][i]]]
                    play = Game(gameData)
                    player.update({data[1][i]: play})

            ownData = [username, data[2][username]]
            player.update({username: Game(ownData)})

        elif ((data[0] == "hit") and (draw_before_exceed_21 == True)):
            text = (str("You drew: ") + str(data[1][-2]))
            result_text.set(text)
            play = player[username]
            play.update(data[1])
            if status == False:
                draw_before_exceed_21 = False
                result_text.set("You lose, your score exceeded 21")

        if data[0] == "busted":
            stay()
            result_text.set("You lose, your score exceeded 21 Note: auto stay")

        if data[0] == "end":
            status = True
            result_text.set("")
            for p in player:
                play = player[p].destroy()
            player = {}
            try:
                dealer.destroy()
            except Exception as e:
                None
            dealer = None

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


def check_condition():
    global status
    if (status == False):
        result_text.set("You Lose, All button can't be pressed.")
        return False
    else:
        return True


def ready():
    global client
    if (check_condition()):
        msg = "ready"
        client.send(msg.encode())


def hit():
    global client
    if (check_condition()):
        msg = "hit"
        client.send(msg.encode())


def stay():
    global client
    if (check_condition()):
        msg = "stay"
        client.send(msg.encode())


def new_game():
    global client
    if (check_condition()):
        msg = "new"
        client.send(msg.encode())


# initialize tkinter application
mainWindow = tkinter.Tk()
mainWindow.title("Black Jack")
mainWindow.geometry("1280x720")
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

# game messages
result_text = tkinter.StringVar()
result = tkinter.Label(mainWindow, textvariable=result_text)
result.pack(side=tkinter.TOP)

# print(cards)
botFrame = tkinter.Frame(mainWindow)
btnReady = tkinter.Button(botFrame, text="Ready", command=lambda: ready())
btnReady.pack(side=tkinter.LEFT)
btnHit = tkinter.Button(botFrame, text="Hit", command=lambda: hit())
btnHit.pack(side=tkinter.LEFT)
btnStay = tkinter.Button(botFrame, text="Stay", command=lambda: stay())
btnStay.pack(side=tkinter.LEFT)
btnNew = tkinter.Button(botFrame, text="New Game", command=lambda: new_game())
btnNew.pack(side=tkinter.LEFT)
botFrame.pack(side=tkinter.BOTTOM)
displayFrame = tkinter.Frame(mainWindow)

mainWindow.mainloop()
