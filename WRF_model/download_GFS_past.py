import requests
from datetime import datetime, timedelta
import os
import sys

# 명령줄 인자로부터 날짜를 받아오기
if len(sys.argv) != 3:
    print("Usage: python download_GFS_past.py <start_time> <end_time>")
    sys.exit(1)

start_time_str = sys.argv[1]
end_time_str = sys.argv[2]

# 시작 시간과 끝 시간 파싱
start_time = datetime.strptime(start_time_str, "%Y-%m-%d %H")
end_time = datetime.strptime(end_time_str, "%Y-%m-%d %H")

print(f"Downloading past GFS data from {start_time} to {end_time}")

# 다운로드할 경로 설정
download_directory = '/home/yjtech/WRFmodel/geog_data/GFS'  # 원하는 디렉토리 경로


# 파일 존재 여부를 확인하는 함수
def check_file_exists(file_url, file_name):
    print(f"Checking for file: {file_url}")
    response = requests.head(file_url)  # HEAD 요청을 사용해서 파일 존재 여부만 확인
    if response.status_code == 200:
        print(f"File exists: {file_url}")
        download_file(file_url, file_name)
    else:
        print(f"File does not exist: {file_url}")


# 파일 다운로드 함수
def download_file(file_url, file_name):
    # 다운로드할 경로와 파일 이름 결합
    file_path = os.path.join(download_directory, file_name)

    print(f"Downloading file: {file_url}")
    response = requests.get(file_url)
    if response.status_code == 200:
        # 다운로드할 경로에 파일 저장
        with open(file_path, 'wb') as f:
            f.write(response.content)
        print(f"File downloaded successfully: {file_path}")
    else:
        print(f"Failed to download the file: {file_path}")


# 시작 시간부터 끝 시간까지 3시간 간격으로 파일을 체크하는 코드
current_time = start_time  # current_time은 시작 시간으로 초기화

# 현재 시간이 끝 시간을 넘을 때까지 반복
while current_time <= end_time:
    # 날짜를 YYYYMMDD 형식으로 변환
    date_str = current_time.strftime("%Y%m%d")

    # 해당 날짜에 대한 GFS 데이터 폴더 URL
    folder_url = f"https://nomads.ncep.noaa.gov/pub/data/nccf/com/gfs/prod/gfs.{date_str}/18/atmos/"

    # 각 시간대별로 f000, f003, f006 파일을 확인 (현재 시간에 맞는 파일만 확인)
    f = (current_time.hour // 3) * 3  # f000, f003, f006, ... 으로 파일 선택
    file_url = f"{folder_url}gfs.t18z.pgrb2.0p25.f{str(f).zfill(3)}"
    file_name = f"gfs_t00z_{date_str}_f{str(f).zfill(3)}.grib2"

    # 해당 파일이 존재하는지 확인하고, 존재하면 다운로드
    check_file_exists(file_url, file_name)

    # 3시간씩 증가
    current_time += timedelta(hours=3)

    # current_time이 end_time을 초과하면 종료
    if current_time >= end_time:
        break  # end_time을 초과하면 반복문을 종료
