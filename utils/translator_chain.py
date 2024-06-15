from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from .llm import llm

chat_prompt_template = PromptTemplate(
    template="""<|begin_of_text|><|start_header_id|>system<|end_header_id|>

          You are a usefull a good translator, tasked with translating into different languages with excellent accuracy make sure to translate the given text don't add extra lines with no preamble or explanation. if you find urls just keep it as it is don't translate urls or emails
          

          <|eot_id|><|start_header_id|>user<|end_header_id|>
          hey there please translate me the following text to {language}: 
          {text} 
          \n <|eot_id|><|start_header_id|>assistant<|end_header_id|>
          """,
    input_variables=["text", "language"],
)

translator_chain = chat_prompt_template | llm | StrOutputParser()