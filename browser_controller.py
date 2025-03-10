from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import logging
import time
import os

class YouTubeBrowserController:
    def __init__(self):
        self.driver = None
        self.logger = logging.getLogger("YouTubeBrowserController")

    def start_browser(self, url):
        """유튜브 URL을 열고 오디오만 재생하도록 브라우저 설정"""
        try:
            chrome_options = Options()
            chrome_options.add_argument("--window-position=0,0")
            chrome_options.add_argument("--window-size=800,600")  # 창 크기 약간 키움

            # 자동화 감지 우회 설정
            chrome_options.add_argument("--disable-infobars")
            chrome_options.add_argument("--disable-popup-blocking")
            chrome_options.add_argument("--autoplay-policy=no-user-gesture-required")
            chrome_options.add_argument("--disable-blink-features=AutomationControlled")
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option("useAutomationExtension", False)
            chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36")

            # uBlock Origin 확장 프로그램 추가 - 드라이버 생성 전에 추가
            extension_path = os.path.join(os.path.dirname(__file__), "ublock_origin.crx")
            if os.path.exists(extension_path):
                try:
                    chrome_options.add_extension(extension_path)
                    self.logger.info("uBlock Origin 확장 프로그램이 추가되었습니다.")
                except Exception as e:
                    self.logger.error(f"확장 프로그램 추가 실패: {str(e)}")
            else:
                self.logger.warning(f"uBlock Origin 확장 프로그램 파일을 찾을 수 없습니다: {extension_path}")

            # ChromeDriver 관련 설정 및 드라이버 생성
            service = Service()  # 또는 Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=chrome_options)

            # 자동화 감지 우회 스크립트 실행
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

            self.driver.get("https://www.youtube.com")  # 유튜브 접속
            time.sleep(5)  # 페이지 로딩 대기

            # 유튜브 URL로 이동
            self.driver.get(url)
            
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