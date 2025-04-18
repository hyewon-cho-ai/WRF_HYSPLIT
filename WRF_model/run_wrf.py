import subprocess
import re
import time
from datetime import datetime
import threading
import os

WRF_RUN_DIR = "/home/yjtech/WRFmodel/WRF/test/em_real"
WPS_DIR = "/home/yjtech/WRFmodel/WPS"
NAMELIST_INPUT_PATH = f"{WRF_RUN_DIR}/namelist.input"
NAMELIST_WPS_PATH = f"{WPS_DIR}/namelist.wps"
RSL_FILE_PATH = os.path.join(WRF_RUN_DIR, "rsl.out.0000")
progress_stop_flag = False

def extract_times_from_namelist_wps():
    with open(NAMELIST_WPS_PATH, 'r') as f:
        content = f.read()
    start_match = re.search(r"start_date\s*=\s*'([\d\-_:]+)'", content)
    end_match = re.search(r"end_date\s*=\s*'([\d\-_:]+)'", content)
    if not (start_match and end_match):
        raise ValueError("start_date or end_date not found in namelist.wps")
    start_time = datetime.strptime(start_match.group(1), "%Y-%m-%d_%H:%M:%S")
    end_time = datetime.strptime(end_match.group(1), "%Y-%m-%d_%H:%M:%S")
    print(f"Start time: {start_time}, End time: {end_time}")
    return start_time, end_time

def update_namelist_times(start_time, end_time):
    print("Updating namelist.input time settings...")
    total_hours = int((end_time - start_time).total_seconds() // 3600)
    run_days = total_hours // 24
    run_hours = total_hours % 24

    with open(NAMELIST_INPUT_PATH, "r") as file:
        lines = file.readlines()

    def replace_time_value(line, key, value):
        if key in line:
            return f" {key:<35}= {value},\n"
        return line

    new_lines = []
    for line in lines:
        line = replace_time_value(line, "start_year", start_time.year)
        line = replace_time_value(line, "start_month", f"{start_time.month:02d}")
        line = replace_time_value(line, "start_day", f"{start_time.day:02d}")
        line = replace_time_value(line, "start_hour", f"{start_time.hour:02d}")
        line = replace_time_value(line, "end_year", end_time.year)
        line = replace_time_value(line, "end_month", f"{end_time.month:02d}")
        line = replace_time_value(line, "end_day", f"{end_time.day:02d}")
        line = replace_time_value(line, "end_hour", f"{end_time.hour:02d}")
        line = replace_time_value(line, "run_days", run_days)
        line = replace_time_value(line, "run_hours", run_hours)
        new_lines.append(line)

    with open(NAMELIST_INPUT_PATH, "w") as file:
        file.writelines(new_lines)

    print("namelist.input updated.")

def link_met_files():
    print("Linking met_em.d0* files...")
    subprocess.run("rm -f met_em.d0*", shell=True, cwd=WRF_RUN_DIR)
    subprocess.run(f"ln -s {WPS_DIR}/met_em.d0* .", shell=True, cwd=WRF_RUN_DIR, check=True)
    print("met_em.d0* linking complete.")

def monitor_progress(start_time, end_time):
    print("Monitoring wrf.exe progress...")
    global progress_stop_flag
    last_progress = -1
    while not progress_stop_flag:
        if os.path.exists(RSL_FILE_PATH):
            with open(RSL_FILE_PATH, "r") as f:
                lines = f.readlines()
                lines.reverse()
                for line in lines:
                    if "Timing for main:" in line:
                        match = re.search(r"time\s+(\d{4}-\d{2}-\d{2}_\d{2}:\d{2}:\d{2})", line)
                        if match:
                            current_time = datetime.strptime(match.group(1), "%Y-%m-%d_%H:%M:%S")
                            total = (end_time - start_time).total_seconds()
                            elapsed = (current_time - start_time).total_seconds()
                            percent = max(0, min(100, int((elapsed / total) * 100)))
                            if percent != last_progress:
                                print(f"Progress: {percent}%")
                                last_progress = percent
                        break
        time.sleep(5)

def run_executable_with_log(executable_name, start_time=None, end_time=None):

    print(f"Running {executable_name}...")
    start = time.time()

    monitor_thread = None
    global progress_stop_flag
    if executable_name == "wrf.exe" and start_time and end_time:
        progress_stop_flag = False
        monitor_thread = threading.Thread(target=monitor_progress, args=(start_time, end_time))
        monitor_thread.start()

    # ✅ 환경 변수 설정: OMP_NUM_THREADS
    env = os.environ.copy()
    env["OMP_NUM_THREADS"] = "3"

    # ✅ wrf.exe는 병렬 실행, real.exe는 단일 실행
    if executable_name == "wrf.exe":
        command = f"mpirun -np 4 ./{executable_name}"
    else:
        command = f"./{executable_name}"

    process = subprocess.Popen(
        command,
        cwd=WRF_RUN_DIR,
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        universal_newlines=True,
        bufsize=1,
        env=env  # 🧠 환경변수 적용
    )

    for line in process.stdout:
        print(line.strip())

    process.wait()
    end = time.time()

    if executable_name == "wrf.exe" and monitor_thread:
        progress_stop_flag = True
        monitor_thread.join()

    if process.returncode != 0:
        print(f"{executable_name} failed.")
        exit(1)

    print(f"{executable_name} completed in {end - start:.2f} seconds.")
