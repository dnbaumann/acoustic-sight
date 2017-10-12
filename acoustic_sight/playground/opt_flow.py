#!/usr/bin/env python3

import cv2
import numpy as np

from webcam import FrameProcessor


def transform_frame(frame, side=256):
    out = FrameProcessor.square_crop(frame)
    out = cv2.resize(out, (side, side))
    return out


def main():
    cap = cv2.VideoCapture(0)

    _, frame = cap.read()
    frame = transform_frame(frame)
    prvs = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    hsv = np.zeros_like(frame)
    hsv[..., 1] = 255

    while True:
        _, frame = cap.read()
        frame = transform_frame(frame)
        next = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        flow = cv2.calcOpticalFlowFarneback(prvs, next, None, 0.5, 3, 15, 3, 5, 1.2, 0)
        mag, ang = cv2.cartToPolar(flow[..., 0], flow[..., 1])
        hsv[..., 0] = ang*180/np.pi/2
        hsv[..., 2] = cv2.normalize(mag, None, 0, 255, cv2.NORM_MINMAX)
        rgb = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)

        cv2.imshow('frame2', rgb)
        k = cv2.waitKey(30) & 0xff
        if k == 27 or k == ord('q'):
            break
        elif k == ord('s'):
            cv2.imwrite('opticalmyhsv.pgm', rgb)

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()