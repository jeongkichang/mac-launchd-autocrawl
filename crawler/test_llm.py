from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain.llms import HuggingFacePipeline
from transformers import GPT2LMHeadModel, GPT2Tokenizer
from transformers import pipeline

def initialize_huggingface_gpt2():
    model_name = "gpt2"
    model = GPT2LMHeadModel.from_pretrained(model_name)
    tokenizer = GPT2Tokenizer.from_pretrained(model_name)
    
    hf_pipeline = pipeline(
        "text-generation", 
        model=model, 
        tokenizer=tokenizer,
        max_length=1024,
        max_new_tokens=200,
        pad_token_id=tokenizer.eos_token_id
    )
    return hf_pipeline

def initialize_langchain_llm(hf_pipeline):
    return HuggingFacePipeline(pipeline=hf_pipeline)

def extract_swimming_info(html_content):
    prompt_template = PromptTemplate(
        input_variables=["html"],
        template="""
        아래 HTML 콘텐츠에서 "자유 수영" 관련 정보를 표 형식으로 추출해 주세요. 
        표에는 구분, 강좌명, 요일, 시간, 정원, 대상 및 회비 컬럼이 포함되어야 합니다.
        
        HTML 콘텐츠:
        {html}
        
        표로 정리된 결과:
        """
    )
    
    hf_pipeline = initialize_huggingface_gpt2()
    llm = initialize_langchain_llm(hf_pipeline)
    chain = LLMChain(llm=llm, prompt=prompt_template)
    
    result = chain.run(html=html_content)
    return result

if __name__ == "__main__":
    html_content = """
    <html>
    <!-- 여기에 사용자가 제공한 HTML 전문을 넣으세요 -->
    </html>
    """
    
    swimming_info = extract_swimming_info(html_content)
    print("추출된 자유 수영 정보:\n", swimming_info)
