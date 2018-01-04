def square_crop(img):
    (height, width, *_) = img.shape

    side = min((width, height))
    left = (width - side) // 2
    right = left + side
    top = (height - side) // 2
    bottom = top + side

    return img[top:bottom, left:right]