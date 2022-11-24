from socket import AF_INET,socket, SOCK_STREAM
from threading import Thread


def accept_incoming_connections():
    while True:
        client, client_address = SERVER.accept()
        print(type(client))
        print("%s:%s has connected." % client_address)
        addresses[client] = client_address
        Thread(target=handle_client, args=(client,)).start()

def handle_client(client:socket):  # Takes client socket as argument.
    name:str = ("%s:%s" % addresses[client])
    clients[name] = client
    welcome = f"Xin chào {name} !"
    serverSendToIP(welcome,name)
    msg = "%s đã tham gia phòng chat!" % name
    serverSendToAll(msg,blacklist=name)
    while True:
        msg:str = client.recv(BUFSIZ).decode("utf8").strip()
        split_msg = msg.split(" ")
        prefix = split_msg[0]
        match prefix:
            case 'quit':
                msg = msg.replace(prefix,"",1).strip()
                client.close()
                del clients[name]
                temp_key = []
                key:int
                for key in groups:
                    if name in groups[key]:
                        if len(groups[key])>1:
                            groups[key].remove(name)
                            serverSendToGroup(id_group=key,msg="%s đã thoát group chat." % name)
                        else: 
                            temp_key.append(key)
                if len(temp_key)>1:
                    for key in temp_key:
                        del groups[key]
                    temp_key.clear()    
                serverSendToAll("%s đã thoát phòng chat." % name)
                break
            case 'net':
                msg = msg.replace(prefix,"",1).strip()
                print(msg)
                split_msg = msg.split(" ")
                prefix = split_msg[0]
                match prefix:
                    case 'send':
                        msg = msg.replace(prefix,"",1).strip()
                        split_msg = msg.split(" ")
                        prefix = split_msg[0]
                        match prefix:
                            case "all":
                                msg = msg.replace(prefix,"",1).strip()
                                sendToAll(msg,name)
                            case "group":
                                msg = msg.replace(prefix,"",1).strip()
                                split_msg = msg.split(" ")
                                if len(split_msg)>1:
                                    prefix = split_msg[0]
                                    if prefix.isnumeric():
                                        id = int(prefix)
                                        if id in groups and name in groups[id]:
                                            msg = split_msg[1]
                                            sendToGroup(msg=msg,name=name,id_group=id)  
                                        else:
                                            serverSendToIP(ip=name, msg="group không tồn tại")   
                                    else:
                                        serverSendToIP(ip=name, msg="id group phải là dạng số")
                                else :
                                    serverSendToIP(ip=name,msg="tin nhắn không được bỏ trống ")
                                    
                            case _:
                                msg = msg.replace(prefix,"",1).strip()
                                ip = prefix
                                if ip in clients and msg != "":
                                    sendToIP(msg,ip,name) 
                                else : 
                                    serverSendToIP(f"IP not recognized \'{ip}\'",name)
                    case "group":
                                msg = msg.replace(prefix,"",1).strip()
                                split_msg = msg.split(" ")
                                prefix = split_msg[0]
                                match prefix:
                                    case 'create':
                                        msg = msg.replace(prefix,"",1).strip()
                                        split_msg = msg
                                        prefix = split_msg
                                        if prefix != "": 
                                            print(prefix.isnumeric())
                                            if prefix.isnumeric():
                                                id = int(prefix)
                                                if id not in groups:    
                                                    groups[id] = [name]
                                                    # groups_ad[id] = name
                                                    serverSendToIP(ip=name,msg="Đã tạo group '%s' thành công" % str(id))
                                                else:
                                                    serverSendToIP(ip=name,msg="Group '%s' đã tồn tại" % str(id))
                                            else:
                                                serverSendToIP(ip=name,msg="ID group phải là dạng số" % str(id))
                                        else:
                                            serverSendToIP(ip=name,msg="ID group không được bỏ trống" % str(id))
                                    case 'add':
                                        msg = msg.replace(prefix,"",1).strip()
                                        split_msg = msg.split(" ")
                                        prefix = split_msg[0]
                                        if prefix != "" and len(split_msg)>1: 
                                            if prefix.isnumeric():
                                                id = int(prefix)
                                                ip = split_msg[1]
                                                if id in groups and name in groups[id] and ip in clients:  
                                                    groups[id].append(ip)
                                                    serverSendToGroup(msg=f"{name} đã thêm {ip} vào group {id}",id_group=id)
                                                else:
                                                    serverSendToIP(ip=name,msg="Thêm người dùng thất bại")  
                                            else:
                                                serverSendToIP(ip=name,msg="ID group phải là dạng số")
                                        else:
                                            serverSendToIP(ip=name,msg="ID group không được bỏ trống") 
                                    case _:
                                        print(msg)
                                        serverSendToIP(f"Command not recognized \'{prefix}\'",name)
                    case _:
                        serverSendToIP(f"Command not recognized \'{prefix}\'",name)
            case _:
                serverSendToIP(f"Command not recognized \'{prefix}\'",name)
                



def serverSendToAll(msg:str,blacklist=""):  # prefix is for name identification.
    sock:socket
    for sock in clients.values():
        if blacklist not in clients or sock != clients[blacklist]: 
            sock.send(bytes("server -> all : "+msg, "utf8"))
            # print(bytes("server -> all : "+msg, "utf8"))
def sendToAll(msg:str,name:str):  # prefix is for name identification.
    sock:socket
    for sock in clients.values():
        sock.send(bytes(name+" -> all : "+msg, "utf8"))
def sendToIP(msg:str,ip:str,name:str):  # prefix is for name identification.
    client:socket = clients[ip]
    client.send(bytes(name+" -> "+ ip+" : "+msg, "utf8"))
    if ip != name :
        client = clients[name]
        client.send(bytes(name+" -> "+ ip+" : "+msg, "utf8"))
def sendToGroup(msg:str,name:str,id_group):
    if id_group in groups:
        for temp_name in groups[id_group]:
            client:socket = clients[temp_name]
            client.send(bytes(name+" -> group "+ str(id_group)+" : "+msg, "utf8"))                      
        
def serverSendToIP(msg:str,ip:str):  # prefix is for name identification.
    client:socket = clients[ip]
    client.send(bytes("server -> you : "+msg, "utf8"))
    
def serverSendToGroup(msg:str,id_group):
    if id_group in groups:
        for temp_name in groups[id_group]:
            client:socket = clients[temp_name]
            client.send(bytes("Server -> group "+ str(id_group)+" : "+msg, "utf8"))


HOST = '127.0.0.1'
PORT = 3064
BUFSIZ = 1024
ADDR = (HOST, PORT)

clients = {}
addresses = {}
groups = {}
groups_ad = {}
SERVER = socket(AF_INET, SOCK_STREAM)
SERVER.bind(ADDR)
if __name__ == "__main__":
    SERVER.listen(5)
    print("Chờ kết nối từ các client...")
    ACCEPT_THREAD = Thread(target=accept_incoming_connections)
    ACCEPT_THREAD.start()
    ACCEPT_THREAD.join()
    SERVER.close()