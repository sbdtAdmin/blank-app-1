import streamlit as st
from helpers import get_or_create_bitcoin_address, check_balance, send_bitcoins, display_qr_code

def wallet_page():
    st.write(f"Добро пожаловать, {st.session_state['username']}!")
    username = st.session_state['username']

    # Получение или создание биткоин-адреса
    private_key, wallet_address = get_or_create_bitcoin_address(username)
    st.write(f"Ваш приватный ключ: {private_key}")
    st.write(f"Ваш Bitcoin адрес: {wallet_address}")
    display_qr_code(wallet_address)

    # Форма для отправки биткоинов
    with st.form("send_bitcoins_form"):
        st.header("Отправка биткоинов")
        to_address = st.text_input("Введите адрес получателя")
        amount = st.number_input("Введите сумму для отправки (в BTC)", min_value=0.0, format="%.8f")
        send_button = st.form_submit_button("Отправить")

    if send_button:
        tx_hash = send_bitcoins(private_key, to_address, amount)
        if tx_hash:
            st.success(f"Транзакция отправлена! Хэш транзакции: {tx_hash}")

    # Проверка баланса
    st.header("Проверка баланса")
    balance = check_balance(wallet_address)
    st.write(f"Текущий баланс: {balance} BTC")
