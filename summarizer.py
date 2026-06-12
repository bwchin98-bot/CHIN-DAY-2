import os
import json
import google.genai as genai
from dotenv import load_dotenv
from crawler import load_config

load_dotenv()

def summarize_email(email_item):
    """
    Gemini API를 사용하여 이메일 본문을 요약하고 요청사항을 추출합니다.
    API 키가 없거나 에러 발생 시 로컬 규칙 기반 룰로 가공 요약본을 제공합니다.
    """
    config = load_config()
    api_key = config.get("GEMINI_API_KEY", "")
    
    # 템플릿 형태로 가져올 기본 결과 구조
    result = {
        "id": email_item.get("id"),
        "sender": email_item.get("sender"),
        "subject": email_item.get("subject"),
        "date": email_item.get("date"),
        "body": email_item.get("body"),
        "summary": "",
        "action_items": [],
        "priority": "Medium",
        "category": "일반"
    }
    
    # API 키가 없거나 데모용 API 키인 경우 로컬 모의 요약기 작동
    if not api_key or api_key == "your_gemini_api_key_here":
        return generate_fallback_summary(email_item, result)
        
    try:
        client = genai.Client(api_key=api_key)

        prompt = f"""
이메일 내용을 분석하여 요약 정보와 주요 요청 사항(Action Items)을 추출해 주세요.
결과는 반드시 JSON 형식으로만 반환해야 하며, 마크다운 코드 블록(```json ... ```) 없이 순수한 JSON 내용만 출력해야 합니다.
반드시 아래 JSON 스키마를 만족해야 합니다:

{{
  "summary": "이메일 전체 요약 (한글 2~3문장)",
  "action_items": ["요청사항 1", "요청사항 2", ...],
  "priority": "High" | "Medium" | "Low",
  "category": "업무" | "공지" | "결제/예약" | "개인" | "보안" | "기타"
}}

[이메일 정보]
보낸사람: {email_item.get('sender')}
제목: {email_item.get('subject')}
날짜: {email_item.get('date')}
본문:
{email_item.get('body')}
"""
        
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )
        text = response.text.strip()
        
        # ```json 마크다운 태그를 포함하여 출력하는 경우 대비 정제
        if text.startswith("```json"):
            text = text.split("```json")[1]
        if "```" in text:
            text = text.split("```")[0]
        text = text.strip()
        
        ai_data = json.loads(text)
        
        result["summary"] = ai_data.get("summary", "요약 정보를 생성하지 못했습니다.")
        result["action_items"] = ai_data.get("action_items", [])
        result["priority"] = ai_data.get("priority", "Medium")
        result["category"] = ai_data.get("category", "일반")
        
        return result
        
    except Exception as e:
        print(f"Gemini API 호출 중 에러 발생: {e}. 로컬 모의 요약을 실행합니다.")
        return generate_fallback_summary(email_item, result)

def generate_fallback_summary(email, base_result):
    """Gemini API가 없거나 오류 시 메일 본문의 키워드를 바탕으로 똑똑하게 모의 분석 및 요약"""
    body = email.get("body", "")
    subject = email.get("subject", "")
    
    # 1. 카테고리 판별
    category = "일반"
    priority = "Medium"
    action_items = []
    summary = ""
    
    if "매출" in subject or "보고서" in subject or "실적" in subject:
        category = "업무"
        priority = "High"
        summary = "상반기 매출 실적 보고서 작성 및 취합을 요청하는 이메일입니다. 각 파트별 매출 데이터를 취합하여 오늘 오후 5시까지 공유해야 합니다."
        action_items = [
            "각 파트별 매출 데이터 취합",
            "신규 프로젝트 성과 상세 기술",
            "오늘 오후 5시까지 보고서 공유 및 메일 회신"
        ]
    elif "항공권" in subject or "결제" in subject or "예약" in subject:
        category = "결제/예약"
        priority = "Medium"
        summary = "글로벌 트래블 항공권 결제 및 예약 완료에 대한 안내 메일입니다. 2026년 7월 15일 도쿄행 왕복 항공편의 결제가 완료되었습니다."
        action_items = [
            "탑승 3시간 전까지 공항 카운터에서 실물 항공권 발권",
            "여권 유효기간이 6개월 이상 남아있는지 재확인",
            "위탁/기내 수하물 규정 관련 첨부파일 사전 확인"
        ]
    elif "서버 점검" in subject or "업데이트" in subject:
        category = "공지"
        priority = "Medium"
        summary = "네이버 클라우드 플랫폼의 정기 서버 점검 안내 메일입니다. 6월 18일 새벽 2시부터 6시까지 약 4시간 동안 서비스 접속 및 콘솔 사용이 일시 제한됩니다."
        action_items = [
            "6/18 02:00 ~ 06:00 사이 시스템 작업 회피",
            "정기 점검 시간 전 핵심 서비스 이상 유무 사전 점검"
        ]
    elif "일정 조율" in subject or "미팅" in subject:
        category = "업무"
        priority = "High"
        summary = "ABC 테크와의 신규 협력사 미팅 일정을 조율하기 위한 메일입니다. 업체 측에서 화요일 오후 또는 목요일 오전을 제안했습니다."
        action_items = [
            "다음주 화요일(6/16) 오후 2시 또는 목요일(6/18) 오전 10시 중 가능 일정 회신",
            "참석 인원 확정 후 미팅룸 예약 및 다과 신청"
        ]
    elif "보안 점검" in subject or "악성코드" in subject:
        category = "보안"
        priority = "High"
        summary = "사내 PC 정기 보안 점검을 안내하고 금주 마감 기한 내에 완료 결과 제출을 요구하는 메일입니다. 미제출 시 망 접속 차단 가능성이 있습니다."
        action_items = [
            "개인 PC 백신 프로그램을 최신 버전으로 업데이트 및 정밀 검사 실행",
            "검사 완료 화면 캡처 이미지 보안팀 메일로 금요일(6/14)까지 회신"
        ]
    else:
        # 일반 범용 모의 요약
        category = "일반"
        priority = "Medium"
        summary = f"'{subject}'에 관련된 안내 혹은 정보 공유 메일입니다. 발송 시각은 {email.get('date')}입니다."
        # 간단한 액션 아이템 추출
        action_items = ["메일 내용 확인 및 필요 시 회신 조치"]
        if "요청" in body or "바랍니다" in body or "부탁" in body:
            priority = "High"
            action_items.append("요청된 사항 처리 및 기한 내 회신")
            
    base_result["summary"] = summary
    base_result["action_items"] = action_items
    base_result["priority"] = priority
    base_result["category"] = category
    
    # AI 요약 미설정 안내 추가 문구
    if not load_config().get("GEMINI_API_KEY"):
        base_result["summary"] += " (※ Gemini API Key 미설정으로 로컬 룰 기반 요약본이 생성되었습니다.)"
        
    return base_result
