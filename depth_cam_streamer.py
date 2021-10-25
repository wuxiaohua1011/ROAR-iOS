import logging
from websocket import create_connection
from typing import List, Optional, Tuple, List
import cv2
import numpy as np
from pathlib import Path
from ROAR.utilities_module.module import Module
import socket
from ROAR.utilities_module.utilities import get_ip

import datetime
import websocket

MAX_DGRAM = 9600


class DepthCamStreamer(Module):
    def save(self, **kwargs):
        # no need to save. use Agent's saving mechanism
        pass

    def __init__(self, ios_addr, ios_port, pc_port, show=False, resize: Optional[Tuple] = None,
                 name: str = "depth_cam", threaded: bool = True,
                 update_interval: float = 0.5):
        super().__init__(threaded=threaded, name=name, update_interval=update_interval)
        self.logger = logging.getLogger(f"{self.name} server on [{ios_addr}:{ios_port}]")
        self.host = ios_addr
        self.port = ios_port
        self.pc_port = pc_port

        self.ws = websocket.WebSocket()
        self.s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.s.bind((get_ip(), self.pc_port))

        self.resize = resize
        self.show = show

        self.curr_image: Optional[np.ndarray] = None
        self.intrinsics: Optional[np.ndarray] = None
        self.logger.info(f"{name} initialized")

    def connect(self):
        try:
            self.ws.connect(f"ws://{self.host}:{self.port}/{self.name}", timeout=0.1)
        except:
            raise Exception("Unable to connect to Depth streamer")
        self.dump_buffer()

    def receive(self):
        try:
            intrinsics_str: str = self.ws.recv()

            intrinsics_arr = [float(i) for i in intrinsics_str.split(",")]
            self.intrinsics = np.array([
                [intrinsics_arr[0], 0, intrinsics_arr[2]],
                [0, intrinsics_arr[1], intrinsics_arr[3]],
                [0, 0, 1]
            ])
            """
            width=256 height=192 bytesPerRow=1024 pixelFormat=fdep
            """
            img = self.recv_img()
            self.curr_image = np.rot90(img.reshape((192, 256)), k=-1)
        except Exception as e:
            self.logger.error(f"Failed to recv depth image: {e}")

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
                    img = np.frombuffer(dat, dtype=np.float32)
                    return img
                except Exception as e:
                    print(e)
                return None

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

    def shutdown(self):
        super(DepthCamStreamer, self).shutdown()
        self.s.close()
        self.ws.close()
