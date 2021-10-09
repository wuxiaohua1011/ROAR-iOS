import urllib.request
import cv2
import numpy as np
import websocket
import time


def main(host):
    # ws = websocket.WebSocket()
    # ws.connect(f"ws://{host}:81/ws")
    start = time.time()
    while True:
        imgResp = urllib.request.urlopen(f'http://{host}/cam-lo.jpg')
        imgNp = np.array(bytearray(imgResp.read()), dtype=np.uint8)
        img = cv2.imdecode(imgNp, -1)
        # all the opencv processing is done here
        cv2.imshow('test', img)
        if ord('q') == cv2.waitKey(1):
            exit(0)
        # res = input("Enter throttle, steering: ")
        res = "1800,1600"
        throttle, steering = res.split(",")
        urllib.request.urlopen(f'http://{host}/cmd/({throttle},{steering})')

        print(f"Frame rate = {1 / (time.time() - start)}")
        start = time.time()
        time.sleep(0.025)


if __name__ == "__main__":
    host = "10.0.0.14"
    main(host=host)
