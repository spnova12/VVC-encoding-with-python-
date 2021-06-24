import os
import shutil
import glob
import math
import argparse
import warnings
import numpy as np
import cv2
from tqdm import tqdm
from multiprocessing.dummy import Pool as ThreadPool
from multiprocessing import cpu_count

from sklearn_extra.cluster import KMedoids
from sklearn.cluster import KMeans
from skimage.feature import local_binary_pattern
import random


def read_one_from_yuvs(file_YUV_dir, w, h, start_frame, channel='y', bit=8):
    # 10bit 영상일 경우 16bit 로 읽어준다.
    YUVs = open(file_YUV_dir, 'rb')
    y_size = w * h
    if channel == 'y' or channel == 'yuv' or channel == 'y_u_v':
        channel_bytes = 0
    elif channel == 'u':
        channel_bytes = y_size
        w = int(w * 0.5)
        h = int(h * 0.5)
    else:
        channel_bytes = int(y_size * (5/4))
        w = int(w * 0.5)
        h = int(h * 0.5)

    if bit == 8:
        dtype = np.uint8
        mybyte = 1
    elif bit == 10:
        dtype = np.uint16
        mybyte = 2  # 10bit 를 읽을것이나, 16bit 로 처리를 해준다.

    YUVs.seek(int(y_size * 1.5) * mybyte * start_frame + channel_bytes)

    if channel == 'yuv':
        YUVs_buf = YUVs.read(int(y_size * 1.5) * mybyte)
        frame = np.frombuffer(YUVs_buf, dtype=dtype)
        frame_out = frame.copy()
    elif channel == 'y_u_v':
        YUVs_buf = YUVs.read(int(y_size * 1.5) * mybyte)
        yuv_byte = np.frombuffer(YUVs_buf, dtype=dtype)
        y = yuv_byte[0:y_size]
        y = y.reshape(h, w).copy()
        u = yuv_byte[y_size:y_size + int(y_size / 4)]
        u = u.reshape(int(h * 0.5), int(w * 0.5)).copy()
        v = yuv_byte[y_size + int(y_size / 4):]
        v = v.reshape(int(h * 0.5), int(w * 0.5)).copy()
        frame_out = {'y': y, 'u': u, 'v': v}
    else:
        YUVs_buf = YUVs.read(w * h * mybyte)
        frame = np.reshape(np.frombuffer(YUVs_buf, dtype=dtype), [h, w])
        frame_out = frame.copy()

    YUVs.close()

    return frame_out, w, h



##########################################################################################
##########################################################################################

folder = '/hdd1/works/datasets/ssd2/etri/vvc/STF/STF/STF2'
yuv_dirs = sorted(glob.glob(f"{folder}/*.yuv"))
yuv_dirs = yuv_dirs

print(f"cpu count : {cpu_count()}")
print('imagePaths_total :', len(yuv_dirs))

#########################################

eight_bit_dir = f'../../STF/STF2_8bit'
os.makedirs(f'{eight_bit_dir}', exist_ok=True)


def ten2eight_bit_save(ten_bit_dir):
    basename = os.path.splitext(os.path.basename(ten_bit_dir))[0]
    basename_splited = basename.split('_')
    w, h = basename_splited[-2].split('x')
    name_wo_bit = '_'.join(basename_splited[:-1])
    ten_bit_img, _, _ = read_one_from_yuvs(ten_bit_dir, int(w), int(h), 0, channel='yuv', bit=10)

    def Ten2EightBit(b):
        # 16bit 인데 10 로 사용하는 거니까 2 더한다고 오류가 생기지 않는다.
        b = (b + 2) / 4
        b = b.clip(0, 255)
        b = b.astype(np.uint8)
        return b

    eight_bit_img = Ten2EightBit(ten_bit_img)

    # save yuv420
    with open(f'{eight_bit_dir}/{name_wo_bit}_8bit.yuv', "wb") as f_yuv:
        f_yuv.write(eight_bit_img.astype('uint8').tobytes())

    progressive_bar.update(1)


pool = ThreadPool(cpu_count())
progressive_bar = tqdm(total=len(yuv_dirs))
result = pool.map(ten2eight_bit_save, yuv_dirs)
pool.close()
pool.join()
progressive_bar.close()
