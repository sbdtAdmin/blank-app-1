import streamlit as st
import json
import os
from bitcoin import *
import qrcode
from io import BytesIO

USERS_DB = 'users.json'

def load_users():
    if os.path.exists(USERS_DB):
        with open(USERS_DB, 'r') as file:
            users = json.load(file)
            if isinstance(users, dict):
                return users
            else:
                st.error("Ошибка в структуре данных пользователя.")
                return {}
    else:
        return {}

def save_users(users):
    with open(USERS_DB, 'w') as file:
        json.dump(users, file)

def hash_password(password):
    return password.encode('utf-8') if isinstance(password, str) else password

def register_user(username, password):
    if not username or not password:
        st.warning("Логин и пароль не могут быть пустыми.")
        return
    users = load_users()
    if username in users:
        st.warning("Пользователь уже существует.")
    else:
        hashed_password = hash_password(password)
        if hashed_password:
            users[username] = {'password': hashed_password}
            save_users(users)
            st.success("Регистрация успешна!")

def login_user(username, password):
    if not username or not password:
        st.warning("Логин и пароль не могут быть пустыми.")
        return
    users = load_users()
    hashed_password = hash_password(password)
    if hashed_password and username in users and users[username]['password'] == hashed_password:
        st.session_state['logged_in'] = True
        st.session_state['username'] = username
        st.success("Вход выполнен успешно!")
    else:
        st.error("Неверный логин или пароль.")

def get_or_create_bitcoin_address(username):
    users = load_users()
    if 'private_key' in users[username]:
        private_key = users[username]['private_key']
        st.write("Загружен сохраненный приватный ключ.")
    else:
        private_key = random_key()
        users[username]['private_key'] = private_key
        save_users(users)
        st.write("Создан новый приватный ключ.")
    public_key = privtopub(private_key)
    address = pubtoaddr(public_key)
    return private_key, address

def display_qr_code(address):
    qr = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_L, box_size=10, border=4)
    qr.add_data(address)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    buffer = BytesIO()
    img.save(buffer, format="PNG")
    st.image(buffer.getvalue(), caption="Ваш Bitcoin адрес")

def check_balance(address):
    try:
        url = f"https://blockchain.info/q/addressbalance/{address}"
        response = requests.get(url)
        if response.status_code == 200:
            balance_satoshi = int(response.text)
            balance_btc = balance_satoshi / 1e8
            return balance_btc
        else:
            st.error("Ошибка при получении баланса")
            return None
    except Exception as e:
        st.error(f"Ошибка: {e}")
        return None

def send_bitcoins(private_key, to_address, amount):
    try:
        my_address = privtoaddr(private_key)
        txs = history(my_address)
        outputs = [(to_address, int(amount * 100000000))]
        tx = mktx(txs, outputs)
        signed_tx = sign(tx, 0, private_key)
        tx_hash = send(signed_tx)
        return tx_hash
    except Exception as e:
        st.error(f"Ошибка при отправке биткоинов: {str(e)}")
        return None
