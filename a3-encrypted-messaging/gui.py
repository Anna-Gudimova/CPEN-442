__author__ = 'andrew'

from tkinter import *
from tkinter import ttk


class Gui:

    # List to hold references to all the current widgets
    widgets = []

    # Variables for setting up the server and the client
    ip = ""
    port = ""
    masterKey = ""

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
    IP_PLACEHOLDER_TXT = "127.0.0.0.1"
    PORT_LBL = "Port"
    PORT_PLACEHOLDER_TXT = "80"
    MASTERKEY_LBL = "Master Key"
    MASTERKEY_PLACEHOLDER_TXT = "Make one up, lazy"
    OK_BTN = "OK"

    def __init__(self, session_manager):
        self.session = session_manager
        pass

    def run(self):
        root, mainframe = self.initGUI()
        root.mainloop()
        pass

    def initGUI(self):
        #Initialise the window
        root = Tk()
        root.title(self.PROGRAM_NAME)
        root.minsize(width=600, height=600)
        root.maxsize(width=600, height=600)

        #Initialize the root Frame
        mainframe = ttk.Frame(root, padding="3 3 12 12")
        mainframe.grid(column=0, row=0, sticky=(N, W, E, S))
        mainframe.columnconfigure(0, weight=1)
        mainframe.rowconfigure(0, weight=1)

        #Initialize the first Screen 
        self.initWelcomeScreenGUI(mainframe);

        #Add all elements to the GUI
        for child in mainframe.winfo_children(): child.grid_configure(padx=5, pady=5)

        return [root, mainframe]

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
        a = ttk.Label(parentFrame, text=self.CHOICE_LBL)
        a.grid(column=2, row=1, sticky=W)
        self.widgets.append(a)

        b = ttk.Button(parentFrame, text=self.SERVER_BTN, command= lambda: self.initServerGUI(parentFrame))
        b.grid(column=1, row=5, sticky=W)
        self.widgets.append(b)

        c = ttk.Button(parentFrame, text=self.CLIENT_BTN, command= lambda: self.initClientGUI(parentFrame))
        c.grid(column=3, row=5, sticky=W)
        self.widgets.append(c)
        pass

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
        pass

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
        pass


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

        pass

    def initMessagingGui(self, parentFrame):
        self.ip = self.ip.get()
        self.port = self.port.get()
        self.masterKey = self.masterKey.get()

        if self.ip and self.port and self.masterKey:
            self.clearScreen()
            # Add a window to hold all messages
            # Add a window to hold type box entry
            # Add a button to hold
        pass

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

if __name__ == '__main__':
    gui = Gui()
    root, mainframe = gui.initGUI()
    root.mainloop()