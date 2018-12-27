import bluetooth
from collections import deque
import threading

class My_Bluetooth:
    #  class variables
    RFCOMM = 3
    def __init__(self, port, buff_size, address=None):
        #  define instance variables
        self.socket = bluetooth.BluetoothSocket(My_Bluetooth.RFCOMM)
        print "Sockets Created."
        self.port = port
        self.buff_size = buff_size
        self.send_queue = deque([])
        self.recv_queue = deque([])
        self.stop_thread = 1
        #client
        self.s_address = address
        #server
        self.c_socket=0
        self.c_address=0
        if self.s_address == None:
            self.open_socket()
        else:
            self.connect(self.s_address)
        ############################## to do: start threads
        self.send_thread = threading.Thread(target=self._send)
        self.recv_thread = threading.Thread(target=self._recv)
        self.send_thread.start()
        self.recv_thread.start()
            
    def search(self):
        #  discover devices
        print "Searching for devices..."
        print "Devices: ", bluetooth.discover_devices(lookup_names = True)
    def connect(self, address):
        #  connect to specific address and port
        print "Connecting to", address , "at port", self.port, "..."
        try:
            self.socket.connect((address, self.port))
            print "Connected."
        except IOError:
            print "Cannot connect...check to see if server is avaliable..."
    def open_socket(self):
        try:
            self.socket.bind(("", self.port))
            self.socket.listen(1)
            self.c_socket, self.c_address = self.socket.accept()
            print "Accepted..."
        except Exception as e:
            print "Cannot open socket... (", e, ")"
            
    def send(self, data): #  add to send queue
        self.send_queue.append(data)
        
    def recv(self):
        #  recieves data
        try:
            data = self.recv_queue.popleft()
        except IndexError:
            data = "null"
        return data
       

    def _recv(self):
        while(self.stop_thread):
            try:
                if self.c_socket == 0:
                    data = self.socket.recv(self.buff_size)
                else:
                    data = self.c_socket.recv(self.buff_size)
            except Exception as e:
                print "Cannot recieve data... (", e, ")"
            data = data.split('`')
            data.pop()
            for x in data:
                self.recv_queue.append(x)

    def _send(self) #private send
        #encode
        while(self.stop_thread):
            while(1):
                try:
                    data = self.send_queue.popleft()
                    break
                except IndexError:
                    pass
            data = str(data)
            data = data+'`'
            #send data
            try:
                if self.c_socket == 0:
                    data = self.socket.send(data)
                else:
                    data = self.c_socket.send(data)
            except Exception as e:
                print "Cannot send data... (", e, ")"
    def close(self):
        #  close connection
        self.stop_thread = 0
        print "Closing connection to server for connection:", self.s_address
        self.socket.close()

def sendTimer(conn):
    threading.Timer(1.0, sendTimer, args=[conn]).start()
    conn.send(str(conn.send_queue))
    print str(conn.recv_queue)

if __name__ == "__main__":
    raspPi_address = "B8:27:EB:A4:7B:46"
    c = My_Bluetooth(4, 1024, raspPi_address)
    sendTimer(c)
    c.close()
