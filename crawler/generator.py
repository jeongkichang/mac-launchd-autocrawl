import os
import google.generativeai as genai

def get_refined_swim_info(removed_html_tag_from_content):
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY is not set in the .env file")

    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-1.5-flash")

    text = f"""
    <content></content> 내용을 참고해서 자유 수영에 대한 정보를 정리해줘.
    1회 이용에 대한 정보만 정리해줘.
    보통, 1회 이용료는 20,000원이 넘지 않아. 그것들은 제외해줘.
    같은 시간대에 요금이 상이하면, 상이한대로 시간과 함께 구별해서 모두 표기해줘.
    아래와 같은 형식으로 만들어줘.

    ex.
    월 : 10:00-10:50 / 성인 54,500 / 중고생 40,500
    월 : 11:00-12:50 / 성인 54,500 / 중고생 40,500
    ...
    화 : 11:00-12:50 / 성인 54,500 / 중고생 40,500
    ...

    <content>
    {removed_html_tag_from_content}
    </content>
    """

    response = model.generate_content(text)
    return response.text
