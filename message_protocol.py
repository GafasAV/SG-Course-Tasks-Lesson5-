"""
message_protocol.py module implement simple class to create, check and parse
message in json-like object.
Example: {"name": "user1", "msg": "Some user1 message for user2", "to": "user2"}<end>

This object use in client-server chat program for communication.

"""

import json


__author__ = "Andrew Gafiychuk"


class MessageProtocol(object):
    """
    Class to construct simple json object for network connecting.
    Takes user-name, data, and addressee, create JSON-like object.
    - create() return a ready json-like object
    - check_to_private() check if message is private or public
    - parse_and_print(str) get a json-like obj, parse it to strings
                           and print it.
    """
    def __init__(self, name, msg, to=""):
        self.name = name
        self.msg = msg
        self.to = to

    def create(self):
        """
        Create json-like msg object.
        
        """
        self._check_private_marker()

        s = {"name": self.name,
             "msg": self.msg,
             "to": self.to
        }

        data = json.dumps(s) + "<end>"

        return data

    def _check_private_marker(self):
        """
        Check for private-msg marker (user:).
        If exist - create a private json-like msg object.
        
        """
        if "user:" in self.msg:
            self.to = self.msg.partition("user:")[2].split()[0]
            self.msg = " ".join(self.msg.partition("user:")[2]
                                .split()[1:])

    @staticmethod
    def parse_and_print(string, u_name):
        """
        If data from server contains more than one msg:
        Parse the json-like msg object from server.
        Check if msg is private or public and print it...
        
        """
        for el in string.split("<end>"):
            if not el:
                continue

            js = json.loads(el)
            if js["name"] == js["to"]:
                print("to MYSELF: {0}".format(js["msg"]))
            elif js["to"] == u_name:
                print("[private {0}]: {1}"
                      .format(js["name"], js["msg"]))
            elif js["name"] == u_name:
                pass
            else:
                print("{0}: {1}".format(js["name"], js["msg"]))

    @staticmethod
    def to_json(string):
        """
         Takes msg from server, split it to json and return.
         
        """
        msg = string.split("<end>")[0]
        return json.loads(msg)