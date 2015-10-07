__author__ = 'andrew'


class Messenger:
    def __init__(self, target):
        self.target = target  # the the ip/port to message to

    def send_msg(self, msg):
        # return True if message is successfully sent
        pass

    def receive_msg(self):
        # return a new message, if recieved. else return None
        pass
