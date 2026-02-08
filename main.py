import requests
import threading
import time
from queue import Queue

BANNER = """
===========================
   KAIROX PROXY SCRAPER
===========================
"""

print(BANNER)

SOURCES = [
    "https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/http.txt",
    "https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/http.txt",
    "https://raw.githubusercontent.com/ShiftyTR/Proxy-List/master/http.txt"
]

THREADS = 60
TIMEOUT = 6

proxies = set()
live = []
queue = Queue()

print("[+] Downloading proxy lists...\n")

for url in SOURCES:
    try:
        r = requests.get(url, timeout=10)
        for line in r.text.splitlines():
            if ":" in line:
                proxies.add(line.strip())
    except:
        pass

print(f"[✓] Loaded {len(proxies)} proxies\n")

for p in proxies:
    queue.put(p)

lock = threading.Lock()

def tester():
    while not queue.empty():
        proxy = queue.get()
        start = time.time()
        try:
            requests.get(
                "http://httpbin.org/ip",
                proxies={
                    "http": f"http://{proxy}",
                    "https": f"http://{proxy}"
                },
                timeout=TIMEOUT
            )
            ping = round(time.time() - start, 2)

            with lock:
                live.append((proxy, ping))
                print(f"[LIVE] {proxy} | {ping}s")

        except:
            pass

        queue.task_done()

print("[*] Testing proxies...\n")

for _ in range(THREADS):
    threading.Thread(target=tester, daemon=True).start()

queue.join()

live.sort(key=lambda x: x[1])

with open("working_proxies.txt", "w") as f:
    for p in live:
        f.write(f"{p[0]} | {p[1]}s\n")

print("\n====================")
print(f"WORKING: {len(live)}")
print("Saved => working_proxies.txt")
print("====================\n")
