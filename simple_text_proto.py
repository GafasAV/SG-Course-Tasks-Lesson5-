import json
import abc

__author__ = "Andrew Gafiychuk"


class TextProto(object):

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

        if not s["to"]:
            s.pop("to")

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
    def to_json(string):
        msg = string.split("<end>")[0]
        print(type(msg))
        return json.loads(msg)


if __name__ == "__main__":
    name = str(input("Name: "))
    msg = str(input("Msg: "))
    msg = TextProto(name, msg)
    some_t = msg.create()

    print("Some text: " + some_t)

    js = TextProto.to_json(some_t)
    print(type(js))
    print(js["name"])
    print(js["msg"])
    print(js["to"])