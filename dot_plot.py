# dot_plot.py

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import numpy as np
import os

st.set_page_config(layout="wide")
st.title("🎯 대학 전형별 결과 등급 분포 시각화")

# 1. 한글 폰트 설정
font_path = "KoPub Dotum Bold.ttf"        # 사용자 업로드 폰트 파일 경로[^1]
fm.fontManager.addfont(font_path)
font_name = fm.FontProperties(fname=font_path).get_name()
plt.rcParams['font.family'] = font_name
plt.rcParams['axes.unicode_minus'] = False          # 마이너스 기호 정상 표시

# 1-0. 사이드바 : 그래프 제목 설정
st.sidebar.header("그래프 제목 설정")
title_text = st.sidebar.text_input(
    "그래프 제목 입력", 
    value="지원자/합격자/불합격자 분포"  # 기본값 설정[^1]
)

# 1-1. 사이드바 : 그래프 크기 설정
st.sidebar.header("그래프 크기 설정")
width = st.sidebar.slider(
    "가로크기(width)",
    min_value=4.0, max_value=32.0, value=16.0, step=1.0
)
height = st.sidebar.slider(
    "세로크기(height)",
    min_value=4.0, max_value=20.0, value=9.0, step=1.0
)

# 1-2. 사이드바 : X축 최대값 설정
st.sidebar.header("X축 설정")
max_grade = st.sidebar.slider(
    "X축 최대값 (등급)", 
    min_value=2.0, max_value=9.0, value=4.5, step=0.5
)  # ← 0.5 단위로 등급 범위를 조정


# 1-3. 범례 위치선택
st.sidebar.header("범례 위치 설정")
legend_loc = st.sidebar.radio(
    "범례 위치를 선택하세요",
    options=[
        "upper right",
        "lower right"
    ],
    index=0 
)

# 1-4. 사이드바 : 선 두께 및 마커 크기 설정
st.sidebar.header("점 스타일 설정")
line_width = st.sidebar.slider(
    "선 두께 (linewidth)",
    min_value=0.5, max_value=10.0, value=2.0, step=0.5
)
marker_size = st.sidebar.slider(
    "마커 크기 (s)",
    min_value=10, max_value=200, value=50, step=10
)


# 2. CSV, XLSX 파일 업로드
# uploaded_file = st.file_uploader("CSV 파일을 업로드하세요", type=["csv"])
uploaded_file = st.file_uploader(
     "CSV 또는 Excel 파일을 업로드하세요",
    type=["csv", "xlsx"]    # CSV와 XLSX 둘 다 허용
    )
if uploaded_file:
    # df = pd.read_csv(uploaded_file, encoding='cp949')
    ext = os.path.splitext(uploaded_file.name)[1].lower()
    if ext == ".csv":
        df = pd.read_csv(uploaded_file, encoding='cp949')
    elif ext in [".xlsx", ".xls"]:
        df = pd.read_excel(uploaded_file, engine='openpyxl')
    else:
        st.error("지원하지 않는 파일 형식입니다.")
        st.stop()

    # 필수 컬럼 확인
    required_cols = {'대학명_전형', '등급', '결과'}
    if not required_cols.issubset(df.columns):
        st.error(f"다음 컬럼이 필요합니다: {required_cols}")
    else:
        # 3. 색상 및 마커 매핑
        color_map = {'합': 'blue', '추합': 'green', '불': 'red'}
        marker_map = {'합':   'o','추합': 'o', '불': r'$\times$'}
        alpha_map  = {'합': 0.9,   '추합': 0.9,   '불': 0.5}  # 투명도 매핑[^1]
        zorder_map = {'합': 3, '추합': 3, '불': 1}

        df['color']  = df['결과'].map(color_map).fillna('gray')
        df['marker'] = df['결과'].map(marker_map).fillna('o')

        # 4.시각화
        fig, ax = plt.subplots(figsize=(width, height))
        # 외곽 테투리 색상 및 두께 설정
        for spine in ax.spines.values():
            spine.set_edgecolor('white')
            spine.set_linewidth(1)
        #전형목록 = df['대학명_전형'].unique()
        #전형목록 = df['대학명_전형'].drop_duplicates().tolist()
        전형목록 = df['대학명_전형'].drop_duplicates().tolist()[::-1]  # csv 파일의 원본 순서 유지
        # 5. y축 카테고리별 연한 회색 가로선 추가 할 경우 사용
        ax.set_axisbelow(True)
        for lvl in 전형목록:
            ax.axhline(
                y=lvl,
                color="lightgray",
                linestyle="--",
                linewidth=0.5
            )

        for 전형 in 전형목록:
            subset = df[df['대학명_전형'] == 전형]
            for res in subset['결과'].unique():
                sub2 = subset[subset['결과'] == res]
                ax.scatter(
                    sub2['등급'], 
                    [전형] * len(sub2),
                    facecolors='none',
                    edgecolors=sub2['color'],   # 테두리 색상 지정
                    marker=marker_map[res],
                    linewidths=line_width,
                    s=marker_size,
                    alpha=alpha_map[res],
                    zorder=zorder_map[res],
                    label=res
                )

        # ax.set_xlabel("교과등급 (Grade)", fontsize=15)
        # ax.set_xlim(0.9, 4.5)
        # ax.set_xticks([1.0,1.5,2.0,2.5,3.0,3.5,4.0])

        # 1-2 슬라이더에서 선택한 max_grade 동적 반영
        ax.set_xlim(0.9, max_grade)
        # 0.5 간격으로 1.0 이상 max_grade 미만(또는 포함) 값을 xticks로 생성
        ticks = np.arange(1.0, max_grade+0.01, 0.5)  
        ax.set_xticks([round(t,1) for t in ticks])

        ax.set_title(title_text, fontsize=18, pad=20)
        ax.grid(True, axis='x', linestyle='--', alpha=0.5)

        # 범례 정리
        # 1) 표시할 순서를 명시
        desired_order = ["합", "추합", "불"]      # legend 순서 고정
        # 2) 기존 handles/labels 수집
        handles, labels = ax.get_legend_handles_labels()
        by_label = dict(zip(labels, handles))
        # 3) 순서대로 handles, labels 재정렬
        ordered_handles = [by_label[r] for r in desired_order if r in by_label]
        ordered_labels  = [r for r in desired_order    if r in by_label]
        # 4) 고정된 순서로 legend 출력
        ax.legend(
            ordered_handles, ordered_labels,
            title="결과",
            loc=legend_loc
        )      # 선택된 위치로 고정



        # ax.legend(ordered_handles, ordered_labels,
        #         #title="결과", 
        #         bbox_to_anchor=(1.05, 1), loc='upper left')

        st.pyplot(fig)
