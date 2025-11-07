import json
import requests

# ⚠️ 자신의 Slack Incoming Webhook URL로 교체
SLACK_WEBHOOK_URL = "https://hooks.slack.com/services/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"

def send_slack_message(text):
    """Slack으로 메시지 보내기"""
    payload = {
        "text": text,
        "username": "맛송이 봇 🤖",
        "icon_emoji": ":cherry_blossom:"
    }
    try:
        response = requests.post(SLACK_WEBHOOK_URL, data=json.dumps(payload))
        if response.status_code == 200:
            print("✅ Slack 메시지 전송 성공!")
        else:
            print(f"⚠️ Slack 전송 실패: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"🚨 Slack 전송 중 오류 발생: {e}")

if __name__ == "__main__":
    # 테스트 메시지
    send_slack_message("테스트 메시지입니다! 🎉")
