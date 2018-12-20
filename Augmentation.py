# coding: utf-8
#Copyright (c) 2018  Shotaro Ishigami
#作成した画像を更に増やします。

from Union import *
from UnionKit import *
import cv2
from PIL import Image, ImageDraw, ImageFilter
import numpy as np
import os
import csv

def count_files(in_directory):
    joiner= (in_directory + os.path.sep).__add__
    return sum(
        os.path.isfile(filename)
        for filename
        in map(joiner, os.listdir(in_directory))
    )
def darkmode(tar):
    img=cv2.imread(tar)
    h,w,_=img.shape

    blur=w/150
    if(blur%2==0):
        blur+=1

    img=TargetSmoothingBlur(img,blur)
    # display_cv_image(img)
    img=LensFilter(img,"blue",1)
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    pil=Image.fromarray(img)
    img=PIL_point(0.6,pil)
    #PILからOpenCVへ変換
    img = cv2.cvtColor(np.array(img),cv2.COLOR_BGR2RGB)
    img=ModChroma(img,5)

    img=OpenCV_gamma(0.6,img)
    return img

if __name__=='__main__':

    #入力ディレクトリ
    INPUT_DIR="./Output/"
    #出力ディレクトリ
    OUTPUT_DIR="./Output/"
    #アノテーションファイル
    ANNOTATION_FILE="./annotation.csv"

    image_data=csv_read(ANNOTATION_FILE,"utf-8")

    cnt=0
    for image in image_data:
        #夜っぽくする
        dst=darkmode(OUTPUT_DIR+str(image[5]))
        cv2.imwrite(OUTPUT_DIR+"dark_out_"+str(cnt)+".jpg",dark)
        label=image[0]
        xmin=image[1]
        ymin=image[2]
        xmax=image[3]
        ymax=image[4]
        filename="dark_out_"+str(cnt)+".jpg"
        with open("./annotation.bak.csv","a") as f:
            print >> f,label+","+str(xmin)+","+str(ymin)+","+str(xmax)+","+str(ymax)+","+filename
        cnt+=1
    
    print(str(count_files(OUTPUT_DIR))+" files")