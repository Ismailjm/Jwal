from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from .llm import llm

chat_prompt_template = PromptTemplate(
    template="""<|begin_of_text|><|start_header_id|>system<|end_header_id|>

          You are a usefull travel assistant, tasked with providing useful planning guide to the user
          
          This is the your conversation history
          {history}

          <|eot_id|><|start_header_id|>user<|end_header_id|>
          Hey there! I need your help planning an awesome trip. After i provide you with my choices write me a detailed plan or guide so i can benfit the most of my vacation while respecting my provided prefrenHere’s what you need to know about me:
            Age: {age}
            Gender: {gender}
            Do I have any disabilities? (if yes, please specify): {disability}
            What kind of activities am I into? (e.g., adventure, relaxation, cultural, etc.): {activities_type}
            Where do I want to go? (list specific places or regions): {destinations}
            How long will I be traveling? (number of days): {duration_of_travel}
            What’s my budget like? : {budget_level}
          \n <|eot_id|><|start_header_id|>assistant<|end_header_id|>
          """,
    input_variables=["age", "gender","disability","activities_type","destinations","duration_of_travel", "budget_level", "history"],
)

planner_chain = chat_prompt_template | llm | StrOutputParser()