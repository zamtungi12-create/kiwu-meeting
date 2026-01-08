import streamlit as st
import pandas as pd
import gspread
from datetime import datetime

# --- [1] 기본 설정 및 디자인 ---
st.set_page_config(page_title="KIWU Smart Meeting", page_icon="🎓", layout="wide")

# 깔끔한 디자인을 위한 CSS (표 헤더 색상, 카드 디자인 등)
st.markdown("""
    <style>
    .main-header { font-size: 2.2rem; color: #003478; font-weight: bold; margin-bottom: 10px; }
    .sub-header { font-size: 1.0rem; color: #666; margin-bottom: 20px; }
    .card-box { 
        background-color: white; 
        padding: 20px; 
        border-radius: 12px; 
        border: 1px solid #e0e0e0; 
        box-shadow: 0 4px 6px rgba(0,0,0,0.05); 
        text-align: center; 
    }
    .stDataFrame { border-radius: 10px; overflow: hidden; }
    </style>
""", unsafe_allow_html=True)

# --- [2] 구글 시트 연결 함수 (클라우드 & 로컬 호환 모드) ---
def get_google_sheet():
    # 1. 만약 클라우드(Streamlit Cloud)에 비밀키가 있다면 그걸 사용
    if "gcp_service_account" in st.secrets:
        creds_dict = st.secrets["gcp_service_account"]
        gc = gspread.service_account_from_dict(creds_dict)
    # 2. 내 컴퓨터(Local)라면 json 파일을 사용
    else:
        gc = gspread.service_account(filename='service_account.json')
        
    sheet = gc.open("경인여대 스마트회의 DB").sheet1 
    return sheet

# --- [3] 사이드바 메뉴 ---
with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/commons/2/25/Gyeongin_Women%27s_University_Emblem.png", width=80)
    st.title("KIWU Admin")
    st.caption("경인여자대학교 혁신지원사업단")
    
    menu = st.radio("MENU", ["📊 대시보드 (Dashboard)", "📝 안건 등록 (Input)"], index=0)
    
    st.markdown("---")
    st.info("💡 Tip: 모바일에서도 입력이 가능합니다.")
    if st.button("🔄 데이터 새로고침"):
        st.rerun()

# --- [4] 기능 1: 대시보드 (업그레이드 버전!) ---
if menu == "📊 대시보드 (Dashboard)":
    st.markdown('<div class="main-header">🎓 대학혁신 주간 업무보고</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="sub-header">📅 기준일: {datetime.now().strftime("%Y년 %m월 %d일")} | 종이 없는 스마트 회의</div>', unsafe_allow_html=True)
    
    try:
        sheet = get_google_sheet()
        data = sheet.get_all_records()
        df = pd.DataFrame(data)

        if not df.empty:
            # ---------------------------------------------------------
            # [1] 상단 핵심 지표 (Metrics)
            # ---------------------------------------------------------
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.markdown(f'<div class="card-box"><h5>📑 전체 안건</h5><h2>{len(df)}건</h2></div>', unsafe_allow_html=True)
            with col2:
                ongoing = len(df[df['진행상태'] == '진행중'])
                st.markdown(f'<div class="card-box"><h5>🔥 진행 중</h5><h2 style="color:#e67e22;">{ongoing}건</h2></div>', unsafe_allow_html=True)
            with col3:
                done = len(df[df['진행상태'] == '완료'])
                st.markdown(f'<div class="card-box"><h5>✅ 완료</h5><h2 style="color:#27ae60;">{done}건</h2></div>', unsafe_allow_html=True)
            with col4:
                # 부서 개수 세기
                dept_count = df['부서명'].nunique()
                st.markdown(f'<div class="card-box"><h5>🏢 참여 부서</h5><h2>{dept_count}개</h2></div>', unsafe_allow_html=True)
            
            st.markdown("---")

            # ---------------------------------------------------------
            # [2] 검색 및 필터링 기능 (새로 추가됨!)
            # ---------------------------------------------------------
            st.subheader("🔍 업무 현황 상세")
            
            # 레이아웃을 쪼개서 왼쪽에 필터, 오른쪽에 그래프 배치
            filter_col, graph_col = st.columns([1, 2])

            with filter_col:
                st.markdown("#### 🗂️ 부서별 모아보기")
                # 부서 목록을 자동으로 가져와서 선택 버튼 생성
                dept_list = list(df['부서명'].unique())
                selected_dept = st.multiselect("확인할 부서를 선택하세요:", dept_list, default=dept_list)
                
                # 선택한 부서만 남기기 (데이터 필터링)
                filtered_df = df[df['부서명'].isin(selected_dept)]

            with graph_col:
                # 간단한 막대 그래프 (부서별 안건 수)
                if not filtered_df.empty:
                    chart_data = filtered_df['부서명'].value_counts()
                    st.bar_chart(chart_data, color="#003478", height=250)

            # ---------------------------------------------------------
            # [3] 메인 데이터 표 (접기/펼치기 기능 적용)
            # ---------------------------------------------------------
            st.markdown("<br>", unsafe_allow_html=True)
            
            with st.expander("📋 전체 안건 목록 펼쳐보기 (Click)", expanded=True):
                # 보기 좋게 컬럼 순서 정리
                display_cols = ['부서명', '구분', '업무내용', '진행상태', '마감기한', '담당자', '비고']
                
                # 데이터프레임 보여주기
                st.dataframe(
                    filtered_df[display_cols],
                    use_container_width=True,
                    hide_index=True,
                    height=400
                )
        else:
            st.warning("등록된 데이터가 없습니다.")

    except Exception as e:
        st.error("연결 오류가 발생했습니다.")
        st.write(e)

# --- [5] 기능 2: 안건 등록 (디자인 개선) ---
elif menu == "📝 안건 등록 (Input)":
    st.markdown('<div class="main-header">📝 주간 업무 등록</div>', unsafe_allow_html=True)
    
    with st.container(): # 박스로 감싸기
        with st.form("input_form", clear_on_submit=True):
            st.markdown("###### ✅ 이번 주 주요 추진 실적 및 계획을 입력해주세요.")
            
            col_a, col_b = st.columns(2)
            with col_a:
                input_dept = st.selectbox("부서", ["기획처", "교무처", "입학처", "사무처", "산학협력단", "평생교육원", "도서관"])
                input_type = st.selectbox("구분", ["주요현안", "일반보고", "협조요청"])
            with col_b:
                input_status = st.selectbox("진행 상태", ["진행중", "완료", "지연", "예정"])
                input_date = st.date_input("마감 기한")
            
            input_content = st.text_area("업무 내용", height=120, placeholder="예: 2026학년도 신입생 충원율 제고 방안 보고")
            
            col_c, col_d = st.columns(2)
            with col_c:
                input_name = st.text_input("담당자명", placeholder="이름을 입력하세요")
            with col_d:
                input_note = st.text_input("비고", placeholder="예산, 협조부서 등")
            
            submit_btn = st.form_submit_button("💾 안건 등록하기", type="primary") # 버튼 강조색

            if submit_btn:
                try:
                    sheet = get_google_sheet()
                    now = datetime.now().strftime("%Y-%m-%d %H:%M")
                    new_row = [now, input_dept, input_type, input_content, input_status, str(input_date), input_name, input_note]
                    sheet.append_row(new_row)
                    st.success("✅ 안전하게 등록되었습니다!")
                except Exception as e:
                    st.error(f"등록 실패: {e}")