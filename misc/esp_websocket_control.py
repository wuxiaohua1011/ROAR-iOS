import urllib.request
import numpy as np
import cv2
import websocket
import requests
import time


def main(host):
    ws = websocket.WebSocket()
    ws.connect(f"ws://{host}:81/ws")
    while True:
        ws.send("(1500,1400)")
        time.sleep(0.025)
        print("Sent")


if __name__ == "__main__":
    host = "192.168.1.29"
    main(host=host)
