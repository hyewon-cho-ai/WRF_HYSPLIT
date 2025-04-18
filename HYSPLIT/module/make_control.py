# control_generator.py
import requests
from datetime import datetime, timedelta, timezone

def geocode_address_kakao(address, kakao_api_key):
    url = "https://dapi.kakao.com/v2/local/search/address.json"
    headers = {"Authorization": f"KakaoAK {kakao_api_key}"}
    params = {"query": address}
    response = requests.get(url, headers=headers, params=params)
    result = response.json()

    if result.get('documents'):
        doc = result['documents'][0]
        loc = doc.get('address') or doc.get('road_address')
        if loc:
            lat = float(loc['y'])
            lon = float(loc['x'])
            return lat, lon

    raise Exception(f"❌ 주소를 찾을 수 없습니다: {address}")


def create_trajectory_control_file(lat, lon, alt=100, start_dt=None):
    if start_dt is None:
        start_dt = datetime.now(timezone.utc)

    control_lines = [
        start_dt.strftime("%Y %m %d %H"),
        "1",
        f"{lat:.4f} {lon:.4f} {alt}",
        "24",
        "1",  # backward
        "10000.0",
        "1",
        "/home/yjtech/hysplit/working/",
        "ARLDATA.BIN",
        "/home/yjtech/hysplit/output/",
        "tdump"
    ]

    with open("/home/yjtech/hysplit/working/CONTROL", "w") as f:
        f.write("\n".join(control_lines))
    print("✅ [Trajectory] CONTROL 파일 생성 완료!")


def create_dispersion_control_file(lat, lon, alt=10, start_dt=None):
    if start_dt is None:
        start_dt = datetime.now(timezone.utc)

    start_date = start_dt.strftime("%y %m %d %H")
    start_date_full = start_dt.strftime("%y %m %d %H %M")
    end_dt = start_dt + timedelta(hours=5)
    end_date_full = end_dt.strftime("%y %m %d %H %M")

    control_lines = [
        start_date,
        "1",
        f"{lat:.6f} {lon:.4f} {alt}",
        "3",
        "0",  # forward
        "10000.0",
        "1",
        "/home/yjtech/hysplit/working/",
        "ARLDATA.BIN",
        "1",
        "TEST",
        "1.0",
        "1.0",
        start_date_full,
        "1",
        f"{lat:.6f} {lon:.4f}",
        "0.01 0.01",
        "1.0 1.0",
        "./",
        "cdump",
        "1",
        "100",
        start_date_full,
        end_date_full,
        "00 01 00",
        "1",
        "5.0 6.0 1.0",
        "0.0 0.0 0.0 0.0 0.0",
        "0.0 8.0E-05 8.0E-05",
        "0.0",
        "0.0"
    ]

    with open("/home/yjtech/hysplit/working/CONTROL", "w") as f:
        f.write("\n".join(control_lines))
    print("✅ [Dispersion] CONTROL 파일 생성 완료!")
