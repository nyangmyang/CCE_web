import sys
import os  # os 모듈 임포트
import glob
import chardet
import pandas as pd
from openpyxl import load_workbook

# sys.path에 Parsing 디렉토리의 상위 경로 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from .csvParsing import make_excel_report
from .makechart import create_chart, make_col_chart
from .runMecro import run_macro

script_dir = os.path.dirname(os.path.abspath(__file__))

def process_csv_files():
    # result 폴더 내의 모든 csv 파일 경로를 찾음
    csv_files = glob.glob('result/*.csv')
    print(csv_files)

    print("점검 시스템 개수: " + str(len(csv_files)))

    excel_file = os.path.join(script_dir, "취약점 진단 상세 보고서_0603.xlsm")
    result_file = '취약점 진단 상세 보고서_result.xlsx'

    run_macro(excel_file, len(csv_files) - 1)
    # 엑셀 로드
    excel = load_workbook(excel_file)


    # 시스템별 점검 결과_시스템 번호(시트 번호)
    sheet_num = 1

    # 항목별 통계_시스템에 따라 열 지정
    stats_column = 'L'

    def next_column(column):
        if column[-1] == 'Z':  # 마지막 문자가 Z이면 다음 열은 AA, AB 등이 됩니다.
            return column[:-1] + 'A' + 'A' if column[:-1] == '' else chr(ord(column[:-1]) + 1) + 'A'
        else:
            return column[:-1] + chr(ord(column[-1]) + 1)  # 마지막 문자 다음 알파벳으로 업데이트

    for csv_file in csv_files:
        with open(csv_file, 'rb') as f:
            result = chardet.detect(f.read())
            encoding = result['encoding']

        # 두 번째 헤더를 사용하여 CSV 파일 읽기
        csv_data = pd.read_csv(csv_file, encoding=encoding, header=0, quotechar='"', on_bad_lines='skip')

        # csv 파일_구분 항목 추출
        category = csv_data['구분']
        code = csv_data['진단코드']
        explanation = csv_data['진단항목']
        inspection_result = csv_data['점검결과']
        detail = csv_data['시스템 실제 결과값']
        solution = csv_data['상세설명 및 조치방안']

        ip = category.iloc[-1]
        os_info = code.iloc[-1]  # os라는 이름 대신 os_info로 변경
        name = explanation.iloc[-1]

        # 엑셀 시트 지정
        system_result = excel['시스템 별 점검 결과']
        system_copied = excel.copy_worksheet(system_result)
        system_copied.title = f"시스템별 점검 결과_{name}"

        create_chart(system_copied)
        make_excel_report(sheet_num, excel, result_file, system_copied, inspection_result, detail, solution,
                          stats_column, ip, os_info, name, len(csv_files))  # os 대신 os_info 사용

        print(f"{sheet_num}_번 시스템 결과 생성 완료")
        stats_column = next_column(stats_column)  # 다음 열로 업데이트
        sheet_num += 1
    make_col_chart(len(csv_files), excel["요약 통계"], "V6", excel["보안 수준 통계"])
    make_col_chart(len(csv_files), excel["요약 통계"], "H27", excel["요약 통계"])

    excel.save(result_file)

    print("모든 시스템 결과 생성 완료")
    return result_file

if __name__=="__main__":
    process_csv_files()