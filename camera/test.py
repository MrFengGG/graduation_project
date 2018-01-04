import socket
sock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
sock.sendto('{"command":"analyze"}'.encode(),("192.168.137.58",9998))