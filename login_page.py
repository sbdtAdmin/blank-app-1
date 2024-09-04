import streamlit as st
from helpers import register_user, login_user

def login_or_register():
    st.header("Вход или регистрация")

    # Форма для регистрации или входа
    with st.form("login_form"):
        choice = st.radio("Выберите действие", ["Вход", "Регистрация"])
        username = st.text_input("Логин")
        password = st.text_input("Пароль", type="password")
        submit_button = st.form_submit_button("Подтвердить")

    if submit_button:
        if choice == "Регистрация":
            register_user(username, password)
        else:
            login_user(username, password)
