import telebot
from librouteros import connect
import schedule
import time

# Inisialisasi bot Telegram
bot = telebot.TeleBot('6187243758:AAH0hlAuFl2t8j8CdQ2CU9YB2YRxe8JUHks')

# Fungsi untuk membagi pesan menjadi beberapa bagian


def split_message(message, max_length):
    return [message[i:i+max_length] for i in range(0, len(message), max_length)]

# Fungsi untuk mengirim pesan notifikasi ke Telegram


def send_notification(message):
    # Maksimal panjang pesan adalah 4096 karakter
    message_parts = split_message(message, 4096)

    for part in message_parts:
        # Ganti CHAT_ID dengan ID chat yang sesuai
        bot.send_message('-1001574229468', part)

# Fungsi untuk memonitor perangkat MikroTik


def monitor_mikrotik(username, password):
    try:
        # Membuat koneksi ke perangkat MikroTik
        connection = connect(
            username=username, password=password, host=host)

        # Mencetak informasi koneksi
        print("Berhasil terhubung ke perangkat MikroTik!")
        notification_message = "Perangkat MikroTik berhasil terhubung!\n"

        # Memantau penggunaan CPU
        cpu_load = list(connection('/system/resource/print'))[0]['cpu-load']
        cpu_load_percentage = int(cpu_load)
        cpu_load_message = "CPU Load: {}%".format(cpu_load)
        print(cpu_load_message)
        notification_message += cpu_load_message + "\n"

        # Memantau penggunaan memori
        mem_usage = list(connection('/system/resource/print')
                         )[0]['free-memory']
        mem_usage_bytes = int(mem_usage)
        mem_usage_message = "Memory Usage: {} bytes".format(mem_usage)
        print(mem_usage_message)
        notification_message += mem_usage_message + "\n"

        # Memantau penggunaan penyimpanan
        storage_usage = list(connection('/system/resource/print'))[0]
        free_hdd_space = storage_usage['free-hdd-space']
        total_hdd_space = storage_usage['total-hdd-space']
        storage_usage_message = "Storage Usage:\n- Free HDD Space: {}\n- Total HDD Space: {}".format(
            free_hdd_space, total_hdd_space)
        print(storage_usage_message)
        notification_message += storage_usage_message + "\n"

        # Memantau log dan kejadian
        log_entries = connection('/log/print')
        log_message = "Log Entries:\n"
        for entry in log_entries:
            log_message += "- {}\n".format(entry['message'])
        print(log_message)
        notification_message += log_message

        # Menutup koneksi
        connection.close()

    except Exception as e:
        print("Failed to connect to MikroTik:", str(e))
        notification_message = "Kesalahan: Tidak dapat terhubung ke MikroTik."

    # Mengirim pesan notifikasi ke Telegram
    send_notification(notification_message)

# Fungsi untuk menjadwalkan tugas monitor_mikrotik() setiap 10 detik


def schedule_monitor(username, password):
    schedule.every(10).seconds.do(monitor_mikrotik, username, password)

# Fungsi untuk menjalankan scheduler


def run_scheduler():
    while True:
        schedule.run_pending()
        time.sleep(5)


if __name__ == "__main__":
    # Meminta input username dan password
    host = input("Masukkan IP MikroTik: ")
    username = input("Masukkan username MikroTik: ")
    password = input("Masukkan password MikroTik: ")

    # Menjadwalkan tugas monitor_mikrotik()
    schedule_monitor(username, password)
    run_scheduler()  # Menjalankan scheduler
