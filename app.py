import streamlit as st
import pandas as pd
import gspread
from datetime import datetime

# --- [0] 부서 순서 정의 (고정 리스트) ---
# 이곳의 순서를 바꾸면 입력 폼과 조회 화면의 정렬 순서가 동시에 바뀝니다.
DEPT_ORDER = [
    "교목실", "감사팀", "기획팀", "미래전략센터", "혁신지원사업단", 
    "교무수업팀", "교무인사팀", "교육혁신센터", "학사학위센터", 
    "학생복지팀", "장애학생지원센터", "학생상담센터", "사회공헌센터", 
    "커뮤니케이션팀", "입학지원팀", "취창업진로지원센터", "산학운영팀", 
    "RISE사업단", "현장실습지원센터", "일학습병행공동훈련센터", 
    "총무팀", "시설안전팀", "국제교육팀", "글로벌커리어센터", 
    "글로벌인재정주지원센터", "평생교육원", "도서관", "전산정보원", "SG캠퍼스사업단"
]

# --- [1] 기본 설정 및 디자인 ---
st.set_page_config(page_title="KIWU Smart Meeting", page_icon="🎓", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #f8f9fa; }
    .main-header { 
        font-size: 2.2rem; 
        color: #003478; 
        font-weight: 800; 
        margin-top: 10px;
        margin-bottom: 5px; 
    }
    .sub-header {
        font-size: 1.0rem;
        color: #666;
        margin-bottom: 25px;
    }
    .card-box { 
        background-color: white; 
        padding: 25px; 
        border-radius: 15px; 
        border: 1px solid #edf2f7; 
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05); 
        text-align: center; 
        border-top: 5px solid #003478; 
        transition: all 0.3s ease; 
    }
    .card-box:hover {
        transform: translateY(-5px);
        box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
    }
    .admin-box { 
        background-color: #fff5f5; 
        padding: 20px; 
        border-radius: 10px; 
        border: 1px solid #ffcccc; 
    }
    </style>
