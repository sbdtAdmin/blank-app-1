import streamlit as st
from login_page import login_or_register
from wallet_page import wallet_page

#st.markdown(
    """
<style>
#MainMenu {visibility: hidden}
footer {visibility: hidden}
</style>
    """,
#    unsafe_allow_html=True
#)

# Проверка состояния сессии
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False

# Основной процесс
if not st.session_state['logged_in']:
    login_or_register()
else:
    wallet_page()
