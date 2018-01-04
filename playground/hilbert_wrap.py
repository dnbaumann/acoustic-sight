#!/usr/bin/env python3

import cv2
import numpy as np

from acoustic_sight import hilbert_curve


def get_line(n, shift=0) -> np.ndarray:
    line = np.concatenate((
        np.linspace(0, 1, num=n/2, endpoint=True),
        np.linspace(1, 0, num=n/2, endpoint=True)
    )).reshape((n, 1))

    if shift != 0:
        line = np.roll(line, shift)

    return line


class HilbertCurveExample:
    LINEAR = 'Linear'
    SQUARE = 'Square'
    WRAPPED = 'Wrapped'
    EXPANDED = 'Expanded'

    @classmethod
    def get_window_names(cls):
        return cls.LINEAR, cls.SQUARE, cls.WRAPPED, cls.EXPANDED

    def __init__(self, magnitude=4):
        self.magnitude = magnitude
        self.side = 2**self.magnitude
        self.length = self.side**2

        self.line_shift = 0
        self.square_x = self.side // 2
        self.square_y = self.side // 2

    def get_content(self):
        line = get_line(self.length, shift=self.line_shift)
        segment = get_line(self.side)
        wrapped = hilbert_curve.hilbert_wrap(line)

        square = np.matmul(segment, segment.transpose())
        square_x = self.square_x % square.shape[1] + square.shape[1] // 2
        square_y = self.square_y % square.shape[0] + square.shape[0] // 2
        square = np.roll(square, square_x)
        square = np.roll(square, square_y, axis=0)

        line_alike = np.tile(line.transpose(), (100, 1))
        expanded = np.tile(hilbert_curve.hilbert_expand(square).reshape((1, self.length)), (100, 1))

        return dict(zip(self.get_window_names(), (line_alike, square, wrapped, expanded)))

    def draw_content(self):
        for name, img in self.get_content().items():
            cv2.imshow(name, img)

    def set_line_shift(self, line_shift):
        self.line_shift = line_shift
        self.draw_content()

    def set_square_x_y(self, square_x, square_y):
        self.square_x = square_x
        self.square_y = square_y
        self.draw_content()


def main():
    hce = HilbertCurveExample()
    hce.draw_content()

    def linear_mouse_handler(event, x, y, flags, param):
        hce.set_line_shift(x)

    def square_mouse_handler(event, x, y, flags, param):
        hce.set_square_x_y(x, y)

    # cv2.namedWindow(HilbertCurveExample.LINEAR)
    cv2.setMouseCallback(HilbertCurveExample.LINEAR, linear_mouse_handler)

    # cv2.namedWindow(HilbertCurveExample.SQUARE)
    cv2.setMouseCallback(HilbertCurveExample.SQUARE, square_mouse_handler)

    while True:
        k = cv2.waitKey(30) & 0xff
        if k == 27 or k == ord('q'):
            break

    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
