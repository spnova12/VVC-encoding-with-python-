encod_ox 에서 영상 encoding 을 ox 로 한다. 



2. 폴더를 두개로 쪼개주자. 
seperate_STF.py 사용.
   


3. 10bit_to_8bit_yuv.py 를 이용해서 8bit input 영상을 만들어준다. 
이때 b = (b + 2) / 4 공식을 이용하였다.
   


4. encoder 를 돌리기 위한 .sh 를 만든다. -> 이거 안하기로함.
terminal 크기 제한때문에 core dump 애러 발생됨.
create_sh_encoder.py 사용하려 했었음...
   
그래서 python 으로 encoder 돌려주는 코드 작성.
encoder_on_python.py 사용.