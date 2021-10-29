import logging
import websocket
from typing import List, Optional, Tuple, List
import cv2
import numpy as np
from pathlib import Path
from ROAR_iOS.udp_receiver import UDPStreamer
from ROAR.utilities_module.module import Module
import socket
import time
from ROAR.utilities_module.utilities import get_ip
from collections import deque

MAX_DGRAM = 9600


class RGBCamStreamer(UDPStreamer):
    def __init__(self, resize: Optional[Tuple[int, int]] = None, **kwargs):
        super().__init__(**kwargs)
        self.curr_image: Optional[np.ndarray] = None
        self.resize = resize

    def run_in_series(self, **kwargs):
        try:
            data = self.recv()
            img_data = data[:-32]
            intinsics = data[-32:]
            print(intinsics)
            img = np.frombuffer(img_data, dtype=np.uint8)
            img = cv2.imdecode(img, cv2.IMREAD_UNCHANGED)
            if img is not None:
                self.curr_image = img
        except OSError:
            self.should_continue_threaded = False

        except Exception as e:
            self.logger.error(e)


if __name__ == '__main__':
    ir_image_server = RGBCamStreamer(ios_addr="10.142.143.48", ios_port=8005, name="world_cam")
    ir_image_server.run_in_series()
