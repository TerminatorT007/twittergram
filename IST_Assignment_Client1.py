import tkinter as tk
from tkinter import messagebox
import socket
import threading

# Create top level window
window = tk.Tk()
window.title("Client")
username = " "

# Create frame
topFrame = tk.Frame(window)

# Create label
lblName = tk.Label(topFrame, text = "Name:").pack(side=tk.LEFT)
entName = tk.Entry(topFrame)
entName.pack(side=tk.LEFT)

# Create button to connect
btnConnect = tk.Button(topFrame, text="Connect", command=lambda : connect())
btnConnect.pack(side=tk.LEFT)
#btnConnect.bind('<Button-1>', connect)
topFrame.pack(side=tk.TOP)

#create frame
displayFrame = tk.Frame(window)
lblLine = tk.Label(displayFrame, text="*********************************************************************").pack()
variable = tk.StringVar()
variable.set("Everyone")

# Write client names to txt file
with open('client_names.txt', 'r') as reading:
    names = reading.readlines()
    print(names)
w = tk.OptionMenu(displayFrame, variable, value = 'Everyone')
w.pack()

# make scroll bar
scrollBar = tk.Scrollbar(displayFrame)
scrollBar.pack(side=tk.RIGHT, fill=tk.Y)
tkDisplay = tk.Text(displayFrame, height=20, width=55)

# Theming options
tkDisplay.tag_configure('tag-right', justify='right')
tkDisplay.pack(side=tk.LEFT, fill=tk.Y, padx=(5, 0))
tkDisplay.tag_config("tag_your_message", foreground="blue")

# Configure scroll bar
scrollBar.config(command=tkDisplay.yview)
tkDisplay.config(yscrollcommand=scrollBar.set, background="#F4F6F7", highlightbackground="grey", state="disabled")
displayFrame.pack(side=tk.TOP)


bottomFrame = tk.Frame(window)

# Readline
with open('clients.txt', 'r') as r:
    content = r.readline()

# Write messages to window
tkLabel = tk.Label(bottomFrame, text = f'Clients {content}')
tkLabel.pack()
tkMessage = tk.Text(bottomFrame, height=2, width=55)
tkMessage.pack(side=tk.LEFT, padx=(5, 13), pady=(5, 10))
tkMessage.config(highlightbackground="grey", state="disabled")
tkMessage.bind("<Return>", (lambda event: getChatMessage(tkMessage.get("1.0", tk.END))))
bottomFrame.pack(side=tk.BOTTOM)

# Make sure that clients have a name and can connect
def connect():
    global username, client
    if len(entName.get()) < 1:
        tk.messagebox.showerror(title="ERROR!!!", message="You MUST enter your first name <e.g. John>")
    else:
        username = entName.get()
        connect_to_server(username)


# network client
client = None
HOST_ADDR = "0.0.0.0"
HOST_PORT = 8080

# Connecting to server
def connect_to_server(name):
    global client, HOST_PORT, HOST_ADDR
    try:
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect((HOST_ADDR, HOST_PORT))
        client.send(name.encode()) # Send name to server after connecting

        entName.config(state=tk.DISABLED)
        btnConnect.config(state=tk.DISABLED)
        tkMessage.config(state=tk.NORMAL)

        # start a thread to keep receiving message from server
        # do not block the main thread :)
        threading._start_new_thread(receive_message_from_server, (client, "m"))
    except Exception as e:
        tk.messagebox.showerror(title="ERROR!!!", message="Cannot connect to host: " + HOST_ADDR + " on port: " + str(HOST_PORT) + " Server may be Unavailable. Try again later")


def receive_message_from_server(sck, m):
    while True:
        from_server = sck.recv(4096).decode()

        if not from_server: break

        # display message from server on the chat window

        # enable the display area and insert the text and then disable.
        # why? Apparently, tkinter does not allow us insert into a disabled Text widget :(
        texts = tkDisplay.get("1.0", tk.END).strip()
        tkDisplay.config(state=tk.NORMAL)
        if len(texts) < 1:
            tkDisplay.insert(tk.END, from_server)
        else:
            tkDisplay.insert(tk.END, "\n\n"+ from_server, 'tag-right')

        tkDisplay.config(state=tk.DISABLED)
        tkDisplay.see(tk.END)

        # print("Server says: " +from_server)

    sck.close()
    window.destroy()


def getChatMessage(msg):

    msg = msg.replace('\n', '')
    texts = tkDisplay.get("1.0", tk.END).strip()

    # enable the display area and insert the text and then disable.
    # why? Apparently, tkinter does not allow use insert into a disabled Text widget :(
    tkDisplay.config(state=tk.NORMAL)
    if len(texts) < 1:
        tkDisplay.insert(tk.END, "You->" + msg, "tag_your_message") # no line
    else:
        tkDisplay.insert(tk.END, "\n\n" + "You->" + msg, "tag_your_message")

    tkDisplay.config(state=tk.DISABLED)

    send_mssage_to_server(msg)

    tkDisplay.see(tk.END)
    tkMessage.delete('1.0', tk.END)

# Sending message_ to server
def send_mssage_to_server(msg):
    tkLabel.update()
    client_msg = str(msg)
    client.send(client_msg.encode())
    if msg == "exit":
        client.close()
        window.destroy()
    print("Sending message")


window.mainloop()