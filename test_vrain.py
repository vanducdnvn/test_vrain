
import requests

URL = "https://data.vrain.vn/public/current/all.json"

try:
    r = requests.get(URL, timeout=30)

    print("HTTP:", r.status_code)
    print("MIME:", r.headers.get("Content-Type"))
    print("Size:", len(r.content))

    r.raise_for_status()
    data = r.json()

    print("Kiểu dữ liệu:", type(data).__name__)
    print("Số bản ghi:", len(data))

    if isinstance(data, list) and data:
        print("Trạm đầu tiên:", data[0])

except Exception as e:
    print("LỖI:", str(e))
