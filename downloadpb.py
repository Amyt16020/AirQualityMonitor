import urllib.request
import os

url = "https://raw.githubusercontent.com/oyyd/frozen_east_text_detection.pb/master/frozen_east_text_detection.pb"
filename = "frozen_east_text_detection.pb"

if not os.path.exists(filename):
    print(f"正在下載模型檔案至 {filename}...")
    urllib.request.urlretrieve(url, filename)
    print("下載完成！")
else:
    print("模型檔案已存在。")