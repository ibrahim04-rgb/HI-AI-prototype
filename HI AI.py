import streamlit as st
from streamlit_option_menu import option_menu
import hmac
import openai 

# Set up the page configuration
st.set_page_config(
    page_title="AI Text to Graph",
    page_icon="static/LOGO.png",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Hide default Streamlit elements like the hamburger menu and footer
st.markdown('''
<style>
#MainMenu {visibility:hidden;}
footer {visibility: hidden;}
</style>
''', unsafe_allow_html=True)

# Function to handle login
def check_password():
    """Returns `True` if the user had a correct password."""

    def password_entered():
        """Checks whether a password entered by the user is correct."""
        if st.session_state["username"] in st.secrets["passwords"] and hmac.compare_digest(
            st.session_state["password"], st.secrets["passwords"][st.session_state["username"]]):
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # Don't store the password.
            del st.session_state["username"]
        else:
            st.session_state["password_correct"] = False

    # Show login form if the user hasn't logged in
    if "password_correct" not in st.session_state or not st.session_state["password_correct"]:
        # Show the logo only on the login page
        st.image("static/LOGO.png", width=100)

        # Show the login form
        with st.form("Credentials"):
            st.text_input("Username", key="username")
            st.text_input("Password", type="password", key="password")
            submitted = st.form_submit_button("Log in", on_click=password_entered)

        # Display error message if login fails
        if "password_correct" in st.session_state and not st.session_state["password_correct"]:
            st.error("😕 User not known or password incorrect")

        # Stop the app from proceeding if login failed or not yet attempted
        return False

    return True

# Check if the user has logged in correctly
if check_password():
    # If login is successful, hide the login page content and show the main app content
    st.empty()  # Clears the logo and login form from the page

    # Display the sidebar
    add_selectbox = st.sidebar.selectbox(
     "How would you like to be contacted?",
      ("Email", "Home phone", "Mobile phone")
    )
    with st.sidebar:
       add_radio = st.radio(
         "Choose a shipping method",
         ("Standard (5-15 days)", "Express (2-5 days)")
    )
    # Chatbot section
    st.title("HI AI chat")

    # Initialize OpenAI client using API key from secrets
   

    if "openai_model" not in st.session_state:
        st.session_state["openai_model"] = "gpt-3.5-turbo"

    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display chat messages from history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Accept user input and generate response
    if prompt := st.chat_input("What is up?"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            response = ""
            stream = openai.ChatCompletion.create(
                model=st.session_state["openai_model"],
                messages=[
                    {"role": m["role"], "content": m["content"]}
                    for m in st.session_state.messages
                ],
                stream=True,
            )
            # Concatenate streamed content to get the full response
            for chunk in stream:
                response += chunk.choices[0].delta.get("content", "")

            st.markdown(response)
            st.session_state.messages.append({"role": "assistant", "content": response})
