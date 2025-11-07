import streamlit as st
import requests
import json
import os

SLACK_WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL", "https://hooks.slack.com/services/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")

def send_slack_message(text):
    payload = {
        "text": text,
        "username": "맛송이 봇 🤖",
        "icon_emoji": ":cherry_blossom:"
    }
    try:
        response = requests.post(SLACK_WEBHOOK_URL, data=json.dumps(payload))
        if response.status_code != 200:
            st.warning(f"⚠️ 슬랙 전송 실패: {response.status_code} - {response.text}")
    except Exception as e:
        st.error(f"🚨 슬랙 전송 중 오류 발생: {e}")
