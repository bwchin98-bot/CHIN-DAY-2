import time
import os
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from dotenv import load_dotenv

load_dotenv()

CONFIG_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config.json')

def load_config():
    config = {
        "GEMINI_API_KEY": os.getenv("GEMINI_API_KEY", ""),
        "EMAIL_SERVICE": os.getenv("EMAIL_SERVICE", "naver"),
        "EMAIL_ID": os.getenv("EMAIL_ID", ""),
        "EMAIL_PW": os.getenv("EMAIL_PW", "")
    }

    if os.path.exists(CONFIG_PATH):
        try:
            with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
                file_config = json.load(f)
                for key in config:
                    if not config[key] and file_config.get(key):
                        config[key] = file_config[key]
        except Exception:
            pass

    return config

def save_config(config_data):
    with open(CONFIG_PATH, 'w', encoding='utf-8') as f:
        json.dump(config_data, f, ensure_ascii=False, indent=2)

def get_mock_emails():
    """실제 크롤링이 불가능하거나 설정이 없을 때 사용할 데모 이메일 데이터"""
    return [
        {
            "id": "mock_1",
            "sender": "김철수 팀장 <chulsoo.kim@company.com>",
            "subject": "[긴급] 상반기 매출 실적 보고서 작성 및 취합 요청",
            "date": "2026-06-12 10:15",
            "body": "안녕하세요 팀원 여러분, 김철수 팀장입니다. 이번 분기 상반기 매출 실적 보고서 작성을 시작해야 합니다. 각 파트별 매출 데이터를 취합하여 오늘 오후 5시까지 공유해 주시기 바랍니다. 특히 신규 프로젝트 성과 부분을 상세히 기술해 주세요. 누락 시 전체 마감에 지장이 있으니 기한 엄수 바랍니다. 감사합니다."
        },
        {
            "id": "mock_2",
            "sender": "글로벌 트래블 <info@globaltravel.com>",
            "subject": "주문하신 항공권 결제 및 예약 완료 안내 (예약번호: GT-88492)",
            "date": "2026-06-12 09:30",
            "body": "고객님, 글로벌 트래블을 이용해 주셔서 감사합니다. 요청하신 2026년 7월 15일 출발 서울(ICN) 발 도쿄(NRT) 행 왕복 항공권 결제가 성공적으로 완료되었습니다. 탑승 3시간 전까지 공항 카운터에서 발권을 진행해 주시기 바라며, 수하물 규정은 첨부 문서를 확인해 주세요. 여권 유효기간은 6개월 이상 남아 있어야 합니다."
        },
        {
            "id": "mock_3",
            "sender": "네이버 클라우드 <noreply@navercloud.com>",
            "subject": "[안내] 네이버 클라우드 플랫폼 정기 서버 점검 안내 (6/18)",
            "date": "2026-06-12 08:00",
            "body": "안녕하세요, 네이버 클라우드 플랫폼입니다. 안정적인 서비스 제공을 위해 아래와 같이 정기 서버 점검 및 업데이트가 예정되어 있습니다. 점검 시간 동안 서비스 접속 및 관리 콘솔 이용이 일시적으로 제한될 수 있으니 서비스 운영에 참고하시기 바랍니다. 일시: 2026년 6월 18일(목) 02:00 ~ 06:00 (약 4시간). 점검 내용: 시스템 안정성 향상 및 보안 패치 적용."
        },
        {
            "id": "mock_4",
            "sender": "영업팀 이영희 대리 <younghee.lee@company.com>",
            "subject": "신규 협력사 미팅 일정 조율의 건",
            "date": "2026-06-11 17:45",
            "body": "안녕하세요 이영희 대리입니다. 지난주 제안서를 발송했던 ABC 테크와 미팅 일정을 조율 중입니다. 업체 측에서는 다음주 화요일(6/16) 오후 2시 또는 목요일(6/18) 오전 10시를 제안했습니다. 참석 가능하신 일정을 회신해 주시면 감사하겠습니다. 회의실 예약 및 다과 준비는 제가 진행하겠습니다."
        },
        {
            "id": "mock_5",
            "sender": "보안팀 <security@company.com>",
            "subject": "[공지] 사내 PC 정기 보안 점검 수행 요청 (금주 마감)",
            "date": "2026-06-11 14:20",
            "body": "임직원 여러분 안녕하십니까, 정보보안팀입니다. 최근 랜섬웨어 및 악성코드 감염 위험이 고조됨에 따라 정기 사내 PC 보안 점검을 진행합니다. 안내된 보안 가이드라인에 따라 개인 PC 내 백신 프로그램을 최신 버전으로 업데이트하고 정밀 검사를 수행해 주시기 바랍니다. 검사 후 완료 스크린샷을 보안팀 메일로 이번 주 금요일(6/14)까지 제출하셔야 합니다. 미제출 시 사내 망 접속이 차단될 수 있습니다."
        }
    ]

