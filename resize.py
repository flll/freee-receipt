from PIL import Image

def resize_image(img):
    """
    PIL Imageオブジェクトを受け取り、必要に応じてリサイズしたImageオブジェクトを返す
    """
    width, height = img.size

    condition1 = (width * height >= 1150000) and (width >= 1568 and height >= 1568)
    condition2 = (width * height) / 750 >= 1000

    if condition1 or condition2:
        if condition1:
            ratio = 1568 / max(width, height)
        else:
            ratio = (750000 / (width * height)) ** 0.5

        new_width = int(width * ratio)
        new_height = int(height * ratio)

        return img.resize((new_width, new_height), Image.Resampling.LANCZOS)

    return img