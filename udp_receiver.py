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
        self.logs = [dict(), dict()]

    def connect(self):
        # self.dump_buffer()
        self.logger.info("Frame aligned")

    def dump_buffer(self):
        while True:
            seg, addr = self.s.recvfrom(MAX_DGRAM)
            prefix_num = int(seg[0:3].decode('ascii'))
            total_num = int(seg[3:6].decode('ascii'))
            curr_buffer = int(seg[6:9].decode('ascii'))
            if prefix_num == total_num:
                # self.logger.debug("finish emptying buffer")
                break

    # def recv(self) -> bytes:
    #     dat = b''
    #     while True:
    #         seg, addr = self.s.recvfrom(MAX_DGRAM)
    #         prefix_num = int(seg[0:3].decode('ascii'))
    #         total_num = int(seg[3:6].decode('ascii'))
    #         print(prefix_num)
    #         if prefix_num > 1:
    #             dat += seg[6:]
    #         else:
    #             dat += seg[6:]
    #             return dat

    # def recv(self) -> bytes:
    #     log = dict()
    #     while True:
    #         seg, addr = self.s.recvfrom(MAX_DGRAM)
    #         prefix_num = int(seg[0:3].decode('ascii'))
    #         total_num = int(seg[3:6].decode('ascii'))
    #         if prefix_num in log:
    #             # print(prefix_num, len(log), total_num)
    #
    #             self.dump_buffer()
    #             log = dict()
    #         else:
    #             log[prefix_num] = seg[6:]
    #
    #             # print(prefix_num, len(log), total_num)
    #
    #             if len(log) == total_num:
    #                 dat = b''
    #                 for k in sorted(log.keys(), reverse=True):
    #                     dat += log[k]
    #                 return dat
    # def recv(self) -> bytes:
    #     while True:
    #         seg, addr = self.s.recvfrom(MAX_DGRAM)
    #         prefix_num = int(seg[0:3].decode('ascii'))
    #         total_num = int(seg[3:6].decode('ascii'))
    #         curr_buffer = int(seg[6:9].decode('ascii'))
    #         print(f"curr_buff = {curr_buffer} | prefix_num = {prefix_num} | total_num = {total_num} | "
    #               f"len(self.logs[0]) = {len(self.logs[0])} | len(self.logs[1]) = {len(self.logs[1])}")
    #         if prefix_num not in self.logs[curr_buffer]:
    #             self.logs[curr_buffer][prefix_num] = seg[9:]
    #             if len(self.logs[curr_buffer]) == total_num:
    #                 dat = b''
    #                 for k in sorted(self.logs[curr_buffer].keys()):
    #                     dat += self.logs[curr_buffer][k]
    #                 self.logs[curr_buffer] = dict()
    #
    #                 if len(self.logs[1-curr_buffer]) > 0:
    #                     # clear the other buffer if the other one has more than half of the content
    #                     self.logs[1-curr_buffer] = dict()
    #
    #                 return dat
    #         else:
    #             self.logs[curr_buffer] = dict()

    def recv(self) -> bytes:
        buffer_num = -1
        log = dict()
        dat = b''
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

            if len(log)-1 == total_num:
                data = b''
                for k in sorted(log.keys()):
                    data += log[k]
                # print()
                return data
            # print()

    def recv_naive(self) -> bytes:
        dat = b''
        while True:
            seg, addr = self.s.recvfrom(MAX_DGRAM)
            prefix_num = int(seg[0:3].decode('ascii'))
            total_num = int(seg[3:6].decode('ascii'))
            curr_buffer = int(seg[6:9].decode('ascii'))
            if prefix_num == total_num:
                dat += seg[9:]
                return dat
            else:
                dat += seg[9:]

    def shutdown(self):
        self.s.close()


if __name__ == '__main__':
    import numpy as np
    import cv2
    import struct
    logging.basicConfig(format='%(levelname)s - %(asctime)s - %(name)s '
                               '- %(message)s',
                        datefmt="%H:%M:%S",
                        level=logging.DEBUG)
    udp_streamer = UDPStreamer(pc_port=8002)
    udp_streamer.connect()
    while True:
        start = time.time()
        data = udp_streamer.recv()
        # img_data = data[16:]
        # img = np.frombuffer(img_data, dtype=np.uint8)
        # img = cv2.imdecode(img, cv2.IMREAD_UNCHANGED)
        #
        # if img is None:
        #     print("OH NO")
        #
        # if img is not None:
        #     try:
        #         cv2.imshow("img", cv2.rotate(img, cv2.ROTATE_90_CLOCKWISE))
        #         k = cv2.waitKey(1) & 0xff
        #         if k == ord('q') or k == 27:
        #             break
        #         # print(f"{1 / (time.time() - start)} Image received")
        #     except Exception as e:
        #         print(e)
        intrinsics = data[0:32]
        fx, fy, cx, cy = struct.unpack('f', intrinsics[0:4])[0], \
                         struct.unpack('f', intrinsics[8:12])[0], \
                         struct.unpack('f', intrinsics[16:20])[0], \
                         struct.unpack('f', intrinsics[24:28])[0]
        intrinsics_array = np.array([
            [fx, 0, cx],
            [0, fy, cy],
            [0, 0, 1]
        ])
        # print(fx, fy, cx, cy)
        img = np.frombuffer(data[32:], dtype=np.float32)
        if img is None:
            continue
        else:
            try:
                img = np.rot90(img.reshape((192, 256)), k=-1)
                cv2.imshow("img", img)
                cv2.waitKey(1)
                # print(f"{time.time()} Image received")
            except Exception as e:
                print(e)
