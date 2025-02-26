import base64
import streamlit as st
from openai_client import ask_bot
from PIL import Image

from streamlit_cropper import st_cropper
import yaml
from yaml.loader import SafeLoader
import streamlit_authenticator as stauth

from common import Message, FoundCapMessage, FoundSimilarCapsMessage, ImageMessage
from cap import Cap

from dotenv import load_dotenv
load_dotenv()


def crop_image_with_coords(img):
    found_coords = (st.session_state.coords[0], st.session_state.coords[2], st.session_state.coords[1], st.session_state.coords[3])
    cropped_img = st_cropper(img, default_coords=found_coords, realtime_update=True, box_color='#0000FF', aspect_ratio=(1,1))
    return cropped_img

def store_cropped_image(cropped_img):
    st.session_state.cropped_image = {"image": cropped_img}
    st.session_state.messages.append(ImageMessage(role="user", text_content="Yes, that is the cap", image=cropped_img))

def the_cap_is_found():
    img = Image.open(cap_image)
    cropped_img = crop_image_with_coords(img)
    store_cropped_image(cropped_img)

# Crop dialog 
@st.dialog("Crop the image")
def crop_image():

    if cap_image:
        img = Image.open(cap_image)
        # Get a cropped image from the frontend
        # use default_coords
        # The (xl, xr, yt, yb) coords to use by default
        if len(st.session_state.coords) > 0:     
            cropped_img = crop_image_with_coords(img)
        else:
            cropped_img = st_cropper(img, realtime_update=True, box_color='#0000FF', aspect_ratio=(1,1))

        # Manipulate cropped image at will
        st.write("Preview")
        _ = cropped_img.thumbnail((150,150))
        st.image(cropped_img)

        if st.button("Submit"):
            store_cropped_image(cropped_img)
            st.rerun()
            #  TODO: add spinner
            # st.spinner("Processing...")

            
    else:
        st.error("No image uploaded")
 

# App title
st.set_page_config(page_title="💬 ChapGPT", page_icon="img/chapgpt.gif")

# Load the configuration file
with open('config/config.yaml') as file:
    config = yaml.load(file, Loader=SafeLoader)

# Create an authenticator object
authenticator = stauth.Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days']
    )

# Credentials
with st.sidebar:
    st.image("img/chapgpt_logo.png")
    st.title('💬 ChapGPT 🍾🤖')
 
    try:
        authenticator.login(location='sidebar')
    except Exception as e:
        st.error(e)


    if st.session_state['authentication_status']:
        authenticator.logout(location='sidebar')
        st.sidebar.write(f'Welcome *{st.session_state["name"]}*')
    elif st.session_state['authentication_status'] is False:
        st.error('Username/password is incorrect')
    elif st.session_state['authentication_status'] is None:
        st.warning('Please enter your username and password')

# display the file uploader in the sidebar
cap_image = st.sidebar.file_uploader("Upload image", type=["jpg", "jpeg", "png"])
if cap_image and not st.session_state.get("image") or st.session_state.get("image") != cap_image: # only the first time or if the image changes
    st.session_state.image = cap_image
    st.sidebar.write("Image uploaded successfully!")    
    st.session_state.messages.append(ImageMessage(role="user", text_content="Image uploaded", image=cap_image))

# Store LLM generated responses
if "messages" not in st.session_state.keys():
    st.session_state.messages = [
        Message(role="assistant", text_content="I can help you checking if Isa has a cap in her collection")
    ]


def show_list_cap_images(cap_list: list[Cap]):
    num_columns = len(cap_list)
    columns = st.columns(num_columns)
    for (cap, column, index) in zip(cap_list, columns, range(1, num_columns+1)):
        cap_image_bytes = base64.b64decode(cap.base64)
        column.image(cap_image_bytes, width=100)
        column.write(f"{index}. {cap.brand} n. {cap.brand_num}")


def manage_history_chat_messages():
    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message.role):
            match message:                
                case FoundCapMessage():
                    st.image(message.image, width=300)
                    st.write(message.text)
                case FoundSimilarCapsMessage():
                    show_list_cap_images(message.caps)
                    st.write(message.text)                    
                case ImageMessage():
                    st.image(message.image, width=100)
                    st.write(message.text)
                case Message():
                    st.write(message.text)
                case _:
                    st.write(f"ERROR: what is this? {message}")

manage_history_chat_messages()

# Function for generating LLM response
def generate_response(prompt_input) -> Message:
    if st.session_state['authentication_status']:
        message_answer = ask_bot(prompt_input)
    return message_answer


# User-provided prompt
if prompt := st.chat_input(disabled=not st.session_state['authentication_status']):
    st.session_state.messages.append(Message(role="user", text_content=prompt))
    with st.chat_message("user"):
        st.write(prompt)


# Generate a new response if last message is not from assistant
if st.session_state.messages[-1].role != "assistant":
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            if not prompt:
                prompt = st.session_state.messages[-1].image
            answer = generate_response(prompt)
            st.session_state.messages.append(answer)  # can i save the answer here?

            match answer:                
                case FoundSimilarCapsMessage():
                    # found similar caps
                    show_list_cap_images(answer.caps)
                    st.write(answer.text)
                case FoundCapMessage():
                    # In this message the bot should show the image with the cap in the square
                    # but sometimes the cap has not been found.
                    st.image(answer.image, width=300)
                    st.session_state.coords = answer.points 
                    st.write(answer.text)  
                    # only if the bot thinks that it has found the cap, give to the user
                    # the possibility to continue with that imag cropped.
                    # if not, he/she will need to select the cap in the image manually.     
                    if answer.points:
                        button_yes, button_no = st.columns(2)
                        with button_yes:
                            st.button("Yep! That is the cap", on_click=the_cap_is_found)
                        with button_no:
                            st.button("Let me crop the image", on_click=crop_image)
                    else:
                        st.button("Let me crop the image", on_click=crop_image)            
                case Message():
                    if "upload" in answer.text.lower():
                        response = "Please upload the cap image using the uploader in the sidebar."
                        st.write(response)
                    else: 
                        st.write(answer.text)
                case _:
                    st.write(f"ERROR: what is this? {answer}")
                



   
