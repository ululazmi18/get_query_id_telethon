import os
import sys
import json
import urllib.parse
import asyncio  # Tambahkan import asyncio
from telethon import TelegramClient, functions

# Pastikan folder 'sessions' ada
if not os.path.exists("sessions"):
    os.makedirs("sessions")

CONFIG_FILE = "config.json"
DEFAULT_CONFIG = {
    "api_id": 0,
    "api_hash": "your_api_hash_here"
}
if not os.path.exists(CONFIG_FILE):
    with open(CONFIG_FILE, "w") as file:
        json.dump(DEFAULT_CONFIG, file, indent=4)
        print("Harap isi api_id dan api_hash Anda di dalam config.json, lalu jalankan ulang program.")
        sys.exit()
with open(CONFIG_FILE, "r") as file:
    config = json.load(file)
if config["api_id"] == 0 or config["api_hash"] == "your_api_hash_here":
    print("Harap isi api_id dan api_hash Anda di dalam config.json, lalu jalankan ulang program.")
    sys.exit()
    
def buat_sesi_baru():
    api_id, api_hash = config["api_id"], config["api_hash"]
    phone_number = input("Masukkan nomor telepon: ")
    session_file = os.path.join("sessions", f"{phone_number}.session")
    if os.path.exists(session_file):
        print(f"Sesi untuk nomor {phone_number} sudah ada.")
        return

    # Membuat klien baru dengan nama file sesuai nomor telepon
    app = TelegramClient(
        session=session_file,
        api_id=api_id,
        api_hash=api_hash,
        device_model='Ulul Azmi',
        app_version='telethon'
    )
    app.start(phone_number)
    print(f"Sesi untuk nomor {phone_number} berhasil dibuat dan disimpan di folder 'sessions/'.")
    app.disconnect()

BOT_FILE = "bot.json"
# Fungsi untuk memuat atau membuat file bot.json
def load_bot_data():
    if not os.path.exists(BOT_FILE):
        with open(BOT_FILE, 'w') as file:
            json.dump({}, file)
    with open(BOT_FILE, 'r') as file:
        return json.load(file)

# Fungsi untuk menyimpan data ke file bot.json
def save_bot_data(data):
    with open(BOT_FILE, 'w') as file:
        json.dump(data, file, indent=2)

# Fungsi untuk menampilkan daftar bot yang tersedia
def select_bot():
    bot_data = load_bot_data()
    bot_usernames = list(bot_data.keys())

    print("Pilih Bot:")
    print("0. Kembali")
    print("1. Input bot untuk sesi ini")
    print("2. Tambah bot baru")

    for index, bot_username in enumerate(bot_usernames, start=3):
        print(f"{index}. {bot_username}")

    choice = input("Masukkan pilihan Anda: ")
    if choice == '0':
        print("Kembali ke menu sebelumnya.")
        return 0
    elif choice == '1':
        bot_username = input("Silakan masukkan bot username (misalnya, @YourBot): ")
        referral_url = input("Silakan masukkan URL Refferal: ")
        print(f"Bot {bot_username} dengan URL: {referral_url} telah diinput untuk sesi ini.")
        return {'bot_username': bot_username, 'referral_url': referral_url}
    elif choice == '2':
        bot_username = input("Silakan masukkan bot username (misalnya, @YourBot): ")
        referral_url = input("Silakan masukkan URL Refferal: ")
        bot_data[bot_username] = referral_url
        save_bot_data(bot_data)
        print(f"Bot {bot_username} telah disimpan dengan URL: {referral_url}")
        return {'bot_username': bot_username, 'referral_url': referral_url}
    else:
        index = int(choice) - 3
        if 0 <= index < len(bot_usernames):
            bot_username = bot_usernames[index]
            referral_url = bot_data[bot_username]
            print(f"Menggunakan bot: {bot_username} dengan URL: {referral_url}")
            return {'bot_username': bot_username, 'referral_url': referral_url}
        else:
            print("Pilihan tidak valid.")
            return None

async def minta_query_id_ke_semua_klien():
    
    session_files = [f for f in os.listdir("sessions") if f.endswith(".session")]
    if not session_files:
        print("Tidak ada sesi yang ditemukan di folder 'sessions'.")
        return

    bot_selection = select_bot()
    if bot_selection == 0:
        return
    if not bot_selection:
        return
    api_id, api_hash = config["api_id"], config["api_hash"]
    bot_username = bot_selection['bot_username']
    referral_url = bot_selection['referral_url']
    
    user = []
    query_id = []

    for session_file in session_files:
        session_name = session_file.replace(".session", "")
        
        session_file = os.path.join("sessions", f"{session_file}")

        app = TelegramClient(
            session_file,
            api_id=api_id,
            api_hash=api_hash,
            device_model='Ulul Azmi',
            app_version='telethon'
        )
        async with app:
            attempt = 0
            while attempt < 3:
                try:
                    bot_peer = bot_username
                    start_param = referral_url.split("startapp=")[1]
                    result = await app(functions.messages.RequestWebViewRequest(
                        peer=bot_peer,
                        bot=bot_peer,
                        platform="android",
                        url=referral_url,
                        from_bot_menu=False,
                        start_param=start_param,
                    ))
                    result1 = await app(functions.messages.RequestWebViewRequest(
                        peer=bot_peer,
                        bot=bot_peer,
                        platform="android",
                        url=result.url,
                        from_bot_menu=False,
                        start_param=start_param
                    ))
                    result2 = await app(functions.messages.RequestWebViewRequest(
                        peer=bot_peer,
                        bot=bot_peer,
                        platform="android",
                        url=result1.url,
                        from_bot_menu=False,
                        start_param=start_param
                    ))
                    decoded_once = urllib.parse.unquote(result1.url)
                    extracted_user = decoded_once.split("tgWebAppData=")[1].split("&tgWebAppVersion=")[0]
                    user.append(extracted_user)
                    extracted_query_id = decoded_once.split("tgWebAppData=")[-1].split("&tgWebAppVersion=")[0]
                    query_id.append(extracted_query_id)
                    
                    print(f"\x1b[32mGET Query ID\x1b[0m : {session_name}")
                    attempt = 3
                except Exception as e:
                    attempt += 1
                    print(f"Gagal membuka WebView untuk {session_name}: {e}")
        
    with open("user.txt", "w") as data_file:
        data_file.writelines("\n".join(user))
    with open("query_id.txt", "w") as query_id_file:
        query_id_file.writelines("\n".join(query_id))
    
def tampilkan_menu():
    print("\n--- Menu ---")
    print("1. Buat sesi baru")
    print("2. Minta query ID ke semua klien")
    print("3. Exit")

async def main():
    while True:
        tampilkan_menu()
        pilihan = input("Pilih menu: ")

        if pilihan == "1":
            buat_sesi_baru()
        elif pilihan == "2":
            await minta_query_id_ke_semua_klien()  # Tambahkan await
        elif pilihan == "3":
            print("Keluar dari program.")
            sys.exit()
        else:
            print("Pilihan tidak valid. Silakan coba lagi.")

if __name__ == "__main__":
    asyncio.run(main())  # Jalankan main dengan asyncio
