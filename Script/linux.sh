#!/bin/bash

# 실행할 스크립트 파일들을 배열에 추가
scripts=(U-01.sh U-02.sh U-03.sh U-04.sh U-05.sh U-06.sh U-07.sh U-08.sh U-09.sh U-10.sh U-11.sh U-12.sh U-13.sh U-14.sh U-15.sh U-16.sh U-17.sh U-18.sh U-19.sh U-20.sh U-21.sh U-22.sh U-23.sh U-24.sh U-25.sh U-26.sh U-27.sh U-28.sh U-29.sh U-30.sh U-31.sh U-32.sh U-33.sh U-34.sh U-35.sh U-36.sh info.sh)

# 배열에 추가한 스크립트 파일들을 차례대로 실행
for script in "${scripts[@]}"
do
    dos2unix "./linux/$script"
    bash "./linux/$script"
    echo "[$script] execution completed."
done
