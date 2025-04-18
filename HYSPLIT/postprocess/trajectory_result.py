import xml.etree.ElementTree as ET

xml_path = "/home/yjtech/hysplit/output/trajectory_result.xml"

tree = ET.parse(xml_path)
root = tree.getroot()

# 📌 header 정보 출력
print("\n📄 [Header]")
for child in root.find("header"):
    print(f"{child.tag}: {child.text}")

# 📌 trajectory body 일부 출력
print("\n[Body] 일부 좌표 데이터:")
for data in root.find("body").findall("data")[:5]:  # 처음 5개만 출력
    lat = data.find("LAT").text
    lon = data.find("LON").text
    print(f"▶ LAT: {lat}, LON: {lon}")