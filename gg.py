import requests
import time
import sys
import threading

API_VERSION = "5.199"

# ========== ВСТАВЬ СВОИ ТОКЕНЫ (уже твои) ==========
TOKENS = [
    "vk1.a.2BVAUKXOB7n-flnE_TzLLfrlDda7OHxxdLWFSSczv89yk21Ok-Ojh5QES9aV_48vYia599BtSdMRzdio6kZKzpkkI-q3pE-8owETEFL4VTTEoFSIiQDgL0cwUy1iFKixu-y-l2eq9hhGabDqc3_AOALH-WCd2vgU_SPgZqtzdxUDqhQJZq402Cdd971cVEuv1XxX_0lbdDI7iCckQWs2kw",
    "vk1.a.sZbkVf5JWMEwsiH4dkaFz8hjAZf8bVYKXNVCe-vNkCukCzXpyQXaClOVAkLh92b2BqSkxjNSOyN4EhRx4qm1x-AgYfOJ0tNBfWCyfGNdf_WRfJ_sF--6jGETqVJT7M6BOwME0m1An0fVah_D4m4_EFLEgkjD59thys5NcJY8t74rh9ylCQZbMxzXuL9QqYRCW6cy1MhgLO46rFuq9TQnBg",
    "vk1.a.EZumsKgqBc3hkv1CCbe3hPB348XAYAFViCFKfE0RvyuTzSV37X1YKlDCbKNZNdtXhOLIoXeNAN0JPTDnKweBNedmS3ej9RfqWJ8Ftt7kHGRk5IC-KMrjWWCL75EdxO4dRf8JVB81NOzuqSbC0vrKsY3kjcik4jWJIH1pP4PIaaSts1844aQDP0omnnzY6_DlKDLWc-9Pug0ClrMZtJeW1w"
]
# ===================================================

captured = False
capture_time_ms = 0
lock = threading.Lock()

def try_capture(token, group_id, short_name):
    url = "https://api.vk.com/method/groups.edit"
    params = {
        "access_token": token.strip(),
        "v": API_VERSION,
        "group_id": group_id,
        "screen_name": short_name
    }
    try:
        resp = requests.get(url, params=params, timeout=3)
        data = resp.json()
        if "error" in data:
            err_code = data['error'].get('error_code')
            if err_code in (6, 9):
                return "FLOOD"
            return "ERROR"
        if data.get("response") == 1:
            return "SUCCESS"
        return "ERROR"
    except Exception:
        return "ERROR"

def worker(token, group_id, short_name, thread_id):
    global captured, capture_time_ms
    while not captured:
        start_req = time.time()
        result = try_capture(token, group_id, short_name)
        req_ms = (time.time() - start_req) * 1000

        if result == "SUCCESS":
            with lock:
                if not captured:
                    captured = True
                    capture_time_ms = req_ms
            print(f"\n✅ ПОТОК {thread_id} ЗАХВАТИЛ! Время запроса: {req_ms:.2f} мс")
            sys.exit(0)
        elif result == "FLOOD":
            print('.', end='', flush=True)  # точка вместо волны
            time.sleep(0.5)
        else:
            print('.', end='', flush=True)  # точка на любую ошибку

def main():
    print("=== МНОГОПОТОЧНЫЙ ЗАХВАТ (0 задержка) ===\n")
    print(f"📡 Используется {len(TOKENS)} встроенных токенов.\n")
    
    try:
        group_id = int(input("Введите ID сообщества: ").strip())
    except:
        print("Неверный ID группы.")
        return
    
    short_name = input("Введите желаемый короткий адрес: ").strip()
    if not short_name:
        print("Адрес не введён.")
        return
    
    try:
        num_threads = int(input("Количество потоков (рекомендуется 5-20): ").strip())
    except:
        num_threads = 10
    
    print(f"\n🚀 ЗАПУСК {num_threads} ПОТОКОВ. ИНТЕРВАЛ 0 СЕК.")
    print(f"🎯 Цель: {short_name} | Группа: {group_id}")
    print("💥 Как только адрес освободится – будет захвачен.\n")
    
    threads = []
    for i in range(num_threads):
        token = TOKENS[i % len(TOKENS)]
        t = threading.Thread(target=worker, args=(token, group_id, short_name, i+1))
        t.daemon = True
        t.start()
        threads.append(t)
    
    try:
        while not captured:
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("\n❌ Скрипт остановлен.")
        sys.exit(0)
    
    print(f"\n✅ УСПЕХ! Домен {short_name} захвачен!")
    print(f"🚀 Время выполнения запроса: {capture_time_ms:.2f} мс")
    sys.exit(0)

if __name__ == "__main__":
    main()
