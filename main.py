import streamlit as st
from assets.chakra_info import app_text

# Перенаправляем пользователя на нужную страницу
st.set_page_config(
    page_title="KIRLIAN PLATFORM",
    page_icon="🧘",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state for language
if 'language' not in st.session_state:
    st.session_state.language = 'ru'  # Default to Russian

# Get text based on selected language
def get_text(key):
    return app_text[st.session_state.language][key]

# Custom CSS for black background
st.markdown("""
<style>
body {
    background-color: black !important;
    color: white !important;
}
.stApp {
    background-color: black !important;
    color: white !important;
}
.css-1kyxreq {
    background-color: black !important;
}
</style>
""", unsafe_allow_html=True)

# Добавляем простую страницу-перенаправление
st.title("KIRLIAN PLATFORM")
st.markdown("### Выберите 'Bioresonans Lab' в меню слева для начала работы с приложением")
st.markdown("### Choose 'Bioresonans Lab' in the left menu to start working with the application")