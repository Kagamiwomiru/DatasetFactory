#!/usr/bin/env python
# coding: utf-8
# # データ拡張します。

from sklearn import preprocessing
from tqdm import tqdm, trange
import tensorflow as tf
import cv2
from PIL import Image, ImageDraw, ImageFilter
import matplotlib.pyplot as plt
import numpy as np
import os
import shutil
import csv
from Union import csv_read
import sys
from ToolKit import KSImageKit as KS
from ToolKit import KagamiDevKit as KD
import glob

# コマンドライン引数
tf.app.flags.DEFINE_string("input_dir", "./", "入力画像ディレクトリ")
tf.app.flags.DEFINE_string("output_dir", "./", "出力ディレクトリ")
tf.app.flags.DEFINE_string(
    "annotation", "./annotation.csv", "アノテーションファイル(.csv")
tf.app.flags.DEFINE_bool("debug_mode", False, "デバッグモードを有効にする")


def main(_):

    # コマンドライン引数

    flags = tf.app.flags.FLAGS

    #イニシャライズ#
    # 入力ディレクトリ
    INPUT_DIR = flags.input_dir
    # 出力ディレクトリ
    OUTPUT_DIR = flags.output_dir
    # アノテーションファイル
    ANNOTATION_FILE = flags.annotation
    # tmpディレクトリ
    tmp_dir = "/home/kagamiwomiru/datasets/ProjectDatasetFactory/tmp/"

    image_data = csv_read(ANNOTATION_FILE, "utf-8")

    print("画像を削除中...")
    if(os.path.isdir(tmp_dir)):
        shutil.rmtree(tmp_dir)
    os.mkdir(tmp_dir)
    os.mkdir(OUTPUT_DIR)

    # 画像データ読み込み
    # print("画像を読み込み中")
    # KS.size_unification(
    #     input_dir=INPUT_DIR, output_dir=tmp_dir, size=50, mode='edge', isdebug=flags.debug_mode)

    print("画像縮小中")
    # KS.size_unification(
    #   input_dir=INPUT_DIR, output_dir=OUTPUT_DIR, size=50, mode='edge', isdebug=flags.debug_mode)
    cnt = 0
    AG_img = []
    CSV_data = KD.csv_read(ANNOTATION_FILE, "utf-8")
    for img in tqdm(CSV_data[1:]):
        cnt += 1
        KD.Debug_Print(img, isDebug=flags.debug_mode)
        KS.image_square(img[5], tmp_dir, deko=str(
            cnt), size=50, mode='edge')  # 画像を正方形にする。tmp_dir+0.jpg



        #アノテーション書き出し準備 ここから
        img_ag = OUTPUT_DIR+str(cnt)+".jpg" #AG画像保存先
        org = plt.imread(img[5])  # 元画像を読み込み
        org = np.asarray(org)
        tiny = plt.imread(tmp_dir+str(cnt)+".jpg")  # 縮小画像読み込み
        tiny = np.asarray(tiny)
        tiny.flags.writeable = True
        tinyShape = [0] * 3
        for i in range(0, 2):
            tinyShape[i] = org.shape[i] / tiny.shape[i]

        min_x = int(img[1]) / tinyShape[1]
        min_y = int(img[2]) / tinyShape[0]
        max_x = int(img[3]) / tinyShape[1]
        max_y = int(img[4]) / tinyShape[0]

        AG_annotation_data = [0]*8  # [0,0,0,0,0,0,0,0]を作成
        AG_annotation_data[0] = img[0]
        AG_annotation_data[1] = str(min_x)
        AG_annotation_data[2] = str(min_y)
        AG_annotation_data[3] = str(max_x)
        AG_annotation_data[4] = str(max_y)
        AG_annotation_data[5] = img_ag
        AG_annotation_data[6] = str(cnt)+".jpg"
        AG_annotation_data[7] = img[7]

        AG_img.append(AG_annotation_data)
        shutil.move(tmp_dir+str(cnt)+".jpg",img_ag)

  
    annotationMaker(ANNOTATION_FILE, array=AG_img)

    # In[8]:

    # ImageData = KS.LoadData_LikeCifar10(tmp_dir)
    # x_train = ImageData.astype('float32') / 255

    # x_train_std = np.zeros(x_train.shape)
    # print("正規化中...")
    # for i in trange(0, x_train.shape[0]):
    #     for j in trange(0, x_train.shape[3]):
    #         x_train_std[i, :, :, j] = preprocessing.scale(x_train[i, :, :, j])
    #     plt.imsave(OUTPUT_DIR+"norm_"+str(i)+"_.jpg",normalizeImage(x_train_std[i]))

    # print("ZCA白色化中...")
    # x_zcaw = x_train.reshape(x_train.shape[0], -1)
    # zcaw = ZCAWhitening().fit(x_zcaw)
    # x_zcaw = zcaw.transform(x_zcaw).reshape(x_train.shape)

    # cnt=0
    # for x_zcaws in x_zcaw:
    #     plt.imsave(OUTPUT_DIR+"zcaw_"+str(i)+"_.jpg",normalizeImage(x_train_std[i,:,:,:]))
    #     cnt+=1


def annotationMaker(annotation, array):
    '''
    アノテーションデータに１行追記します。

    Parameter
    ---------
    annotation  : str
      アノテーションファイルパス(csv)

    array : array
      １行分の追記するデータ
    '''

    # KD.csv_read(annotation,encoding="utf-8")
    # アノテーションファイルに記録
    s=annotation
    annotation_AG=s.replace('.csv','_AG.csv')
    shutil.copyfile(annotation, annotation_AG)
    for data in array:
        with open(annotation_AG, "a") as f:
            print >> f, data[0]+","+data[1]+","+data[2]+","+data[3]+","+data[4]+","+data[5]+","+data[6]+","+data[7]



class ZCAWhitening:
    def __init__(self, epsilon=1E-6):
        self.epsilon = epsilon
        self.mean = None
        self.zca = None

    def fit(self, x):
        with tqdm(total=100) as pbar:
            self.mean = np.mean(x, axis=0)
            pbar.update(15)
            x_ = x - self.mean
            pbar.update(15)
            cov = np.dot(x_.T, x_) / x_.shape[0]
            pbar.update(15)
            E, D, _ = np.linalg.svd(cov)
            pbar.update(15)
            D = np.sqrt(D) + self.epsilon
            pbar.update(15)
            self.zca = np.dot(E, np.dot(np.diag(1.0 / D), E.T))
            pbar.update(25)

        return self

    def transform(self, x):
        x_ = x - self.mean
        return np.dot(x_, self.zca.T)


# source:http://kikei.github.io/ai/2018/03/28/cifar10-whitening.html
# 正規化したデータを画像化する。
def normalizeMinMax(x, axis=0, epsilon=1E-5):
    vmin = np.min(x, axis)
    vmax = np.max(x, axis)
    return (x - vmin) / (vmax - vmin + epsilon)


def normalizeImage(x):
    img = x.reshape(x.shape[0] * x.shape[1], x.shape[2])
    img = normalizeMinMax(img, axis=0)
    return img.reshape(x.shape)


if __name__ == "__main__":
    tf.app.run()
