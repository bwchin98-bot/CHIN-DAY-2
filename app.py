import os
import json
import time
from flask import Flask, render_template, jsonify, request
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import google.genai as genai
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

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
    try:
        with open(CONFIG_PATH, 'w', encoding='utf-8') as f:
            json.dump(config_data, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print(f"설정 저장 실패: {e}")
        return False

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/get-settings', methods=['GET'])
def get_settings():
    config = load_config()
    # 패스워드는 마스킹하여 반환
    masked_config = config.copy()
    if masked_config.get("EMAIL_PW"):
        masked_config["EMAIL_PW"] = "********"
    return jsonify(masked_config)

@app.route('/api/save-settings', methods=['POST'])
def update_settings():
    data = request.json
    config = load_config()
    
    if "GEMINI_API_KEY" in data:
        config["GEMINI_API_KEY"] = data["GEMINI_API_KEY"]
    if "EMAIL_SERVICE" in data:
        config["EMAIL_SERVICE"] = data["EMAIL_SERVICE"]
    if "EMAIL_ID" in data:
        config["EMAIL_ID"] = data["EMAIL_ID"]
    if "EMAIL_PW" in data and data["EMAIL_PW"] != "********":
        config["EMAIL_PW"] = data["EMAIL_PW"]
        
    if save_config(config):
        return jsonify({"status": "success", "message": "설정이 성공적으로 저장되었습니다."})
    return jsonify({"status": "error", "message": "설정 저장에 실패했습니다."})

@app.route('/api/fetch-mails')
def fetch_mails():
    config = load_config()
    api_key = config.get("GEMINI_API_KEY", "")
    target_url = request.args.get("url", "").strip()
    
    # 1. 크롬 디버깅 포트 연결 시도
    driver = None
    try:
        chrome_options = Options()
        chrome_options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
        chrome_options.set_capability("goog:loggingPrefs", {"browser": "ALL"})
        driver = webdriver.Chrome(options=chrome_options)
    except Exception as e:
        # 디버거 포트가 안 열려있는 경우 Mock 데이터로 대체
        print(f"Chrome 연결 실패: {e}. Mock 데이터로 대체합니다.")
        driver = None

    try:
        # Chrome이 없으면 Mock 데이터 사용
        if not driver:
            from crawler import get_mock_emails
            mock_data = get_mock_emails()
            raw_titles = [email["subject"] for email in mock_data]
        else:
            # 사용자가 입력한 특정 메일함 주소가 있다면 해당 주소로 브라우저 이동
            if target_url:
                driver.get(target_url)
                time.sleep(3) # 페이지 로딩 대기

            # 2. 메일 제목 요소 긁어오기 (다양한 네이버 메일 버전 선택자 대응)
            # 기본 클래스명 'text' 및 최신 네이버 메일 클래스명 'text_area', 'mail_title' 적용
            selectors = ["span.text_area", "a.mail_title", ".text", "div.name + a"]
            mail_elements = []


            for selector in selectors:
                try:
                    elements = driver.find_elements(By.CSS_SELECTOR, selector)
                    if elements:
                        mail_elements = elements
                        break
                except Exception:
                    continue

            if not mail_elements:
                # 기본 By.CLASS_NAMEFallback
                try:
                    mail_elements = driver.find_elements(By.CLASS_NAME, "text")
                except Exception:
                    pass

            raw_titles = []
            for elem in mail_elements:
                try:
                    t = elem.text.strip()
                    if t and len(t) > 2:
                        raw_titles.append(t)
                        if len(raw_titles) >= 5:  # 과도한 API 호출 방지를 위해 상위 5개 제한
                            break
                except Exception:
                    continue

            if not raw_titles:
                return jsonify({
                    "status": "success",
                    "data": [],
                    "message": "현재 크롬 창에서 감지된 메일 제목이 없습니다. 메일 수신함 화면이 맞는지 확인해 주세요."
                })

        # 3. Gemini AI 설정 및 분석 진행
        use_gemini = bool(api_key and api_key != "your_gemini_api_key_here")
        client = None
        if use_gemini:
            try:
                client = genai.Client(api_key=api_key)
            except Exception as e:
                print(f"Gemini 초기화 실패: {e}")
                use_gemini = False

        processed_data = []
        for i, title in enumerate(raw_titles, 1):
            summary = "요약 정보를 추출할 수 없습니다."
            action = "확인 필요"
            priority = "Medium"
            category = "일반"
            
            if use_gemini:
                prompt = f"""
당신은 사내 업무를 돕는 AI 비서입니다. 아래의 이메일 제목을 분석하여 다음 정보를 JSON 형식으로만 응답해 주세요.
응답에 마크다운 태그(```json 등)를 포함하지 말고 순수 JSON 텍스트만 리턴해야 합니다.

출력 JSON 포맷:
{{
  "summary": "메일의 핵심 맥락 1줄 요약 (정중한 경어체)",
  "action": "메일 수신자가 취해야 할 행동 요약 (3~5단어 단답형, 예: 회신 필요, 일정 캘린더 등록, 서버 점검 확인)",
  "priority": "High" | "Medium" | "Low",
  "category": "업무" | "공지" | "결제" | "보안" | "기타"
}}

이메일 제목: "{title}"
"""
                try:
                    response = client.models.generate_content(
                        model="gemini-2.5-flash",
                        contents=prompt
                    )
                    ai_output = response.text.strip()
                    
                    # 정제 작업
                    if ai_output.startswith("```json"):
                        ai_output = ai_output.split("```json")[1]
                    if "```" in ai_output:
                        ai_output = ai_output.split("```")[0]
                    ai_output = ai_output.strip()
                    
                    parsed = json.loads(ai_output)
                    summary = parsed.get("summary", summary)
                    action = parsed.get("action", action)
                    priority = parsed.get("priority", priority)
                    category = parsed.get("category", category)
                except Exception as e:
                    print(f"Gemini 호출 실패 (인덱스 {i}): {e}")
                    summary = f"'{title}' 건 요약 (API 오류)"
                    action = "수동 확인"
            else:
                # API Key가 없는 경우 로컬 규칙 기반 룰로 가공 요약본 제공 (체험용 데모)
                summary, action, priority, category = get_fallback_ai_analysis(title)

            processed_data.append({
                "idx": i,
                "title": title,
                "summary": summary,
                "action": action,
                "priority": priority,
                "category": category
            })

        return jsonify({"status": "success", "data": processed_data, "is_mock_ai": not use_gemini})

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})
    finally:
        if driver:
            try:
                driver.quit()
            except Exception:
                pass

