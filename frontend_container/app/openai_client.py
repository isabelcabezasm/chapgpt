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
global language

# Initialize the language to English
language = "english"

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
                The intentions can be 'check if I have a given bottle crown cap in my collection' or 
                'ask for a bottle crown cap information',
                'change the language to Spanish' or 
                'something else'. 
                If the user says 'yes' is because the user wants to check if the bottle crown cap is in the collection."""
            },
            {
                "role": "user",
                "content": f"Determine the intent of the following query: {query}"
            }
        ]
    intention =  generate_answer(prompt)

    if "check if I have a given bottle crown cap in my collection" in intention:
        return "check"
    elif "ask for a bottle crown cap" in intention:
        return "information"
    elif "Spanish" in intention:
        return "spanish"
    else:
        return "unknown"


def give_similar_caps() -> str:   
    if language == "spanish":
        return "Encontré algunas chapas similares en la colección. Si tu chapa es alguna de ellas, ¿me puedes decir el número? si no, por favor, escribe 'no'"
    return "I found some similar bottle crown caps in the collection. If your cap is any of them, can you tell me the number? if not, please, write 'no'"


def ask_for_image() -> str:
    if language == "spanish":
        return "Por favor, sube la imagen de la chapa de botella que quieres comprobar desde el menú lateral."
    return "Please upload the image of the bottle crown cap you want to check."


def cap_found_message() -> str:
    if language == "spanish":
        return "¡Encontré una chapa en la imagen! ¿Está bien seleccionada? Puedes mejorar el recorte en el botón 'Crop the image'."
    return "I found the cap in the image! Is it correctly selected? You can improve the crop in the 'Crop the image' button."


def not_cap_found_message() -> str:
    if language == "spanish":
        return "Lo siento, no pude encontrar ninguna chapa en la imagen. ¿Puedes seleccionarla con el botón 'Crop the image'?"
    return "I'm sorry, I could not find any cap in the picture. Can you select it?" 


def ask_for_information() -> str:
    if language == "spanish":
        return "Por favor, proporciona la información que deseas saber sobre la chapa de botella."
    return "Please provide the information you want to know about the bottle crown cap."

def get_digit_from_message(message: str) -> int:
    return int(''.join(filter(str.isdigit, message)))

def get_cap_from_similar_caps_message(cap_number:int) -> Cap:
    for message in reversed(chat_history):
        if message.role == "assistant" and isinstance(message, FoundSimilarCapsMessage):
            return message.caps[cap_number-1]
    return None

def confirm_cap_found(cap_number:int) -> str:
    cap = get_cap_from_similar_caps_message(cap_number)

    if language == "spanish":
        answer = "¡Genial! Tengo la chapa!"
        if cap:
            answer = answer + f" La marca es {cap.brand} y el pais es {cap.country}"	
    answer =  "Cool! We found the cap!!"
    if cap:
        answer = answer + f" The brand is {cap.brand} and the country is {cap.country}"
    
    return answer

def no_similar_caps_found() -> str:
    if language == "spanish":
        return "Loooo siento!! No encontré ninguna chapa similar en la colección."
    return "I'm sorry, I could not find any similar cap in the collection."


def no_understand_message() -> str:
    if language == "spanish":
        return "Lo siento, no entendí tu mensaje. ¿Puedes intentarlo de nuevo?"
    return "I'm sorry, I did not understand your message. Can you try again?"


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
    # user_message.seek(0)

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
            message = "I'm sorry, I could not find any similar cap in the collection."
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
            answer = Message("assistant", ask_for_image())
            save_history_chat_messages(answer)
            return answer
        elif intention == "information":
            # ask the user for the information
            answer = Message("assistant", ask_for_information())
            save_history_chat_messages(answer)
            return answer
        elif intention == "spanish":
            global language
            language = "spanish"
            answer = Message("assistant", "Claro que sí!!!! Puedo ayudarte a verificar si Isa tiene una chapa en su colección")
            save_history_chat_messages(answer)
            return answer
        else: 
            answer = Message("assistant", no_understand_message())
            save_history_chat_messages(answer)
            return answer
        

if __name__ == "__main__":
    message = "yes"
    print(ask_bot(message))











    

  
