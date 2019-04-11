import argparse
import os

import numpy as np
from PIL import Image
import cv2


def run(args):
    target_path = args.target_pic_file
    if not os.path.exists(target_path):
        raise FileExistsError()
    else:
        target_img = Image.open(target_path)
        w, h = target_img.size
        res = []
        pics = gen_pics(args)
        img = np.array(target_img)
        for y in range(w):
            t = []
            for x in range(h):
                t_B = img[x, y, 0]
                t_G = img[x, y, 1]
                t_R = img[x, y, 2]
                file_path = sorted(pics, key=lambda p: (p.r - t_R) ** 2 +
                                                       (p.g - t_G) ** 2 +
                                                       (p.b - t_B) ** 2)[0].path
                t.append(file_path)
                print("像素最相近图像", file_path)
            res.append(t)
        del pics
        genImage(res, (w, h), args)


def genImage(matrix, shape, args):
    w, h = shape
    img = np.zeros((h * args.img_size, w * args.img_size, 3)).astype(np.uint8)
    for y in range(w):
        for x in range(h):
            img[x * args.img_size:(x + 1) * args.img_size, y * args.img_size:(y + 1) * args.img_size, :] = np.array(
                Image.open(matrix[y][x]))
            print("合并图像 {} / {}".format(y * h + x, w * h))
    tmp_path = os.path.join(args.pic_dir, 'tmp')
    print("删除缓存文件")
    for file in os.listdir(tmp_path):
        os.remove(os.path.join(tmp_path, file))
    # os.remove(tmp_path)
    print("最终图像大小", img.shape)
    # img = Image.fromarray(img)
    print("保存图像中")
    # img.save(args.save_path)
    cv2.imwrite(args.save_path, img[:, :, ::-1])
    print("图像保存路径：", args.save_path)


class pic:
    def __init__(self, path, r, g, b):
        self.path = path
        self.r = r
        self.g = g
        self.b = b


def gen_pics(args):
    if not os.path.exists(args.pic_dir):
        raise FileExistsError('Directory path of material pictures doesn\'t exist')
    else:
        pics = []
        tmp_save_dir = os.path.join(args.pic_dir, 'tmp')
        if not os.path.exists(tmp_save_dir):
            os.makedirs(tmp_save_dir)
        for file in os.listdir(args.pic_dir):
            file_name = os.path.basename(file)
            print(file_name)
            if os.path.splitext(file)[1] in ['.jpg', '.gif', '.png', '.jpeg']:
                img = Image.open(os.path.join(args.pic_dir, file)).convert('RGB')
                w, h = img.size
                if w < args.img_size or h < args.img_size:
                    s = args.img_size / min(w, h)
                    img = img.resize((w * s, h * s))
                    if w > h:
                        p = (w * s - args.img_size) // 2
                        img = img.crop((p, 0, args.img_size + p, args.img_size))
                    else:
                        p = (h * s - args.img_size) // 2
                        img = img.crop((0, p, args.img_size, args.img_size + p))
                else:
                    pw = (w - args.img_size) // 2
                    ph = (h - args.img_size) // 2
                    img = img.crop((pw, ph, pw + args.img_size, ph + args.img_size))
                file_save_path = os.path.join(tmp_save_dir, file_name)
                img.save(file_save_path)
                img_array = np.array(img)
                b = np.sum(img_array[:, :, 0]) / (args.img_size ** 2)
                g = np.sum(img_array[:, :, 1]) / (args.img_size ** 2)
                r = np.sum(img_array[:, :, 2]) / (args.img_size ** 2)
                del img_array, img
                pics.append(pic(file_save_path, r, g, b))
            else:
                print("{} is not an image file".format(file))
        return pics


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--pic-dir', '-d', type=str, help='directory path contains material pictures', required=True)
    parser.add_argument('--target-pic-file', '-f', type=str, help='path of target picture file', required=True)
    parser.add_argument('--save-path', '-s', type=str, help='path to save the result image', required=True)
    parser.add_argument('--img-size', '-i', type=int, help='height and width size to crop material pictures',
                        required=True)
    args = parser.parse_args()
    run(args)
