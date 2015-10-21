__author__ = 'andrew'

#GUI Libs
from tkinter import *
from tkinter import ttk

#App Libs
import logging
from crypto import encrypt, decrypt, generate_keystream, generate_init_vector, generateAorB
from messenger import Messenger
import socket
import sys
from threading import Thread
from sessionmanager import *
import traceback
import queue
from threading import Timer



class Gui:
    LOG_FILE_NAME = "log.txt"

    PROGRAM_NAME = "Best Assignment 3 lol kiddingnotkidding. Hi Illdar :)"
    
    #Initial Screen 
    CHOICE_LBL = "Choose the option you would like to run the code under: "
    SERVER_BTN = "Server"
    CLIENT_BTN = "Client"

    #Client Screen
    CLT_CONFIG_LBL = "Client Configuration Parameters: "

    #Server Screen
    SVR_CONFIG_LBL = "Server Configuration Parameters: "

    #Client/Server Shared Screen
    IP_LBL = "IP"
    IP_PLACEHOLDER_TXT = '127.0.0.1'
    PORT_LBL = "Port"
    PORT_PLACEHOLDER_TXT = "80"
    MASTERKEY_LBL = "Master Key"
    MASTERKEY_PLACEHOLDER_TXT = "Make one up, lazy"
    OK_BTN = "OK"

    #Messaging Screen
    SENT_MESSAGE_DEFAULT = "You have not received any messages yet."
    MSG_INSPECTOR_DEFAULT = "You may expand a messages content here."
    SEND_BTN_TXT = "Send"
    POLL_DELAY_MS = 150


    def __init__(self):
        # Variables for setting up the server and the client
        self.ip = ""
        self.port = ""
        self.masterKey = ""
        self.rawMsg = ""
        self.errorMessage = ""
        self.g=-1

        # List to hold references to all the current widgets
        self.widgets = []
        pass

    def run(self):
        root, mainframe = self.initGUI()
        root.mainloop()
        pass

    """
    Initiate all non-GUI related parts of the system during
    the initial setup.
    params:
        N/A
    returns:
    after:
        self.log: handle to the logger
    """
    def initSystem(self): 
        # set up logging, create a logger for the local scope
        init_logger(self.LOG_FILE_NAME)
        self.log = logging.getLogger(__name__)
        pass

    def initGUI(self):
        #Init non-GUI related elements of the system
        self.initSystem()

        #Initialise the window
        self.root = Tk()
        self.root.title(self.PROGRAM_NAME)
        self.root.minsize(width=600, height=600)
        self.root.maxsize(width=600, height=600)

        #Initialize the root Frame
        mainframe = ttk.Frame(self.root, padding="3 3 12 12")
        mainframe.grid(column=0, row=0, sticky=(N, W, E, S))
        mainframe.columnconfigure(0, weight=1)
        mainframe.rowconfigure(0, weight=1)

        #Initialize the first Screen 
        self.initWelcomeScreenGUI(mainframe)

        #Add all elements to the GUI
        for child in mainframe.winfo_children(): child.grid_configure(padx=5, pady=5)

        return [self.root, mainframe]

    def hideAllCurrentWidgets(self):
        pass

    """
    Add necessary elements for the first UI. Allows the user
    to select which mode of operation they would like to run the
    program in.
    params: 
        @parentFrame: the parent in the GUI hierarchy where the widgets 
        will be added
    returns: N/A
    """
    def initWelcomeScreenGUI(self, parentFrame):
        a = ttk.Label(parentFrame, text=self.errorMessage + "\n" + self.CHOICE_LBL)
        a.grid(column=2, row=1, sticky=W)
        self.widgets.append(a)

        b = ttk.Button(parentFrame, text=self.SERVER_BTN, command= lambda: self.initServerGUI(parentFrame))
        b.grid(column=1, row=5, sticky=W)
        self.widgets.append(b)

        c = ttk.Button(parentFrame, text=self.CLIENT_BTN, command= lambda: self.initClientGUI(parentFrame))
        c.grid(column=3, row=5, sticky=W)
        self.widgets.append(c)

    """
    Add necessary UI elements for the client configuration options. 
    Allows the user to input the IP Address, the port and the master key.
    params: 
        @parentFrame: the parent in the GUI hierarchy where the widgets 
        will be added
    returns: N/A
    """
    def initClientGUI(self, parentFrame):
        self.initConfigurationGUI(parentFrame, False)

    """
    Add necessary UI elements for the server configuration options. 
    Allows the user to see the IP Address, and inputthe port and the master key.
    params: 
        @parentFrame: the parent in the GUI hierarchy where the widgets 
        will be added
    returns: N/A
    """
    def initServerGUI(self, parentFrame):
        self.initConfigurationGUI(parentFrame, True)


    def initConfigurationGUI(self, parentFrame, isServer):
        self.clearScreen()

        self.ip = StringVar()
        self.port = StringVar()
        self.masterKey = StringVar()

        a = ttk.Label(parentFrame, text=self.CLT_CONFIG_LBL)
        a.grid(column=2, row=1, sticky=W)
        self.widgets.append(a)

        b = ttk.Label(parentFrame, text=self.IP_LBL)
        b.grid(column=2, row=3, sticky=W)
        self.widgets.append(b)

        if(not isServer):
            ipEntry = ttk.Entry(parentFrame, width=7, textvariable=self.ip)
            ipEntry.grid(column=3, row=3, sticky=W)
            self.widgets.append(ipEntry)

        c = ttk.Label(parentFrame, text=self.PORT_LBL)
        c.grid(column=2, row=5, sticky=W)
        self.widgets.append(c)
        portEntry = ttk.Entry(parentFrame, width=7, textvariable=self.port)
        portEntry.grid(column=3, row=5, sticky=W)
        self.widgets.append(portEntry)

        d = ttk.Label(parentFrame, text=self.MASTERKEY_LBL)
        d.grid(column=2, row=7, sticky=W)
        self.widgets.append(d)

        masterKeyEntry = ttk.Entry(parentFrame, width=7, textvariable=self.masterKey)
        masterKeyEntry.grid(column=3, row=7, sticky=W)
        self.widgets.append(masterKeyEntry)

        e = ttk.Button(parentFrame, text=self.OK_BTN, command= lambda: self.initMessagingGui(parentFrame))
        e.grid(column=3, row=9, sticky=W)
        self.widgets.append(e)


    def initMessagingGui(self, parentFrame):
        # Get all the string variables
        self.ip = self.ip.get()
        self.port = self.port.get()
        self.masterKey = self.masterKey.get()

        # If in server mode, the ip is irrelevant
        if self.ip in ["", '']:
            self.ip = None
        
        # Create a new thread to run the session manager
        try:
            self.session = SessionManager(int(self.port), self.ip, self.masterKey)
            # TODO: Add a timer that polls the queue every x ms
            self.root.after(self.POLL_DELAY_MS, self.checkReceivedMessageQueue)
        except: 
            # The connection failed, or the thread failed to be created
            traceback.print_exc()
            self.errorMessage = "Whoops! We couldn't connect you. #sorrynotsorry"
            self.clearScreen()
            self.initWelcomeScreenGUI(parentFrame) # Try again from main screen

        # Session Manager thread created, so initialise the Chat GUI
        self.clearScreen()

        self.receivedMessageTextWidget = Text(parentFrame, width=41, height=20)
        self.receivedMessageTextWidget.insert('1.0', self.SENT_MESSAGE_DEFAULT)
        self.receivedMessageTextWidget.grid(column=0, row=0, sticky=(N, W, E, S), padx=2, pady=2)
        self.receivedMessageTextWidget.config(state=DISABLED) # Read-only

        self.sentMessageTextWidget = Text(parentFrame, width=41, height=10)
        self.sentMessageTextWidget.grid(column=0, row=1, sticky=(N, W, E, S), padx=2, pady=2)

        self.messageInspectorTextWidget = Text(parentFrame, width=41, height=30)
        self.messageInspectorTextWidget.insert('1.0', self.MSG_INSPECTOR_DEFAULT)
        self.messageInspectorTextWidget.grid(column=7, row=0, sticky=(N, W, E, S), padx=2, pady=2)
        self.messageInspectorTextWidget.config(state=DISABLED) # Read-only
        
        self.sendBtn = ttk.Button(parentFrame, text=self.SEND_BTN_TXT, command=self.sendMessage)
        self.sendBtn.grid(column=7, row=1, padx=10, pady=10)


    """
    Polls the receivedMessageQueue to add messages to the chat window.
    params:
    returns:
    post:
    """
    def checkReceivedMessageQueue(self):
        # Get any new messages
        newMsg = self.session.checkReceivedMessages()

        if not newMsg == 0:

            # Add the message to the text widget to view
            self.postMessage("Remote User: ", str(newMsg))
            print("msg: " + str(newMsg) + "\n")
            
        # Schedule this to be called again 
        self.root.after(self.POLL_DELAY_MS, self.checkReceivedMessageQueue)
      

    """
    Send the message currently typed into the send message text box to the other user
    connected to the session.
    params: 
        none, but the contents in the send box are what will be sent 
    return:
    post: 
        - the message is added to the sendQueue so that the session manager may grab it
        and send it to the other user
        - the send message text box is clear
    """
    def sendMessage(self):
        # Get the text from the widget
        currentMsg = self.sentMessageTextWidget.get('1.0', 'end')
        # Clear the text box so the next message may be sent
        self.sentMessageTextWidget.delete('1.0', 'end')
        # Add the message to the received text widget for historical purposes
        self.postMessage("Me", currentMsg)
        # Send the message through the session manager
        self.session.send(currentMsg)


    """
    Adds a message to the message sent queue so that the session messenger can send it.
    params:
    returns:
    post:
    """
    def postMessage(self, userName, msg):
        # Post message to received message text box
        self.receivedMessageTextWidget.config(state=NORMAL) # make widget read/write
        self.receivedMessageTextWidget.insert('1.0', userName + ": " + str(msg) + "\n\n")
        self.receivedMessageTextWidget.config(state=DISABLED) #make widget read only again

    """
    Remove all current widgets in the GUI in order to update the contents of the screen.
    params:
    returns: empties out the array of current widgets, and removes each one from the GUI
        as it does so.
    """
    def clearScreen(self):
        for index in self.widgets:
            index.destroy()
        self.widgets = []
        pass

"""
Initialize the system logging
"""
def init_logger(file_name=None):
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)

    # log to console
    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(logging.DEBUG)
    logger.addHandler(ch)

    # log to file
    if file_name is not None:
        fh = logging.FileHandler(file_name)
        fh.setLevel(logging.INFO)
        logger.addHandler(fh)


"""
Main Run Loop
"""
if __name__ == '__main__':
    gui = Gui()
    root, mainframe = gui.initGUI()
    root.mainloop()