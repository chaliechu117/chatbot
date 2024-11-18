import streamlit as st
import google.generativeai as genai

# Streamlit UI 초기화
st.title("💬 개인정보 탐지 Chatbot")
st.write(
    "Gemini 모델을 사용하여 텍스트 내 개인정보를 탐지하는 챗봇입니다. "
    "Gemini API 키를 입력한 후 텍스트를 입력하세요."
)

# 사용자로부터 Gemini API 키 입력 받기
gemini_api_key = st.text_input("Gemini API Key", type="password")
if not gemini_api_key:
    st.info("Gemini API 키를 입력해주세요.", icon="🔑")
else:
    genai.configure(api_key=gemini_api_key)

    # Gemini 모델 설정
    system_instruction_first = """
        ## 개인정보 탐지 수행 방법
        ...
    """
    system_instruction_second = """
        ## 개인정보 탐지 수행 방법
        ...
    """

    model_first = genai.GenerativeModel("gemini-1.5-flash", system_instruction=system_instruction_first)
    model_second = genai.GenerativeModel("gemini-1.5-flash", system_instruction=system_instruction_second)
    chat_session_first = model_first.start_chat(history=[])
    chat_session_second = model_second.start_chat(history=[])

    # 사용자 입력 받기
    user_input = st.text_area("텍스트 입력", placeholder="분석할 텍스트를 입력하세요...")
    if user_input:
        if st.button("분석 시작"):
            # First Stage
            input_first = f"""
                ## 탐지
                입력 >> {user_input}
                태그 >>
                결과 >>
            """
            response_first = chat_session_first.send_message(input_first)
            output_first = response_first.text.strip().split('\n')

            # Second Stage
            input_second = f"""
                ## 답변
                입력 >> {output_first[0]}
                태그 >> {output_first[1]}
                결과 >> {output_first[2]}

                ## 차근차근 분석해보자
                작성방법에 맞추어 작성했는지 분석하시오.
                분석한 결과를 참고하여 각 태그가 올바르게 분류되었는지 확인해보시오.
                분석한 결과를 참고하여 결과에서 집계한 건수가 정확한지 확인해보시오.
                개인정보 탐지 수행 방법에 알맞게 답변을 수정하시오.

                ## 최종 답변
                입력 >> {output_first[0]}
                태그 >> 
                결과 >> 인적사항 _건, 신체적정보 _건, 사회적정보 _건, 재산적정보 _건, 정신적 정보 _건, 기타 정보 _건
            """
            response_second = chat_session_second.send_message(input_second)

            # 결과 출력
            st.subheader("2단계 최종 결과")

            # 결과 데이터 파싱
            result_lines = response_second.text.strip().split('\n')
            formatted_result = {
                "입력": "",
                "태그": "",
                "결과": ""
            }

            for line in result_lines:
                if line.startswith("입력 >>"):
                    formatted_result["입력"] = line.replace("입력 >>", "").strip()
                elif line.startswith("태그 >>"):
                    formatted_result["태그"] = line.replace("태그 >>", "").strip()
                elif line.startswith("결과 >>"):
                    formatted_result["결과"] = line.replace("결과 >>", "").strip()

            # 결과 표시
            st.write("**입력된 텍스트**")
            st.text_area("입력", value=formatted_result["입력"], height=150, disabled=True)

            st.write("**탐지된 태그**")
            st.text_area("태그", value=formatted_result["태그"], height=150, disabled=True)

            # 집계 결과를 표 형식으로 정리
            st.write("**집계 결과**")
            summary_data = {
                "구분": ["인적사항", "신체적 정보", "사회적 정보", "재산적 정보", "정신적 정보", "기타 정보"],
                "건수": [
                    formatted_result["결과"].split(', ')[0].split()[-1],
                    formatted_result["결과"].split(', ')[1].split()[-1],
                    formatted_result["결과"].split(', ')[2].split()[-1],
                    formatted_result["결과"].split(', ')[3].split()[-1],
                    formatted_result["결과"].split(', ')[4].split()[-1],
                    formatted_result["결과"].split(', ')[5].split()[-1],
                ]
            }
            st.table(summary_data)

            # 상세 분석 결과를 숨길 수 있는 섹션으로 표시
            with st.expander("상세 분석 결과 보기"):
                st.text_area("상세 분석 결과", value=response_second.text, height=200, disabled=True)



