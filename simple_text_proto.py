import json
import abc

__author__ = "Andrew Gafiychuk"


class TextProto(object):
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
        self.check_to_private()

        s = {"name": self.name,
             "msg": self.msg,
             "to": self.to
        }

        data = json.dumps(s) + "<end>"

        return data

    def check_to_private(self):
        if "user:" in self.msg:
            self.to = self.msg.partition("user:")[2].split()[0]
            self.msg = " ".join(self.msg.partition("user:")[2]
                                .split()[1:])

    @staticmethod
    def parse_and_print(string):
        for el in string.split("<end>"):
            if not el:
                continue
            js = json.loads(el)
            print("{0}: {1}".format(js["name"], js["msg"]))

    @staticmethod
    def _to_json(string):
        msg = string.split("<end>")[0]
        return json.loads(msg)