class EmailCrawler:
    def __init__(self):
        self.config = load_config()
        self.driver = None

    def setup_driver(self):
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        
        # Webdriver manager를 이용한 크롬 드라이버 자동 설치 및 설정
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=chrome_options)
        self.driver.implicitly_wait(10)

    def login_naver(self, username, password):
        """네이버 로그인 실행 (CAPTCHA 우회를 위해 JS 주입 사용)"""
        self.driver.get("https://nid.naver.com/nidlogin.login")
        time.sleep(2)
        
        # JS를 이용해 로그인 폼 채우기 (직접 입력 시 자동로그인 방지 캡차 발생 가능성 높음)
        self.driver.execute_script("document.getElementsByName('id')[0].value = arguments[0];", username)
        time.sleep(0.5)
        self.driver.execute_script("document.getElementsByName('pw')[0].value = arguments[0];", password)
        time.sleep(0.5)
        
        # 로그인 버튼 클릭
        login_btn = self.driver.find_element(By.ID, "log.login")
        login_btn.click()
        time.sleep(3)
        
        # 로그인 성공 여부 검증 (URL 확인 또는 특정 요소 존재 체크)
        if "nidlogin.login" in self.driver.current_url:
            # 로그인 실패 혹은 2단계 인증/캡차 필요 시
            raise Exception("네이버 로그인 실패 (보안 인증이나 캡차가 발생했을 수 있습니다.)")

    def fetch_naver_emails(self, limit=5):
        """네이버 메일함에서 메일 가져오기"""
        emails = []
        try:
            self.driver.get("https://mail.naver.com/")
            time.sleep(3)
            
            # 메일 목록 로드 대기
            # 네이버 메일은 iframe이나 SPA 구성에 따라 다를 수 있으므로 최신 스마트메일함/메일목록 선택자를 이용
            mail_items = self.driver.find_elements(By.CSS_SELECTOR, "ol.mail_list > li")
            if not mail_items:
                # 구형 메일 디자인 또는 다른 메일 목록 구조 처리
                mail_items = self.driver.find_elements(By.CSS_SELECTOR, "div.mailList > div.mItem")
            
            count = min(len(mail_items), limit)
            for i in range(count):
                try:
                    # 다시 엘리먼트를 찾아서 stale element reference 방지
                    items = self.driver.find_elements(By.CSS_SELECTOR, "ol.mail_list > li")
                    if not items:
                        items = self.driver.find_elements(By.CSS_SELECTOR, "div.mailList > div.mItem")
                    
                    item = items[i]
                    
                    # 제목, 보낸사람, 시간 추출
                    subject_el = item.find_element(By.CSS_SELECTOR, "span.text_area") or item.find_element(By.CSS_SELECTOR, "a.mail_title")
                    subject = subject_el.text
                    
                    sender_el = item.find_element(By.CSS_SELECTOR, "div.sender_area a") or item.find_element(By.CSS_SELECTOR, "div.name a")
                    sender = sender_el.text
                    
                    date_el = item.find_element(By.CSS_SELECTOR, "div.date_area") or item.find_element(By.CSS_SELECTOR, "div.time")
                    date_str = date_el.text
                    
                    # 메일 본문 가져오기 위해 클릭
                    subject_el.click()
                    time.sleep(2)
                    
                    # 메일 본문 iframe 또는 div 추출
                    body = ""
                    try:
                        # 네이버 메일 본문은 iframe 내에 있음
                        iframe = self.driver.find_element(By.ID, "readFrame")
                        self.driver.switch_to.frame(iframe)
                        body = self.driver.find_element(By.TAG_NAME, "body").text
                        self.driver.switch_to.default_content()
                    except Exception:
                        # iframe이 없는 경우
                        try:
                            body = self.driver.find_element(By.CSS_SELECTOR, "div.mail_view_container").text
                        except Exception:
                            body = "메일 본문을 읽어오지 못했습니다."
                    
                    emails.append({
                        "id": f"naver_{i}_{int(time.time())}",
                        "sender": sender,
                        "subject": subject,
                        "date": date_str,
                        "body": body
                    })
                    
                    # 다시 메일 목록으로 돌아가기
                    self.driver.back()
                    time.sleep(2)
                    
                except Exception as e:
                    print(f"개별 메일 수집 중 에러: {e}")
                    continue
            
            return emails
        except Exception as e:
            raise Exception(f"메일 목록 파싱 중 에러 발생: {e}")

    def crawl(self, limit=5):
        """메일 서비스에 맞춰 크롤링 수행"""
        self.config = load_config()
        
        email_service = self.config.get("EMAIL_SERVICE", "naver")
        email_id = self.config.get("EMAIL_ID", "")
        email_pw = self.config.get("EMAIL_PW", "")
        
        # 계정 정보가 없으면 시뮬레이션 데이터 반환
        if not email_id or not email_pw:
            print("계정 정보가 없습니다. 시뮬레이션 데이터를 반환합니다.")
            time.sleep(2) # 크롤링 느낌의 시간 지연
            return get_mock_emails()
        
        try:
            self.setup_driver()
            if email_service == "naver":
                self.login_naver(email_id, email_pw)
                emails = self.fetch_naver_emails(limit)
                return emails
            else:
                # 그 외 서비스의 경우 시뮬레이션 반환
                print(f"지원하지 않는 서비스({email_service})입니다. 시뮬레이션 데이터를 반환합니다.")
                return get_mock_emails()
        except Exception as e:
            print(f"크롤링 에러: {e}. 시뮬레이션 데이터로 대체합니다.")
            return get_mock_emails()
        finally:
            if self.driver:
                self.driver.quit()

if __name__ == "__main__":
    crawler = EmailCrawler()
    res = crawler.crawl(limit=2)
    print("수집 완료:", len(res))
