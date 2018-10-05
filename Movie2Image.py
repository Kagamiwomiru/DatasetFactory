# coding: utf-8
# # 動画から画像を作ります。
# 引数で画像の生成頻度を変更できます。（X秒毎)
import cv2
import os,glob
import shutil
import sys

def video_2_frames(video_file=None, image_dir=None,sec=0.03,fps=30,cnt=None):


    # 画像抽出開始
    if(cnt==None):
        i = 0 #画像数

    frame_cnt=0 #フレーム画像数
    
#     秒数をフレームに変換
    num=float(sec)*fps
    print("*----設定----*")
    print("頻度:"+str(sec)+"秒")
    print("FPS:"+str(fps))
    print("フレーム頻度:"+str(num))
    print("*------------*")
#     動画読み込み
    cap = cv2.VideoCapture(video_file)
    
    while(cap.isOpened()):
        flag, frame = cap.read()  # 画像取得
        if flag == False:  # Is a frame left?
            break
        if frame_cnt % num==0:
            imgName=image_dir+"out_"+str(cnt)+".jpg"
            cv2.imwrite(imgName,frame)
            print("保存中："+str(imgName))
            cnt+=1
        frame_cnt += 1

    cap.release()  # When everything done, release the capture
    return cnt 



if __name__=='__main__':

    args=sys.argv
    if(len(args)!=4):
        print("使い方：python Movie2Image.py 動画ディレクトリ 出力先ディレクトリ　頻度(秒数指定)")
        sys.exit(1)

    video_dir=args[1]
    output_dir=args[2]
    sec=args[3]

    # Make the directory if it doesn't exist.
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
       
    cnt=0
    for movie in glob.glob(video_dir+"*.mp4"):

        cnt=video_2_frames(movie,image_dir=output_dir,sec=sec,cnt=cnt)

