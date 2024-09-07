import streamlit as st
from login_page import login_or_register
from wallet_page import wallet_page

st.markdown(
"""
<style>
header {visibility: hidden};
button[data-testid="manage-app-button"] {visibility: hidden};
.styles_terminalButton__JBj5T {visibility: hidden};
#MainMenu {visibility: hidden};
.share_shareMenuFooter__A3x5P {visibility: hidden};
</style>
    """,
    unsafe_allow_html=True
)

# Проверка состояния сессии
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False

# Основной процесс
if not st.session_state['logged_in']:
    login_or_register()
else:
    wallet_page()
