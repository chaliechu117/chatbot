import streamlit as st
import pandas as pd
import google.generativeai as genai

# Streamlit UI 설정
st.title("💬 개인정보 탐지 시스템")
st.write(
    "이 앱은 게시물 내 개인정보를 탐지하고 태그를 생성합니다. "
    "Google Gemini 모델을 사용하여 동작합니다."
)

# Gemini API Key 입력
genai_api_key = st.text_input("Gemini API Key", type="password")
if not genai_api_key:
    st.info("Gemini API 키를 입력해주세요.", icon="🗝️")
else:
    # Gemini 클라이언트 구성
    genai.configure(api_key=genai_api_key)

    # Gemini 모델 설정
    system_instruction_generate = """
        입력된 게시물에서 아래의 개인정보 요소가 포함되어 있는지 확인하세요. 
        입력된 게시물에서 개인정보 요소는 해당 내용에 맞는 [ ] 태그로 표시해 주세요.

        ## 개인정보 요소
        1. 인적사항
            1.1 일반정보: 성명, 주민등록번호, 주소, 연락처, 생년월일, 출생지, 성별 등
            1.2 가족정보: 가족관계 및 가족구성원 정보 등
        2. 신체적 정보
            2.1 신체정보: 얼굴, 홍채, 음성, 유전자 정보, 지문, 키, 몸무게 등
            2.2 의료건강정보: 건강상태, 진료기록, 신체장애, 장애등급, 병력, 혈액형, IQ, 약물테스트 등의 신체검사 정보 등
        3. 사회적정보
            3.1 교육정보: 학력, 성적, 출석현황, 기술 자격증 및 전문 면허증 보유내역, 상벌기록, 생활기록부, 건강기록부 등
            3.2 병역정보: 병역여부, 군번 및 계급, 제대유형, 근무부대, 주특기 등
            3.3 근로정보: 직장, 고용주, 근무처, 근로경력, 상벌기록, 직무평가기록 등
            3.4 법적정보: 전과 범죄 기록, 재판 기록, 과태료 납부내역 등
        4. 재산적 정보
            4.1 소득정보: 봉급액, 보너스 및 수수료, 이자소득, 사업소득 등
            4.2 신용정보: 대출 및 담보설정 내역, 신용카드번호, 통장계좌번호, 신용평가 정보 등
            4.3 부동산정보: 소유주택, 토지, 자동차, 기타 소유차량, 상점 및 건물 등
            4.4 기타수익정보: 보험(건강, 생명 등), 가입현황, 휴가, 병가 등

        ## 답변 예시
        게시물 >> 어제는 인천 남동구복지관 어울림봉사단에서 인사나눔으로 마스크 5매와 사탕을 동대표 정호씨와 주민들에게 나누어 주었습니다. 아들도 함께 나온 정호씨는 고지혈증을  3년전에 진단 받아 약을 받았어요.
        태그 >> 어제는 [주소]인천 남동구[/주소]복지관 어울림봉사단에서 인사나눔으로 마스크 5매와 사탕을 동대표 [이름]정호씨[/이름]와 주민들에게 나누어 주었습니다. [가족관계]아들[/가족관계]도 함께 나온 정호씨는 [의료건강정보]고지혈증을  3년전에 진단[/의료건강정보] 받아 약을 받았어요.
        탐지결과 >> 인적사항 3건, 신체적정보 1건, 사회적정보 0건, 재산적정보 0건
    """
    gemini_model = genai.GenerativeModel("gemini-1.5-flash", system_instruction=system_instruction_generate)
    chat_session = gemini_model.start_chat(history=[])

    # 세션 상태 초기화
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "results" not in st.session_state:
        st.session_state.results = []

    # Gemini 응답 처리 및 검증 함수
    def process_gemini_response(response_text):
        """
        Gemini 응답을 처리하고 개인정보 탐지 결과를 요약합니다.
        """
        lines = response_text.split("\n")
        tags = []
        detection_result = {}
        in_tags_section = False
        
        for line in lines:
            if line.strip().startswith("태그 >>"):
                in_tags_section = True
                continue
            if line.strip().startswith("탐지결과 >>"):
                in_tags_section = False
                continue
            if in_tags_section:
                tags.append(line.strip())
            if line.strip().startswith(("인적사항", "신체적정보", "사회적정보", "재산적정보")):
                key, value = line.split(" ", 1)
                detection_result[key.strip()] = int(value.strip().replace("건", ""))
        
        return {
            "tags": tags,
            "detection_result": detection_result
        }

    # 사용자 입력 처리
    if prompt := st.chat_input("게시물을 입력하세요:"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Gemini 모델 처리
        with st.spinner("Gemini 모델이 게시물을 처리 중입니다..."):
            gemini_response = chat_session.send_message(prompt)
            response_text = gemini_response.text

        processed_result = process_gemini_response(response_text)
        st.session_state.results.append(processed_result)

        # 결과 출력
        with st.chat_message("assistant"):
            st.markdown(response_text)

        st.subheader("Gemini 탐지 결과")
        st.write(f"**태그**: {', '.join(processed_result['tags'])}")
        st.write(f"**탐지결과**: {processed_result['detection_result']}")

    # 결과 저장 및 표시
    if st.session_state.results:
        result_df = pd.DataFrame(st.session_state.results)
        st.subheader("전체 탐지 결과")
        st.dataframe(result_df)

        with st.chat_message("assistant"):
            response = st.write_stream(stream)
        st.session_state.messages.append({"role": "assistant", "content": response})
