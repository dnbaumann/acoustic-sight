from typing import Callable, List, Tuple

import numpy as np


class FrameProcessor:
    def __init__(self, side_in: int, side_out: int, buffer_size:int=2):
        self.side_in = side_in
        self.side_out = side_out
        self.buffer_size = buffer_size
        self.frame_buffer: List[np.ndarray] = list()

    def _store_frame(self, frame: np.ndarray):
        self.frame_buffer.append(frame)
        if len(self.frame_buffer) > self.buffer_size:
            self.frame_buffer = self.frame_buffer[1:]

    @staticmethod
    def apply_chain(img: np.ndarray, transform_chain: List[Callable[[np.ndarray], np.ndarray]]) -> np.ndarray:
        for transform in transform_chain:
            img = transform(img)
        return img

    def process_frame(self, frame: np.ndarray) -> Tuple[np.ndarray, ...]:
        self._store_frame(frame)

        return frame,
