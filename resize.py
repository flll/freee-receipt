from PIL import Image

def resize_image(img):
    """
    PIL Imageオブジェクトを受け取り、必要に応じてリサイズしたImageオブジェクトを返す
    """
    width, height = img.size

    # 条件1: 1.15メガピクセル以上かつ両方の寸法が1568px以上
    condition1 = (width * height >= 1150000) and (width >= 1568 and height >= 1568)

    # 条件2: (幅 * 高さ) / 750 が1000以上
    condition2 = (width * height) / 750 >= 1000

    # いずれかの条件に該当する場合、リサイズを実行
    if condition1 or condition2:
        if condition1:
            ratio = 1568 / max(width, height)
        else:
            ratio = (750000 / (width * height)) ** 0.5

        new_width = int(width * ratio)
        new_height = int(height * ratio)

        # リサイズを実行して返す
        return img.resize((new_width, new_height), Image.Resampling.LANCZOS)

    # リサイズが不要な場合は元の画像をそのまま返す
    return img