""", unsafe_allow_html=True)

# --- [2] 구글 시트 연결 함수 (캐싱 적용으로 속도 향상 🚀) ---
@st.cache_resource
def get_connection():
    """구글 시트와의 연결을 한 번만 맺고 캐싱(저장)합니다."""
    try:
        # 1. 스트림릿 클라우드 배포 환경 (Secrets 사용)
        if "gcp_service_account" in st.secrets:
            creds_dict = st.secrets["gcp_service_account"]
            gc = gspread.service_account_from_dict(creds_dict)
        # 2. 로컬 개발 환경 (파일 사용)
        else:
            gc = gspread.service_account(filename='service_account.json')
    except Exception:
        # 예외 발생 시 로컬 파일 시도
        gc = gspread.service_account(filename='service_account.json')
    return gc

def get_google_sheet(sheet_name):
    """캐싱된 연결을 사용하여 시트를 엽니다."""
    gc = get_connection() # 위에서 만든 '빠른 연결'을 가져옴
    doc = gc.open("경인여대 스마트회의 DB")
    return doc.worksheet(sheet_name)

# --- [3] 사이드바 메뉴 ---
with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/commons/2/25/Gyeongin_Women%27s_University_Emblem.png", width=80)
    st.title("KIWU Admin")
    
    menu = st.radio("메뉴 선택", ["📊 금주 현황 (Current)", "📝 안건 등록 (Input)", "🗄️ 지난 기록 (History)", "⚙️ 관리자 (Admin)"])
    
    st.markdown("---")
    if st.button("🔄 새로고침"):
        st.rerun()

# --- [4] 기능 1: 금주 현황 (Current) ---
if menu == "📊 금주 현황 (Current)":
    
    current_hour = datetime.now().hour 
    if 6 <= current_hour < 18:
        banner_image = "campus_day.png"
        caption_text = "경인여자대학교의 힘찬 하루"
    else:
        banner_image = "campus_night.png"
        caption_text = "경인여자대학교의 빛나는 열정"

    try:
        st.image(banner_image, use_container_width=True, caption=caption_text)
    except:
        pass

    st.markdown('<div class="main-header">🎓 경인여자대학교 전략회의</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="sub-header">📅 기준일: {datetime.now().strftime("%Y년 %m월 %d일")} | 종이 없는 스마트 회의 시스템</div>', unsafe_allow_html=True)
    
    try:
        sheet = get_google_sheet("Current")
        data = sheet.get_all_records()
        df = pd.DataFrame(data)

        if not df.empty:
            col1, col2, col3 = st.columns(3)
            with col1: st.markdown(f'<div class="card-box"><h5>전체 안건</h5><h2>{len(df)}건</h2></div>', unsafe_allow_html=True)
            with col2: st.markdown(f'<div class="card-box"><h5>참여 부서</h5><h2>{df["부서명"].nunique()}개</h2></div>', unsafe_allow_html=True)
            with col3: 
                ongoing = len(df[df['진행상태'] == '진행중'])
                st.markdown(f'<div class="card-box"><h5>진행 중</h5><h2 style="color:#e67e22;">{ongoing}건</h2></div>', unsafe_allow_html=True)
            
            st.markdown("---")
            
            # [수정] 부서 필터 순서를 DEPT_ORDER 기준으로 정렬
            # 데이터에 있는 부서만 추려내되, 순서는 DEPT_ORDER를 따름
            unique_depts = df['부서명'].unique()
            sorted_depts = [d for d in DEPT_ORDER if d in unique_depts]
            
            # 혹시 리스트에 없는 부서(예: 오타, 옛날 부서명)가 있다면 맨 뒤에 추가
            others = [d for d in unique_depts if d not in DEPT_ORDER]
            final_dept_list = sorted_depts + others

            selected_dept = st.multiselect("부서 필터:", final_dept_list, default=final_dept_list)
            
            # 데이터 필터링
            filtered_df = df[df['부서명'].isin(selected_dept)]
            
            # [수정] 표 데이터 자체도 부서 순서대로 정렬 (Categorical Sort)
            filtered_df['부서명'] = pd.Categorical(filtered_df['부서명'], categories=DEPT_ORDER + others, ordered=True)
            filtered_df = filtered_df.sort_values('부서명')

            st.dataframe(
                filtered_df, 
                use_container_width=True, 
                hide_index=True,
                column_config={
                    "입력일시": st.column_config.TextColumn("입력일시", width="small"),
                    "부서명": st.column_config.TextColumn("부서명", width="small"),
                    "구분": st.column_config.TextColumn("구분", width="small"),
                    "업무내용": st.column_config.TextColumn("업무내용", width="large"),
                    "진행상태": st.column_config.TextColumn("진행상태", width="small"),
                    "마감기한": st.column_config.TextColumn("마감기한", width="small"),
                    "담당자": st.column_config.TextColumn("담당자", width="small"),
                    "비고": st.column_config.TextColumn("비고", width="small"),
                }
            )
            
        else:
            st.info("👋 아직 등록된 안건이 없습니다. 이번 주 안건을 등록해주세요.")

    except Exception as e:
        st.error(f"오류: {e}")

# --- [5] 기능 2: 안건 등록 (Input) ---
elif menu == "📝 안건 등록 (Input)":
    st.markdown('<div class="main-header">📝 안건 등록</div>', unsafe_allow_html=True)
    st.info("입력된 내용은 '이번 주 현황'에 즉시 반영됩니다.")

    with st.form("input_form", clear_on_submit=True):
        col_a, col_b = st.columns(2)
        with col_a:
            # [수정] 위에서 정의한 DEPT_ORDER 변수를 사용하여 순서 고정
            input_dept = st.selectbox("부서", DEPT_ORDER)
            input_type = st.selectbox("구분", ["주요현안", "일반보고", "협조요청"])
        with col_b:
            input_status = st.selectbox("상태", ["진행중", "완료", "지연", "예정"])
            input_date = st.date_input("마감 기한")
        
        input_content = st.text_area("업무 내용", height=100)
        col_c, col_d = st.columns(2)
        with col_c: input_name = st.text_input("담당자")
        with col_d: input_note = st.text_input("비고")
        
        if st.form_submit_button("💾 등록하기", type="primary"):
            try:
                sheet = get_google_sheet("Current")
                now = datetime.now().strftime("%Y-%m-%d %H:%M")
                sheet.append_row([now, input_dept, input_type, input_content, input_status, str(input_date), input_name, input_note])
                st.success("등록되었습니다!")
            except Exception as e:
                st.error(f"저장 실패: {e}")

# --- [6] 기능 3: 지난 기록 (History) ---
elif menu == "🗄️ 지난 기록 (History)":
    st.markdown('<div class="main-header">🗄️ 지난 회의 기록 보관소</div>', unsafe_allow_html=True)
    
    try:
        sheet = get_google_sheet("History")
        data = sheet.get_all_records()
        df = pd.DataFrame(data)

        if not df.empty:
            meeting_dates = list(df['회차정보'].unique())
            selected_date = st.selectbox("보고 싶은 회차를 선택하세요:", meeting_dates)
            
            history_df = df[df['회차정보'] == selected_date]
            
            # [수정] 지난 기록에서도 부서 순서대로 정렬해서 보여주기
            unique_depts_hist = df['부서명'].unique()
            others_hist = [d for d in unique_depts_hist if d not in DEPT_ORDER]
            
            history_df['부서명'] = pd.Categorical(history_df['부서명'], categories=DEPT_ORDER + others_hist, ordered=True)
            history_df = history_df.sort_values('부서명')

            st.dataframe(
                history_df, 
                use_container_width=True, 
                hide_index=True,
                column_config={
                    "회차정보": st.column_config.TextColumn("회차정보", width="medium"),
                    "입력일시": st.column_config.TextColumn("입력일시", width="small"),
                    "부서명": st.column_config.TextColumn("부서명", width="small"),
                    "업무내용": st.column_config.TextColumn("업무내용", width="large"),
                    "비고": st.column_config.TextColumn("비고", width="small"),
                }
            )
        else:
            st.warning("보관된 기록이 없습니다.")
    except Exception as e:
        st.error(f"오류: {e}")

# --- [7] 기능 4: 관리자 (Admin) ---
elif menu == "⚙️ 관리자 (Admin)":
    st.markdown('<div class="main-header">⚙️ 관리자 페이지</div>', unsafe_allow_html=True)
    
    password = st.text_input("관리자 비밀번호를 입력하세요.", type="password")

    try:
        if "admin" in st.secrets:
            real_password = st.secrets["admin"]["password"]
        else:
            real_password = "1234"
    except Exception:
        real_password = "1234"
    
    if password == real_password:
        st.success("✅ 관리자 모드 접속 완료")
        
        st.markdown("""
        <div class="admin-box">
            <h4>🔴 주간 회의 마감 (Data Closing)</h4>
            <p>이 버튼을 누르면 <b>[Current]</b>의 모든 데이터가 <b>[History]</b>로 이동하고,<br>
            <b>[Current]</b> 시트는 <b>초기화</b>되어 다음 주 입력을 받을 준비를 합니다.</p>
        </div>
        """, unsafe_allow_html=True)
        
        meeting_name = st.text_input("이번 마감할 회차 이름을 입력하세요 (예: 2026-01-08 정기회의)")
        
        # [2번 추가됨] 실수 방지용 체크박스
        confirm_close = st.checkbox("⚠️ 정말로 이번 주 데이터를 마감하고 초기화하시겠습니까?")
        
        if st.button("🚀 마감 실행 및 데이터 이관"):
            # [2번 로직] 체크박스가 체크되지 않았으면 실행 안 함
            if not confirm_close:
                st.error("위의 '마감 확인' 체크박스를 먼저 선택해주세요! (실수 방지)")
            elif not meeting_name:
                st.warning("회차 이름을 먼저 입력해주세요!")
            else:
                try:
                    cur_sheet = get_google_sheet("Current")
                    his_sheet = get_google_sheet("History")
                    
                    data = cur_sheet.get_all_values()
                    
                    if len(data) <= 1:
                        st.warning("이관할 데이터가 없습니다.")
                    else:
                        records = data[1:]
                        for row in records:
                            row.insert(0, meeting_name)
                        
                        his_sheet.append_rows(records)
                        cur_sheet.batch_clear(["A2:Z1000"])
                        
                        st.balloons()
                        st.success(f"✅ [{meeting_name}] 마감이 완료되었습니다! Current 시트가 초기화되었습니다.")
                except Exception as e:
                    st.error(f"마감 중 오류 발생: {e}")
    
    elif password:
        st.error("비밀번호가 틀렸습니다.")