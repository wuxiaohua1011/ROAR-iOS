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
        self.ios_addr = ("192.168.1.15", 8004)
        self.s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.s.bind((get_ip(), self.pc_port))
        self.logs = [dict(), dict()]
        self.counter = 0

    def connect(self):
        seg, self.ios_addr = self.s.recvfrom(MAX_DGRAM)
        self.logger.debug(f"Server started on {(get_ip(), self.pc_port)}")

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
                return data

    def send(self, data:str):
        if self.counter % 1000 == 0:
            seg, self.ios_addr = self.s.recvfrom(MAX_DGRAM)
        self.s.sendto(data.encode('utf-8'), ("192.168.1.15", 8004))
        self.counter += 1

    def shutdown(self):
        super(UDPStreamer, self).shutdown()
        self.s.close()


if __name__ == '__main__':
    import numpy as np

    logging.basicConfig(format='%(levelname)s - %(asctime)s - %(name)s '
                               '- %(message)s',
                        datefmt="%H:%M:%S",
                        level=logging.DEBUG)
    udp_streamer = UDPStreamer(pc_port=8004)
    try:
        # udp_streamer.connect()
        while True:
            start = time.time()
            udp_streamer.send("0.5, 0.5")
    except Exception as e:
        print(e)
        print("handling gracefully")
        udp_streamer.shutdown()
