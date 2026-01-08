import streamlit as st
import pandas as pd
import gspread
from datetime import datetime

# --- [1] 기본 설정 및 디자인 ---
st.set_page_config(page_title="KIWU Smart Meeting", page_icon="🎓", layout="wide")

st.markdown("""
    <style>
    .main-header { font-size: 2.0rem; color: #003478; font-weight: bold; margin-bottom: 10px; }
    .card-box { background-color: white; padding: 20px; border-radius: 12px; border: 1px solid #e0e0e0; box-shadow: 0 4px 6px rgba(0,0,0,0.05); text-align: center; }
    .admin-box { background-color: #fff5f5; padding: 20px; border-radius: 10px; border: 1px solid #ffcccc; }
    </style>
""", unsafe_allow_html=True)

# --- [2] 구글 시트 연결 함수 (에러 방지 기능 추가!) ---
def get_google_sheet(sheet_name):
    try:
        # 1. 클라우드 환경인지 확인 (비밀금고가 있는지 시도)
        if "gcp_service_account" in st.secrets:
            creds_dict = st.secrets["gcp_service_account"]
            gc = gspread.service_account_from_dict(creds_dict)
        else:
            # 금고는 있는데 키가 없는 경우 (거의 없음)
            gc = gspread.service_account(filename='service_account.json')
    except Exception:
        # 2. 내 컴퓨터라서 비밀금고 파일 자체가 없는 경우 -> 그냥 내 파일 씀
        gc = gspread.service_account(filename='service_account.json')
        
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
    st.markdown('<div class="main-header">📅 이번 주 회의 안건</div>', unsafe_allow_html=True)
    
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
            
            dept_list = list(df['부서명'].unique())
            selected_dept = st.multiselect("부서 필터:", dept_list, default=dept_list)
            filtered_df = df[df['부서명'].isin(selected_dept)]
            
            st.dataframe(filtered_df, use_container_width=True, hide_index=True)
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
            input_dept = st.selectbox("부서", ["기획처", "교무처", "입학처", "사무처", "산학협력단", "평생교육원", "도서관"])
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
            st.dataframe(df[df['회차정보'] == selected_date], use_container_width=True, hide_index=True)
        else:
            st.warning("보관된 기록이 없습니다.")
    except Exception as e:
        st.error(f"오류: {e}")

# --- [7] 기능 4: 관리자 (Admin) ---
elif menu == "⚙️ 관리자 (Admin)":
    st.markdown('<div class="main-header">⚙️ 관리자 페이지</div>', unsafe_allow_html=True)
    
    password = st.text_input("관리자 비밀번호를 입력하세요.", type="password")

    # [수정된 부분] 안전하게 비밀번호 가져오기
    try:
        # 클라우드에 'admin' 설정이 있으면 가져오기
        if "admin" in st.secrets:
            real_password = st.secrets["admin"]["password"]
        else:
            real_password = "1234"
    except Exception:
        # 내 컴퓨터(로컬)라서 에러나면 그냥 "1234"로 설정
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
        
        if st.button("🚀 마감 실행 및 데이터 이관"):
            if not meeting_name:
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