import streamlit as st
import uuid
import time
from datetime import datetime, timedelta
import base64
import logging
import os
import json
from browser_controller import YouTubeBrowserController
from scheduler import YouTubeScheduler

# 로깅 설정
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 알림음 파일 생성 (없을 경우)
def generate_audio_files():
    if not os.path.exists("notification.wav"):
        # 간단한 삐 소리 파일 생성 (base64로 인코딩된 작은 WAV 파일)
        audio_data = "UklGRpQDAABXQVZFZm10IBAAAAABAAEARKwAAESsAAABAAgAZGF0YXADAAAAAAAAAAAAAAAAgH+Af4B/gH+Af4B/gH+Af4B/gH+Af4B/gH+Af4B/gH+Af4B/gH+Af4B/gH+Af4B/gH+Af4B/gH+Af4B/gH+Af4B/gH+Af4B/gH+Af4B/gH+Af4B/gH+Af4B/gH+Af4B/gH+Af4B/gH+Af4B/gH+Af4B/gH+Af4B/gH+Af4B/gH+Af4B/gH+Af4B/gH+Af4B/gH+Af4B/gH+Af4B/gH+Af4B/gH+Af4B/gH+Af4B/gH+Af4B/gH+Af4B/gH+Af4B/gH+Af4B/gH+Af4B/gH+Af4B/gH+Af4B/gH+Af4B/gH+Af4B/gH+Af4B/gH+Af4B/gH+Af4B/gH+Af4B/gH+Af4B/gH+Af4B/gH+Af4B/gH+Af4B/gH+Af4B/gH+Af4B/gH+Af4B/gH+Af4B/gH+Af4B/gH+Af4B/gH+Af4B/gH+Af4B/gH+Af4B/gH+Af4B/gH+Af4B/gH+Af4B/gH+Af4B/gH+Af4B/gH+Af4B/gH+Af4B/gH+Af4B/gH+Af4B/gH+Af4B/gH+Af4B/gH+Af4B/gH+Af4B/gH+Af4B/gH+Af4B/gH+Af4B/gH+Af4B/gH+Af4B/gH+Af4B/gH+Af4B/gH+Af4B/gH+Af4B/gH+Af4B/gH+Af4B/gH+Af4B/gH+Af4B/gH+Af4B/gH+Af4B/gH+Af4B/gH+Af4B/gH+Af4B/gH+Af4B/gH+Af4B/gH+Af4B/gH+Af4B/gH+Af4B/gH+Af4B/gH+Af4B/gH+Af4B/gH+Af4B/gH+Af4B/gH+Af4B/gH+Af4B/gH+Af4B/gH+Af4B/gH+Af4B/gH+Af4B/gH+Af4B/gH+Af4B/gH+Af4B/gH+Af4B/gH+Af4B/gH+Af4B/gH+Af4B/gH+Af4B/gH+Af4B/gH+Af4B/gH+Af4B/gH+Af4B/gH+Af4B/gH+Af4B/gH+Af4B/gH+Af4B/gH+Af4B/gH+Af4B/gH+Af4B/gH+Af4B/gH+Af4B/gH+Af4B/gH+Af4B/gH+Af4B/gH+Af4B/gH+Af4B/gH+Af4B/gH+Af4B/gH+Af4B/gH+Af4B/gH+Af4B/gH+Af4B/gH+Af4B/gH+Af4B/gA=="
        with open("notification.wav", "wb") as f:
            f.write(base64.b64decode(audio_data))

# 알림 히스토리 저장/로드 함수
def save_notifications():
    try:
        with open("notifications.json", "w") as f:
            json.dump({
                "notifications": st.session_state.notifications,
                "error_logs": st.session_state.error_logs
            }, f)
    except Exception as e:
        logger.error(f"알림 저장 중 오류: {str(e)}")

def load_notifications():
    try:
        if os.path.exists("notifications.json"):
            with open("notifications.json", "r") as f:
                data = json.load(f)
                if "notifications" in data:
                    st.session_state.notifications = data["notifications"]
                if "error_logs" in data:
                    st.session_state.error_logs = data["error_logs"]
    except Exception as e:
        logger.error(f"알림 로드 중 오류: {str(e)}")

# 알림음 파일 생성
generate_audio_files()

# 페이지 설정
st.set_page_config(
    page_title="유튜브 자동 스트리밍 시스템",
    page_icon="🎵",
    layout="wide",
)

