# Importing necessary modules
import tkinter as tk
import socket
import threading

# Login Screen
def login_screen():
    # Create top-level root window
    global root
    root = tk.Tk()
    root.title("Login")
    root.geometry("350x200")
    root.resizable(False,False)

    # Create labels
    username = tk.Label(root, text = 'Username ')
    username.place(x = 40, y = 30)

    password = tk.Label(root, text = 'Password ')
    password.place(x = 40, y = 70)

    # Create entry fields
    user_variable = tk.StringVar()
    user_input = tk.Entry(root, textvariable = user_variable)
    user_input.place(x = 110, y = 28)

    pass_variable = tk.StringVar()
    pass_input = tk.Entry(root, textvariable = pass_variable, show = "•")
    pass_input.place(x = 110, y = 68)

    # Define button functions
    def close1():
        quit()

    def commence():
        if user_variable.get() == 'admin' and pass_variable.get() == 'twittergram':
            print('Welcome back to Twittergram!')
            root.destroy()
            root.quit()
            main_code()
        else:
            wrong = tk.Label(root, text = 'The username or password is incorrect.')
            wrong.place(x = 40, y = 110)
    
    # Create and assign buttons
    close = tk.Button(root, text = 'Cancel', command = close1)
    close.place(x = 40, y = 150)

    start = tk.Button(root, text = 'Enter', command = commence)
    start.place(x = 208, y = 150)

    # Run code in main loop
    root.mainloop()

# Main code
def main_code():
    counts = 1
    window = tk.Tk()
    window.title("Sever")

    # Top frame consisting of two buttons widgets (i.e. btnStart, btnStop)
    topFrame = tk.Frame(window)
    btnStart = tk.Button(topFrame, text="Connect", command=lambda : start_server())
    btnStart.pack(side=tk.LEFT)
    btnStop = tk.Button(topFrame, text="Stop", command=lambda : stop_server(), state=tk.DISABLED)
    btnStop.pack(side=tk.LEFT)
    topFrame.pack(side=tk.TOP, pady=(5, 0))

    # Middle frame consisting of two labels for displaying the host and port info
    middleFrame = tk.Frame(window)
    lblHost = tk.Label(middleFrame, text = "Host: X.X.X.X")
    lblHost.pack(side=tk.LEFT)
    lblPort = tk.Label(middleFrame, text = "Port:XXXX")
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
    tkDisplay.config(yscrollcommand=scrollBar.set, background="#F4F6F7", highlightbackground="grey", state="disabled")
    clientFrame.pack(side=tk.BOTTOM, pady=(5, 10))

    # Necessary server information

    server = None
    HOST_ADDR = "0.0.0.0"
    HOST_PORT = 8080
    client_name = " "
    clients = []
    clients_names = []


    # Start server function
    def start_server():
         # code is fine without this
        btnStart.config(state=tk.DISABLED)
        btnStop.config(state=tk.NORMAL)

        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        print(socket.AF_INET)
        print(socket.SOCK_STREAM)

        server.bind((HOST_ADDR, HOST_PORT))
        server.listen(5)  # server is listening for client connection

        threading._start_new_thread(accept_clients, (server, " "))
        with open('clients.txt', 'w') as txtfile:
            txtfile.write(str(counts))
            txtfile.close()

        lblHost["text"] = "Host: " + HOST_ADDR
        lblPort["text"] = "Port: " + str(HOST_PORT)


    # Stop server function
    def stop_server():
        global server
        btnStart.config(state=tk.NORMAL)
        btnStop.config(state=tk.DISABLED)

    # How to accept clients
    def accept_clients(the_server, y):
        nonlocal counts
        counts += 1
        with open('clients.txt', 'w') as txtfile:
            txtfile.write(str(counts))
            txtfile.close()
        # Keep track of number of clients
        while True:
            client, addr = the_server.accept()
            clients.append(client)
            # use a thread so as not to clog the gui thread
            threading._start_new_thread(send_receive_client_message, (client, addr))


    # Function to receive message from current client AND
    # Send that message to other clients
    def send_receive_client_message(client_connection, client_ip_addr):
        global server, client_name, clients, clients_addr
        client_msg = " "

        # send welcome message to client
        client_name  = client_connection.recv(4096).decode()
        welcome_msg = "Welcome " + client_name + ". Use 'exit' to quit"
        client_connection.send(welcome_msg.encode())

        clients_names.append(client_name)

        update_client_names_display(clients_names)  # update client names display


        while True:
            data = client_connection.recv(4096).decode()
            if not data: break
            if data == "exit": break

            client_msg = data

            idx = get_client_index(clients, client_connection)
            sending_client_name = clients_names[idx]

            for c in clients:
                if c != client_connection:
                    server_msg = str(sending_client_name + "->" + client_msg)
                    c.send(server_msg.encode())

        # find the client index then remove from both lists(client name list and connection list)
        idx = get_client_index(clients, client_connection)
        del clients_names[idx]
        del clients[idx]
        server_msg = "BYE!"
        client_connection.send(server_msg.encode())
        client_connection.close()

        with open('client_names.txt', 'w') as writing:
            writing.write(clients_names)
            writing.close()
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


    window.mainloop()
login_screen()