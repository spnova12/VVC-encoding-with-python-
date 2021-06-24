from glob import glob
import os
import random


from os import listdir
from os.path import join
import os

"""
아래와 같이 총 4 조건을 encode 해야된다.

[STF1] 
22
24
32
34
42
19_under

[STF1_]
19
27
29
37
39


[STF2] (8bit)
22
24
32
34
42
19_under

[STF2] (8bit)
19
27
29
37
39


"""

# =============================================================================================================
# 먼저 병렬로 실행하기 위해 비디오들의 그룹을 만들어준다.
multi_count = 20
video_groups = []
for x in range(multi_count):
    video_groups.append([])

ori_folder_dir = '/hdd1/works/datasets/ssd2/etri/vvc/STF/ori/STF1'

# YUV imgs in YUV_I420 folder
ori_dirs = sorted(glob(os.path.join(ori_folder_dir, '*.yuv')))

ori_dirs = ori_dirs[0:1]

print("전체 비디오 개수 :", len(ori_dirs))


##################################################################################################
##################################################################################################

# 셔플을 해서 골고루 균형이 잘 맞게 분산되길 기원한다.
random.shuffle(ori_dirs)

idx = 0
for ori_dir in ori_dirs:
    video_groups[idx].append(ori_dir)
    idx += 1
    if idx == multi_count:
        idx = 0

print("\n그룹당 비디오의 개수")
for i, t in enumerate(video_groups):
    print(f'group{i} :', len(t))


# =============================================================================================================

# 이제 그룹별로 나눠진 비디오들을 엔코딩할 수 있게 해보자.

encoder = 'EncoderAppStatic'
cfg = os.path.abspath('../encoder_intra_vtm_xx.cfg')

my_sh = open(f'RUN_ENC_intra_STF.sh', mode='wt', encoding='utf-8')

encoder_dir = '/hdd1/works/datasets/ssd2/etri/vvc/STF/source'


