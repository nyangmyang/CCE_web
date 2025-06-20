from openpyxl.chart import BarChart, Reference
from openpyxl.chart.label import DataLabelList

def create_chart(sheet):
    chart = BarChart()
    chart.type = "bar"
    chart.grouping = "stacked"
    chart.style = 2
    chart.title = "요약 결과"

    cats = Reference(sheet, min_col=3, min_row=16, max_row=19)
    data = Reference(sheet, min_col=6, min_row=15, max_col=9, max_row=19)
    chart.add_data(data, titles_from_data=True)
    chart.set_categories(cats)
    chart.overlap=100

    # 데이터 레이블 추가
    chart.dataLabels = DataLabelList()
    chart.dataLabels.showVal = True

    sheet.add_chart(chart, "N5")

def make_col_chart(all_system_num, sheet, position, target_sheet):
    # 차트 객체 생성
    chart = BarChart()
    chart.type = "col"

    # 데이터 범위 설정 ('요약 통계'!$P$27:$Q$29)
    data_range = Reference(sheet, min_col=17, min_row=27, max_col=17, max_row=27 + all_system_num)
    chart.add_data(data_range, titles_from_data=True)

    # 범례 항목 설정 ('요약 통계'!$Q$27)
    series_title = Reference(sheet, min_col=17, min_row=27, max_row=27)
    chart.set_categories(series_title)

    # Y값 설정 ('요약 통계'!$Q$28:$Q$29)
    y_values = Reference(sheet, min_col=17, min_row=28, max_row=28 + all_system_num)
    chart.series[0].values = y_values

    # 가로(항목) 축 레이블 설정 ('요약 통계'!$P$28:$P${28+all_system_num})
    x_labels = Reference(sheet, min_col=16, min_row=28, max_row=28 + all_system_num-1)
    chart.set_categories(x_labels)

    chart.series[0].graphicalProperties.solidFill = "156082"
    chart.legend = None

    # 데이터 레이블 추가
    chart.dataLabels = DataLabelList()
    chart.dataLabels.showVal = True

    # 차트를 워크시트에 추가
    target_sheet.add_chart(chart, position)