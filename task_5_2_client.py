import socket
import sys
import logging
from simple_text_proto import TextProto


__author__ = "Andrew Gafiychuk"


HOST = "localhost"
PORT = 55555


if __name__ == "__main__":
    """
    Main function that create connection and start session.
    HOST and PORT are constant.

    Must input user name.
    All message Transmitted through the json format.
    
    """
    logging.basicConfig(level=logging.INFO)
    logging.debug("[-]App started...")

    name = str(input("Input name:"))

    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((HOST, PORT))

        logging.debug("[-]Socket created...")
    except socket.error as err:
        logging.debug("[-]Socket creating\connecting error..."
                      "Exiting...")
        logging.debug(err)

        print("Disconnected from chatroom! Exiting...")
        s.close()
        sys.exit(1)

    s.send(name.encode("utf-8"))
    sys_msg = s.recv(1024).decode("utf-8")

    msg = TextProto.parse_and_print(sys_msg)

    logging.debug("[-]Start the session:")
    while 1:
        s.settimeout(2)
        data = input(">>>")

        if not data:
            logging.debug("[-]Input error try again:")
            data = input(">>>")

        msg = TextProto(name, data)
        msg = msg.create()

        byte = msg.encode("utf-8")

        try:
            s.send(byte)
        except ConnectionResetError as err:
            logging.debug("[-]Data send error..." + err)
            logging.debug("[-]Connecting problem...")

            break

        try:
            sreply = s.recv(1024)
            sreply = sreply.decode("utf-8")

            msg = TextProto.parse_and_print(sreply)
        except (InterruptedError, ConnectionResetError) as err:
            logging.debug("[-]Receive data error..." + err)
            logging.debug("[-]Connecting problem...")

            break

    print("Done...Close...")
    s.close()
    sys.exit(0)