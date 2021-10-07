import urllib.request
import cv2
import numpy as np
import websocket
import time


def main(host):
    ws = websocket.WebSocket()
    ws.connect(f"ws://{host}:81/ws")
    print("Connected")

    while True:
        imgResp = urllib.request.urlopen(f'http://{host}/cam-lo.jpg')
        imgNp = np.array(bytearray(imgResp.read()), dtype=np.uint8)
        print(f"received {time.time()}")
        img = cv2.imdecode(imgNp, -1)
        # all the opencv processing is done here
        cv2.imshow('test', img)
        if ord('q') == cv2.waitKey(1):
            exit(0)
        # res = input("Enter throttle, steering: ")
        res = "1600,1500"
        throttle, steering = res.split(",")
        ws.send(f"({throttle},{steering})")
        time.sleep(0.025)


if __name__ == "__main__":
    host = "10.0.0.8"
    main(host=host)
