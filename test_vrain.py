import requests
from datetime import datetime, timezone

url = 'https://data.vrain.vn/public/current/20.json'
try:
    r = requests.get(url, timeout=25, headers={'Accept': 'application/json'})
    print('UTC:', datetime.now(timezone.utc).isoformat())
    print('HTTP:', r.status_code)
    print('Server:', r.headers.get('Server'))
    print('Content-Type:', r.headers.get('Content-Type'))
    if r.status_code == 200:
        data = r.json()
        print('Số trạm Hà Nội:', len(data) if isinstance(data, list) else 'JSON không phải mảng')
    else:
        print('Phản hồi:', r.text[:500])
        raise SystemExit('VRain từ chối yêu cầu; chưa thể thu thập tự động từ runner này.')
except requests.RequestException as exc:
    raise SystemExit(f'Lỗi kết nối: {exc}')
