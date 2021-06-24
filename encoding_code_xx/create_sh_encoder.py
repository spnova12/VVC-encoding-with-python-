from glob import glob
import os
import random


from os import listdir
from os.path import join
import os


# =============================================================================================================
# 먼저 병렬로 실행하기 위해 비디오들의 그룹을 만들어준다.
multi_count = 20
video_groups = []
for x in range(multi_count):
    video_groups.append([])

ori_video_folder_dir = '/home/lab/works/datasets/ssd/etri2020/BVI_DVC/BVI_DVC'

# YUV imgs in YUV_I420 folder
ori_video_dirs = sorted(glob(os.path.join(ori_video_folder_dir, '*.yuv')))
print("전체 비디오 개수 :", len(ori_video_dirs))


##################################################################################################
##################################################################################################
def get_name(n):
    return os.path.splitext(os.path.basename(n))[0]

def get_name_from_list(l):
    l2 = []
    for x in l:
        l2.append(get_name(x))
    return l2


# 완성된 파일들을 채집하였다.
results_dir = '../BVI_DVC_results'
results_dir = [join(results_dir, x) for x in sorted(listdir(results_dir))]

result_dirs = {}
for result in results_dir[1:]:
    yuvs = sorted(listdir(result + '/yuv'))
    yuvs = get_name_from_list(yuvs)

    bins = sorted(listdir(result + '/bin'))
    bins = get_name_from_list(bins)

    dict = {'yuv': yuvs, 'bin': bins}
    result_dirs[result.split('/')[-1]] = dict


new_ori_video_dirs = []
# 채집한 파일들이 yuv 4개씩, bin 4개씩 있는지 확인한다.
for ori_video in ori_video_dirs:
    nn = os.path.splitext(os.path.basename(ori_video))[0]

    nn = '_'.join(nn.split('_')[:-2]) + f'_8bit'

    if nn + '_qp22' not in result_dirs['qp22']['yuv']:
        new_ori_video_dirs.append(ori_video)
    elif nn + '_qp27' not in result_dirs['qp27']['yuv']:
        new_ori_video_dirs.append(ori_video)
    elif nn + '_qp32' not in result_dirs['qp32']['yuv']:
        new_ori_video_dirs.append(ori_video)
    elif nn + '_qp37' not in result_dirs['qp37']['yuv']:
        new_ori_video_dirs.append(ori_video)
    elif nn + '_qp22' not in result_dirs['qp22']['bin']:
        new_ori_video_dirs.append(ori_video)
    elif nn + '_qp27' not in result_dirs['qp27']['bin']:
        new_ori_video_dirs.append(ori_video)
    elif nn + '_qp32' not in result_dirs['qp32']['bin']:
        new_ori_video_dirs.append(ori_video)
    elif nn + '_qp37' not in result_dirs['qp37']['bin']:
        new_ori_video_dirs.append(ori_video)


print(len(new_ori_video_dirs))
new_ori_video_dirs = list(set(new_ori_video_dirs))
print(len(new_ori_video_dirs))
ori_video_dirs = sorted(new_ori_video_dirs)

##################################################################################################
##################################################################################################


# 셔플을 해서 골고루 균형이 잘 맞게 분산되길 기원한다.
random.shuffle(ori_video_dirs)
idx = 0
for ori_video_dir in ori_video_dirs:
    bn = os.path.basename(ori_video_dir)

    video_groups[idx].append(ori_video_dir)
    idx += 1
    if idx == multi_count:
        idx = 0

print("\n그룹당 비디오의 개수")
for i, t in enumerate(video_groups):
    print(f'group{i} :', len(t))


# =============================================================================================================

# 이제 그룹별로 나눠진 비디오들을 엔코딩할 수 있게 해보자.

c = 'encoder_randomaccess_main.cfg'
encoder = 'TAppEncoderStatic0'

my_sh = open(f'RUN_ENC_RA_BVI_DVC.sh', mode='wt', encoding='utf-8')
my_sh.write('\nsource /home/lab/works/virtualenvs/torch1.5/bin/activate')
my_sh.write('\ncfg="../encoder_randomaccess_main.cfg"')

