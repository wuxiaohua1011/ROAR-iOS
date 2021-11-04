import logging
import socket
import sys, os
from pathlib import Path
import time

sys.path.append(Path(os.getcwd()).parent.as_posix())
from ROAR.utilities_module.module import Module
from ROAR.utilities_module.utilities import get_ip
from collections import defaultdict

MAX_DGRAM = 9620


class UDPStreamer(Module):
    def save(self, **kwargs):
        pass

    def __init__(self, pc_port=8001, **kwargs):
        super().__init__(**kwargs)
        self.logger = logging.getLogger(f"{self.name}")
        self.pc_port = pc_port
        self.s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.s.settimeout(1)
        self.counter = 0
        self.ios_addr = None
        self.logs = defaultdict(dict)

    def connect(self):
        self.s.bind((get_ip(), self.pc_port))
        self.logger.debug(f"Server started on {(get_ip(), self.pc_port)}. Waiting for client...")
        # while True:
        #     try:
        #         _ = self.s.recv(9600)
        #         self.logger.debug("Client Found!")
        #         break
        #     except socket.timeout as e:
        #         self.logger.error(f"{e} Waiting for client...")

    def dump_buffer(self):
        while True:
            seg, addr = self.s.recvfrom(MAX_DGRAM)
            prefix_num = int(seg[0:3].decode('ascii'))
            total_num = int(seg[3:6].decode('ascii'))
            curr_buffer = int(seg[6:9].decode('ascii'))
            if prefix_num == total_num:
                # self.logger.debug("finish emptying buffer")
                break

    def recv(self) -> bytes:
        """
        If we have a really large data, we are going to chunk it and send it. Since iOS platform can only handle
        a maximum size of 9620, we use 9600 for each chunk here to make some room for extra header.

        So on the sender's side, the chunk size <= 9200 bytes of data + 3 + 3 + 3 bytes of header
        On the receiver's side, the chunk size <= 9200 bytes of data + 3 + 3 + 3 bytes of header

        And therefore, our buffer must be set to a number that is greater than or equal to 9209. We will take 9600

        ----------
        |  9600  |
        |--------|
        |  9600  |
        |--------|
        ...


        Each chunk is going to be structured like this:
        XXXYYYZZZDATA

        where XXX == 3 bytes long int encoded in ascii representing prefix num
        where YYY == 3 bytes long int encoded in ascii representing total num
        where ZZZ == 3 bytes long int encoded in ascii curr_buffer
        where DATA represent the actual data

        Returns:

        """
        buffer_num = -1
        log = dict()
        while True:
            seg, addr = self.s.recvfrom(MAX_DGRAM)
            prefix_num = int(seg[0:3].decode('ascii'))
            total_num = int(seg[3:6].decode('ascii'))
            curr_buffer = int(seg[6:9].decode('ascii'))

            # print(f"BEFORE curr_buff = {curr_buffer} | prefix_num = {prefix_num} "
            #       f"| total_num = {total_num} | len(log) = {len(log)}")
            if buffer_num == -1:
                # initializing
                buffer_num = curr_buffer
                if prefix_num != 0:
                    # if the first one is not the starting byte, dump it.
                    self.dump_buffer()
                    buffer_num = -1
                    log = dict()
                else:
                    # if the first one is the starting byte, start recording
                    log[prefix_num] = seg[9:]
            else:
                if prefix_num in log:
                    # if i received a frame from another sequence
                    self.dump_buffer()
                    buffer_num = -1
                    log = dict()
                else:
                    log[prefix_num] = seg[9:]
            # print(f"AFTER curr_buff = {curr_buffer} | prefix_num = {prefix_num} | total_num = {total_num} "
            #       f"| len(log) = {len(log)} | log.keys = {list(sorted(log.keys()))}")

            if len(log) - 1 == total_num:
                data = b''
                for k in sorted(log.keys()):
                    data += log[k]
                # print()
                return data
            # print()

    def _send_data(self, data: str):
        try:
            seg, self.ios_addr = self.s.recvfrom(MAX_DGRAM)
            self.s.sendto(data.encode('utf-8'), self.ios_addr)
            self.counter += 1
        except socket.timeout:
            pass
        except Exception as e:
            self.logger.error(e)

    def shutdown(self):
        super(UDPStreamer, self).shutdown()
        self.s.close()


if __name__ == '__main__':
    import numpy as np
    import cv2
    import struct

    logging.basicConfig(format='%(levelname)s - %(asctime)s - %(name)s '
                               '- %(message)s',
                        datefmt="%H:%M:%S",
                        level=logging.DEBUG)
    udp_streamer = UDPStreamer(pc_port=8001)
    udp_streamer.connect()
    while True:
        start = time.time()
        # print("about to recv")
        data = udp_streamer.recv()
        # d = np.frombuffer(data, dtype=np.float32)
        # print(d)
        # print(1 / (time.time() - start))

        # Receiving RGB
        img_data = data[16:]
        img = np.frombuffer(img_data, dtype=np.uint8)
        img = cv2.imdecode(img, cv2.IMREAD_UNCHANGED)

        if img is None:
            print("OH NO")

        if img is not None:
            try:
                cv2.imshow("img", cv2.rotate(img, cv2.ROTATE_90_CLOCKWISE))
                k = cv2.waitKey(1) & 0xff
                if k == ord('q') or k == 27:
                    break
                # print(f"{1 / (time.time() - start)} Image received")
            except Exception as e:
                print(e)


        """
        Receiving depth
        
        # intrinsics = data[0:32]
        # fx, fy, cx, cy = struct.unpack('f', intrinsics[0:4])[0], \
        #                  struct.unpack('f', intrinsics[8:12])[0], \
        #                  struct.unpack('f', intrinsics[16:20])[0], \
        #                  struct.unpack('f', intrinsics[24:28])[0]
        # intrinsics_array = np.array([
        #     [fx, 0, cx],
        #     [0, fy, cy],
        #     [0, 0, 1]
        # ])
        # # print(fx, fy, cx, cy)
        # img = np.frombuffer(data[32:], dtype=np.float32)
        # if img is None:
        #     continue
        # else:
        #     try:
        #         img = np.rot90(img.reshape((144, 256)), k=-1)
        #         cv2.imshow("img", img)
        #         cv2.waitKey(1)
        #         # print(f"{time.time()} Image received")
        #     except Exception as e:
        #         print(e)
        """
