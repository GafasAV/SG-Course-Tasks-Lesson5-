import socket
import sys
import logging
import threading
import time
from message_protocol import MessageProtocol


__author__ = "Andrew Gafiychuk"


HOST = "localhost"
PORT = 55555
BUFF_SIZE = 1024
WAIT_TIME_OUT = 1


def check_name_format(name):
    """
    Function that check correct name format.
    Name must be without "space"
    
    """
    u_name = name
    if not u_name:
        print("Name error ! Input name !\n"
              "Try again")

        return False
    elif " " in u_name:
        print("Unsupported name format ! (No <space>)\n"
              "Try again:")

        return False
    else:
        return True


def listener(sock, stop_event, u_name):
    """
    Function that start and listen the port.
    It waiting some data from server.
    If data came, function parse it and print to console.
    
    """
    logging.debug("[-]Listener thread is started...")

    while not stop_event.is_set():
        time.sleep(WAIT_TIME_OUT)

        try:
            reply = sock.recv(BUFF_SIZE)

            if not reply:
                continue

            msg = reply.decode("utf-8")
            MessageProtocol.parse_and_print(msg, u_name)
        except socket.error as err:
            logging.debug("[-]Receive data error...\n"
                          "[-]Connecting problem...\n"
                          "{0}".format(err))

            print("Disconnected from chat-room! Exiting...")
            break

    logging.debug("[-]Listener thread is done...\n"
                  "[-]Exiting...\n")

    stop_event.set()


def writer(sock, u_name):
    """
    Function that start and wait user data input.
    If is data, function check it, parse and send to
    server.

    -   Command <exit> to disconnect from server and
        exit program.
        
    """
    logging.debug("[-]Writer thread is started...")

    command = str(input(""))

    while command != "<exit>".lower():
        time.sleep(WAIT_TIME_OUT)

        msg = MessageProtocol(u_name, command)
        msg = msg.create()

        byte = msg.encode("utf-8")
        try:
            sock.send(byte)
        except socket.error as err:
            logging.debug("[-]Writer data send error...\n"
                          "[-]Connecting problem\n"
                          "{0}".format(err))

            print("Disconnected from chat-room! Exiting...")
            break

        command = str(input(""))

    logging.debug("[-]Writer thread is done...\n"
                  "[-]Exiting...\n")


if __name__ == "__main__":
    """
    Main function that create connection and start session.
    HOST and PORT are constant.

    Must input user name.
    All message Transmitted through the json format.
    
    """
    logging.basicConfig(level=logging.INFO)
    logging.debug("[-]App started...")

    name = str(input("Input name: "))
    if not check_name_format(name):
        sys.exit(1)

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        s.connect((HOST, PORT))

        logging.debug("[-]Socket created...\n"
                      "[-]Connecting started...\n")
    except socket.error as err:
        logging.debug("[-]Socket creating\connecting error...\n"
                      "[-]Exiting...\n"
                      "{0}".format(err))

        print("Connecting problem! Exiting...")
        s.close()
        sys.exit(1)

    s.send(name.encode("utf-8"))
    sys_msg = s.recv(BUFF_SIZE).decode("utf-8")

    js = MessageProtocol.to_json(sys_msg)
    msg = MessageProtocol.parse_and_print(sys_msg, name)

    if "<rejected>" in js["msg"]:
        print("Disconnected from chat-room! Exiting...")
        s.close()
        sys.exit(0)

    logging.debug("[-]Start the session...")

    threads = []

    stop_event = threading.Event()
    lsn_thrd = threading.Thread(target=listener,
                                args=(s, stop_event, name,))
    lsn_thrd.start()
    threads.append(lsn_thrd)

    wrt_thrd = threading.Thread(target=writer,
                                args=(s, name,))
    wrt_thrd.start()
    threads.append(wrt_thrd)
    wrt_thrd.join()

    logging.debug("[-]All done...Stop all tasks...Waiting...")

    stop_event.set()
    time.sleep(3)

    if threads:
        del threads

    s.close()

    print("Done...Close...")
    sys.exit(0)
