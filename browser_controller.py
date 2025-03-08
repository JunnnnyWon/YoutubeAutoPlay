from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import logging
import time

class YouTubeBrowserController:
    def __init__(self):
        self.driver = None
        self.logger = logging.getLogger("YouTubeBrowserController")

    def start_browser(self, url):
        """유튜브 URL을 열고 오디오만 재생하도록 브라우저 설정"""
        try:
            chrome_options = Options()
            chrome_options.add_argument("--window-position=0,0")
            chrome_options.add_argument("--window-size=1,1")
            
            # ChromeDriver 관련 설정 수정
            service = Service()  # ChromeDriverManager().install() 사용하지 않음
            self.driver = webdriver.Chrome(options=chrome_options)
            self.driver.get(url)
            
            # 유튜브 재생 버튼 클릭
            WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "button.ytp-play-button"))
            ).click()
            
            # 음소거 해제 (유튜브가 기본적으로 음소거일 수 있음)
            time.sleep(2)  # 페이지 로딩 기다리기
            try:
                mute_button = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, "button.ytp-mute-button"))
                )
                if "음소거 해제" in mute_button.get_attribute("title") or "Unmute" in mute_button.get_attribute("title"):
                    mute_button.click()
            except Exception as e:
                self.logger.warning(f"음소거 버튼 관련 오류: {str(e)}")
                
            return True, "브라우저가 성공적으로 시작되었습니다."
        except Exception as e:
            error_msg = f"브라우저 시작 중 오류 발생: {str(e)}"
            self.logger.error(error_msg)
            return False, error_msg

    def close_browser(self):
        """브라우저 닫기"""
        try:
            if self.driver:
                self.driver.quit()
                self.driver = None
                return True, "브라우저가 성공적으로 종료되었습니다."
            return False, "브라우저가 실행 중이지 않습니다."
        except Exception as e:
            error_msg = f"브라우저 종료 중 오류 발생: {str(e)}"
            self.logger.error(error_msg)
            return False, error_msg
