from common import Message, FoundCapMessage, FoundSimilarCapsMessage
from cap import Cap

import PIL
from dotenv import load_dotenv
import os
import httpx
from openai import AzureOpenAI
from azure.identity import DefaultAzureCredential, get_bearer_token_provider 
from user_image import search_similar_caps_cropped_cap, search_the_cap_in_the_image
from streamlit.runtime.uploaded_file_manager import UploadedFile
import cv2
import numpy as np
from PIL import Image


load_dotenv(dotenv_path='frontend_container/.env') 
        
endpoint = os.getenv("AZURE_OPENAI_ENDPOINT", "https://chapgpt.openai.azure.com/")  
deployment = os.getenv("DEPLOYMENT_NAME", "gpt-4o-mini")  

chat_history: list[Message] = []

# Initialize Azure OpenAI Service client with Entra ID authentication
token_provider = get_bearer_token_provider(  
    DefaultAzureCredential(),  
    "https://cognitiveservices.azure.com/.default"  
)  


def connect_openai():
    http_client = httpx.Client(verify=False)
    openai_client = AzureOpenAI(  
        azure_endpoint=endpoint,  
        azure_ad_token_provider=token_provider,  
        api_version="2024-08-01-preview",  
        http_client=http_client,
    )      
    return openai_client


def generate_answer(prompt: str) -> str:
    openai_client = connect_openai() 
    response = openai_client.chat.completions.create(
        model=deployment,
        messages=prompt,
        max_tokens=800,  
        temperature=0.7,  
        top_p=0.95,  
        frequency_penalty=0,  
        presence_penalty=0,
        stop=None,  
        stream=False  
    )
    return response.choices[0].message.content


def give_me_intention(query: str) -> str:
    prompt = [
            {
                "role": "system",
                "content": """You are an AI assistant that helps to determine the intent of user queries. 
                The intentions can be 
                'check if I have a cap in my collection' if he/she ask about a cap in the collection or something like check the cap, 
                'ask for a bottle crown cap information' if he/she ask about information of a cap,
                'something else'. 
                If the user says 'yes' is because the user wants to check if the bottle crown cap is in the collection."""
            },
            {
                "role": "user",
                "content": f"Determine the intent of the following query: {query}"
            }
        ]
    intention =  generate_answer(prompt)

    if "check if I have a cap in my collection" in intention:
        return "check"
    elif "ask for a bottle crown cap" in intention:
        return "information"
    elif "Spanish" in intention:
        return "spanish"
    else:
        return "unknown"


def give_similar_caps() -> str:  
    message = get_last_user_message()
    prompt = [
            {
                "role": "system",
                "content": """You are an AI assistant that helps to check if a collection has a cap that the user gives. 
                You have found some caps similar to the one the user gave. 
                You need to ask the user to tell you the number of the cap if he/she finds it, or to say 'no' if he/she does not find it."""
            },
            {
                "role": "user",
                "content": f"Please, ask the user to tell you the image of the cap in the same language. Message: {message}."
            }
        ]
    return generate_answer(prompt)


def ask_for_image(user_message:str) -> str:
    prompt = [
            {
                "role": "system",
                "content": """You are an AI assistant tasked with verifying if a collection includes a specific bottle cap provided by the user. 
                Please prompt the user to upload an image of the cap using the 'Browse files' button located in the sidebar menu.  
                The cap in Spanish is 'chapa'.              
                """
            },
            {
                "role": "user",
                "content": f"{user_message}"
            }
        ]
    return generate_answer(prompt)


def cap_found_message() -> str:
    prompt = [
            {
                "role": "system",
                "content": """You are an AI assistant that helps to check if a collection has a cap that the user gives. 
                You have found one cap in an image that the user gave to you, but you're not sure if the selection is correct. 
                You need to ask the user if the thing selected is the correct cap that he/she wants to check, 
                and if not, you need to ask him/her to crop the image with the button 'Crop the image'.
                Only if the message is written in Spanish, note that in Spanish, translate "cap" to "chapa". 
                Don't translate the answer if the user message is not in Spanish.  
                """
            },
            {
                "role": "user",
                "content": get_last_user_message() if get_last_user_message() else "Can you check if Isa has this cap in the collection?"
            }
        ]
    return generate_answer(prompt)


def not_cap_found_message() -> str:
    prompt = [
            {
                "role": "system",
                "content": """You are an AI assistant that helps to check if a collection has a cap that the user gives. 
                You haven't found any cap in the image that the user gave to you. 
                you need to ask him/her to crop the image with the button 'Crop the image'.
                The cap in Spanish is 'chapa'.
                """
            },
            {
                "role": "user",
                "content": get_last_user_message()
            }
        ]
    return generate_answer(prompt)


def ask_for_information(user_message: str) -> str:
    prompt = [
            {
                "role": "system",
                "content": """You are an AI assistant that helps to check if a collection has a cap that the user gives. 
                The user asked information about a cap, but we don't have that functionality implemented yet.
                The cap in Spanish is 'chapa'.
                """
            },
            {
                "role": "user",
                "content":user_message
            }
        ]
    return generate_answer(prompt)


def get_digit_from_message(message: str) -> int:
    return int(''.join(filter(str.isdigit, message)))


def get_last_user_message() -> str:
    for message in reversed(chat_history):
        # search a real message from the user, not one generated
        if (message.role == "user" and 
           "UploadedFile" not in str(message.text) and 
           "PIL.Image" not in str(message.text)):
            return message.text

    return None


def get_cap_from_similar_caps_message(cap_number:int) -> Cap:
    for message in reversed(chat_history):
        if message.role == "assistant" and isinstance(message, FoundSimilarCapsMessage):
            return message.caps[cap_number-1]
    return None


