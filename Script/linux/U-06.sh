#!/bin/bash

# PATH 환경변수 값
path_value=$(echo $PATH)

# PATH 값에 "."이 맨 앞이나 중간에 포함 확인
# "."이 맨 앞이나 중간에 포함되어 있는지를 확인
if [[ $path_value == *.:* || $path_value == *:.* || $path_value == .* ]]; then
    echo -e "파일 및 디렉토리 관리,U-06,root 홈 패스 디렉터리 권한 및 패스 설정,상,취약,\"echo \$PATH의 결과입니다 : \n$path_value\",PATH 환경변수에 "."이 맨 앞이나 중간에 포함되어 있습니다. 클라우드 취약점 점검 가이드를 참고하시어 \"/etc/profile\"파일의 PATH 환경변수에 \".\"이 맨 앞이나 중간에 포함되지 않도록 적용하여 주시기 바랍니다." >> linux_report_$USER.csv
else
    echo -e "파일 및 디렉토리 관리,U-06,root 홈 패스 디렉터리 권한 및 패스 설정,상,양호,\"echo \$PATH의 결과입니다 : \n$path_value\",PATH 환경변수에 "."이 맨 앞이나 중간에 포함되지 않고 있습니다." >> linux_report_$USER.csv
fi

#ok2
