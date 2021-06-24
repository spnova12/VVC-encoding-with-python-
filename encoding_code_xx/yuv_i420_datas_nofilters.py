import cv2
import numpy as np
import math
from glob import glob
import os
import tqdm
from random import *

def psnr(img1, img2):
    mse = np.mean( (img1 - img2) ** 2 )
    if mse == 0:
        return 100
    PIXEL_MAX = 255.0
    return 20 * math.log10(PIXEL_MAX / math.sqrt(mse))

def img_odd2even(img):
    h, w = img.shape[:2]
    if not h % 2 == 0:
        h -= 1
    if not w % 2 == 0:
        w -= 1
    return img[:h, :w]

def img_to_multipleof16(img):
    h, w = img.shape[:2]
    h = (h//16)*16
    w = (w//16)*16
    return img[:h, :w]



def makedir(my_dir):
    if not os.path.exists(my_dir):
        os.makedirs(my_dir)
    return my_dir



if __name__ == '__main__':

    # YUV_I420 folder dir
    origin_path = '../train2017_yuv'

    # YUV imgs in YUV_I420 folder
    origin_yuv_datas = glob(os.path.join(origin_path, '*.yuv'))

    # new dir
    new_path = '../x'

    # 22, 27, 32, 37 각각에 해당하는 0_RUN_Encoder 의 새 dir
    f_22_path = 'coco_RUN_ENC_AI_nofilter_QP22.sh'
    f_27_path = 'coco_RUN_ENC_AI_nofilter_QP27.sh'
    f_32_path = 'coco_RUN_ENC_AI_nofilter_QP32.sh'
    f_37_path = 'coco_RUN_ENC_AI_nofilter_QP37.sh'
    f_rand_path = 'coco_RUN_ENC_AI_nofilter_QPrandom_under22.sh'

    f_22 = open(f_22_path, 'w')
    f_27 = open(f_27_path, 'w')
    f_32 = open(f_32_path, 'w')
    f_37 = open(f_37_path, 'w')
    f_rand = open(f_rand_path, 'w')

    for img_path in tqdm.tqdm(origin_yuv_datas):
        basename = os.path.splitext(os.path.basename(img_path))[0]
        wh = basename.split('_')[-1].split('x')

        # 예시 : name--1920x1080_600frm_P420_8b_qp37
        basename_new = f'{basename}_1frm_P420_8bit'

        # -------------------------------------------------------------------------
        c = 'encoder_intra_main_nofilters.cfg'
        i = img_path
        wdt = wh[0]
        hgt = wh[1]
        f = 1  # FramesToBeEncoded
        fr = '30'


        q = 22
        b = f'{new_path}/qp{q}/bin/{basename_new}_QP{q}.bin'  # BitstreamFile
        o = f'{new_path}/qp{q}/yuv/{basename_new}_QP{q}.yuv'  # ReconFile
        f_22.write(f'./TAppEncoderStatic -c {c} -i {i} -wdt {wdt} -hgt {hgt} '
                   f'-f {f} -q {q} -fr {fr} -b {b} -o {o}\n\n')

        q = 27
        b = f'{new_path}/qp{q}/bin/{basename_new}_QP{q}.bin'  # BitstreamFile
        o = f'{new_path}/qp{q}/yuv/{basename_new}_QP{q}.yuv'  # ReconFile
        f_27.write(f'./TAppEncoderStatic -c {c} -i {i} -wdt {wdt} -hgt {hgt} '
                   f'-f {f} -q {q} -fr {fr} -b {b} -o {o}\n\n')

        q = 32
        b = f'{new_path}/qp{q}/bin/{basename_new}_QP{q}.bin'  # BitstreamFile
        o = f'{new_path}/qp{q}/yuv/{basename_new}_QP{q}.yuv'  # ReconFile
        f_32.write(f'./TAppEncoderStatic -c {c} -i {i} -wdt {wdt} -hgt {hgt} '
                   f'-f {f} -q {q} -fr {fr} -b {b} -o {o}\n\n')

        q = 37
        b = f'{new_path}/qp{q}/bin/{basename_new}_QP{q}.bin'  # BitstreamFile
        o = f'{new_path}/qp{q}/yuv/{basename_new}_QP{q}.yuv'  # ReconFile
        f_37.write(f'./TAppEncoderStatic -c {c} -i {i} -wdt {wdt} -hgt {hgt} '
                   f'-f {f} -q {q} -fr {fr} -b {b} -o {o}\n\n')

        # 22 이하 random qp
        q = randint(1, 21)
        b = f'{new_path}/qp_random_under22/bin/{basename_new}_QP{q}.bin'  # BitstreamFile
        o = f'{new_path}/qp_random_under22/yuv/{basename_new}_QP{q}.yuv'  # ReconFile
        f_rand.write(f'./TAppEncoderStatic -c {c} -i {i} -wdt {wdt} -hgt {hgt} '
                     f'-f {f} -q {q} -fr {fr} -b {b} -o {o}\n\n')

    f_22.close()
    f_27.close()
    f_32.close()
    f_37.close()
    f_rand.close()