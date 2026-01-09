import streamlit as st
import pandas as pd
import gspread
from datetime import datetime

# --- [0] 부서 순서 정의 (고정 리스트) ---
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
    
    # [수정] 메뉴에 '수정/삭제' 추가
    menu = st.radio("메뉴 선택", ["📊 금주 현황 (Current)", "📝 안건 등록 (Input)", "🛠️ 수정/삭제 (Edit)", "🗄️ 지난 기록 (History)", "⚙️ 관리자 (Admin)"])
    
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
            
            unique_depts = df['부서명'].unique()
            sorted_depts = [d for d in DEPT_ORDER if d in unique_depts]
            others = [d for d in unique_depts if d not in DEPT_ORDER]
            final_dept_list = sorted_depts + others

            selected_dept = st.multiselect("부서 필터:", final_dept_list, default=final_dept_list)
            
            filtered_df = df[df['부서명'].isin(selected_dept)]
            
            filtered_df['부서명'] = pd.Categorical(filtered_df['부서명'], categories=DEPT_ORDER + others, ordered=True)
            filtered_df = filtered_df.sort_values('부서명')

            # [추가] 현황판에서는 '비밀번호' 컬럼이 보이면 안 되므로 제거 후 출력
            if '비밀번호' in filtered_df.columns:
                display_df = filtered_df.drop(columns=['비밀번호'])
            else:
                display_df = filtered_df

            st.dataframe(
                display_df, 
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
            input_dept = st.selectbox("부서", DEPT_ORDER)
            input_type = st.selectbox("구분", ["주요현안", "일반보고", "협조요청"])
        with col_b:
            input_status = st.selectbox("상태", ["진행중", "완료", "지연", "예정"])
            input_date = st.date_input("마감 기한")
        
        input_content = st.text_area("업무 내용", height=100)
        col_c, col_d = st.columns(2)
        with col_c: input_name = st.text_input("담당자")
        with col_d: input_note = st.text_input("비고")
        
        # [추가] 비밀번호 입력란 (수정/삭제용)
        st.markdown("---")
        st.caption("🔒 수정/삭제를 위해 비밀번호(숫자 4자리)를 입력해주세요.")
        input_pw = st.text_input("비밀번호", type="password", max_chars=4, placeholder="예: 1234")
        
        if st.form_submit_button("💾 등록하기", type="primary"):
            # 비밀번호 미입력 시 경고
            if not input_pw:
                st.warning("비밀번호를 입력해주세요!")
            else:
                try:
                    sheet = get_google_sheet("Current")
                    now = datetime.now().strftime("%Y-%m-%d %H:%M")
                    # [추가] 비밀번호를 맨 마지막 컬럼에 함께 저장
                    sheet.append_row([now, input_dept, input_type, input_content, input_status, str(input_date), input_name, input_note, input_pw])
                    st.success("등록되었습니다!")
                except Exception as e:
                    st.error(f"저장 실패: {e}")

# --- [NEW] 기능 3: 수정/삭제 (Edit) ---
elif menu == "🛠️ 수정/삭제 (Edit)":
    st.markdown('<div class="main-header">🛠️ 안건 수정 및 삭제</div>', unsafe_allow_html=True)
    
    try:
        sheet = get_google_sheet("Current")
        data = sheet.get_all_records()
        df = pd.DataFrame(data)
        
        if df.empty:
            st.info("수정할 데이터가 없습니다.")
        else:
            # 1. 수정할 안건 찾기
            st.subheader("1. 수정할 안건 선택")
            
            # 검색 편의를 위해 부서 선택
            dept_list_for_edit = sorted(df['부서명'].unique())
            edit_dept = st.selectbox("부서를 선택하세요", dept_list_for_edit)
            target_df = df[df['부서명'] == edit_dept]
            
            # 안건 선택 (시간 + 내용으로 구분)
            if not target_df.empty:
                task_options = target_df.apply(lambda x: f"[{x['입력일시']}] {x['업무내용'][:20]}...", axis=1)
                selected_task_idx = st.selectbox("안건을 선택하세요", task_options.index, format_func=lambda x: task_options[x])
                
                selected_row = df.loc[selected_task_idx]
                st.info(f"선택된 안건: {selected_row['업무내용']}")
                
                # 2. 비밀번호 확인
                st.subheader("2. 비밀번호 확인")
                chk_pw = st.text_input("등록할 때 입력한 비밀번호를 입력하세요", type="password")
                
                if st.button("확인"):
                    # 비밀번호 비교 (문자열로 변환하여 비교)
                    if str(selected_row.get('비밀번호', '')) == str(chk_pw):
                        st.session_state['auth_success'] = True
                        st.session_state['target_idx'] = selected_task_idx 
                    else:
                        st.error("비밀번호가 일치하지 않습니다.")
                
                # 3. 수정/삭제 폼 (인증 성공 시에만 표시)
                if st.session_state.get('auth_success', False):
                    st.divider()
                    st.subheader("3. 내용 수정")
                    
                    with st.form("edit_form"):
                        # 기존 값 불러오기
                        e_type = st.selectbox("구분", ["주요현안", "일반보고", "협조요청"], index=["주요현안", "일반보고", "협조요청"].index(selected_row['구분']))
                        e_status = st.selectbox("상태", ["진행중", "완료", "지연", "예정"], index=["진행중", "완료", "지연", "예정"].index(selected_row['진행상태']))
                        e_content = st.text_area("업무 내용", value=selected_row['업무내용'])
                        e_note = st.text_input("비고", value=selected_row['비고'])
                        
                        c1, c2 = st.columns(2)
                        with c1:
                            update_btn = st.form_submit_button("수정 저장", type="primary")
                        with c2:
                            delete_btn = st.form_submit_button("🗑️ 삭제하기")
                        
                        # 엑셀의 실제 행 번호 (헤더가 1행 + 0부터 시작하는 인덱스 + 1 = 인덱스 + 2)
                        real_row_num = selected_task_idx + 2 
                        
                        if update_btn:
                            # 업데이트 (3열:구분, 4열:내용, 5열:상태, 8열:비고)
                            sheet.update_cell(real_row_num, 3, e_type)
                            sheet.update_cell(real_row_num, 4, e_content)
                            sheet.update_cell(real_row_num, 5, e_status)
                            sheet.update_cell(real_row_num, 8, e_note)
                            
                            st.success("수정되었습니다! 새로고침 해주세요.")
                            del st.session_state['auth_success'] # 초기화
                            
                        if delete_btn:
                            sheet.delete_rows(real_row_num)
                            st.success("삭제되었습니다! 새로고침 해주세요.")
                            del st.session_state['auth_success'] # 초기화
            else:
                st.warning("해당 부서에 등록된 안건이 없습니다.")

    except Exception as e:
        st.error(f"오류: {e}")

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
        
        confirm_close = st.checkbox("⚠️ 정말로 이번 주 데이터를 마감하고 초기화하시겠습니까?")
        
        if st.button("🚀 마감 실행 및 데이터 이관"):
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