def get_fallback_ai_analysis(title):
    """API 키가 없을 때 제공하는 키워드 매칭 기반 분석 룰"""
    title_lower = title.lower()
    
    if "매출" in title_lower or "실적" in title_lower or "보고" in title_lower:
        return "상반기 실적 보고 및 각 팀별 매출 데이터를 취합 요청 건입니다.", "데이터 취합 후 기한 내 회신", "High", "업무"
    elif "항공권" in title_lower or "결제" in title_lower or "예약" in title_lower:
        return "항공 예약 완료 및 사전 체크인, 여권 유효기간 확인 요청 안내입니다.", "일정 확인 및 티켓 발권", "Medium", "결제"
    elif "점검" in title_lower or "서버" in title_lower or "장애" in title_lower:
        return "사내 시스템 정기 점검 및 서비스 일시 중단에 대한 공지사항입니다.", "공지 시간 확인 및 작업 백업", "High", "보안"
    elif "미팅" in title_lower or "회의" in title_lower or "일정" in title_lower:
        return "외부 협력사와의 신규 미팅 일정 조율 및 참석 여부 확인 요청입니다.", "참석 가능 여부 회신", "Medium", "업무"
    elif "보안" in title_lower or "비밀번호" in title_lower or "권한" in title_lower:
        return "사내 보안 가이드라인 준수 및 임직원 PC 정밀 검사 수행 요청입니다.", "백신 검사 수행 및 결과 제출", "High", "보안"
    else:
        return f"제목 '{title}'에 관한 수신 메일 안내입니다. 상세 내용을 참조하십시오.", "메일 본문 확인 및 피드백", "Medium", "기타"

if __name__ == '__main__':
    app.run(port=5000, debug=True)
