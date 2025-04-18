import os
import requests
from datetime import datetime, timedelta, timezone

def download_gfs_main(start_time: datetime, end_time: datetime, download_directory: str):
    os.makedirs(download_directory, exist_ok=True)

    # 오늘 날짜 기준 - 어제 날짜 폴더에서 18z GFS 데이터 받기
    kst_now = datetime.now()
    folder_date = (kst_now - timedelta(days=1)).strftime("%Y%m%d")
    folder_url = f"https://nomads.ncep.noaa.gov/pub/data/nccf/com/gfs/prod/gfs.{folder_date}/18/atmos/"

    # 기준 시간 (UTC 기준 어제 18시)
    base_time = datetime(kst_now.year, kst_now.month, kst_now.day, 18, 0, 0) - timedelta(days=1)

    # 반복 다운로드
    current_time = start_time
    while current_time <= end_time:
        # 둘 다 naive datetime이므로 연산 가능
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

# 테스트용 실행
if __name__ == "__main__":
    # KST 기준 오늘 00시 → UTC로 -9시간
    kst_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    utc_start = kst_start - timedelta(hours=9)
    utc_end = utc_start + timedelta(days=3)

    download_gfs_main(utc_start, utc_end, "/home/yjtech/WRFmodel/geog_data/GFS")