for i, video_group in enumerate(video_groups):  # whole 20 video_groups
    # 한 process 를 만들어준다.
    my_sh.write('\n\n{')
    for video in video_group:
        basename = os.path.splitext(os.path.basename(video))[0]
        basename_splited = basename.split('_')
        w, h = basename_splited[-2].split('x')
        InputBitDepth = basename_splited[-1]

        # frame_count 를 계산해준다.
        # input video is 10 bit (it is same with 16bit) so here is '* 0.5'
        #frame_count = int(os.path.getsize(video) * 0.5 / (int(wh[0]) * int(wh[1]) * 1.5))
        frame_count = 1

        FrameRate = '60'

        qp = 19

        def my_encoder(qp):
            n = basename
            nn = basename
            my_sh.write(f'\n\n\nn="{n}_qp{qp}"')
            my_sh.write(f'\nmkdir ${{n}}')
            my_sh.write(f'\ncp {encoder} ${{n}}/{encoder}')
            my_sh.write(f'\nchmod 777 ${{n}}/{encoder}')
            my_sh.write(f'\necho "InputBitDepth : {InputBitDepth}" > ${{n}}/InputBitDepth.cfg')
            my_sh.write(f'\nprintf "Level : 6" >> ${{n}}/InputBitDepth.cfg')
            my_sh.write(f'\nInputFile="{video}"')
            my_sh.write(f'\nwdt={w}')
            my_sh.write(f'\nhgt={h}')
            my_sh.write(f'\nFramesToBeEncoded={frame_count}')
            my_sh.write(f'\nQP={qp}')

            os.makedirs(f'{encoder_dir}/log{InputBitDepth}/{qp}', exist_ok=True)
            os.makedirs(f'{encoder_dir}/bin{InputBitDepth}/{qp}', exist_ok=True)
            os.makedirs(f'{encoder_dir}/yuv{InputBitDepth}/{qp}', exist_ok=True)
            log =     f"{encoder_dir}/log{InputBitDepth}/{qp}/{nn}_qp{qp}.log"
            bin_dir = f"{encoder_dir}/bin{InputBitDepth}/{qp}/{nn}_qp{qp}.bin"
            rec_dir = f"{encoder_dir}/yuv{InputBitDepth}/{qp}/{nn}_qp{qp}.yuv"

            my_sh.write(
                f'\n(cd ${{n}} && ./{encoder} -c {cfg} -c InputBitDepth.cfg -i $InputFile -o {rec_dir} -wdt $wdt -hgt $hgt -f $FramesToBeEncoded -fr {FrameRate} -q $QP> {log} && mv str.bin {bin_dir} && cd .. && rm -r $n);')


        # qp = 27
        # nn = n
        # my_sh.write(f'\n\n\nn="{n}_qp{qp}"')
        # my_sh.write(f'\nmkdir ${{n}}')
        # my_sh.write(f'\ncp {encoder} ${{n}}/{encoder}')
        # my_sh.write(f'\nchmod 777 ${{n}}/{encoder}')
        # my_sh.write(f'\necho "InputBitDepth : 10" > ${{n}}/InputBitDepth.cfg')
        # my_sh.write(f'\nprintf "Level : 6" >> ${{n}}/InputBitDepth.cfg')
        # my_sh.write(f'\nInputFile="{video}"')
        # my_sh.write(f'\nwdt={wh[0]}')
        # my_sh.write(f'\nhgt={wh[1]}')
        # my_sh.write(f'\nFramesToBeEncoded={frame_count}')
        # my_sh.write(f'\nQP={qp}')
        # log = f"/ssd3/etri/vvc/BVI_DVC_OO/AI/log/{nn}_qp{qp}.log"
        # bin_dir = f"/ssd3/etri/vvc/BVI_DVC_OO/AI/bin/{nn}_qp{qp}.bin"
        # rec_dir = f'/ssd3/etri/vvc/BVI_DVC_OO/AI/yuv/{nn}_qp{qp}.yuv'
        #
        # my_sh.write(
        #     f'\n(cd ${{n}} && ./{encoder} -c {cfg} -c InputBitDepth.cfg -i $InputFile -o {rec_dir} -wdt $wdt -hgt $hgt -f $FramesToBeEncoded -fr {FrameRate} -q $QP > {log} && mv str.bin {bin_dir} && cd .. && rm -r $n);')
        #
        #
        #
        #
        # qp = 32
        # nn = n
        # my_sh.write(f'\n\n\nn="{n}_qp{qp}"')
        # my_sh.write(f'\nmkdir ${{n}}')
        # my_sh.write(f'\ncp {encoder} ${{n}}/{encoder}')
        # my_sh.write(f'\nchmod 777 ${{n}}/{encoder}')
        # my_sh.write(f'\necho "InputBitDepth : 10" > ${{n}}/InputBitDepth.cfg')
        # my_sh.write(f'\nprintf "Level : 6" >> ${{n}}/InputBitDepth.cfg')
        # my_sh.write(f'\nInputFile="{video}"')
        # my_sh.write(f'\nwdt={wh[0]}')
        # my_sh.write(f'\nhgt={wh[1]}')
        # my_sh.write(f'\nFramesToBeEncoded={frame_count}')
        # my_sh.write(f'\nQP={qp}')
        # log = f"/ssd3/etri/vvc/BVI_DVC_OO/AI/log/{nn}_qp{qp}.log"
        # bin_dir = f"/ssd3/etri/vvc/BVI_DVC_OO/AI/bin/{nn}_qp{qp}.bin"
        # rec_dir = f'/ssd3/etri/vvc/BVI_DVC_OO/AI/yuv/{nn}_qp{qp}.yuv'
        #
        # my_sh.write(
        #     f'\n(cd ${{n}} && ./{encoder} -c {cfg} -c InputBitDepth.cfg -i $InputFile -o {rec_dir} -wdt $wdt -hgt $hgt -f $FramesToBeEncoded -fr {FrameRate} -q $QP > {log} && mv str.bin {bin_dir} && cd .. && rm -r $n);')
        #
        #
        #
        # qp = 37
        # nn = n
        # my_sh.write(f'\n\n\nn="{n}_qp{qp}"')
        # my_sh.write(f'\nmkdir ${{n}}')
        # my_sh.write(f'\ncp {encoder} ${{n}}/{encoder}')
        # my_sh.write(f'\nchmod 777 ${{n}}/{encoder}')
        # my_sh.write(f'\necho "InputBitDepth : 10" > ${{n}}/InputBitDepth.cfg')
        # my_sh.write(f'\nprintf "Level : 6" >> ${{n}}/InputBitDepth.cfg')
        # my_sh.write(f'\nInputFile="{video}"')
        # my_sh.write(f'\nwdt={wh[0]}')
        # my_sh.write(f'\nhgt={wh[1]}')
        # my_sh.write(f'\nFramesToBeEncoded={frame_count}')
        # my_sh.write(f'\nQP={qp}')
        # log = f"/ssd3/etri/vvc/BVI_DVC_OO/AI/log/{nn}_qp{qp}.log"
        # bin_dir = f"/ssd3/etri/vvc/BVI_DVC_OO/AI/bin/{nn}_qp{qp}.bin"
        # rec_dir = f'/ssd3/etri/vvc/BVI_DVC_OO/AI/yuv/{nn}_qp{qp}.yuv'
        #
        # my_sh.write(
        #     f'\n(cd ${{n}} && ./{encoder} -c {cfg} -c InputBitDepth.cfg -i $InputFile -o {rec_dir} -wdt $wdt -hgt $hgt -f $FramesToBeEncoded -fr {FrameRate} -q $QP > {log} && mv str.bin {bin_dir} && cd .. && rm -r $n);')
        #
        #
        # qp = 42
        # nn = n
        # my_sh.write(f'\n\n\nn="{n}_qp{qp}"')
        # my_sh.write(f'\nmkdir ${{n}}')
        # my_sh.write(f'\ncp {encoder} ${{n}}/{encoder}')
        # my_sh.write(f'\nchmod 777 ${{n}}/{encoder}')
        # my_sh.write(f'\necho "InputBitDepth : 10" > ${{n}}/InputBitDepth.cfg')
        # my_sh.write(f'\nprintf "Level : 6" >> ${{n}}/InputBitDepth.cfg')
        # my_sh.write(f'\nInputFile="{video}"')
        # my_sh.write(f'\nwdt={wh[0]}')
        # my_sh.write(f'\nhgt={wh[1]}')
        # my_sh.write(f'\nFramesToBeEncoded={frame_count}')
        # my_sh.write(f'\nQP={qp}')
        # log = f"/ssd3/etri/vvc/BVI_DVC_OO/AI/log/{nn}_qp{qp}.log"
        # bin_dir = f"/ssd3/etri/vvc/BVI_DVC_OO/AI/bin/{nn}_qp{qp}.bin"
        # rec_dir = f'/ssd3/etri/vvc/BVI_DVC_OO/AI/yuv/{nn}_qp{qp}.yuv'
        #
        # my_sh.write(
        #     f'\n(cd ${{n}} && ./{encoder} -c {cfg} -c InputBitDepth.cfg -i $InputFile -o {rec_dir} -wdt $wdt -hgt $hgt -f $FramesToBeEncoded -fr {FrameRate} -q $QP > {log} && mv str.bin {bin_dir} && cd .. && rm -r $n);')

    # 마지막 끝날때는 & 를 붙이지 않는다.
    if i == multi_count - 1:
        my_sh.write('\n}')
    else:
        my_sh.write('\n}&')


my_sh.close()
