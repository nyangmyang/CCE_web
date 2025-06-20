#!/bin/bash

# world writable 파일 검색
#writable_files=$(find / -type f ! \( -path "/proc*" -o -path "sys/fs*" -o -path "/usr/local*" -prune \) -perm -2 -exec ls -al {} \; 2>/dev/null)

#result="양호"
#detail="world writable 파일이 존재하지 않거나 존재 시 설정 이유를 확인하고 있는 경우입니다."
#if [[ -n "$writable_files" ]]; then
  # 찾은 파일들 중에서 타 사용자 쓰기 권한이 있는지 확인
  #while IFS= read -r file; do
    # 파일 권한 확인
    #permissions=$(echo "$file" | awk '{print $1}')
    #if [[ "${permissions:8:1}" == "w" ]]; then
      #result="취약"
      #detail="world writable 파일이 존재하나 해당 설정 이유를 확인하고 있지 않는 경우입니다. 클라우드 취약점 점검 가이드를 참고하시어 일반 사용자 쓰기 권한을 제거하여 주시기 바랍니다."
      #break
    #fi
  #done <<< "$writable_files"
#fi

# 결과에 따라 리포트 파일에 추가
echo -e "파일 및 디렉토리 관리,U-16,world writable 파일 점검,상,인터뷰,담당자 확인이 필요한 항목입니다.,\"클라우드 취약점 점검 가이드를 참고하시어 world writable 파일의 존재 유무와 존재 시 설정 이유를 확인하여 주시기 바랍니다.\n추가 점검 명령어: find / -type f ! \( -path '/proc*' -o -path 'sys/fs*' -o -path '/usr/local*' -prune \) -perm -2 -exec ls -al {} \;\"" >> linux_report_$USER.csv



