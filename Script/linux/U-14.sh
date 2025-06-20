#!/bin/bash

# SUID/SGID 파일 검색
suid_files=$(find / -user root -type f \( -perm -4000 -o -perm -2000 \) -exec ls -lg {} \; 2>/dev/null | tr '\n' '|')

#if [[ -n "$suid_files" ]]; then
    #vulnerability_found=0  # 취약점 발견 여부 플래그
    # setuid가 설정된 파일에 대해 권한 검증
    #while IFS= read -r file; do
        #permissions=$(stat -c "%a" "$file")  # 파일의 권한을 확인
        # 파일 권한이 4750이 아니면 취약점 발견
        #if [[ $permissions != "4750" ]]; then
            #vulnerability_found=1
            #break
        #fi
    #done <<< "$suid_files"
   
    # 취약점을 발견한 경우
    #if [[ $vulnerability_found -eq 1 ]]; then
        #echo -e "파일 및 디렉토리 관리,U-14,SUID SGID Sticy bit 설정 파일 점검,상,취약,\"find / -user root -type f \( -perm -4000 -o -perm -2000 \) -exec ls -lg {} \;의 결과입니다 : \n$suid_files\",주요 실행파일의 권한에 SUID와 SGID에 대한 설정이 부여되어 있는 경우입니다.  클라우드 취약점 점검 가이드를 참고하시어 주요 실행파일의 권한을 4750(-rwsr-x---)으로 변경하시거나 불필요하게 설정된 \"SUID\"를 제거하여 주시기 바랍니다." >> linux_report.csv
    #else
        # 취약점을 발견하지 못한 경우
        #echo -e "파일 및 디렉토리 관리,U-14,SUID SGID Sticy bit 설정 파일 점검,상,양호,\"find / -user root -type f \( -perm -4000 -o -perm -2000 \) -exec ls -lg {} \;의 결과입니다 : \n$suid_files\",주요 실행파일의 권한에 SUID와 SGID에 대한 설정이 부여되어 있지 않은 경우입니다." >> linux_report.csv
    #fi
#else
    # setuid가 설정된 파일을 찾지 못한 경우
    echo -e "파일 및 디렉토리 관리,U-14,SUID SGID Sticy bit 설정 파일 점검,상,인터뷰,담당자 확인이 필요한 항목입니다.,\"클라우드 취약점 점검 가이드를 참고하시어 SUID,GUID 파일의 접근권한이 적절하게 설정되어 있는지 점검하여 주시기 바랍니다.\n추가 점검 명령어: find / -user root -type f \( -perm -4000 -o -perm -2000 \) -exec ls -lg {} \;\"">> linux_report_$USER.csv
#fi



