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

ori_folder_dir = '/ssd3/etri/vvc/ori'

# YUV imgs in YUV_I420 folder
ori_dirs = sorted(glob(os.path.join(ori_folder_dir, '*.yuv')))
bin_dirs = sorted(glob(os.path.join('/home/lab/works/datasets/ssd3/etri/vvc/BVI_DVC_OO/AI/bin', '*.bin')))
print("전체 비디오 개수 :", len(ori_dirs))  # 720 sequences


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
# results_dir = 'BVI_DVC/qp17'
# results_dir = [join(results_dir, x) for x in sorted(listdir(results_dir))]
#
# result_dirs = {}
# for result in results_dir[1:]:
#     yuvs = sorted(listdir(result + '/yuv'))
#     yuvs = get_name_from_list(yuvs)
#
#     bins = sorted(listdir(result + '/bin'))
#     bins = get_name_from_list(bins)
#
#     dict = {'yuv': yuvs, 'bin': bins}
#     result_dirs[result.split('/')[-1]] = dict
#
#
# new_ori_video_dirs = []
# # 채집한 파일들이 yuv 4개씩, bin 4개씩 있는지 확인한다.
# for ori_video in ori_video_dirs:
#     nn = os.path.splitext(os.path.basename(ori_video))[0]
#
#     nn = '_'.join(nn.split('_')[:-2]) + f'_8bit'
#
#     if nn + '_qp22' not in result_dirs['qp22']['yuv']:
#         new_ori_video_dirs.append(ori_video)
#     elif nn + '_qp27' not in result_dirs['qp27']['yuv']:
#         new_ori_video_dirs.append(ori_video)
#     elif nn + '_qp32' not in result_dirs['qp32']['yuv']:
#         new_ori_video_dirs.append(ori_video)
#     elif nn + '_qp37' not in result_dirs['qp37']['yuv']:
#         new_ori_video_dirs.append(ori_video)
#     elif nn + '_qp22' not in result_dirs['qp22']['bin']:
#         new_ori_video_dirs.append(ori_video)
#     elif nn + '_qp27' not in result_dirs['qp27']['bin']:
#         new_ori_video_dirs.append(ori_video)
#     elif nn + '_qp32' not in result_dirs['qp32']['bin']:
#         new_ori_video_dirs.append(ori_video)
#     elif nn + '_qp37' not in result_dirs['qp37']['bin']:
#         new_ori_video_dirs.append(ori_video)
#
#
# print(len(new_ori_video_dirs))
# new_ori_video_dirs = list(set(new_ori_video_dirs))
# print(len(new_ori_video_dirs))
# ori_video_dirs = sorted(new_ori_video_dirs)

##################################################################################################
##################################################################################################
#completed_path = '/home/lab/works/datasets/ssd/etri2020/BVI_DVC_VVC/qp22/yuv'
#completed_sequences = os.listdir(completed_path)


# 셔플을 해서 골고루 균형이 잘 맞게 분산되길 기원한다.
random.shuffle(ori_dirs)
#bin이 없는 video와 qp만 골라낸다.
idx = 0
for ori_dir in ori_dirs:
    ori_bn = os.path.basename(ori_dir).split('_')[0]
    bin_bn = os.path.basename(bin_dir)
    for qp in [22, 27, 32, 37, 42]:
        if ori_bn+f'_qp{qp}.bin' is not bin_bn:
            video_groups[idx].append([ori, qp])
            idx += 1
        if idx == multi_count:
            idx = 0
            

'''
for ori_dir in ori_dirs:
    bn = os.path.basename(ori_dir)
    #if bn not in completed_sequences:
    video_groups[idx].append(bin_dir)
    idx += 1
    if idx == multi_count:
        idx = 0
'''


print("\n그룹당 비디오의 개수")
for i, t in enumerate(video_groups):
    print(f'group{i} :', len(t))


# =============================================================================================================

# 이제 그룹별로 나눠진 비디오들을 엔코딩할 수 있게 해보자.

encoder = 'EncoderAppStatic'
cfg = '../encoder_intra_vtm.cfg'

my_sh = open(f'RUN_ENC_RA_BVI_DVC.sh', mode='wt', encoding='utf-8')

