import logging
import socket
import sys, os
from pathlib import Path
import time

sys.path.append(Path(os.getcwd()).parent.as_posix())
from ROAR.utilities_module.module import Module
from ROAR.utilities_module.utilities import get_ip

MAX_DGRAM = 9600


class UDPStreamer(Module):
    def save(self, **kwargs):
        pass

    def __init__(self, pc_port=8001, **kwargs):
        super().__init__(**kwargs)
        self.logger = logging.getLogger(f"{self.name}")
        self.pc_port = pc_port
        self.s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.s.bind((get_ip(), self.pc_port))

    def connect(self):
        self.dump_buffer()
        self.logger.info("Frame aligned")

    def dump_buffer(self):
        while True:
            seg, addr = self.s.recvfrom(MAX_DGRAM)
            prefix_num = int(seg[0:3].decode('ascii'))
            if prefix_num == 1:
                self.logger.debug("finish emptying buffer")
                break

    def recv(self) -> bytes:
        dat = b''
        while True:
            seg, addr = self.s.recvfrom(MAX_DGRAM)
            prefix_num = int(seg[0:3].decode('ascii'))
            total_num = int(seg[3:6].decode('ascii'))
            if prefix_num > 1:
                dat += seg[6:]
            else:
                dat += seg[6:]
                return dat

    def shutdown(self):
        self.s.close()


if __name__ == '__main__':
    import numpy as np
    import cv2

    logging.basicConfig(format='%(levelname)s - %(asctime)s - %(name)s '
                               '- %(message)s',
                        datefmt="%H:%M:%S",
                        level=logging.DEBUG)
    udp_streamer = UDPStreamer(pc_port=8001)
    udp_streamer.connect()
    while True:
        data = udp_streamer.recv()

        img = np.frombuffer(data, dtype=np.uint8)
        img = cv2.imdecode(img, cv2.IMREAD_UNCHANGED)
        if img is not None:
            try:
                cv2.imshow("img", cv2.rotate(img, cv2.ROTATE_90_CLOCKWISE))
                cv2.waitKey(1)
                print(f"{time.time()} Image received")
            except Exception as e:
                print(e)

        # img = np.frombuffer(data, dtype=np.float32)
        # if img is None:
        #     continue
        # else:
        #     try:
        #         img = np.rot90(img.reshape((192, 256)), k=-1)
        #         cv2.imshow("img", img)
        #         cv2.waitKey(1)
        #         print(f"{time.time()} Image received")
        #     except Exception as e:
        #         print(e)
