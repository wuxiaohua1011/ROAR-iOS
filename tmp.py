import socket

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.sendto(b'ack', ("192.168.1.15", 8003))
print(s.recvfrom(1024))

