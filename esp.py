import urllib.request
import numpy as np
import cv2
import websocket
import requests
import time


def main(host):
    ws = websocket.WebSocket()
    # ws.connect(f"ws://{host}:81/ws")
    url = f'http://{host}/cam-lo.jpg'

    while True:
        imgResp = urllib.request.urlopen(url)
        imgNp = np.array(bytearray(imgResp.read()), dtype=np.uint8)
        img = cv2.imdecode(imgNp, -1)

        # all the opencv processing is done here
        cv2.imshow('test', img)
        if ord('q') == cv2.waitKey(1):
            exit(0)
        # ws.send("(1500,1500)")
        time.sleep(0.025)


if __name__ == "__main__":
    host = "192.168.1.22"
    main(host=host)