for i, video_group in enumerate(video_groups):
    # 한 process 를 만들어준다.
    my_sh.write('\n\n{')
    for video in video_group:
        n = os.path.splitext(os.path.basename(video))[0]
        wh = n.split('_')[1].split('x')

        # frame_count 를 계산해준다.
        # input video is 10 bit (it is same with 16bit) so here is '* 0.5'
        frame_count = int(os.path.getsize(video) * 0.5 / (int(wh[0]) * int(wh[1]) * 1.5))



        qp = 22
        nn = '_'.join(n.split('_')[:-2]) + f'_8bit'
        my_sh.write(f'\n\n\nn="{n}_qp{qp}"')
        my_sh.write(f'\nmkdir $n')
        my_sh.write(f'\ncp {encoder} ${{n}}/{encoder}')
        my_sh.write(f'\ncp RA_frames_to_Normal.py ${{n}}/RA_frames_to_Normal.py')
        my_sh.write(f'\nchmod 777 ${{n}}/{encoder}')
        my_sh.write(f'\nInputFile="{video}"')
        my_sh.write(f'\nwdt={wh[0]}')
        my_sh.write(f'\nhgt={wh[1]}')
        my_sh.write(f'\nFramesToBeEncoded={frame_count}')
        my_sh.write(f'\nFrameRate=60')
        my_sh.write(f'\nQP={qp}')
        log =         f"/home/lab/works/datasets/ssd/etri2020/BVI_DVC/BVI_DVC_results/qp{qp}/log/{nn}_qp{qp}.log"
        rec_nof_dir = f"/home/lab/works/datasets/ssd/etri2020/BVI_DVC/BVI_DVC_results/qp{qp}/yuv/{nn}_qp{qp}.yuv"
        bin_dir =     f"/home/lab/works/datasets/ssd/etri2020/BVI_DVC/BVI_DVC_results/qp{qp}/bin/{nn}_qp{qp}.bin"
        rec_ori_dir = f"/home/lab/works/datasets/ssd/etri2020/BVI_DVC/BVI_DVC_results/ori/{nn}.yuv"

        my_sh.write(f'\n(cd ${{n}} && ./TAppEncoderStatic0 -c $cfg -c ../InputBitDepth.cfg -i $InputFile -wdt $wdt -hgt $hgt -f $FramesToBeEncoded -q $QP -fr $FrameRate > {log} && mv rec_nof.yuv {rec_nof_dir} && mv bin.bin {bin_dir} && mv rec_ori.yuv {rec_ori_dir} && cd .. && rm -r $n);')


        qp = 27
        nn = '_'.join(n.split('_')[:-2]) + f'_8bit'
        my_sh.write(f'\n\n\nn="{n}_qp{qp}"')
        my_sh.write(f'\nmkdir $n')
        my_sh.write(f'\ncp {encoder} ${{n}}/{encoder}')
        my_sh.write(f'\ncp RA_frames_to_Normal.py ${{n}}/RA_frames_to_Normal.py')
        my_sh.write(f'\nchmod 777 ${{n}}/{encoder}')
        my_sh.write(f'\nInputFile="{video}"')
        my_sh.write(f'\nwdt={wh[0]}')
        my_sh.write(f'\nhgt={wh[1]}')
        my_sh.write(f'\nFramesToBeEncoded={frame_count}')
        my_sh.write(f'\nFrameRate=60')
        my_sh.write(f'\nQP={qp}')
        log = f"/home/lab/works/datasets/ssd/etri2020/BVI_DVC/BVI_DVC_results/qp{qp}/log/{nn}_qp{qp}.log"
        rec_nof_dir = f"/home/lab/works/datasets/ssd/etri2020/BVI_DVC/BVI_DVC_results/qp{qp}/yuv/{nn}_qp{qp}.yuv"
        bin_dir = f"/home/lab/works/datasets/ssd/etri2020/BVI_DVC/BVI_DVC_results/qp{qp}/bin/{nn}_qp{qp}.bin"

        my_sh.write(
            f'\n(cd ${{n}} && ./TAppEncoderStatic0 -c $cfg -c ../InputBitDepth.cfg -i $InputFile -wdt $wdt -hgt $hgt -f $FramesToBeEncoded -q $QP -fr $FrameRate > {log} && mv rec_nof.yuv {rec_nof_dir} && mv bin.bin {bin_dir} && cd .. && rm -r $n);')




        qp = 32
        nn = '_'.join(n.split('_')[:-2]) + f'_8bit'
        my_sh.write(f'\n\n\nn="{n}_qp{qp}"')
        my_sh.write(f'\nmkdir $n')
        my_sh.write(f'\ncp {encoder} ${{n}}/{encoder}')
        my_sh.write(f'\ncp RA_frames_to_Normal.py ${{n}}/RA_frames_to_Normal.py')
        my_sh.write(f'\nchmod 777 ${{n}}/{encoder}')
        my_sh.write(f'\nInputFile="{video}"')
        my_sh.write(f'\nwdt={wh[0]}')
        my_sh.write(f'\nhgt={wh[1]}')
        my_sh.write(f'\nFramesToBeEncoded={frame_count}')
        my_sh.write(f'\nFrameRate=60')
        my_sh.write(f'\nQP={qp}')
        log = f"/home/lab/works/datasets/ssd/etri2020/BVI_DVC/BVI_DVC_results/qp{qp}/log/{nn}_qp{qp}.log"
        rec_nof_dir = f"/home/lab/works/datasets/ssd/etri2020/BVI_DVC/BVI_DVC_results/qp{qp}/yuv/{nn}_qp{qp}.yuv"
        bin_dir = f"/home/lab/works/datasets/ssd/etri2020/BVI_DVC/BVI_DVC_results/qp{qp}/bin/{nn}_qp{qp}.bin"

        my_sh.write(
            f'\n(cd ${{n}} && ./TAppEncoderStatic0 -c $cfg -c ../InputBitDepth.cfg -i $InputFile -wdt $wdt -hgt $hgt -f $FramesToBeEncoded -q $QP -fr $FrameRate > {log} && mv rec_nof.yuv {rec_nof_dir} && mv bin.bin {bin_dir} && cd .. && rm -r $n);')



        qp = 37
        nn = '_'.join(n.split('_')[:-2]) + f'_8bit'
        my_sh.write(f'\n\n\nn="{n}_qp{qp}"')
        my_sh.write(f'\nmkdir $n')
        my_sh.write(f'\ncp {encoder} ${{n}}/{encoder}')
        my_sh.write(f'\ncp RA_frames_to_Normal.py ${{n}}/RA_frames_to_Normal.py')
        my_sh.write(f'\nchmod 777 ${{n}}/{encoder}')
        my_sh.write(f'\nInputFile="{video}"')
        my_sh.write(f'\nwdt={wh[0]}')
        my_sh.write(f'\nhgt={wh[1]}')
        my_sh.write(f'\nFramesToBeEncoded={frame_count}')
        my_sh.write(f'\nFrameRate=60')
        my_sh.write(f'\nQP={qp}')
        log = f"/home/lab/works/datasets/ssd/etri2020/BVI_DVC/BVI_DVC_results/qp{qp}/log/{nn}_qp{qp}.log"
        rec_nof_dir = f"/home/lab/works/datasets/ssd/etri2020/BVI_DVC/BVI_DVC_results/qp{qp}/yuv/{nn}_qp{qp}.yuv"
        bin_dir = f"/home/lab/works/datasets/ssd/etri2020/BVI_DVC/BVI_DVC_results/qp{qp}/bin/{nn}_qp{qp}.bin"

        my_sh.write(
            f'\n(cd ${{n}} && ./TAppEncoderStatic0 -c $cfg -c ../InputBitDepth.cfg -i $InputFile -wdt $wdt -hgt $hgt -f $FramesToBeEncoded -q $QP -fr $FrameRate > {log} && mv rec_nof.yuv {rec_nof_dir} && mv bin.bin {bin_dir} && cd .. && rm -r $n);')


    # 마지막 끝날때는 & 를 붙이지 않는다.
    if i == multi_count - 1:
        my_sh.write('\n}')
    else:
        my_sh.write('\n}&')


my_sh.close()