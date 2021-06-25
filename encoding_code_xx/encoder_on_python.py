import subprocess
from time import time
import os
import random
from tqdm import tqdm
from glob import glob
from multiprocessing import cpu_count


def multi_proc_scheduler(myworks, my_preprocess, cpu_count, backup=True):
    # 완료된 work 들을 기록해준다.
    if backup:
        f = open("backup.txt", mode='a', encoding='utf-8')

    # tqdm 을 이용해서 progressive bar 을 만들어줄 것이다.
    progressive_bar = tqdm(total=len(myworks))

    # 함수가 실행되면 먼저 사용될 코어들을 None 으로 초기화 해준다.
    cpu_core = []
    cpu_core_info = []
    for i in range(cpu_count):
        cpu_core.append(None)
        cpu_core_info.append(None)

    while True:
        # myworks 가 0 이면 더 이상 새로 할 일이 없다는 뜻 이다.
        if len(myworks) == 0:
            # core 에 실행중인 일이 없으면 while 문을 종료해준다.
            # https://stackoverflow.com/questions/6518394/how-to-check-if-all-items-in-the-list-are-none/6518435 참고
            if all(c is None for c in cpu_core):
                # 프로그램이 종료되면 tqdm 도 종료해준다.
                progressive_bar.close()
                if backup:
                    f.close()
                break

        for i in range(cpu_count):
            # core 에 일이 없으면 일을 시키자.
            if cpu_core[i] is None:
                if len(myworks) > 0:
                    # 일을 하나 뽑아서,
                    mywork = myworks.pop()
                    # 일의 정보를 저장하고,
                    cpu_core_info[i] = mywork
                    # preprocessing 을 해준 후, 이때 my_preprocess 의 output 인 p 는 shell 명령어이다.
                    p = my_preprocess(mywork)
                    # subprocess 로 실행해준다.
                    cpu_core[i] = subprocess.Popen(p, shell=True)
            else:
                # Popen.poll() 은 subprocess 가 종료되면 0 을 반환한다.
                if cpu_core[i].poll() == 0:
                    # 할당된 일이 종료되면 core 에 다시 일이 없음을 표시해준다.
                    cpu_core[i] = None
                    # 할당된 일이 종료되면 tqdm 을 업데이트 해준다.
                    progressive_bar.update(1)
                    # 완료된 일은 정보도 초기화 해준다.
                    if backup:
                        f.write(f'{str(cpu_core_info[i][0])} {str(cpu_core_info[i][1])} \n')  # '\n' 은 한칸 띄고 써준다.
                    cpu_core_info[i] = None


if __name__ == "__main__":
    ########################################################################################
    ########################################################################################
    my_cpu_count = 20
    print(f">> cpu usage (mycpu/total): {my_cpu_count}/{cpu_count()}")

    ########################################################################################
    ########################################################################################
    # 아래와 같이 총 4 조건을 encode 해야된다.

    # STF_type = 'STF1'
    # qps = [22, 24, 32, 34, 42, '19under']

    # STF_type = 'STF1_'
    # qps = [19, 27, 29, 37, 39]

    # # (8bit)
    STF_type = 'STF2_8bit'
    qps = [22, 24, 32, 34, 42, '19under']

    # STF_type = 'STF2_8bit_'
    # qps = [19, 27, 29, 37, 39]

    ori_folder_dir = os.path.abspath(f'../../ori/{STF_type}')

    # YUV imgs in YUV_I420 folder
    ori_dirs = sorted(glob(os.path.join(ori_folder_dir, '*.yuv')))
    ori_dirs = ori_dirs  # [:5]

    print(">> 전체 비디오 개수 :", len(ori_dirs))
    print(">> SFT_type :", STF_type)
    print(">> target qps :", qps)
    print(">> total works len :", len(ori_dirs) * len(qps))

    ########################################################################################
    ########################################################################################

    # 할 일들을 담을 리스트.
    works = []

    # 다양한 이미지가 병렬적으로 처리되는 것이 더 효율 적으로 판단됨.
    random.shuffle(ori_dirs)
    for ori_dir in ori_dirs:
        # 마찬가지로, 병렬로 진행하더라도 동시에 같은 qp 가 encoding 되는 것 보다
        # 다양하게 되는것이 효율적 이라고 생각함. 그래서 순서를 shuffle 함.
        random.shuffle(qps)
        for qp in qps:
            works.append([ori_dir, qp])


    # backup 에 저장된 완료된 work 들은 works 에서 제거해준다.
    try:
        print("backup 읽는 중...")
        f = open("backup.txt", 'r')
        lines = f.readlines()
        for line in lines:
            work_finished = line.split(' ')
            work_finished = [work_finished[0], int(work_finished[1])]
            if work_finished in works:
                works.remove(work_finished)
        f.close()
    except:
        print('no backup')

    print(">> 남은 works len :", len(works))


    ########################################################################################
    ########################################################################################


    def my_preprocess(mywork):
        app_dir = os.path.abspath('EncoderAppStatic')
        outs_dir = os.path.abspath('../../STF_xx')
        cfg = 'encoder_intra_vtm_xx.cfg'

        i = mywork[0]
        q_info = mywork[1]
        FramesToBeEncoded = 1
        FrameRate = 60

        basename = os.path.splitext(os.path.basename(i))[0]
        basename_splited = basename.split('_')
        w, h = basename_splited[-2].split('x')
        InputBitDepth = basename_splited[-1]

        cfg2 = "InputBitDepth.cfg"
        with open(cfg2, "w") as f:
            f.write(f"InputBitDepth : {InputBitDepth}")

        if q_info == '19under':
            q = random.randint(1, 18)
        else:
            q = q_info


        os.makedirs(f'{outs_dir}/log_{STF_type}/{q_info}', exist_ok=True)
        os.makedirs(f'{outs_dir}/bin_{STF_type}/{q_info}', exist_ok=True)
        os.makedirs(f'{outs_dir}/yuv_{STF_type}/{q_info}', exist_ok=True)
        b =         f"{outs_dir}/bin_{STF_type}/{q_info}/{basename}_qp{q}.bin"
        o =         f"{outs_dir}/yuv_{STF_type}/{q_info}/{basename}_qp{q}.yuv"
        log_dir =   f"{outs_dir}/log_{STF_type}/{q_info}/{basename}_qp{q}.log"

        commend = [
            f"(cd {os.path.dirname(app_dir)} && "  # app 의 경로.
            f"./{os.path.basename(app_dir)} "  # app 의 이름.
            f"-c {cfg} "
            f"-c {cfg2} "
            f"-f {FramesToBeEncoded} "
            f"-q {q} "

            f"-wdt {w} "
            f"-hgt {h} "
            f"-fr {FrameRate} "

            f"-i {i} "
            f"-b {b} "
            f"-o {o} "
            f"> {log_dir} "
            f")"
        ]

        # encoder 가 잘 안돌아가면 commend 를 출력해보자.
        # print(commend)

        return commend


    ########################################################################################
    ########################################################################################

    # works 를 my_preprocess 로 가공해서 my_cpu_count 개수만큼 병렬적으로 처리해준다.
    multi_proc_scheduler(works, my_preprocess, my_cpu_count)
