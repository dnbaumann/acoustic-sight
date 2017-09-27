import math

import numpy as np


_curves = dict()


def is_power_of_2(num):
    return ((num & (num - 1)) == 0) and num != 0


def hilbert_curve(n):
    """
    Generate Hilbert curve indexing for (n, n) array. 'n' must be a power of two.
    Taken from http://znah.net/hilbert-curve-indexing.html. Thanks to Alexander Mordvintsev.
    """
    # recursion base
    if n == 1:
        return np.zeros((1, 1), np.int32)
    # make (n/2, n/2) index
    t = hilbert_curve(n//2)
    # flip it four times and add index offsets
    a = np.flipud(np.rot90(t))
    b = t + t.size
    c = t + t.size*2
    d = np.flipud(np.rot90(t, -1)) + t.size*3
    # and stack four tiles into resulting array
    return np.vstack(map(np.hstack, [[a, b], [d, c]]))


def hilbert_expand(arr):
    if not len(arr.shape) == 2:
        raise ValueError('Hilbert expand supports only 2D arrays, %s is given.' % repr(arr.shape))
    if not arr.shape[0] == arr.shape[1]:
        raise ValueError('Hilbert expand supports only square arrays, %s is given.' % repr(arr.shape))
    if not is_power_of_2(arr.shape[0]):
        raise ValueError('Hilbert expand array side should be a power of 2 but %s is given.' % repr(arr.shape))

    n = arr.shape[0]
    if n not in _curves:
        _curves[n] = hilbert_curve(n)
    idx = _curves[n]

    vec = np.zeros((n * n), arr.dtype)

    for i in range(n):
        for j in range(n):
            vec[idx[i][j]] = arr[i][j]

    return vec


def hilbert_wrap(vec):
    if not len(vec.shape) == 1:
        raise ValueError('Hilbert wrap supports only 1D arrays, %s is given.' % repr(vec.shape))
    if not is_power_of_2(vec.size):
        raise ValueError('Hilbert wrap vector side should be a power of 2 size, %s is given.' % repr(vec.size))

    n = math.floor(math.sqrt(vec.size))
    if n not in _curves:
        _curves[n] = hilbert_curve(n)
    idx = _curves[n]

    arr = np.zeros((n, n), vec.dtype)

    for i in range(n):
        for j in range(n):
            arr[i][j] = vec[idx[i][j]]

    return arr


def __test():
    idx = hilbert_curve(4)
    expanded = hilbert_expand(idx)
    wrapped = hilbert_wrap(expanded)

    print(idx)
    print(expanded)
    print(wrapped)


if __name__ == "__main__":
    __test()
