# import cv2
# import socket
# import pickle
# import numpy as np
#
# host = "127.0.0.1"
# port = 5000
# max_length = 9000
#
# sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
# sock.bind((host, port))
#
# frame_info = None
# buffer = None
# frame = None
#
# print("-> waiting for connection")
#
# while True:
#     data, address = sock.recvfrom(max_length)
#
#     if len(data) < 100:
#         frame_info = pickle.loads(data)
#
#         if frame_info:
#             nums_of_packs = frame_info["packs"]
#
#             for i in range(nums_of_packs):
#                 data, address = sock.recvfrom(max_length)
#
#                 if i == 0:
#                     buffer = data
#                 else:
#                     buffer += data
#
#             frame = np.frombuffer(buffer, dtype=np.uint8)
#             frame = frame.reshape(frame.shape[0], 1)
#
#             frame = cv2.imdecode(frame, cv2.IMREAD_COLOR)
#             frame = cv2.flip(frame, 1)
#
#             if frame is not None and type(frame) == np.ndarray:
#                 cv2.imshow("Stream", frame)
#                 if cv2.waitKey(1) == 27:
#                     break
#
# print("goodbye")


# !/usr/bin/env python

from __future__ import division
import cv2
import numpy as np
import socket
import struct

MAX_DGRAM = 2 ** 16


def dump_buffer(s):
    """ Emptying buffer frame """
    while True:
        seg, addr = s.recvfrom(MAX_DGRAM)
        print(seg[0])
        if struct.unpack("B", seg[0:1])[0] == 1:
            print("finish emptying buffer")
            break


def main():
    """ Getting image udp frame &
    concate before decode and output image """

    # Set up socket
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.bind(('192.168.1.4', 12345))
    dat = b''
    dump_buffer(s)

    while True:
        seg, addr = s.recvfrom(MAX_DGRAM)
        if struct.unpack("B", seg[0:1])[0] > 1:
            dat += seg[1:]
        else:
            dat += seg[1:]
            img = cv2.imdecode(np.frombuffer(dat, dtype=np.uint8), cv2.IMREAD_UNCHANGED)
            try:
                cv2.imshow('frame', img)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
            except Exception as e:
                print(e)
            dat = b''

    # cap.release()
    cv2.destroyAllWindows()
    s.close()


if __name__ == "__main__":
    main()