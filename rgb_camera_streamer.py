from typing import List, Optional, Tuple, List
import cv2
import numpy as np
from ROAR_iOS.udp_receiver import UDPStreamer
import struct
MAX_DGRAM = 9600


class RGBCamStreamer(UDPStreamer):
    def __init__(self, resize: Optional[Tuple[int, int]] = None, **kwargs):
        super().__init__(**kwargs)
        self.curr_image: Optional[np.ndarray] = None
        self.resize = resize
        self.intrinsics: Optional[np.ndarray] = None

    def run_in_series(self, **kwargs):
        try:
            data = self.recv()
            img_data = data[16:]
            intrinsics = data[:16]
            fx, fy, cx, cy = struct.unpack('f', intrinsics[0:4])[0], \
                             struct.unpack('f', intrinsics[4:8])[0], \
                             struct.unpack('f', intrinsics[8:12])[0], \
                             struct.unpack('f', intrinsics[12:16])[0]
            self.intrinsics = np.array([
                [fx, 0, cx],
                [0, fy, cy],
                [0, 0, 1]
            ])
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
