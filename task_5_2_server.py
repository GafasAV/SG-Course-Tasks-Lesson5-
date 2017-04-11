import socket
import logging
import threading
from message_protocol import MessageProtocol


__author__ = "Andrew Gafiychuk"


HOST = "localhost"
PORT = 55555
BUFF_SIZE = 1024
MAX_CONNECTING = 10

users = {}
u_lock = threading.RLock()


def add_user(name, conn):
    """
    Function to add new user to connection list.
    
    """
    u_lock.acquire()
    users[conn] = name
    u_lock.release()


def del_user(conn):
    """
    Remove users from connecting list

    """
    u_lock.acquire()
    if conn in users.keys():
        del(users[conn])
    u_lock.release()


def user_match_check(name):
    """
    Check user-name to match.
    
    """
    return True if name in users.values() else False


def say_to_all(msg):
    """
    Function that send user-message to all chat users.
 
    """
    byte = msg.encode("utf-8")
    for cn in list(users.keys()):
        try:
            cn.send(byte)
        except socket.error as err:
            logging.debug("[-]Broadcast data send error:\n"
                          "[-]Connecting error:\n"
                          "{0}".format(err))

            del_user(cn)


def say_private(conn, msg):
    """
    Function send private message between users

    """
    byte = msg.encode("utf-8")
    try:
        conn.send(byte)
    except socket.error as err:
        logging.debug("[-]Private data send error:\n"
                      "[-]Connecting error:\n"
                      "{0}".format(err))

        del_user(conn)


def client_handler(conn):
    """
    Main function.
    User session handler. Takes connecting as param.
    Implement simple data swap between user-server, user-server-user.
    For data swap use simple json protocol implemented in
    message_protocol.py

    """
    try:
        name = conn.recv(BUFF_SIZE)
    except socket.error as err:
        logging.debug("[-]User name error..."
                      "[-]User rejected !"
                      "{0}".format(err))

        conn.close()

    name = name.decode("utf-8")

    if not name:
        msg = MessageProtocol(name="Server",
                              msg="Need to introduce yourself <rejected>",
                              to=name)
        message = msg.create()
        say_private(conn, message)

        conn.close()

    elif user_match_check(name):
        msg = MessageProtocol(name="Server",
                              msg="Name <{0}> is already taken <rejected>"
                              .format(name),
                              to=name)
        message = msg.create()
        say_private(conn, message)

        conn.close()

    else:
        msg = MessageProtocol(name="Server",
                              msg="Welcome to chat, {0}!"
                              .format(name),
                              to=name)
        message = msg.create()

        say_private(conn, message)

        add_user(name, conn)
        print("Added new client: {0}".format(name))

        msg = MessageProtocol(name="Server",
                              msg="{0} entered to chat!"
                              .format(name))
        message = msg.create()

        say_to_all(message)

        while True:
            try:
                data = conn.recv(BUFF_SIZE).decode("utf-8")
            except socket.error as err:
                logging.debug("[-]Data receive error...\n"
                              "[-]May be connecting problem...\n"
                              "{0}".format(err))

                del_user(conn)
                break

            if not data:
                logging.debug("[-]No data - Client exiting...")

                del_user(conn)
                break

            msg = MessageProtocol.to_json(data)

            if msg["to"] == "":
                say_to_all(data)
                print("Client <{0}> send to all: {1}"
                      .format(users[conn], msg["msg"]))
            else:
                dst_name = msg["to"]
                dst_conn = None

                if dst_name not in users.values():
                    msg = MessageProtocol(
                        name="Server",
                        msg="User <{0}> Unauthorized !"
                            .format(dst_name),
                        to=name)
                    message = msg.create()

                    say_private(conn, message)
                else:
                    for conn, u_name in users.items():
                        if dst_name == u_name:
                            dst_conn = conn
                            say_private(dst_conn, data)

        del_user(conn)

        print("User <{0}> came out!".format(name))

        msg = MessageProtocol(name="Server",
                              msg="User <{0}> came out!"
                              .format(name))
        message = msg.create()
        say_to_all(message)

        logging.debug("[-]User handler closed...\n"
                      "[-]User delete, connecting close...")


if __name__ == "__main__":
    """
    Main function. Create socker server.
    HOST and PORT is static.
    
    For each new connecting create new thread and
    start handler for him.
    
    """
    logging.basicConfig(level=logging.INFO)
    logging.debug("[-]App started...")

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        s.bind((HOST, PORT))

        print("Server started on {0}:{1}".format(HOST, PORT))

        logging.debug("[-]Socket created....")
    except socket.error as err:
        logging.debug("[-]Socket error...\n"
                      "{0}".format(err))

        s.close()

    s.listen(MAX_CONNECTING)

    logging.debug("[-]Listening...")
    while True:
        client, addr = s.accept()

        threading.Thread(target=client_handler, args=(client,)).start()

    print("Done...EXITING...")
    s.close()
    sys.exit(0)