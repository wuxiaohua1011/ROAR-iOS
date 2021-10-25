import logging
import websocket
from typing import List, Optional, Tuple, List
import cv2
import numpy as np
from pathlib import Path
from ROAR.utilities_module.module import Module
import socket
import datetime
from ROAR.utilities_module.utilities import get_ip

MAX_DGRAM = 9600


class RGBCamStreamer(Module):
    def save(self, **kwargs):
        pass

    def __init__(self, ios_addr, ios_port, pc_port:int, resize: Optional[Tuple] = None,
                 name: str = "world_cam", threaded: bool = True,
                 update_interval: float = 0.5,
                 has_intrinsics: bool = True,
                 is_ar: bool = False):
        super().__init__(threaded=threaded, name=name, update_interval=update_interval)

        self.logger = logging.getLogger(f"{self.name} server on [{ios_addr}:{ios_port}]")
        self.host = ios_addr
        self.port = ios_port
        self.pc_port = pc_port
        self.ws = websocket.WebSocket()
        self.s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.s.settimeout(0.1)
        self.s.bind((get_ip(), self.pc_port))
        self.intrinsics: Optional[np.ndarray] = None
        self.resize = resize
        self.has_intrinsics = has_intrinsics
        self.is_ar = is_ar

        self.curr_image: Optional[np.ndarray] = None
        self.logger.info(f"{name} initialized")

    def connect(self):
        try:
            self.ws.connect(f"ws://{self.host}:{self.port}/{self.name}", timeout=0.1)
        except:
            raise Exception("Unable to connect to RGB Streamer")
        self.dump_buffer()

    def receive(self):
        try:
            img = self.recv_img()
            self.curr_image = img
            if self.has_intrinsics:
                intrinsics_str = self.ws.recv()
                intrinsics_arr = [float(i) for i in intrinsics_str.split(",")]
                self.intrinsics = np.array([
                    [intrinsics_arr[0], 0, intrinsics_arr[2]],
                    [0, intrinsics_arr[1], intrinsics_arr[3]],
                    [0, 0, 1]
                ])

        except Exception as e:
            # self.logger.error(f"Failed to get image: {e}")
            self.curr_image = None
            pass

    def recv_img(self):
        dat = b''
        while True:
            seg, addr = self.s.recvfrom(MAX_DGRAM)
            prefix_num = int(seg[0:3].decode('ascii'))
            if prefix_num > 1:
                dat += seg[3:]
            else:
                dat += seg[3:]
                try:
                    img = np.frombuffer(dat, dtype=np.uint8)
                    img = cv2.imdecode(img, cv2.IMREAD_UNCHANGED)
                    return img
                except Exception as e:
                    print(e)
                return None

    def shutdown(self):
        super(RGBCamStreamer, self).shutdown()
        self.s.close()
        self.ws.close()

    def run_in_series(self, **kwargs):
        self.receive()

    def dump_buffer(self):
        """ Emptying buffer frame """
        while True:
            seg, addr = self.s.recvfrom(MAX_DGRAM)
            prefix_num = int(seg[0:3].decode('ascii'))
            if prefix_num == 1:
                self.logger.debug("finish emptying buffer")
                break


if __name__ == '__main__':
    ir_image_server = RGBCamStreamer(ios_addr="10.142.143.48", ios_port=8005, name="world_cam")
    ir_image_server.run_in_series()
