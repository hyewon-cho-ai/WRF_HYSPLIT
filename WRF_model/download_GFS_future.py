import os
import requests
from datetime import datetime, timedelta, timezone

# 다운로드 경로
download_directory = "/home/yjtech/WRFmodel/geog_data/GFS"
os.makedirs(download_directory, exist_ok=True)

# 오늘 새벽 1시에 실행된다고 가정하면 → 어제 날짜의 18z 기준
kst_now = datetime.now() + timedelta(hours=9)
folder_date = (kst_now - timedelta(days=1)).strftime("%Y%m%d")

# UTC 기준 어제 18시 (18z)
base_time = datetime(kst_now.year, kst_now.month, kst_now.day, 18, 0, 0) - timedelta(days=1)
base_time = base_time.replace(tzinfo=timezone.utc)

# 다운로드 구간: 오늘(예: 17일) 00시 KST부터 3일치
start_time = base_time + timedelta(hours=6)  # KST 00시 (UTC+9 → f006부터 시작)
end_time = start_time + timedelta(days=3)

folder_url = f"https://nomads.ncep.noaa.gov/pub/data/nccf/com/gfs/prod/gfs.{folder_date}/18/atmos/"

# 다운로드 반복
current_time = start_time
while current_time <= end_time:
    # offset-naive 문제 방지
    current_time = current_time.replace(tzinfo=timezone.utc)

    f_hour = int((current_time - base_time).total_seconds() // 3600)
    f_str = f"{f_hour:03d}"
    file_url = f"{folder_url}gfs.t18z.pgrb2.0p25.f{f_str}"

    print(f"🔍 Checking for file: {file_url}")

    date_str = current_time.strftime("%Y%m%d")
    local_filename = f"gfs_{date_str}_f{f_str}.grib2"
    local_path = os.path.join(download_directory, local_filename)

    if not os.path.exists(local_path):
        response = requests.get(file_url, stream=True)
        if response.status_code == 200:
            with open(local_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            print(f"✅ Downloaded: {local_filename}")
        else:
            print(f"❌ Failed to download: {file_url}")
    else:
        print(f"✅ Already exists: {local_filename}")

    current_time += timedelta(hours=3)
