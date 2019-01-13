# coding: utf-8
# Copyright (c) 2019  Shotaro Ishigami
# 自然画像に対してアノテーションデータを作成します。（合成画像はこのツールを使わず生成できます）
import matplotlib
matplotlib.use('TkAgg')
import os
import csv
import sys
import argparse
from matplotlib.widgets import TextBox
import glob
import matplotlib.pyplot as plt
from PIL import Image
import pylab
import numpy as np

parser = argparse.ArgumentParser(
    description='自然画像に対してアノテーションデータを作成します。（合成画像はこのツールを使わず生成できます）')
parser.add_argument('img_dir', help='自然画像があるディレクトリ')
parser.add_argument('-O', '--output', help='出力先(デフォルト:./annotation.csv)')
args = parser.parse_args()

output_path = "./annotation.csv"
if(args.output is not None):
    output_path = args.output


FLAG = False
resize_width = 600  # 横幅600pxにリサイズ


files = glob.glob(args.img_dir+"*.jpg")
print("全ての背景画像を"+str(resize_width)+"pxにリサイズ中...")
for f in files:
    img = Image.open(f)
    resize_rate = float(resize_width)/img.width
    # print(resize_rate)

    img_resize = img.resize(
        (int(img.width*resize_rate), int(img.height*resize_rate)))
    img_resize.save(f)


with open(output_path, 'w') as f:
    writer = csv.writer(f)
    writer.writerow(['label', 'minX', 'minY', 'maxX',
                     'maxY', 'path', 'file', 'name'])


def onclick(event):
    global x1, y1, FLAG
    print("click")
    try:
        FLAG = True
        x1 = int(round(event.xdata))
        y1 = int(round(event.ydata))
    except:
        return


def ondrag(event):
    global x1, x2, y1, y2, x, y, FLAG
    if FLAG == False:
        return
    try:
        x2 = int(round(event.xdata))
        y2 = int(round(event.ydata))
        drawRect()
        plt.draw()
    except:
        return


def onkey(event):
    global x1, y1, x2, y2

    if event.key == 'e':
        print("DEBUG:データを保存します")
        x1, x2 = sorted([x1, x2])
        y1, y2 = sorted([y1, y2])
        data.append([label, x1, y1, x2, y2, filepath, base, label])
        # print(data)

    if event.key == 'q':
        print('DEBUG:現在の画像を終了します')
        if data:
            with open(output_path, 'a') as f:
                writer = csv.writer(f)
                for i in data:
                    writer.writerow(i)
        plt.close()


def onrelease(event):
    global FLAG
    FLAG = False


def drawRect():
    global x1, y1, x2, y2
    Rect = [[[x1, x2], [y1, y1]],
            [[x2, x2], [y1, y2]],
            [[x1, x2], [y2, y2]],
            [[x1, x1], [y1, y2]]]
    for i, rect in enumerate(Rect):
        lns[i].set_data(rect[0], rect[1])


def input_label_name(text):
    global label
    label = text


def input_img_name(text):
    global img_name
    img_name = text


label = '?'
img_name = '???'
print("e:内容を記録")
print("q:次の画像")

#ユーザ操作開始
try:
    for images in glob.glob(args.img_dir+"*"):
        print("DEBUG:"+images)
        x1 = 0
        y1 = 0
        x2 = 0
        y2 = 0

        data = []
        base = os.path.basename(images)
        filepath = os.path.abspath(images)
        image = Image.open(images)
        image_list = np.asarray(image)

        plt.figure()
        plt.subplot(1, 1, 1)

        Rect = [[[x1, x2], [y1, y1]],
                [[x2, x2], [y1, y2]],
                [[x1, x2], [y2, y2]],
                [[x1, x1], [y1, y2]]]

        lns = []

        for rect in Rect:
            ln, = plt.plot(rect[0], rect[1], color='r', lw=2)
            lns.append(ln)

        plt.connect('button_press_event', onclick)
        plt.connect('motion_notify_event', ondrag)
        plt.connect('button_release_event', onrelease)
        plt.connect('key_press_event', onkey)

        plt.title(images)
        im = plt.imshow(image_list)
        plt.clim(im.get_clim())
        plt.axis('off')
        # テキストボックス
        box1 = plt.axes([0.1, 0.05, 0.8, 0.04])
        # box2 = plt.axes([0.1, 0, 0.8, 0.04])
        label_box = TextBox(box1, 'Label', initial="")
        # imgName_box=TextBox(box2,'ImageName',initial="")
        label_box.on_submit(input_label_name)
        # imgName_box.on_submit(input_img_name)

        plt.show()
except KeyboardInterrupt:
    print("強制終了")
    sys.exit(0)