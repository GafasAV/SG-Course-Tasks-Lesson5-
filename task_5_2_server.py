import socket
import logging
import threading
from simple_text_proto import TextProto


__author__ = "Andrew Gafiychuk"


HOST = "localhost"
PORT = 55555

users = {}
u_lock = threading.RLock()


def add_user(name, conn):
    """
    Function to add new user to connection list.
    
    """
    u_lock.acquire()
    users[conn] = name
    u_lock.release()

    return True


def del_user(conn):
    """
    Remove users from connecting list

    """
    u_lock.acquire()
    del(users[conn])
    u_lock.release()

    return True


def user_match_check(name):
    """
    Check user-name to match.
    
    """
    return True if name in users.values() else False


def say_to_all(msg):
    """
    Function that send user-message to all chat users.
 
    """
    for cl in users:
        cl.send(msg.encode("utf-8"))


def say_private(conn, msg):
    """
    Function send private message between users

    """
    conn.send(msg.encode("utf-8"))


def client_handler(conn):
    """
    Main function.
    User session handler. Takes connecting as param.
    Implement simple data swap between user-server, user-server-user.
    For data swap use simple json protocol implemented in
    simple_text_proto.py

    """
    name = conn.recv(1024)
    name = name.decode("utf-8")

    if not name:
        msg = TextProto(name="Server",
                        msg="Need to introduce yourself", to=name)
        message = msg.create()

        say_private(conn, message)
        return 1
    elif user_match_check(name):
        msg = TextProto(name="Server",
                        msg="Name {0} is already taken".format(name),
                        to=name)
        message = msg.create()

        say_private(conn, message)
        return 1
    else:
        msg = TextProto(name="Server",
                        msg="Welcome to chat !!! {0}".format(name),
                        to=name)
        message = msg.create()

        say_private(conn, message)
        add_user(name, conn)

        print("Added new client: {0}".format(name))

        msg = TextProto(name="Server",
                        msg="{0} entered to chat!".format(name))
        message = msg.create()

        say_to_all(message)

        while True:
            try:
                data = conn.recv(1024)
                data = data.decode("utf-8")
            except (InterruptedError, ConnectionError) as err:
                logging.debug("[-]Data receive error...")
                logging.debug("[-]May be connecting problem...")
                logging.debug(err)

                del_user(conn)
                break

            if not data:
                logging.debug("[-]No data - Exiting...")

                del_user(conn)
                break

            js = TextProto.to_json(data)

            if not js["to"]:
                say_to_all(data)
                print("Client<{0}> send to all: {1}"
                      .format(users[conn], data))
            else:
                dst_name = js["to"]
                dst_conn = None

                for key, val in users.items():
                    if val == dst_name:
                        dst_conn = key

                say_private(dst_conn, data)


if __name__ == "__main__":
    """
    Main function. Create socker server.
    HOST and PORT is static.
    
    For each new connecting create new thread and
    start handler for him.
    
    """
    logging.basicConfig(level=logging.DEBUG)
    logging.debug("[-]App started...")

    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind((HOST, PORT))

        logging.debug("[-]Socket created....")
    except OSError as err:
        print("[ERR]: Connecting error...")
        s.close()

    s.listen(100)
    logging.debug("[-]Listening...")

    while 1:
        client, addr = s.accept()
        threading.Thread(target=client_handler, args=(client,)).start()

    print("Done...EXITING...")
    s.close()
    sys.exit(0)