class_dict = {'A':[3840, 2176], 'B':[1920, 1088], 'C':[960, 544], 'D':[480, 272]}
for i, video_group in enumerate(video_groups):  # whole 20 video_groups
    # 한 process 를 만들어준다.
    my_sh.write('\n\n{')
    for video in video_group:
        name = os.path.splitext(os.path.basename(video))[0]

        # frame_count 를 계산해준다.
        # input video is 10 bit (it is same with 16bit) so here is '* 0.5'
        #frame_count = int(os.path.getsize(video) * 0.5 / (int(wh[0]) * int(wh[1]) * 1.5))
        frame_count = 64  # BVI_DVC contains sequences comprise of whole 64 frames


        #nn = '_'.join(n.split('_')[:-2]) + f'_8bit'
        n = name.split('_')[0]
        wh = class_dict[n[0]]
        w, h = wh[0], wh[1]
        FrameRate = name.split('_')[2][:2]

        qp = 22
        nn = n
        my_sh.write(f'\n\n\nn="{n}_qp{qp}"')
        my_sh.write(f'\nmkdir ${{n}}')
        my_sh.write(f'\ncp {encoder} ${{n}}/{encoder}')
        my_sh.write(f'\nchmod 777 ${{n}}/{encoder}')
        my_sh.write(f'\necho "InputBitDepth : 10" > ${{n}}/InputBitDepth.cfg')
        my_sh.write(f'\nprintf "Level : 6" >> ${{n}}/InputBitDepth.cfg')
        my_sh.write(f'\nInputFile="{video[0]}"')
        my_sh.write(f'\nwdt={wh[0]}')
        my_sh.write(f'\nhgt={wh[1]}')      
        my_sh.write(f'\nFramesToBeEncoded={frame_count}')
        my_sh.write(f'\nQP={qp}')
        log = f"/ssd3/etri/vvc/BVI_DVC_OO/AI/log/{nn}_qp{qp}.log"
        bin_dir = f"/ssd3/etri/vvc/BVI_DVC_OO/AI/bin/{nn}_qp{qp}.bin"
        rec_dir = f'/ssd3/etri/vvc/BVI_DVC_OO/AI/yuv/{nn}_qp{qp}.yuv'

        my_sh.write(
            f'\n(cd ${{n}} && ./{encoder} -c {cfg} -c InputBitDepth.cfg -i $InputFile -o {rec_dir} -wdt $wdt -hgt $hgt -f $FramesToBeEncoded -fr {FrameRate} -q $QP> {log} && mv str.bin {bin_dir} && cd .. && rm -r $n);')


        qp = 27
        nn = n
        my_sh.write(f'\n\n\nn="{n}_qp{qp}"')
        my_sh.write(f'\nmkdir ${{n}}')
        my_sh.write(f'\ncp {encoder} ${{n}}/{encoder}')
        my_sh.write(f'\nchmod 777 ${{n}}/{encoder}')
        my_sh.write(f'\necho "InputBitDepth : 10" > ${{n}}/InputBitDepth.cfg')
        my_sh.write(f'\nprintf "Level : 6" >> ${{n}}/InputBitDepth.cfg')
        my_sh.write(f'\nInputFile="{video}"')
        my_sh.write(f'\nwdt={wh[0]}')
        my_sh.write(f'\nhgt={wh[1]}')      
        my_sh.write(f'\nFramesToBeEncoded={frame_count}')
        my_sh.write(f'\nQP={qp}')
        log = f"/ssd3/etri/vvc/BVI_DVC_OO/AI/log/{nn}_qp{qp}.log"
        bin_dir = f"/ssd3/etri/vvc/BVI_DVC_OO/AI/bin/{nn}_qp{qp}.bin"
        rec_dir = f'/ssd3/etri/vvc/BVI_DVC_OO/AI/yuv/{nn}_qp{qp}.yuv'

        my_sh.write(
            f'\n(cd ${{n}} && ./{encoder} -c {cfg} -c InputBitDepth.cfg -i $InputFile -o {rec_dir} -wdt $wdt -hgt $hgt -f $FramesToBeEncoded -fr {FrameRate} -q $QP > {log} && mv str.bin {bin_dir} && cd .. && rm -r $n);')




        qp = 32
        nn = n
        my_sh.write(f'\n\n\nn="{n}_qp{qp}"')
        my_sh.write(f'\nmkdir ${{n}}')
        my_sh.write(f'\ncp {encoder} ${{n}}/{encoder}')
        my_sh.write(f'\nchmod 777 ${{n}}/{encoder}')
        my_sh.write(f'\necho "InputBitDepth : 10" > ${{n}}/InputBitDepth.cfg')
        my_sh.write(f'\nprintf "Level : 6" >> ${{n}}/InputBitDepth.cfg')
        my_sh.write(f'\nInputFile="{video}"')
        my_sh.write(f'\nwdt={wh[0]}')
        my_sh.write(f'\nhgt={wh[1]}')      
        my_sh.write(f'\nFramesToBeEncoded={frame_count}')
        my_sh.write(f'\nQP={qp}')
        log = f"/ssd3/etri/vvc/BVI_DVC_OO/AI/log/{nn}_qp{qp}.log"
        bin_dir = f"/ssd3/etri/vvc/BVI_DVC_OO/AI/bin/{nn}_qp{qp}.bin"
        rec_dir = f'/ssd3/etri/vvc/BVI_DVC_OO/AI/yuv/{nn}_qp{qp}.yuv'

        my_sh.write(
            f'\n(cd ${{n}} && ./{encoder} -c {cfg} -c InputBitDepth.cfg -i $InputFile -o {rec_dir} -wdt $wdt -hgt $hgt -f $FramesToBeEncoded -fr {FrameRate} -q $QP > {log} && mv str.bin {bin_dir} && cd .. && rm -r $n);')



        qp = 37
        nn = n
        my_sh.write(f'\n\n\nn="{n}_qp{qp}"')
        my_sh.write(f'\nmkdir ${{n}}')
        my_sh.write(f'\ncp {encoder} ${{n}}/{encoder}')
        my_sh.write(f'\nchmod 777 ${{n}}/{encoder}')
        my_sh.write(f'\necho "InputBitDepth : 10" > ${{n}}/InputBitDepth.cfg')
        my_sh.write(f'\nprintf "Level : 6" >> ${{n}}/InputBitDepth.cfg')
        my_sh.write(f'\nInputFile="{video}"')
        my_sh.write(f'\nwdt={wh[0]}')
        my_sh.write(f'\nhgt={wh[1]}')      
        my_sh.write(f'\nFramesToBeEncoded={frame_count}')
        my_sh.write(f'\nQP={qp}')
        log = f"/ssd3/etri/vvc/BVI_DVC_OO/AI/log/{nn}_qp{qp}.log"
        bin_dir = f"/ssd3/etri/vvc/BVI_DVC_OO/AI/bin/{nn}_qp{qp}.bin"
        rec_dir = f'/ssd3/etri/vvc/BVI_DVC_OO/AI/yuv/{nn}_qp{qp}.yuv'

        my_sh.write(
            f'\n(cd ${{n}} && ./{encoder} -c {cfg} -c InputBitDepth.cfg -i $InputFile -o {rec_dir} -wdt $wdt -hgt $hgt -f $FramesToBeEncoded -fr {FrameRate} -q $QP > {log} && mv str.bin {bin_dir} && cd .. && rm -r $n);')
            
            
        qp = 42
        nn = n
        my_sh.write(f'\n\n\nn="{n}_qp{qp}"')
        my_sh.write(f'\nmkdir ${{n}}')
        my_sh.write(f'\ncp {encoder} ${{n}}/{encoder}')
        my_sh.write(f'\nchmod 777 ${{n}}/{encoder}')
        my_sh.write(f'\necho "InputBitDepth : 10" > ${{n}}/InputBitDepth.cfg')
        my_sh.write(f'\nprintf "Level : 6" >> ${{n}}/InputBitDepth.cfg')
        my_sh.write(f'\nInputFile="{video}"')
        my_sh.write(f'\nwdt={wh[0]}')
        my_sh.write(f'\nhgt={wh[1]}')      
        my_sh.write(f'\nFramesToBeEncoded={frame_count}')
        my_sh.write(f'\nQP={qp}')
        log = f"/ssd3/etri/vvc/BVI_DVC_OO/AI/log/{nn}_qp{qp}.log"
        bin_dir = f"/ssd3/etri/vvc/BVI_DVC_OO/AI/bin/{nn}_qp{qp}.bin"
        rec_dir = f'/ssd3/etri/vvc/BVI_DVC_OO/AI/yuv/{nn}_qp{qp}.yuv'

        my_sh.write(
            f'\n(cd ${{n}} && ./{encoder} -c {cfg} -c InputBitDepth.cfg -i $InputFile -o {rec_dir} -wdt $wdt -hgt $hgt -f $FramesToBeEncoded -fr {FrameRate} -q $QP > {log} && mv str.bin {bin_dir} && cd .. && rm -r $n);')

    # 마지막 끝날때는 & 를 붙이지 않는다.
    if i == multi_count - 1:
        my_sh.write('\n}')
    else:
        my_sh.write('\n}&')


my_sh.close()
