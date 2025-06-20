#!/bin/bash

detail1="cat /etc/passwd | grep /home (사용자 홈 디렉토리 경로 확인)의 결과입니다 : "
detail2=""
detail3=""

# 결과 초기화
result="양호"
explain="\"사용자, 시스템 시작 파일 및 환경 파일 소유자가 root 또는 해당 계정이고 권한이 644로 설정되어 있는 경우입니다.\""

# /etc/passwd 파일에서 사용자 홈 디렉토리 경로와 로그인 가능한 사용자 필터링
home_directories=($(getent passwd | grep '/home' | awk -F: '$7 != "/sbin/nologin" {print $6}'))

# detail1 변수 설정
detail1+="$(getent passwd | grep /home)\n"

echo "로그인 가능한 사용자 홈 디렉토리 목록:"
echo "${home_directories[@]}"

# 각 홈 디렉토리에서 파일 검색 및 권한 확인
for directory in "${home_directories[@]}"; do
    echo "홈 디렉토리: $directory"
    if [ -d "$directory" ]; then
        # 홈 디렉토리 소유자 및 권한 확인
        detail2+="ls -ld $directory (홈 디렉토리 소유자 및 권한 확인)의 결과입니다 : \n"
        detail2+="$(ls -ld "$directory")\n"
        
        # 홈 디렉토리 소유자 확인
        owner=$(stat -c '%U' "$directory")

        # 홈 디렉토리 내 환경설정 파일 소유자 및 권한 확인
        detail3+="ls -al $directory (홈 디렉토리 내 환경설정 파일 소유자 및 권한 확인): \n"
        for file in "$directory"/.* "$directory"/*; do
            if [ -f "$file" ]; then
                file_owner=$(stat -c '%U' "$file")
                permissions=$(stat -c '%a' "$file")

                # 사용자 홈 디렉토리 내 파일이 root 또는 해당 계정 소유인지 확인
                if [ "$file_owner" != "$owner" ] && [ "$file_owner" != "root" ]; then
                    result="취약"
                    explain="\"사용자, 시스템 시작파일 및 환경 파일 소유자가 root 또는 해당 계정이 아니거나 권한이 644로 설정되어 있지 않은 경우입니다. 클라우드 취약점 점검 가이드를 참고하시어 사용자, 시스템 시작파일 및 환경파일의 소유자를 root로 변경하시고 권한을 644(-rw-r--r--)로 설정하여 주시기 바랍니다.\""
                    continue 2  # 현재 디렉토리 반복을 종료하고 다음 디렉토리로 넘어갑니다.
                fi

                # 파일 권한이 644가 아닌 경우 취약
                if [ "$permissions" -ne 644 ]; then
                    result="취약"
                    explain="\"사용자, 시스템 시작파일 및 환경 파일 소유자가 root 또는 해당 계정이 아니거나 권한이 644로 설정되어 있지 않은 경우입니다. 클라우드 취약점 점검 가이드를 참고하시어 사용자, 시스템 시작파일 및 환경파일의 소유자를 root로 변경하시고 권한을 644(-rw-r--r--)로 설정하여 주시기 바랍니다.\""
                    continue 2  # 현재 디렉토리 반복을 종료하고 다음 디렉토리로 넘어갑니다.
                fi

                # 환경설정 파일 정보 추가
                detail3+="$(ls -al "$file")\n"
            fi
        done
    fi
done


# 결과에 따라 리포트 파일에 추가
echo -e "파일 및 디렉토리 관리,U-15,사용자 시스템 시작파일 및 환경파일 소유자 및 권한 설정,상,$result,\"$detail1\n$detail2\n$detail3\",$explain" >> linux_report_$USER.csv
