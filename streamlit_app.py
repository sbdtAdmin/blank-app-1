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
    username = st.session_state['username']

    # Функции для работы с биткоин-адресом и транзакциями
    def generate_qr_code(data):
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(data)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        return img

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
        img = generate_qr_code(address)
        buffer = BytesIO()
        img.save(buffer, format="PNG")
        st.image(buffer.getvalue(), caption="Ваш Bitcoin адрес")

    def check_balance(address):
        txs = history(address)
        try:
            url = f"https://blockchain.info/q/addressbalance/{address}"
            response = requests.get(url)
            if response.status_code == 200:
                # Баланс возвращается в сатоши, конвертируем в биткоины
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

    # Получение или создание биткоин-адреса
    private_key, wallet_address = get_or_create_bitcoin_address(username)
    st.write(f"Ваш приватный ключ: {private_key}")
    st.write(f"Ваш Bitcoin адрес: {wallet_address}")
    display_qr_code(wallet_address)

    # Отправка биткоинов
    st.header("Отправка биткоинов")
    to_address = st.text_input("Введите адрес получателя")
    amount = st.number_input("Введите сумму для отправки (в BTC)", min_value=0.0, format="%.8f")
    if st.button("Отправить"):
        tx_hash = send_bitcoins(private_key, to_address, amount)
        if tx_hash:
            st.success(f"Транзакция отправлена! Хэш транзакции: {tx_hash}")

    # Проверка баланса
    st.header("Проверка баланса")
    balance = check_balance(wallet_address)
    st.write(f"Текущий баланс: {balance} BTC")
