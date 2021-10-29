from typing import List, Optional, Tuple, List
import numpy as np
from ROAR_iOS.udp_receiver import UDPStreamer
import struct
MAX_DGRAM = 9600


class DepthCamStreamer(UDPStreamer):
    def __init__(self, resize: Optional[Tuple] = None, **kwargs):
        super().__init__(**kwargs)
        self.curr_image: Optional[np.ndarray] = None
        self.resize = resize
        self.intrinsics: Optional[np.ndarray] = None

    def run_in_series(self, **kwargs):

        try:
            data = self.recv()
            img_data = data[32:]
            intrinsics = data[0:32]
            fx, fy, cx, cy = struct.unpack('f', intrinsics[0:4])[0], \
                             struct.unpack('f', intrinsics[8:12])[0], \
                             struct.unpack('f', intrinsics[16:20])[0], \
                             struct.unpack('f', intrinsics[24:28])[0]
            self.intrinsics = np.array([
                [fx, 0, cx],
                [0, fy, cy],
                [0, 0, 1]
            ])
            img = np.frombuffer(img_data, dtype=np.float32)
            if img is not None:
                self.curr_image = np.rot90(img.reshape((192, 256)), k=-1)
        except OSError:
            self.should_continue_threaded = False
        except Exception as e:
            self.logger.error(e)