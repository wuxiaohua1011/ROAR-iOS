import logging
from websocket import create_connection
from typing import List, Optional, Tuple, List
import cv2
import numpy as np
from pathlib import Path
from ROAR.utilities_module.module import Module
from ROAR_iOS.udp_receiver import UDPStreamer
from ROAR.utilities_module.utilities import get_ip

import datetime
import websocket

MAX_DGRAM = 9600


class DepthCamStreamer(UDPStreamer):
    def __init__(self, resize: Optional[Tuple] = None, **kwargs):
        super().__init__(**kwargs)
        self.curr_image: Optional[np.ndarray] = None
        self.resize = resize

    def run_in_series(self, **kwargs):
        try:
            data = self.recv()
            img_data = data[:-32]

            img = np.frombuffer(img_data, dtype=np.float32)
            if img is not None:
                self.curr_image = np.rot90(img.reshape((192, 256)), k=-1)
        except OSError:
            self.should_continue_threaded = False
        except Exception as e:
            self.logger.error(e)