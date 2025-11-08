# Matsongi — 유미 (YOUME)
<p align="center">
<img width="435" height="313" alt="image" src="https://github.com/user-attachments/assets/ef66b20d-6222-4272-92ca-66590ff12d2d" />
</p>

## 팀 구성

<table>
  <tr>
    <th width="25%" style="text-align:center;">이효림</th>
    <th width="25%" style="text-align:center;">안서희</th>
    <th width="25%" style="text-align:center;">유현서</th>
    <th width="25%" style="text-align:center;">임수연</th>
  </tr>
  <tr>
    <td style="text-align:center;">팀장</td>
    <td style="text-align:center;">팀원</td>
    <td style="text-align:center;">팀원</td>
    <td style="text-align:center;">팀원</td>
  </tr>
  <tr>
    <td style="text-align:center;">벡터 생성 및 시각화, AWS Lambda/Bedrock 연동, SlackBot 연동 </td>
    <td style="text-align:center;">아이디어 제안, 시장 조사, 기획 구체화, pt 자료 제작</td>
    <td style="text-align:center;">FlavorGraph 연동, 벡터 생성, 추천 알고리즘, 데이터 크롤링</td>
    <td style="text-align:center;">Streamlit UI, 설문 로직, 벡터 시각화</td>
  </tr>
</table>




---

## 목차

* 소개
* 주요 기능
* 화면 
* 설치 및 로컬 실행
* 상세 로직: Bedrock, Lambda, FlavorGraph, Slackbot
* 데이터 구조

---

## 소개

이 레포는 설문 기반으로 **사용자 미각 벡터(Taste Vector)** 를 생성하고 이를 활용해 제품 추천을 수행하는 서비스입니다. Streamlit으로 UI를 제공하며, 벡터 생성·업데이트·시각화와 추천 로직의 핵심 유틸 함수들이 포함되어 있습니다.

---

## 주요 기능

* 사용자 미각 벡터 생성을 위한 설문
* 사용자 미각 벡터 생성 (설문 데이터를 벡터로 변환)
* 기존 사용자 벡터 업데이트 (챗봇으로 후기 감성 분석)
* 벡터 유사도 기반 제품 추천
* 벡터 시각화
* Streamlit (설문 UI / 결과 시각화)
* SlackBot 알림 기능

---

## 화면

<img width="500" height="443" alt="image" src="https://github.com/user-attachments/assets/fe940d45-997e-4ef7-954f-99fe9f56744a" />
<img width="500" height="446" alt="image" src="https://github.com/user-attachments/assets/1e18abfa-3674-481e-bd88-fb8cbcaa2265" />
<img width="500" height="523" alt="image" src="https://github.com/user-attachments/assets/bdabd765-bbea-43be-905e-92f155dfe8be" />
<img width="500" height="525" alt="image" src="https://github.com/user-attachments/assets/5fb0e93d-e0a5-464b-96e9-4a6f10850583" />



---

## 설치 및 로컬 실행

사전 준비: Python 3.8+ 권장

1. 저장소 클론

```bash
git clone https://github.com/smct-hackathon-2025/Matsongi.git
cd Matsongi
```

2. 가상환경 생성 및 활성화

```bash
python -m venv .venv
# mac/linux
source .venv/bin/activate
# windows
# .venv\Scripts\activate
```

3. 의존성 설치

```bash
pip install -r requirements.txt
```

4. Streamlit 앱 실행

```bash
streamlit run streamlit/app.py
```

> 로컬에서 실행 시 `.env` 또는 환경변수로 개인정보 설정정

---

## 상세 로직 (Bedrock, Lambda, FlavorGraph, Slackbot)

### AWS Bedrock (챗봇 / 자연어 처리)

* 사용자가 설문 이후 또는 추천 후 제공하는 피드백(예: "조금 심심했어요")을 처리합니다.
* Bedrock 호출을 통해 피드백을 sentiment analyze하고, 분류 결과를 기반으로 `update_user_vector.py`의 함수가 호출되어 **사용자 벡터를 업데이트**합니다.

### AWS Lambda

* 무거운 벡터 연산, 코사인 유사도 계산, 외부 상품 DB 호출 등을 Lambda로 분리하여 **Streamlit UI에서 비동기 호출** 가능하게 구성했습니다.
* Lambda 결과는 사용자 벡터 업데이트 및 추천 결과 반환에 사용됩니다.

### FlavorGraph (맛 벡터 생성 및 관리)

* 제품의 Flavor Vector를 추출하고, 추천 시 **`recommend_products.py`로직에서 사용자 벡터와 비교**하여 TOP-N 제품을 추천합니다.
* 코사인 유사도 기반 계산으로 개인 맞춤 추천을 수행하며, 설문 기반 사용자 벡터가 변경되면 실시간으로 추천 결과가 갱신됩니다.

### Slackbot

* 사용자가 Slack 메시지 내 버튼을 클릭하면 외부 커머스로 이동하며, 클릭 이벤트를 로깅/트래킹합니다.
* Streamlit UI에서의 추천과 Slack 알림을 연계하여 사용자의 선호를 기록합니다.

---

## 데이터 구조

**UserTasteVector (JSON)**

```json
{
  "user_id": "user_1",
  "user_taste_vector": [
    -0.060926192279499684,
    0.021740768218193516,
    -0.0027188794912334593,
    "...300개의 벡터",
    ]
}
```

**ProductFlavorVector (JSON)**

```json
{
    "page": 1,
    "name": "[오뚜기] XX라면",
    "url": "https://www.kurly.com/XXXX",
    "ingredient_raw": "면: 소맥분(밀: 미국산, 호주산), 팜유(말레이시아산), 변성전분, ...원재료명 나열 ",
    "matched_ingredients": [
      "msg",
      "hydrolyzed_vegetable_protein",
      "oil",
      "...원재료명 나열",
    ],
    "product_vector": [
      -0.08285583555698395,
      -0.04597668722271919,
      -0.046292468905448914,
      "...300개의 벡터",
    ]
}
```

---

