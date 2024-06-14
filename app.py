import chainlit as cl
from chainlit import user_session
from ultralytics import YOLO
from utils.chat_chain import chat_chain
from utils.monument_exractor import extract_monument_name
from utils.main_chain import main_chain
from utils.format import format_monument_info
import json
from utils.product_price_graph import product_price_app
from utils.questions import questions
from utils.planner_chain import planner_chain
import webbrowser
from langdetect import detect
from utils.translator_chain import translator_chain
from utils.text_to_audio import text_to_speech

#TODO:
## implement basic chat app with history
## create 3 chat profiles 
## create names for each profile
## change chainlit.md content
## implement on chat resume if needed
## change the prompt responsible for the json and more keys

model = YOLO('models\monument_detection.pt', verbose=False)

user_data = {key: None for key in questions}
user_keys = list(questions.keys())
current_question = 0

@cl.set_chat_profiles
async def chat_profile():
    # TODO: change names **Change the name in all the code**
    # FIXME: when chan
    return [
        cl.ChatProfile(
            name="Jwalens",
            markdown_description="Scan and get information about monuments in Morocco",
            icon="https://www.arganiatravel.com/blog/wp-content/uploads/2019/04/ceramica-marroqui.jpg",
        ),
        cl.ChatProfile(
            name="JwalScam",
            markdown_description="I will help you avoid scams in Morocco",
            icon="https://www.albomadventures.com/wp-content/uploads/2012/11/Moroccan-Markets-101042.jpg",
        ),
        cl.ChatProfile(
            name="JwalGuide",
            markdown_description="I will help you benefit the most from your vacation",
            icon="https://www.ytravelblog.com/wp-content/uploads/2018/11/planning-a-trip-tips-and-challenges-2.jpg",
        ),
    ]

@cl.on_chat_start
async def on_chat_start():
    message_history = user_session.get("MESSAGE_HISTORY", [])
    chat_profile = user_session.get("chat_profile", "Jwalens")
    await cl.Avatar(
        name="JwalGuide",
        url="https://www.ytravelblog.com/wp-content/uploads/2018/11/planning-a-trip-tips-and-challenges-2.jpg",
    ).send()
    
    await cl.Avatar(
        name="JwalScam",
        url="https://www.albomadventures.com/wp-content/uploads/2012/11/Moroccan-Markets-101042.jpg",
    ).send()
    
    await cl.Avatar(
        name="Jwalens",
        url="https://www.arganiatravel.com/blog/wp-content/uploads/2019/04/ceramica-marroqui.jpg",
    ).send()

    await cl.Message(content=f"Welcome! Merhba 😁 I'm your moroccan guide {chat_profile}", author = chat_profile).send()

    # display previous message history
    if message_history:
        for msg in message_history:
            await cl.Message(content=msg).send()

    if chat_profile == "JwalGuide":
        global current_question
        current_question = 0
        response =ask_next_question()
        current_question += 1
        await cl.Message(content=response).send()
        
        # target_url = "http://localhost:8501"
        # webbrowser.open_new_tab(target_url)

    user_session.set("chat_profile", chat_profile)

@cl.on_message
async def on_message(msg: cl.Message):
    # Retrieve message history
    message_history = user_session.get("MESSAGE_HISTORY", [])
    chat_profile = user_session.get("chat_profile")

    if chat_profile == "Jwalens":
        await handle_culture_message(msg, message_history)

    elif chat_profile == "JwalScam":
        await handle_prices_message(msg, message_history)

    elif chat_profile == "JwalGuide":
        global current_question
        if current_question > 0 and current_question - 1 < len(user_keys):
            user_data[user_keys[current_question - 1]] = msg.content.lower()

        response = ask_next_question()

        if response:
            current_question += 1
        else:
            #FIXME: change the prompt for better results and add streaming
            response = cl.Message(content="")
            await response.send()

            inputs = {"history":message_history,
                                  "age":user_data['age'],
                                  "gender":user_data['gender'],
                                  "disability":user_data['disability'],
                                  "activities_type":user_data['activities_type'],
                                  "destinations":user_data['destinations'],
                                  "duration_of_travel":user_data['duration_of_travel'],
                                  "budget_level":user_data['budget_level'],
                                  }
            async for token in planner_chain.astream(inputs):
                token.replace('`', '')
                await response.stream_token(token) 
            await response.update()
            return
            
        await cl.Message(content=response).send()


    else:
        await cl.Message(
            content="Unknown profile, defaulting to Jwalens profile."
        ).send()
        await handle_culture_message(msg, message_history)

async def handle_culture_message(msg, message_history):

    # if the user didn't provide an image
    if not msg.elements:
        inputs = {"input": msg.content, "history": message_history}

        response = cl.Message(content="")
        await response.send()

        async for token in chat_chain.astream(inputs):
            await response.stream_token(token)
        print(response.content)     
        await response.update()
        # ADDED 
        output_name_txt, output_audio_txt = await text_to_speech(response.content)
    
        output_audio_el_txt = cl.Audio(
            name=output_name_txt,
            auto_play=True,
            mime="audio/mpeg",
            content=output_audio_txt,
        )

        message_history.append("User: " + msg.content)
        message_history.append("Assisstant: " + response.content)
        user_session.set("MESSAGE_HISTORY", message_history)
        # ADDED 
        response.elements = [output_audio_el_txt]
        await response.update()
        return
    
    images = [file for file in msg.elements if "image" in file.mime]
    monument = extract_monument_name(model, images[0].path)

    monument_info = main_chain.invoke({"location": monument})
    formatted_info = format_monument_info(monument_info)

    detected_lang = detect(msg.content)
    if detected_lang != "en":
        print('*'*100)
        print(formatted_info)
        print('*'*100)
        formatted_info = translator_chain.invoke({"text": formatted_info, "language": detected_lang})
    await cl.Message(content=formatted_info, author = "Jwalens").send()
    

    message_history.append("User: " + monument)
    message_history.append("Assistant:" + formatted_info)
    user_session.set("MESSAGE_HISTORY", message_history)
    
    if msg.content.strip(" "):
        resp = cl.Message(content="", author = "Jwalens")
        await resp.send()

        inputs = {"input": msg.content, "history": message_history}
        async for token in chat_chain.astream(inputs):
            await resp.stream_token(token) 
        await resp.update()

        user_text = msg.content
        message_history.append("User: " + user_text)
        message_history.append("Assistant:" + resp.content)
        user_session.set("MESSAGE_HISTORY", message_history)



async def handle_prices_message(msg, message_history):
    user_text = msg.content

    inputs = {"question": user_text, "history": message_history}
    result = product_price_app.invoke(inputs)

    message_history.append("User: " + user_text)
    message_history.append("Assistant: " + result["generation"])
    user_session.set("MESSAGE_HISTORY", message_history)

    await cl.Message(content=result["generation"], author = 'JwalGuide').send()

async def handle_planning_message(msg, message_history):
    pass


def ask_next_question():
    global current_question
    if current_question < len(user_keys):
        return questions[user_keys[current_question]]
    return None