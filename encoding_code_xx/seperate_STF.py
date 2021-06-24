"""
seperate
"""

import cv2
import numpy as np
import math
from glob import glob
import os
import tqdm
from random import *
import random
from os import listdir
from os.path import join
import os
import shutil

if __name__ == '__main__':

    db_dir = '/hdd1/works/datasets/ssd2/etri/vvc/STF/STF/STF2_8bit'
    new_db_dir = f'{db_dir}_'
    os.makedirs(f'{new_db_dir}', exist_ok=True)

    contents = [join(db_dir, x) for x in sorted(listdir(db_dir))]
    random.shuffle(contents)

    print(len(contents))
    contents = contents[:len(contents)//2]
    print(len(contents))

    for content in tqdm.tqdm(contents):
        new_name = f'{new_db_dir}/{os.path.basename(content)}'
        shutil.move(content, f"{new_name}")

