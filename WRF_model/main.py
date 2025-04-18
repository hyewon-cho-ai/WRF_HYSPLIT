from datetime import datetime, timedelta
import os
import glob
import sys

sys.path.append(os.path.dirname(__file__))

from modules.download_GFS_main import download_gfs_main
from modules.run_wps import (
    modify_namelist_wps,
    run_link_grib,
    run_geogrid,
    run_ungrib,
    run_metgrid
)
from modules.run_wrf import (
    extract_times_from_namelist_wps,
    update_namelist_times,
    link_met_files,
    run_executable_with_log
)

#시간확인용
import time
start_timer = time.time()

#코드 실행 이전 파일 삭제
def clean_wps_directory(wps_dir):
    print("🧹 Cleaning WPS directory...")
    patterns = [
        "GRIBFILE.*",
        "FILE:*",
        "PFILE:*",
        "met_em.d*"
    ]
    for pattern in patterns:
        for filepath in glob.glob(os.path.join(wps_dir, pattern)):
            try:
                os.remove(filepath)
                print(f"🗑️ Removed {filepath}")
            except Exception as e:
                print(f"⚠️ Failed to remove {filepath}: {e}")

def clean_wrf_directory(wrf_dir):
    print("🧹 Cleaning WRF run directory...")
    patterns = [
        "wrfinput_d*",
        "wrfbdy_d*",
        "wrfout_d*",
        "rsl.*"
    ]
    for pattern in patterns:
        for filepath in glob.glob(os.path.join(wrf_dir, pattern)):
            try:
                os.remove(filepath)
                print(f"🗑️ Removed {filepath}")
            except Exception as e:
                print(f"⚠️ Failed to remove {filepath}: {e}")

GFS_DIR = "/home/yjtech/WRFmodel/geog_data/GFS"

def cleanup_old_gfs_files(directory):
    print("🧹 기존 GFS 파일 삭제 중...")
    for file in os.listdir(directory):
        if file.endswith(".grib2"):
            os.remove(os.path.join(directory, file))
            print(f"삭제됨: {file}")
    print("✅ GFS 디렉토리 정리 완료.")

def run_full_wrf_simulation():
    print("🚀 WRF 시뮬레이션 시작")

    # 1. GFS 정리 및 다운로드
    cleanup_old_gfs_files(GFS_DIR)
    start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    end = start + timedelta(days=3)
    download_gfs_main(start, end, GFS_DIR)

    # 2. WPS 실행 단계
    modify_namelist_wps(start.strftime("%Y-%m-%d_%H"), end.strftime("%Y-%m-%d_%H"))
    run_link_grib()
    run_geogrid()
    run_ungrib()
    run_metgrid()

    # 3. WRF 실행 단계
    start_time, end_time = extract_times_from_namelist_wps()
    update_namelist_times(start_time, end_time)
    link_met_files()
    run_executable_with_log("real.exe")
    run_executable_with_log("wrf.exe", start_time, end_time)

    print("🎉 모든 WRF 시뮬레이션 작업 완료!")

if __name__ == "__main__":
    # 1. 중간파일 정리
    clean_wps_directory("/home/yjtech/WRFmodel/WPS")
    clean_wrf_directory("/home/yjtech/WRFmodel/WRF/test/em_real")

    run_full_wrf_simulation()

    # ⏱️ 종료 후 시간 측정
    end_timer = time.time()
    elapsed = end_timer - start_timer
    print(f"⏱️ 전체 실행 시간: {elapsed:.2f}초")