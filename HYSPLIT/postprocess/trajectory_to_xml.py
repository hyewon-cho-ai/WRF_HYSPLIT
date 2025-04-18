import xml.etree.ElementTree as ET
from datetime import datetime
import os

def parse_tdump_to_xml(tdump_path, output_path, area="10001"):
    data_points = []

    with open(tdump_path, 'r') as f:
        for line in f:
            parts = line.strip().split()
            if len(parts) >= 11 and parts[0].isdigit():
                try:
                    year = int(parts[3]) + 2000  # 2-digit year to 4-digit
                    month = int(parts[4])
                    day = int(parts[5])
                    hour = int(parts[6])
                    minute = int(parts[7])
                    lat = float(parts[8])
                    lon = float(parts[9])
                    # alt = float(parts[10])  # 필요하면 추가 가능

                    timestamp = f"{year:04d}-{month:02d}-{day:02d} {hour:02d}:{minute:02d}"
                    data_points.append({
                        "time": timestamp,
                        "lat": lat,
                        "lon": lon
                    })
                except ValueError:
                    continue

    if not data_points:
        print("❌ 추출된 데이터가 없습니다.")
        return

    # XML 생성
    root = ET.Element("backTraject")

    header = ET.SubElement(root, "header")
    ET.SubElement(header, "dataNum").text = str(len(data_points))
    ET.SubElement(header, "area").text = area
    ET.SubElement(header, "trajectoryHour").text = str(len(data_points) - 1)
    ET.SubElement(header, "traject").text = "-1"
    ET.SubElement(header, "LON").text = str(data_points[0]["lon"])
    ET.SubElement(header, "LAT").text = str(data_points[0]["lat"])

    body = ET.SubElement(root, "body")
    for idx, data in enumerate(data_points):
        d = ET.SubElement(body, "data", seq=str(idx))
        ET.SubElement(d, "TIME").text = data["time"]
        ET.SubElement(d, "LON").text = str(data["lon"])
        ET.SubElement(d, "LAT").text = str(data["lat"])

    tree = ET.ElementTree(root)
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    tree.write(output_path, encoding='utf-8', xml_declaration=True)

    print(f"✅ XML 변환 완료: {output_path}")
