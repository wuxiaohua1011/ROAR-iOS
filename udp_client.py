import cv2
import socket
import math
import pickle
import sys
import time

max_length = 9000
host = "192.168.1.29"
port = 8004

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((host, port))

while True:
    start = time.time()
    content, addr = sock.recvfrom(10)
    sock.sendto(b"1.0,0.4", addr)
    end = time.time()
    print(f'FPS: {1 / (end - start)}')
