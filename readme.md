# VVC encoding with python 
VVC 의 EncoderAppStatic 을 이용하여 python 이 병렬적으로 encoding 을 하도록 하는 코드.  
이 프로젝트에서는 in-loop filter 을 모두 끄고 encoding 하도록 하였음.  

1. 폴더를 두개로 쪼개주자. 
[seperate_STF.py](seperate_STF.py) 사용.
   
   
2. 10bit_to_8bit_yuv.py 를 이용해서 8bit input 영상을 만들어준다.   
   이때 b = (b + 2) / 4 공식을 이용하였다.
   
   
3. encoder 를 돌리기 위한 .sh 를 만들려고 했으나.. terminal 크기 제한때문에 core dump 애러 발생됨.
   [create_sh_encoder.py](create_sh_encoder.py) 사용하려고 했었음...
   

4. 그래서 python 으로 encoder 돌려주는 코드 작성. 병렬적으로 encoding 하는 것을 tqdm 이용하여 시각화도 하였음.
   [encoder_on_python.py](encoder_on_python.py) 사용.
