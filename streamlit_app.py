import streamlit as st
import google.generativeai as genai
import re

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
    system_instruction_first = \
        """
            ## 개인정보 탐지 수행 방법
            1. 입력된 게시물 내용이 개인정보 요소에 포함되어 있는지 확인하세요. 
            2. 답변 시 입력된 게시물에서 개인정보 요소는 해당 내용에 맞는 [ ] 태그로 표시해주세요.
            3. 탐지 예시와 동일하게 답변을 해주세요. 답변에는 입력, 태그, 결과가 모두 포함되어야 합니다.
            
            ## 개인정보 요소
            1. 인적사항
                1.1 일반정보: 성명, 주민등록번호, 주소, 연락처, 생년월일, 출생지, 성별 등
                1.2 가족정보: 가족관계 및 가족구성원 정보 등
            2. 신체적 정보
                2.1 신체정보: 얼굴, 홍채, 음성, 유전자 정보, 지문, 키, 몸무게, 사진이나 동영상에 나온 모습  등
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
            5. 정신적 정보
                5.1 기호.성향 정보: 도서.비디오 등 대여기록, 잡지구독정보, 물품구매내역, 웹사이트검색내역 등
                5.2 내면의 비밀 정보: 사상, 신조, 종교, 가치관, 정당.노조 가입여부 및 활동내역, 인터넷 댓글.게시글, 출판물 등
            6. 기타 정보
                6.1 통신정보: E-mail 주소, 전화통화내역, 로그파일, 쿠키, SNS 주소 등
                6.2 위치정보: GPS 및 휴대폰에 의한 개인의 위치정보 등
                6.3 습관및취미정보: 흡연여부, 음주량, 선호하는 스포츠 및 오락, 여가활동, 도박성성향 등
                
            ## 탐지 예시
            입력 >> 어제는 인천 남동구복지관 어울림봉사단에서 인사나눔으로 마스크 5매와 사탕을 동대표 정호씨와 주민들에게 나누어 주었습니다. 아들도 함께 나온 정호씨는 고지혈증을  3년전에 진단 받아 약을 받았어요.
            태그 >> 어제는 [주소]인천 남동구[/주소]복지관 어울림봉사단에서 인사나눔으로 마스크 5매와 사탕을 동대표 [이름]정호씨[/이름]와 주민들에게 나누어 주었습니다. [가족관계]아들[/가족관계]도 함께 나온 정호씨는 [의료건강정보]고지혈증을  3년전에 진단[/의료건강정보] 받아 약을 받았어요.
            결과 >> 인적사항 3건, 신체적정보 1건, 사회적정보 0건, 재산적정보 0건, 정신적 정보 0건, 기타 정보 0건
        """
    system_instruction_second = \
        """
            ## 개인정보 탐지 수행 방법
            1. 입력된 게시물 내용이 개인정보 요소에 포함되어 있는지 확인하세요. 
            2. 답변 시 입력된 게시물에서 개인정보 요소는 해당 내용에 맞는 [ ] 태그로 표시해 주세요.
            3. 탐지 예시의 스타일과 동일하게 답변을 해주세요. 답변에는 입력, 태그, 결과가 모두 포함되어야 합니다.
            4. 입력된 답변을 분석한 뒤 마지막에 최종 답변을 출력하시오.
            5. 결과는 인적사항, 신체적정보, 사회적정보, 재산적정보, 정신적 정보, 기타 정보에 대해서만 집계하세요.
            
            ## 개인정보 요소
            1. 인적사항
                1.1 일반정보: 성명, 주민등록번호, 주소, 연락처, 생년월일, 출생지, 성별 등
                1.2 가족정보: 가족관계 및 가족구성원 정보 등
            2. 신체적 정보
                2.1 신체정보: 얼굴, 홍채, 음성, 유전자 정보, 지문, 키, 몸무게, 사진이나 동영상에 나온 모습  등
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
            5. 정신적 정보
                5.1 기호.성향 정보: 도서.비디오 등 대여기록, 잡지구독정보, 물품구매내역, 웹사이트검색내역 등
                5.2 내면의 비밀 정보: 사상, 신조, 종교, 가치관, 정당.노조 가입여부 및 활동내역, 인터넷 댓글.게시글, 출판물 등
            6. 기타 정보
                6.1 통신정보: E-mail 주소, 전화통화내역, 로그파일, 쿠키, SNS 주소 등
                6.2 위치정보: GPS 및 휴대폰에 의한 개인의 위치정보 등
                6.3 습관및취미정보: 흡연여부, 음주량, 선호하는 스포츠 및 오락, 여가활동, 도박성성향 등

            ## 최종 답변
            입력 >> 어제는 인천 남동구복지관 어울림봉사단에서 인사나눔으로 마스크 5매와 사탕을 동대표 정호씨와 주민들에게 나누어 주었습니다. 아들도 함께 나온 정호씨는 고지혈증을  3년전에 진단 받아 약을 받았어요.
            태그 >> 어제는 [주소]인천 남동구[/주소]복지관 어울림봉사단에서 인사나눔으로 마스크 5매와 사탕을 동대표 [이름]정호씨[/이름]와 주민들에게 나누어 주었습니다. [가족관계]아들[/가족관계]도 함께 나온 정호씨는 [의료건강정보]고지혈증을  3년전에 진단[/의료건강정보] 받아 약을 받았어요.
            결과 >> 인적사항 3건, 신체적정보 1건, 사회적정보 0건, 재산적정보 0건, 정신적 정보 0건, 기타 정보 0건

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
            output_first = response_first.text.split('\n')

            # Second Stage
            input_second = f"""
                ## 답변
                입력 >> {output_first[0]}
                태그 >> {output_first[1]}
                결과 >> {output_first[2]}

                ## 최종 답변
                입력 >> {output_first[0]}
                태그 >>
                결과 >> 
            """
            response_second = chat_session_second.send_message(input_second)

            # 결과 출력
            st.subheader("2단계 최종 결과")
            result_lines = response_second.text.strip().split('\n')
            formatted_result = {
                "입력": "",
                "태그": "",
                "결과": ""
            }

            # 2단계 결과 파싱
            for line in result_lines:
                if line.startswith("입력 >>"):
                    formatted_result["입력"] = line.replace("입력 >>", "").strip()
                elif line.startswith("태그 >>"):
                    formatted_result["태그"] = line.replace("태그 >>", "").strip()
                elif line.startswith("결과 >>"):
                    formatted_result["결과"] = line.replace("결과 >>", "").strip()

            st.write("**입력된 텍스트**")
            st.text_area("입력", value=formatted_result["입력"], height=150, disabled=True)

            st.write("**탐지된 태그**")
            st.text_area("태그", value=formatted_result["태그"], height=150, disabled=True)

            st.write("**집계 결과**")
            st.markdown(f"""
            - **인적사항**: {formatted_result['결과'].split(', ')[0].split()[-1]}
            - **신체적 정보**: {formatted_result['결과'].split(', ')[1].split()[-1]}
            - **사회적 정보**: {formatted_result['결과'].split(', ')[2].split()[-1]}
            - **재산적 정보**: {formatted_result['결과'].split(', ')[3].split()[-1]}
            - **정신적 정보**: {formatted_result['결과'].split(', ')[4].split()[-1]}
            - **기타 정보**: {formatted_result['결과'].split(', ')[5].split()[-1]}
            """)

            # 1단계 결과를 숨겨진 섹션으로 표시
            # with st.expander("1단계 결과 보기"):
            #     st.text_area("1단계 처리 결과", value=response_first.text, height=200, disabled=True)