# 세션 상태 초기화
if 'scheduler' not in st.session_state:
    browser_controller = YouTubeBrowserController()
    st.session_state.browser_controller = browser_controller
    st.session_state.scheduler = YouTubeScheduler(browser_controller)

if 'notifications' not in st.session_state:
    st.session_state.notifications = []

if 'error_logs' not in st.session_state:
    st.session_state.error_logs = []

if 'play_sound' not in st.session_state:
    st.session_state.play_sound = False

if 'sound_enabled' not in st.session_state:
    st.session_state.sound_enabled = True

if 'last_update_time' not in st.session_state:
    st.session_state.last_update_time = datetime.now()

# 저장된 알림 로드
load_notifications()

# 제목 및 설명
st.title("유튜브 자동 스트리밍 시스템")
st.markdown("""
이 시스템은 설정된 시간에 자동으로 유튜브 영상을 재생하고, 지정된 시간에 종료합니다.
**시간은 1분 단위로 설정할 수 있습니다.**
""")

# 알림 처리 - 스케줄러에서 알림 가져오기
def process_notifications():
    # 스케줄러에서 알림 가져오기
    notifications = st.session_state.scheduler.get_notifications()
    
    if notifications:
        play_sound = False
        
        for notification in notifications:
            if notification["type"] == "error":
                st.session_state.error_logs.append(notification)
            else:
                st.session_state.notifications.append(notification)
            
            # 알림음 재생 트리거
            if st.session_state.sound_enabled:
                play_sound = True
        
        if play_sound and os.path.exists("notification.wav"):
            st.session_state.play_sound = True
            
            # 알림 효과 추가 - 이 부분은 Streamlit 스레드에서 실행되어야 함
            try:
                st.balloons()
            except:
                pass
                
        # 알림 저장
        save_notifications()

# 알림 처리 호출
process_notifications()

# 알림음 재생
if st.session_state.play_sound:
    audio_file = open("notification.wav", "rb")
    audio_bytes = audio_file.read()
    st.audio(audio_bytes, format='audio/wav', start_time=0)
    st.session_state.play_sound = False

# 메인 레이아웃
col1, col2 = st.columns([2, 3])

# 왼쪽 컬럼 - 시간 관리
with col1:
    st.header("시간 관리")
    
    # 새 시간대 추가 폼 - 1분 단위로 시간 설정 가능하도록 수정
    with st.form(key="add_time_form"):
        st.subheader("새 시간대 추가 (1분 단위)")
        
        # 시작 시간 - 시간과 분 분리하여 선택
        st.markdown("**시작 시간:**")
        start_col1, start_col2 = st.columns(2)
        with start_col1:
            start_hour = st.selectbox("시", list(range(24)), index=9, key="start_hour")
        with start_col2:
            start_minute = st.selectbox("분", list(range(60)), key="start_minute")
        
        # 종료 시간 - 시간과 분 분리하여 선택
        st.markdown("**종료 시간:**")
        end_col1, end_col2 = st.columns(2)
        with end_col1:
            end_hour = st.selectbox("시", list(range(24)), index=10, key="end_hour")
        with end_col2:
            end_minute = st.selectbox("분", list(range(60)), key="end_minute")
        
        youtube_url = st.text_input("유튜브 URL", "https://www.youtube.com/watch?v=example")
        
        submit_button = st.form_submit_button(label="추가")
        if submit_button:
            # 시간 형식 변환
            start_time_str = f"{start_hour:02d}:{start_minute:02d}"
            end_time_str = f"{end_hour:02d}:{end_minute:02d}"
            
            # 시작 및 종료 시간 datetime 객체로 변환하여 비교
            now = datetime.now()
            start_dt = now.replace(hour=start_hour, minute=start_minute)
            end_dt = now.replace(hour=end_hour, minute=end_minute)
            
            # 유효성 검사
            if start_dt >= end_dt:
                st.error("종료 시간은 시작 시간보다 이후여야 합니다.")
            elif not youtube_url.startswith("https://www.youtube.com/"):
                st.error("유효한 유튜브 URL을 입력해주세요.")
            else:
                job_id = str(uuid.uuid4())[:8]  # 짧은 ID 생성
                success, message = st.session_state.scheduler.add_job(
                    job_id, start_time_str, end_time_str, youtube_url
                )
                
                if success:
                    st.success(message)
                else:
                    st.error(message)
                    st.session_state.error_logs.append({
                        "type": "error",
                        "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "message": message
                    })
                    save_notifications()
    
    # 현재 시간대 목록
    st.subheader("현재 시간대 목록")
    jobs = st.session_state.scheduler.get_all_jobs()
    
    if not jobs:
        st.info("등록된 시간대가 없습니다.")
    else:
        for job_id, job_info in jobs.items():
            col_info, col_action = st.columns([3, 1])
            with col_info:
                st.write(f"**시작:** {job_info['start_time']} | **종료:** {job_info['end_time']}")
                st.write(f"**URL:** {job_info['youtube_url']}")
                st.write(f"**상태:** {job_info['status']}")
            with col_action:
                if st.button("삭제", key=f"delete_{job_id}"):
                    success, message = st.session_state.scheduler.remove_job(job_id)
                    if success:
                        st.success(message)
                        time.sleep(1)
                        st.experimental_rerun()
                    else:
                        st.error(message)
                        st.session_state.error_logs.append({
                            "type": "error",
                            "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                            "message": message
                        })
                        save_notifications()
            st.markdown("---")

