def square_crop(img):
    (height, width, *_) = img.shape

    side = min((width, height))
    left = (width - side) // 2
    right = left + side
    top = (height - side) // 2
    bottom = top + side

    return img[top:bottom, left:right]


def get_free_port():
    import socket

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(('', 0))
    s.listen(1)
    port = s.getsockname()[1]
    s.close()

    return port
