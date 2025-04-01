import streamlit as st
import openai

# Set your OpenAI API key (ensure you have this set in your Streamlit secrets)
openai.api_key = st.secrets["openai_api_key"]

st.set_page_config(page_title="Coach Chat", page_icon="🏀", layout="centered")

st.title("🏀 Coach Bry: Your Learning Buddy")
st.write("Hi Lily! I'm Coach Bry—let’s learn and have some fun! 💪😊")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Hey Lily! Ready to crush some math today? 🔥"}
    ]

# Display previous messages
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Chat input box
if prompt := st.chat_input("Type here or ask me anything!"):
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""

        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=st.session_state.messages
        )

        full_response = response.choices[0].message["content"]
        message_placeholder.markdown(full_response)

    st.session_state.messages.append({"role": "assistant", "content": full_response})
