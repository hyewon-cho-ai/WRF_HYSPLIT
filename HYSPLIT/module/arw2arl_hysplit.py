import os
import subprocess
from datetime import datetime, timedelta

def convert_wrfout_to_arldata(start_time: datetime, end_time: datetime, wrf_base_path: str, arw2arl_path: str):
    current_time = start_time
    while current_time <= end_time:
        wrfout_filename = current_time.strftime("wrfout_d01_%Y-%m-%d_%H:00:00")
        wrfout_path = os.path.join(wrf_base_path, wrfout_filename)

        if os.path.exists(wrfout_path):
            print(f"🚀 ARLDATA.BIN 생성 중: {wrfout_filename}")
            result = subprocess.run(
                [arw2arl_path, wrfout_path],
                cwd=os.path.dirname(arw2arl_path),
                capture_output=True,
                text=True
            )
            print("📤 stdout:\n", result.stdout)
            print("⚠️ stderr:\n", result.stderr)

            if result.returncode != 0:
                print(f"❌ arw2arl 실패: {wrfout_filename}")
                return False
        else:
            print(f"⚠️ 파일 없음: {wrfout_filename}")

        current_time += timedelta(hours=6)  # 시간 간격 조정 가능

    return True

def run_hysplit(hyts_std_path: str, working_dir: str):
    print("📦 hyts_std 실행 중...")
    hyts_result = subprocess.run(
        [hyts_std_path],
        cwd=working_dir,
        capture_output=True,
        text=True
    )

    print("📤 hyts_std stdout:\n", hyts_result.stdout)
    print("⚠️ hyts_std stderr:\n", hyts_result.stderr)

    if hyts_result.returncode == 0:
        print("✅ HYSPLIT 실행 완료! tdump 생성됨.")
        return True
    else:
        print("❌ hyts_std 실행 실패")
        return False

def run_arw2arl_and_hysplit_range(start_time: datetime, end_time: datetime):
    wrf_base_path = "/home/yjtech/WRFmodel/WRF/test/em_real"
    arw2arl_path = "/home/yjtech/hysplit/exec/arw2arl"
    hyts_std_path = "/home/yjtech/hysplit/exec/hyts_std"
    working_dir = "/home/yjtech/hysplit/working"

    # CONTROL 파일 확인
    control_path = os.path.join(working_dir, "CONTROL")
    if not os.path.exists(control_path):
        print("❌ CONTROL 파일이 존재하지 않습니다. 먼저 생성해주세요.")
        return

    if not convert_wrfout_to_arldata(start_time, end_time, wrf_base_path, arw2arl_path):
        print("❌ ARLDATA.BIN 생성 실패. 중단합니다.")
        return

    run_hysplit(hyts_std_path, working_dir)
