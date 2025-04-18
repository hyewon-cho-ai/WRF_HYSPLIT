import datetime
import subprocess


# 시간을 3의 배수로 수정하는 함수
def adjust_to_nearest_multiple_of_3(time_obj, round_up=True):
    hour = time_obj.hour
    remainder = hour % 3
    if remainder != 0:
        if round_up:
            time_obj += datetime.timedelta(hours=(3 - remainder))
        else:
            time_obj -= datetime.timedelta(hours=remainder)
    return time_obj


def modify_namelist_wps(start_date_str, end_date_str):
    current_time = datetime.datetime.now()
    start_date = datetime.datetime.strptime(start_date_str, "%Y-%m-%d_%H")
    end_date = datetime.datetime.strptime(end_date_str, "%Y-%m-%d_%H")

    start_date = adjust_to_nearest_multiple_of_3(start_date, round_up=False)
    end_date = adjust_to_nearest_multiple_of_3(end_date, round_up=True)

    start_date_str = start_date.strftime("%Y-%m-%d_%H:00:00")
    end_date_str = end_date.strftime("%Y-%m-%d_%H:00:00")

    namelist_path = "/home/yjtech/WRFmodel/WPS/namelist.wps"

    with open(namelist_path, 'r') as file:
        lines = file.readlines()

    for i, line in enumerate(lines):
        if "start_date" in line:
            lines[i] = f" start_date = '{start_date_str}',\n"
        if "end_date" in line:
            lines[i] = f" end_date = '{end_date_str}',\n"

    with open(namelist_path, 'w') as file:
        file.writelines(lines)

    print(f"namelist.wps modified. start_date = {start_date_str}, end_date = {end_date_str}")


def run_link_grib():
    print("Running link_grib.csh...")
    grib_data_path = "/home/yjtech/WRFmodel/geog_data/GFS"
    subprocess.run([f"./link_grib.csh {grib_data_path}/*"], shell=True, check=True, cwd="/home/yjtech/WRFmodel/WPS")


def run_geogrid():
    print("Running geogrid.exe...")
    subprocess.run(["./geogrid.exe"], shell=True, check=True, cwd="/home/yjtech/WRFmodel/WPS")


def run_ungrib():
    print("Running ungrib.exe...")
    subprocess.run(["./ungrib.exe"], shell=True, check=True, cwd="/home/yjtech/WRFmodel/WPS")


def run_metgrid():
    print("Running metgrid.exe...")
    subprocess.run(["./metgrid.exe"], shell=True, check=True, cwd="/home/yjtech/WRFmodel/WPS")