# 오른쪽 컬럼 - 로그 및 알림
with col2:
    st.header("로그 및 알림")
    
    # 알림 설정
    st.subheader("알림 설정")
    sound_enabled = st.checkbox("알림 소리 활성화", value=st.session_state.sound_enabled)
    st.session_state.sound_enabled = sound_enabled
    
    # 오류 로그
    st.subheader("오류 로그")
    if not st.session_state.error_logs:
        st.info("오류 로그가 없습니다.")
    else:
        for log in reversed(st.session_state.error_logs[-10:]):  # 최근 10개만 표시
            st.error(f"**{log['time']}**: {log['message']}")
    
    # 알림 히스토리
    st.subheader("알림 히스토리")
    if not st.session_state.notifications:
        st.info("알림 히스토리가 없습니다.")
    else:
        for notification in reversed(st.session_state.notifications[-10:]):  # 최근 10개만 표시
            if notification["type"] == "start":
                st.success(f"**{notification['time']}**: 작업 {notification['job_id']} 시작됨")
            elif notification["type"] == "end":
                st.info(f"**{notification['time']}**: 작업 {notification['job_id']} 종료됨")

# 사이드바 - 다음 예정 작업 표시
st.sidebar.header("다음 예정 작업")
next_job_container = st.sidebar.empty()

# 다음 예정 작업 업데이트 함수
def update_next_job():
    jobs = st.session_state.scheduler.get_all_jobs()
    now = datetime.now()
    
    # 다음 예정 작업 찾기
    upcoming_jobs = []
    for job_id, job_info in jobs.items():
        if job_info["status"] == "대기중":
            hour, minute = map(int, job_info["start_time"].split(':'))
            job_time = datetime.strptime(job_info["start_time"], "%H:%M").replace(
                year=now.year, month=now.month, day=now.day
            )
            
            if job_time < now:  # 내일 실행될 작업인 경우
                job_time = job_time.replace(day=now.day + 1)
                
            upcoming_jobs.append((job_id, job_info, job_time))
    
    if upcoming_jobs:
        # 시간순으로 정렬
        upcoming_jobs.sort(key=lambda x: x[2])
        next_job_id, next_job_info, next_job_time = upcoming_jobs[0]
        
        next_job_container.write(f"""
        **다음 예정 작업:**
        - 시작 시간: {next_job_info['start_time']}
        - 종료 시간: {next_job_info['end_time']}
        - URL: {next_job_info['youtube_url']}
        """)
    else:
        next_job_container.write("**다음 예정 작업 없음**")

# 다음 예정 작업 업데이트
update_next_job()

# 주기적인 처리
now = datetime.now()
time_diff = now - st.session_state.last_update_time

# 3초마다 알림 처리
if time_diff.total_seconds() >= 3:
    process_notifications()
    update_next_job()
    st.session_state.last_update_time = now

# 앱 종료 시 리소스 정리 (오류 수정)
def cleanup():
    try:
        # st.session_state 직접 접근 대신 조건문으로 안전하게 처리
        scheduler = getattr(st.session_state, 'scheduler', None)
        if scheduler:
            scheduler.shutdown()
        
        browser_controller = getattr(st.session_state, 'browser_controller', None)
        if browser_controller and hasattr(browser_controller, 'driver') and browser_controller.driver:
            browser_controller.close_browser()
    except Exception as e:
        # 콘솔에만 로그 출력 (Streamlit 함수 사용 안함)
        print(f"Cleanup error: {str(e)}")

# 종료 핸들러 등록 (간소화)
try:
    import atexit
    atexit.register(cleanup)
except Exception as e:
    print(f"Failed to register cleanup handler: {str(e)}")