def confirm_cap_found(cap_number:int) -> str:
    cap = get_cap_from_similar_caps_message(cap_number)

    answer =  "Cool! We found the cap!!"
    if cap:
        answer = answer + f" The brand is {cap.brand} and the country is {cap.country}"
    
    if cap.brand == "LA ALHAMBRA":
        return "lavincompaeviejo! Es una Alhambra de Graná!"
    if cap.brand == "VICTORIA":
        return "Ehh! que estoy aliquindoi!! Qué chapa más perita! Canio.. es una Victoria de Málaga!"

    return translate(answer)


def no_similar_caps_found() -> str:
    prompt = [
            {
                "role": "system",
                "content": """You are an AI assistant that helps to check if a collection has a cap that the user gives. 
                The user gave you one image with a cap, but you haven't found any similar cap in the collection.    
                Probably is because the cap is not in the collection.
                The cap in Spanish is 'chapa'.
                """
            },
            {
                "role": "user",
                "content": get_last_user_message()
            }
        ]
    return generate_answer(prompt)


def no_understand_message(user_message:str) -> str:
    prompt = [
            {
                "role": "system",
                "content": """You are an AI assistant that helps to check if a collection has a cap that the user gives. 
                The user said something that you didn't understand, please, tell the user that you only can check if one bottle cap
                is available in a collection but not the thing that he/she asked.
                Only if the message is written in Spanish, note that in Spanish, translate "cap" to "chapa". 
                Don't translate the answer if the user message is not in Spanish.            
                """
            },
            {
                "role": "user",
                "content":user_message
            }
        ]
    return generate_answer(prompt)


def cap_to_list(similar_caps: list) -> list[Cap]:
    return [Cap(
        id=cap["id"],
        brand_id=cap["brand_id"],
        brand=cap["brand"],
        brand_num=cap["brand_num"],
        type=cap["type"],
        brewery=cap["brewery"],
        region=cap["region"],
        country=cap["country"],
        path=None,
        embeddings=[],
        base64=cap["base64"],
    ) for cap in similar_caps]


def save_history_chat_messages(message: Message) -> None:
    chat_history.append(message)


def draw_square(image: UploadedFile, borders: list[int]) -> np.ndarray:
    # Convert user_message (image) to a format suitable for OpenCV
    image = np.array(Image.open(image))    
    if borders:    
        top_left = (borders[0], borders[1])
        bottom_right = (borders[2], borders[3])    
        # Draw a square around the detected borders
        image = cv2.rectangle(image, top_left, bottom_right, (0, 255, 0), 5)
    return image


def ask_bot(user_message: str) -> Message:   
    # first save the user message:
    save_history_chat_messages(Message("user", user_message))

    # if the user message is not a string, it's an cap image
    if isinstance(user_message, PIL.Image.Image):
        #  it's a cropped cap   
        similar_caps = search_similar_caps_cropped_cap(user_message)
        if similar_caps:
            message =  give_similar_caps()
            cap_list = cap_to_list(similar_caps)
            save_history_chat_messages(answer := FoundSimilarCapsMessage("assistant", message, cap_list))
            return answer
        else:
            message = translate("I'm sorry, I could not find any similar cap in the collection.")
            save_history_chat_messages(answer := Message("assistant", message))
            return answer
    elif isinstance(user_message, UploadedFile):
        # it's an uploaded image -> look for the cap.
        borders = search_the_cap_in_the_image(user_message)
        image = draw_square(user_message, borders)
        if borders:
            text_message = cap_found_message()
            save_history_chat_messages(answer := FoundCapMessage("assistant", text_message, image, borders))
            return answer
        else:
            text_message = not_cap_found_message()           
            save_history_chat_messages(answer := FoundCapMessage("assistant", text_message, image, []))
            return answer
        
    # it's a message (text)
    else:    
        # the user message is an string.  
        # first check if there is a number. If there are, it's the cap number
        if any(char.isdigit() for char in user_message): # it's the correct cap.
            # get the digit from the message
            number = get_digit_from_message(user_message)
            answer = Message("assistant", confirm_cap_found(number))
            save_history_chat_messages(answer)
            return answer

        if user_message == "no":            
            answer = Message("assistant", no_similar_caps_found())
            save_history_chat_messages(answer)
            return answer

        intention = give_me_intention(user_message)  
        if intention == "check":
            # ask the user for the image
            answer = Message("assistant", ask_for_image(user_message))
            save_history_chat_messages(answer)
            return answer
        elif intention == "information":
            # ask the user for the information
            answer = Message("assistant", ask_for_information(user_message))
            save_history_chat_messages(answer)
            return answer
        else: 
            answer = Message("assistant", no_understand_message(user_message))
            save_history_chat_messages(answer)
            return answer

def get_language(message: str) -> str:
    prompt = [
            {
                "role": "system",
                "content": """You are an AI assistant that helps to detect the language of a message. 
                """
            },
            {
                "role": "user",
                "content": f"Please, tell me the language of the following message: {message}."
            }
        ]
    return generate_answer(prompt)

def translate(text:str) -> str:
    last_user_message = get_last_user_message()
    if not last_user_message:
        return text
    language = get_language(last_user_message)
    prompt = [
            {
                "role": "system",
                "content": f"""You are an AI assistant that helps to translate. 
                Just give me the translation in {language}, even if it's the same language. Don't add more text to the answer.
                Don't give me the language of the text, just the translation.
                The cap in Spanish is 'chapa'.
                """
            },
            {
                "role": "user",
                "content": f"Please, translate,translate the following message: {text} into {language}. But don't tell me the language nor the first message."
            }
        ]
    return generate_answer(prompt)


if __name__ == "__main__":
    message = "yes"
    print(ask_bot(message))











    

  
