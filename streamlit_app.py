import streamlit as st
from hashlib import sha256
import json
import os
from bitcoin import *
import qrcode
from io import BytesIO

USERS_DB = 'users.json'

# Функции для работы с пользователями
def load_users():
    if os.path.exists(USERS_DB):
        with open(USERS_DB, 'r') as file:
            return json.load(file)
    else:
        return {}

def save_users(users):
    with open(USERS_DB, 'w') as file:
        json.dump(users, file)

def hash_password(password):
    if isinstance(password, str):
        password = password.encode('utf-8')  # Кодируем строку в байты
    try:
        hashed = sha256(password).hexdigest()
        return hashed
    except Exception as e:
        st.error(f"Ошибка при хешировании пароля: {str(e)}")
        return None

def register_user(username, password):
    if not username or not password:
        st.warning("Логин и пароль не могут быть пустыми.")
        return
    users = load_users()
    if username in users:
        st.warning("Пользователь уже существует.")
    else:
        hashed_password = hash_password(password)
        if hashed_password:  # Проверка на успешное хеширование
            users[username] = hashed_password
            save_users(users)
            st.success("Регистрация успешна!")

def login_user(username, password):
    if not username or not password:
        st.warning("Логин и пароль не могут быть пустыми.")
        return
    users = load_users()
    hashed_password = hash_password(password)
    if hashed_password and username in users and users[username] == hashed_password:
        st.session_state['logged_in'] = True
        st.session_state['username'] = username
        st.success("Вход выполнен успешно!")
    else:
        st.error("Неверный логин или пароль.")

def login_or_register():
    st.header("Вход или регистрация")
    choice = st.radio("Выберите действие", ["Вход", "Регистрация"])
    username = st.text_input("Логин")
    password = st.text_input("Пароль", type="password")
    if st.button("Подтвердить"):
        if choice == "Регистрация":
            register_user(username, password)
        else:
            login_user(username, password)

if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False

# Основной процесс
if not st.session_state['logged_in']:
    login_or_register()
else:
    st.write(f"Добро пожаловать, {st.session_state['username']}!")

    # Функции для работы с биткоин-адресом и транзакциями
    def generate_qr_code(data
