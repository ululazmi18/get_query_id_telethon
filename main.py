import os
import json
import asyncio
from telethon import TelegramClient, functions  # Pastikan functions diimpor
from telethon.sessions import StringSession
from telethon.errors import SessionPasswordNeededError
from dotenv import load_dotenv

load_dotenv()  # Mengimpor dotenv

# Konfigurasi API ID dan API Hash
api_id = int(os.getenv("API_ID"))
api_hash = os.getenv("API_HASH")

accounts = {}

# Fungsi untuk menanyakan input pengguna
async def ask_question(question):
    return input(question)

# Fungsi login dengan nomor telepon
async def login_with_phone_number():
    phone_number = await ask_question("Nomor telepon Anda (misalnya, +1234567890): ")
    client = TelegramClient(StringSession(), api_id, api_hash)

    await client.connect()
    if not await client.is_user_authorized():
        try:
            await client.send_code_request(phone_number)
            code = await ask_question("Kode yang Anda terima: ")
            await client.sign_in(phone_number, code)
        except SessionPasswordNeededError:
            password = await ask_question("Kata sandi Anda: ")
            await client.sign_in(password=password)

    print('Login berhasil')
    session_string = client.session.save()
    session_folder = 'sessions'
    os.makedirs(session_folder, exist_ok=True)
    session_file = os.path.join(session_folder, f"{phone_number.replace('+', '')}.session")
    
    with open(session_file, "w") as f:
        f.write(session_string)
    accounts[phone_number] = client
    print(f"Sesi disimpan di {session_file}")

# Fungsi login dengan file sesi
async def login_with_session_file():
    session_folder = 'sessions'
    if not os.path.exists(session_folder):
        print("Tidak ada file sesi yang ditemukan.")
        return

    session_files = [f for f in os.listdir(session_folder) if f.endswith('.session')]
    if not session_files:
        print("Tidak ada file sesi yang ditemukan.")
        return

    for session_file in session_files:
        session_path = os.path.join(session_folder, session_file)
        with open(session_path, "r") as f:
            session_string = f.read().strip()
        client = TelegramClient(StringSession(session_string), api_id, api_hash)
        try:
            await client.connect()
            accounts[session_file.replace('.session', '')] = client
            print(f"Berhasil login dengan sesi dari {session_file}")
        except Exception as e:
            print(f"Gagal login dengan {session_file}: {e}")

# Fungsi untuk meminta WebView
async def request_webview_for_client(client, phone_number, bot_peer, url):
    try:
        result = await client(functions.messages.RequestWebViewRequest(
            peer=bot_peer,
            bot=bot_peer,
            from_bot_menu=False,
            url=url,
            platform='android'
        ))
        web_app_data = result.url.split('#')[1].split('&')[0].split('=')[1]
        with open('cek.txt', 'w') as f:
            json.dump(result.to_dict(), f, indent=2)
        print(f"WebView berhasil diminta untuk {phone_number}")
        return {"phoneNumber": phone_number, "webAppData": web_app_data}
    except Exception as e:
        print(f"Error saat meminta WebView untuk {phone_number}: {e}")
        return None

# Fungsi untuk meminta WebView untuk semua klien dan menyimpan hasilnya per bot
async def request_webview_for_all_clients():
    if not accounts:
        print("Tidak ada akun yang masuk.")
        return

    bot_peer = await ask_question("Silakan masukkan bot peer (misalnya, @YourBot): ")
    url = await ask_question("Silakan masukkan URL refferal: ")
    results = []

    # Membuat folder untuk hasil WebView
    os.makedirs("webview_results", exist_ok=True)

    # Meminta WebView untuk setiap akun yang masuk
    for phone_number, client in accounts.items():
        result = await request_webview_for_client(client, phone_number, bot_peer, url)
        if result:
            results.append(result)
            sanitized_phone = phone_number.replace('+', '')
            with open(f"webview_results/{sanitized_phone}.txt", "a") as f:
                f.write(f"Bot: {bot_peer} | WebAppData: {result['webAppData']}\n")
    
    # Menyimpan semua hasil dalam satu file khusus untuk bot
    bot_file_name = f"{bot_peer.replace('@', '')}.txt"
    query_folder = 'query'
    os.makedirs(query_folder, exist_ok=True)
    bot_file_path = os.path.join(query_folder, bot_file_name)

    all_results = "\n".join([f"{r['webAppData']}" for r in results])
    with open(bot_file_path, "w") as f:
        f.write(all_results)

    print(f"Hasil untuk {bot_peer} disimpan di {bot_file_path}")

# Fungsi utama untuk menangani input pengguna
async def main():
    print("Selamat datang di Utilitas Bot Telegram!")
    
    while True:
        print("1. Login dengan nomor telepon")
        print("2. Login dengan file sesi")
        print("3. Memintan Query ID ke semua klien")
        print("4. Keluar")

        choice = await ask_question("Silakan pilih opsi: ")

        if choice == "1":
            await login_with_phone_number()
        elif choice == "2":
            await login_with_session_file()
        elif choice == "3":
            await request_webview_for_all_clients()
        elif choice == "4":
            break
        else:
            print("Pilihan tidak valid.")

# Menjalankan program
asyncio.run(main())
