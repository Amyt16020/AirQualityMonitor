import cv2
import numpy as np

# 載入預訓練模型
model_path = "frozen_east_text_detection.pb"
net = cv2.dnn.readNet(model_path)

def detect_text(image):
    # 讀取影像並調整大小 (EAST 需要 32 的倍數)
    #image = cv2.imread(image_path)
    orig = image.copy()
    (H, W) = image.shape[:2]
    
    # 設定新的寬高 (Pi 4 建議不要太大，以免過慢)
    (newW, newH) = (320, 320)
    rW = W / float(newW)
    rH = H / float(newH)
    image = cv2.resize(image, (newW, newH))

    # 定義 EAST 模型輸出的兩層名稱
    layerNames = ["feature_fusion/Conv_7/Sigmoid", "feature_fusion/concat_3"]

    # 將影像轉換為 Blob
    blob = cv2.dnn.blobFromImage(image, 1.0, (newW, newH),
                                 (123.68, 116.78, 103.94), swapRB=True, crop=False)
    net.setInput(blob)
    (scores, geometry) = net.forward(layerNames)

    # 取得偵測結果
    (numRows, numCols) = scores.shape[2:4]
    rects = []
    confidences = []

    for y in range(0, numRows):
        scoresData = scores[0, 0, y]
        xData0 = geometry[0, 0, y]
        xData1 = geometry[0, 1, y]
        xData2 = geometry[0, 2, y]
        xData3 = geometry[0, 3, y]
        anglesData = geometry[0, 4, y]

        for x in range(0, numCols):
            if scoresData[x] < 0.5: # 信心度門檻
                continue

            # 計算偏移量與座標
            (offsetX, offsetY) = (x * 4.0, y * 4.0)
            angle = anglesData[x]
            cos = np.cos(angle)
            sin = np.sin(angle)
            h = xData0[x] + xData2[x]
            w = xData1[x] + xData3[x]

            endX = int(offsetX + (cos * xData1[x]) + (sin * xData2[x]))
            endY = int(offsetY - (sin * xData1[x]) + (cos * xData2[x]))
            startX = int(endX - w)
            startY = int(endY - h)

            rects.append((startX, startY, endX, endY))
            confidences.append(scoresData[x])

    # 套用非極大值抑制 (NMS) 移除重疊的框
    from cv2.dnn import NMSBoxes
    indices = NMSBoxes(rects, confidences, 0.5, 0.4)

    for i in indices:
        box = rects[i]
        startX, startY, endX, endY = box
        
        # 縮放回原始影像尺寸
        startX = int(startX * rW)
        startY = int(startY * rH)
        endX = int(endX * rW)
        endY = int(endY * rH)

        cv2.rectangle(orig, (startX, startY), (endX, endY), (0, 255, 0), 2)

    #cv2.imshow("Text Detection", orig)
    #cv2.waitKey(0)
    return orig

#detect_text("test_image.jpg")
if __name__ == "__main__":
    image = cv2.imread("./test_data/20-36-33.png")
    image = detect_text(image)
    cv2.imshow("Text Detection", image)
    cv2.waitKey(0)
