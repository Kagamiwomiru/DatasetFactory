# coding: utf-8
# Union.pyを使って、データセットを作成します。
from Union  import *
import glob
from PIL import Image
import sys
import random
import os
import shutil
import tensorflow as tf
#コマンドライン引数
flags = tf.app.flags

flags.DEFINE_string('recipe_file','./GetPoint.csv','GetPoint.pyで作成した、ターゲットの配置場所がかかれているCSVファイル')
flags.DEFINE_string('annotation_file','./annotation.csv','アノテーションファイル')
flags.DEFINE_string('init',"true",'実行時にアノテーションファイルを初期化するか? ')
flags.DEFINE_string('label','?','ラベルid')
flags.DEFINE_string('Background_dir','./Background/','背景画像が入ったディレクトリ')
flags.DEFINE_string('Target_dir','./Target/','前景画像が入ったディレクトリ')
flags.DEFINE_string('Output_dir','./Output/','出力ディレクトリ')
flags.DEFINE_string('name','???','クラス名(cat,dog,など)')
flags.DEFINE_string('config','./dataset.csv','合成方法の設定ファイル')

FLAGS = flags.FLAGS

def main(_):
# 設定

    RECIPE=FLAGS.recipe_file
    LABEL=FLAGS.label
    BACKGROUND_DIR=FLAGS.Background_dir
    TARGET_DIR=FLAGS.Target_dir
    OUTPUT_DIR=FLAGS.Output_dir
    ANNOTATION_FILE=FLAGS.annotation_file
    INIT=FLAGS.init
    NAME=FLAGS.name
    CONFIG=FLAGS.config

    RESIZE_RATE=8 #背景画像の幅サイズの何分の１にするか
    data=csv_read(RECIPE,"utf-8")

    print ("フォーマット：label,minX,minY,maxX,maxY,path,file,name")

#一時ディレクトリの作成
    if(os.path.isdir("./tmp")):
        None
    else:   
         os.mkdir("./tmp")

#出力ディレクトリの作成

    if(os.path.isdir(OUTPUT_DIR)):
        None
    else:
        os.mkdir(OUTPUT_DIR)
        
#アノテーションファイルの初期化
    if(os.path.exists(ANNOTATION_FILE) and ( INIT is "true" or INIT is "True")):
        os.remove(ANNOTATION_FILE)

    
#DetasetFactoryの設定ファイル読み込み
    config=csv_read(CONFIG,"utf-8")
    config_rows={row[0]:row[1:] for row in config[1:]}
    

#処理
    cnt=0
    for i in range(1,len(data)):
        bak=Image.open(BACKGROUND_DIR+str(data[i][0]))
        bak_w,bak_h=bak.size
        for image in glob.glob(TARGET_DIR+"*"):
            img=Image.open(image) 
            image_w,image_h=img.size

            if os.path.basename(image) in config_rows:
                SharpBackground,SepiaAll,Brightness_mode,Extraction_mode, \
                dilate,erode,angle,R,G,B,Threshold,brightness,BilateralFilter, \
                GausianFilter,HideNum,x1_Ho,y1_Ho,x2_Ho,y2_Ho,x3_Ho,y3_Ho,x4_Ho,y4_Ho, \
                flips,amount,sp_ratio,mean,sigma,kernel=config_rows[os.path.basename(image)]

            else:
                SharpBackground,SepiaAll,Brightness_mode,Extraction_mode, \
                dilate,erode,angle,R,G,B,Threshold,brightness,BilateralFilter, \
                GausianFilter,HideNum,x1_Ho,y1_Ho,x2_Ho,y2_Ho,x3_Ho,y3_Ho,x4_Ho,y4_Ho, \
                flips,amount,sp_ratio,mean,sigma,kernel=config_rows["default"]

            print(kernel)
            #横幅のサイズを再設定(高さ自動で調整される)
            resize=-1*(-1*bak_w//RESIZE_RATE) #切り上げ割り算
            tar_raito=float(resize)/image_w 

            #ターゲットが生成画像で見切れないように配置位置を調整。その際、配置領域より画像のほうが大きい場合も考慮
            if(int(data[i][3])-resize>int(data[i][1])):#X(幅)
                X=random.randint(int(data[i][1]),int(data[i][3])-resize)
            else:
                X=int(data[i][3])-resize

            if(int(data[i][4])-image_h*tar_raito>int(data[i][2])):#Y(高さ)
                Y=random.randint(int(data[i][2]),int(data[i][4])-int(image_h*tar_raito))
            else:
                Y=int(data[i][4])-int(image_h*tar_raito)
    
            #合成開始
            out,tar_h,tar_w=Union(
                label_name=LABEL,
                bak=BACKGROUND_DIR+str(data[i][0]),tar=image,
                X=X,Y=Y,
                resize=2,
                SharpBackground=bool(int(SharpBackground)),
                SepiaAll=bool(int(SepiaAll)),
                Brightness_mode=str(Brightness_mode),
                Extraction_mode=str(Extraction_mode),
                dilate=int(dilate),erode=int(erode),
                angle=int(angle),
                R=int(R),G=int(G),B=int(B),
                Threshold=int(Threshold),
                brightness=float(brightness),
                BilateralFilter=int(BilateralFilter),
                GausianFilter=int(GausianFilter),
                HideNum=int(HideNum),
                x1_Ho=int(x1_Ho),y1_Ho=int(y1_Ho),x2_Ho=int(x2_Ho),y2_Ho=int(y2_Ho),x3_Ho=int(x3_Ho),y3_Ho=int(y3_Ho),x4_Ho=int(x4_Ho),y4_Ho=int(y4_Ho),
                flips=int(flips),
                amount=float(amount),
                sp_ratio=float(sp_ratio),
                mean=int(mean),
                sigma=int(sigma),
                kernel=int(kernel)
                )
            #アノテーションファイルに記録
            with open(ANNOTATION_FILE,"a") as f:
                print >> f,LABEL+","+str(X)+","+str(Y)+","+str(X+tar_w)+","+str(Y+tar_h)+","+OUTPUT_DIR+"out_"+str(cnt)+"label_"+str(LABEL)+".jpg,out_"+str(cnt)+"label_"+str(LABEL)+".jpg,"+str(NAME)
            
            #合成画像の書き出し
            out.save(OUTPUT_DIR+"out_"+str(cnt)+"label_"+str(LABEL)+".jpg",quality=95)
            cnt+=1

    shutil.rmtree("./tmp") #一時ファイルの削除

if __name__=='__main__':
    tf.app.run()