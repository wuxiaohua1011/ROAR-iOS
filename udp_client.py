import cv2
import socket
import math
import pickle
import sys

max_length = 9000
host = "192.168.1.15"
port = 8004

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

while True:
    sock.sendto(b"1500,1500", (host, port))
