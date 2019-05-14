# coding:utf-8
#Union.pyを使って、データセットを作成します。
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
random.seed("1234") #実験のため、ランダム要素を固定
#random.seed()
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

    RESIZE_RATE=10 #背景画像の幅サイズの何分の１にするか
    

    data=csv_read(RECIPE,"utf-8")
    
    # print ("フォーマット：label,minX,minY,maxX,maxY,path,file,name")

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
#下の処理はShellにやらせる    
# #アノテーションファイルの初期化
#     if(os.path.exists(ANNOTATION_FILE) and ( INIT is "true" or INIT is "True")):
#         os.remove(ANNOTATION_FILE)
    
#     #アノテーションファイルに記録
#     with open(ANNOTATION_FILE,"a") as f:
#         print >> f,"label,minX,minY,maxX,maxY,path,file,name"

    
#DetasetFactoryの設定ファイル読み込み
    config=csv_read(CONFIG,"utf-8")
    #print(config)
    config_rows={row[0]:{config[0][i]:row[i] for i in range(1,len(row))} for row in config[1:]}
    #print(config_rows)

#処理
    cnt=0
    i=1
    flag=0

    total = len(filter(lambda f: os.path.isfile(os.path.join(BACKGROUND_DIR, f)),
                        os.listdir(BACKGROUND_DIR)))
    # print(total)#背景画像数

    for j in range(1,total+1):
        if(flag==1):
            i+=1
            flag=0
        bak=Image.open(BACKGROUND_DIR+str(data[i][0]))
        bak_w,bak_h=bak.size
        #print(data[i][0])
        for image in glob.glob(TARGET_DIR+"*"):
            img=Image.open(image) 
            image_w,image_h=img.size
	    
            if os.path.basename(image) in config_rows:
                config_name=image
            else:
                config_name="default"
   		
	    #print(config_name)         
            # print(kernel)
            #横幅のサイズを再設定(高さ自動で調整される)
            resize=-1*(-1*bak_w//RESIZE_RATE) #切り上げ割り算
            tar_raito=float(resize)/image_w 

            #ターゲットが生成画像で見切れないように配置位置を調整。その際、配置領域より画像のほうが大きい場合も考慮
            #同じ背景画像に複数の領域が指定されているときは、それも考慮。重複して画像が生成されないようにする

	    """
            if(str(data[i][0])==str(data[i+1][0])):
                #X(幅)
                if(random.choice([0,1])==0):
                    if(int(data[i][3])-resize>int(data[i][1])):
                        X=random.randint(int(data[i][1]),int(data[i][3])-resize)
                    else:
                        #X=int(data[i][3])-resize
			X=int(data[i][1])
                else:
                    if(int(data[i+1][3])-resize>int(data[i+1][1])):
                        X=random.randint(int(data[i+1][1]),int(data[i+1][3])-resize)
                    else:
                        #X=int(data[i+1][3])-resize
			X=int(data[i+1][1])
                #Y(高さ)
                if(random.choice([0,1])==0):
                    if(int(data[i][4])-image_h*tar_raito>int(data[i][2])):
                        Y=random.randint(int(data[i][2]),int(data[i][4])-int(image_h*tar_raito))
                    else:
                        Y=int(data[i][4])-int(image_h*tar_raito)
                else:
                    if(int(data[i+1][4])-image_h*tar_raito>int(data[i+1][2])):
                        Y=random.randint(int(data[i+1][2]),int(data[i+1][4])-int(image_h*tar_raito))
                    else:
                        Y=int(data[i][4])-int(image_h*tar_raito)
            else:
                #X
                if(int(data[i][3])-resize>int(data[i][1])):
                    X=random.randint(int(data[i][1]),int(data[i][3])-resize)
                else:
                    X=int(data[i][3])-resize
                #Y
                if(int(data[i][4])-image_h*tar_raito>int(data[i][2])):
                    Y=random.randint(int(data[i][2]),int(data[i][4])-int(image_h*tar_raito))
                else:
                    Y=int(data[i][4])-int(image_h*tar_raito)  
	      
	    """

	    #X
            if(int(data[i][3])-resize>int(data[i][1])):
                X=random.randint(int(data[i][1]),int(data[i][3])-resize)
            elif (int(data[i][3])-resize>=0):
                X=int(data[i][3])-resize
            else:
                X=0

            #Y
            if(int(data[i][4])-image_h*tar_raito>int(data[i][2])):
                Y=random.randint(int(data[i][2]),int(data[i][4])-int(image_h*tar_raito))
            elif (int(data[i][4])-int(image_h*tar_raito)>=0):
                Y=int(data[i][4])-int(image_h*tar_raito)
            else:
                Y=0

	
	    if(str(data[i][0])==str(data[i+1][0])):
		if(random.choice([0,1])==0):
                    #X(幅)
                    if(int(data[i+1][3])-resize>int(data[i+1][1])):
                        X=random.randint(int(data[i+1][1]),int(data[i+1][3])-resize)
                    elif (int(data[i+1][3])-resize>=0):
                        X=int(data[i+1][3])-resize
		    else:
			X=0
                        
                    #Y(高さ)
                    if(int(data[i+1][4])-image_h*tar_raito>int(data[i+1][2])):
                        Y=random.randint(int(data[i+1][2]),int(data[i+1][4])-int(image_h*tar_raito))
                    elif (int(data[i+1][4])-int(image_h*tar_raito)>=0):
                        Y=int(data[i+1][4])-int(image_h*tar_raito) 
		    else :
			Y=0

               


            #合成開始
            out,tar_h,tar_w=Union(
                label_name=LABEL,
                bak=BACKGROUND_DIR+str(data[i][0]),tar=image,
                X=X,Y=Y,
                resize=tar_raito,
                SharpBackground=bool(int(config_rows[config_name]["SharpBackground"])),
                SepiaAll=bool(int(config_rows[config_name]["SepiaAll"])),
                Brightness_mode=str(config_rows[config_name]["Brightness_mode"]),
                Extraction_mode=str(config_rows[config_name]["Extraction_mode"]),
                dilate=int(config_rows[config_name]["dilate"]),erode=int(config_rows[config_name]["erode"]),
                Random_rotation=bool(int(config_rows[config_name]["Random_rotation"])),
                angle=int(config_rows[config_name]["angle"]),
                R=int(config_rows[config_name]["R"]),G=int(config_rows[config_name]["G"]),B=int(config_rows[config_name]["B"]),
                Threshold=int(config_rows[config_name]["Threshold"]),
                brightness=float(config_rows[config_name]["brightness"]),
                BilateralFilter=int(config_rows[config_name]["BilateralFilter"]),
                GausianFilter=int(config_rows[config_name]["GausianFilter"]),
                HideNum=int(config_rows[config_name]["HideNum"]),
                x1_Ho=int(config_rows[config_name]["x1_Ho"]),y1_Ho=int(config_rows[config_name]["y1_Ho"]),
                x2_Ho=int(config_rows[config_name]["x2_Ho"]),y2_Ho=int(config_rows[config_name]["y2_Ho"]),
                x3_Ho=int(config_rows[config_name]["x3_Ho"]),y3_Ho=int(config_rows[config_name]["y3_Ho"]),
                x4_Ho=int(config_rows[config_name]["x4_Ho"]),y4_Ho=int(config_rows[config_name]["y4_Ho"]),
                flips=int(config_rows[config_name]["flips"]),
                amount=float(config_rows[config_name]["amount"]),
                sp_ratio=float(config_rows[config_name]["sp_ratio"]),
                mean=float(config_rows[config_name]["mean"]),
                sigma=int(config_rows[config_name]["sigma"]),
                kernel=int(config_rows[config_name]["kernel"]),
		perspective=int(config_rows[config_name]["perspective"])
                )
            #アノテーションファイルに記録
            with open(ANNOTATION_FILE,"a") as f:
                print >> f,LABEL+","+str(X)+","+str(Y)+","+str(X+tar_w)+","+str(Y+tar_h)+","+OUTPUT_DIR+"out_label_"+str(LABEL)+"_"+str(cnt)+".jpg,out_label_"+str(LABEL)+"_"+str(cnt)+".jpg,"+str(NAME)
            
            #合成画像の書き出し
            out.save(OUTPUT_DIR+"out_label_"+str(LABEL)+"_"+str(cnt)+".jpg",quality=95)
            cnt+=1
        if(str(data[i][0])==str(data[i+1][0])):#もし同じ背景画像が次も続くなら
            flag=1
        i+=1


    shutil.rmtree("./tmp") #一時ファイルの削除

if __name__=='__main__':
    tf.app.run()
