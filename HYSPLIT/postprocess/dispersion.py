import csv
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
from shapely.geometry import Point
import contextily as ctx
from pyproj import Transformer

# ====== STEP 1: tdump → CSV 변환 ======
input_path = "/home/yjtech/hysplit/output/tdump"
output_csv = "/home/yjtech/hysplit/output/pre_dispersion.csv"

output_data = []

with open(input_path, 'r') as f:
    lines = f.readlines()

for line in lines:
    parts = line.strip().split()
    if len(parts) >= 7 and parts[0].isdigit():
        hour = float(parts[3])
        lat = float(parts[4])
        lon = float(parts[5])
        alt = float(parts[6])
        output_data.append((hour, lat, lon, alt))

with open(output_csv, 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(["hour", "lat", "lon", "alt"])
    writer.writerows(output_data)

print("✅ tdump → CSV 변환 완료:", output_csv)

# ====== STEP 2: 포항 중심 시각화 ======
plt.rcParams.update({
    "font.size": 16,
    "legend.fontsize": 14,
    "axes.titlesize": 20,
})

df = pd.read_csv(output_csv)
geometry = [Point(xy) for xy in zip(df['lon'], df['lat'])]
gdf = gpd.GeoDataFrame(df, crs="EPSG:4326", geometry=geometry)
gdf = gdf.to_crs(epsg=3857)

# 포항 중심 영역 설정
lat_min, lat_max = 35.95, 36.15
lon_min, lon_max = 129.30, 129.60
transformer = Transformer.from_crs("EPSG:4326", "EPSG:3857", always_xy=True)
x_min, y_min = transformer.transform(lon_min, lat_min)
x_max, y_max = transformer.transform(lon_max, lat_max)

# 시각화
fig, ax = plt.subplots(figsize=(12, 12))
gdf.plot(ax=ax, color='red', markersize=50, alpha=0.8, label='Dispersion points')

# 안정적이고 고해상도로 잘 나오는 배경지도 (zoom=13)
ctx.add_basemap(ax, source=ctx.providers.CartoDB.Positron, zoom=12)

ax.set_xlim([x_min, x_max])
ax.set_ylim([y_min, y_max])
ax.set_title("HYSPLIT Dispersion (Pohang)", fontsize=20)
ax.legend()
ax.axis('off')

# 이미지 저장
output_img = "/home/yjtech/hysplit/output/dispersion_map_stable.png"
plt.savefig(output_img, bbox_inches='tight', dpi=600)
plt.show()

print("🗺️ 지도 저장 완료:", output_img)
