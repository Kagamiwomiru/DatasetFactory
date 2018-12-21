# coding: utf-8
#Copyright (c) 2018  Shotaro Ishigami
# 画像を合成します。
from UnionKit import *
import csv
import cv2


#bak：背景画像
#tar：前景画像（ターゲット）
#これより下の引数は省略できます。
#SharpBackground：背景を鮮鋭化するか
#Brightness_mode：明るさを変更する方法を選択(No,PIL,OpenCV)
#dilate,erode：クロージング時の拡大率と縮小率
#X,Y：前景画像の貼り付け位置（途中の処理で前景画像をリサイズするのでその後の貼り付け位置）
#resize：前景画像を倍数指定でリサイズします
#R,G,B：切り抜かれる色を指定(0〜255）
#Threshold：２値化のの際の閾値（輪郭抽出）
#brightness：明るさ。
#BilateralFilter：バイラテラルフィルタ
#GausianFilter：ガウシアンフィルタ
#HideNum：遮蔽物の数
#x1_Ho,y1_Ho,x2_Ho,y2_Ho=,x3_Ho,y3_Ho,x4_Ho,y4_Ho：射影変換。

def Union(label_name="?",
         bak=None,
         tar=None,
         SharpBackground=False,
         SepiaAll=False,
         Brightness_mode="No",
         Extraction_mode="No",
         dilate=0,erode=0,
         X=0,Y=0,
         angle=0,
         resize=1,
         R=248,G=248,B=248,
         Threshold=248,
         brightness=1.0,
         BilateralFilter=1,
         GausianFilter=1,
         HideNum=0,
         x1_Ho=0,y1_Ho=0,x2_Ho=0,y2_Ho=0,x3_Ho=0,y3_Ho=0,x4_Ho=0,y4_Ho=0
         ):
    
    if(SharpBackground is True):
        #背景画像の鮮鋭化
        cv2.imwrite("./tmp/background.jpg",Sharp(cv2.imread(bak)))
        background=Image.open("./tmp/background.jpg")
    else:
        background=Image.open(bak)
    
    target=Image.open(tar)
    
    w,h=background.size
    tar_w,tar_h=target.size

    
    #前景画像を拡張
    target=img_expansion(target,resize,w,h)
    # target.save("./tmp/tmp_ex.png")    
    #PILからOpenCVへ変換
    target = cv2.cvtColor(np.array(target),cv2.COLOR_BGR2RGB)   
    
    #バイラテラルぼかし
    target=BilateralBlur(img=target,cnt=BilateralFilter)
    cv2.imwrite("./tmp/tmp.png",target)
    
    #前景画像の抽出
    target=cv2.imread("./tmp/tmp.png",-1)
    target=Extraction(tar=target,dilate=dilate, erode=erode,B=B,G=G,R=R,Threshold=Threshold, Extraction_mode=Extraction_mode)
    cv2.imwrite("./tmp/tmp.png",target)
    cv2.imwrite("./hoge.png",target)
    #ホモグラフィー変換

    target=Homography(cv2.imread("./tmp/tmp.png",-1),tar_w=tar_w,tar_h=tar_h,
                          x1=x1_Ho,y1=y1_Ho,x2=x2_Ho,y2=y2_Ho,x3=x3_Ho,y3=y3_Ho,x4=x4_Ho,y4=y4_Ho)

    #アフィン回転
    target=Affine(target,angle)
    
    #トリミング
    target=ImageTrim(target)
    cv2.imwrite("./tmp/tmp.png",target)

    try:
        tar_h,tar_w,_=target.shape[:3]
        org_w=tar_w
        org_h=tar_h
    except AttributeError:
        print("エラー:"+tar)
        sys.exit(1)

    target=HideTarget(target,HideNum)
    target.save("./tmp/tmp.png")

    
    #ターゲット全体にガウシアンぼかし
    target=TargetSmoothingBlur(cv2.imread("./tmp/tmp.png",-1),Blur=GausianFilter)

    cv2.imwrite("./tmp/tmp.png",target)
    tar_h,tar_w,_=target.shape[:3]
   
    # リサイズ
    # tar_raito=float(resize)/org_w 
    
    # target=cv2.resize(target,(resize,int(tar_h*tar_raito)))
    target=cv2.resize(target,(int(tar_w*resize),int(tar_h*resize)))
    cv2.imwrite("./tmp/tmp.png",target)
    tar_h,tar_w,_=target.shape[:3]


    #OpenCVで明度変換
    if (Brightness_mode == "OpenCV"): 
        target=OpenCV_gamma(brightness,cv2.imread("./tmp/tmp.png",-1))
        cv2.imwrite("./tmp/tmp.png",target)

    
    #PILで明度変換
    if (Brightness_mode == "PIL"):
        target=PIL_point(brightness,Image.open("./tmp/tmp.png"))
        target.save("./tmp/tmp.png")

    
    out_image=PasteTarget(x=X,y=Y,background=background)#画像の貼り付け
    out_image.save("./tmp/result.png")
    
    if(SepiaAll is True):
        SepiaImage=Sepia(cv2.imread("./tmp/result.png"))
        cv2.imwrite("./tmp/result.png",SepiaImage)
    
        

    out_image=Image.open("./tmp/result.png")
    # return plt.imshow(out_image)
    return out_image,tar_h,tar_w

#CSVから情報を取り出す
def csv_read(RECIPE,encoding):
    with open(RECIPE,"r") as f:
        recipe=csv.reader(f)
        rows = [[c.decode(encoding) for c in r] for r in recipe]
        return rows

#定義済みのカラー設定を取り出す
def ColorPalet(color):
    if(color=="White"):
        return 244,248,243
    elif(color=="Red"):
        return 255,0,0
    elif(color=="Green"):
        return 0,255,0
    elif(color=="Blue"):
        return 0,0,255
    else:
        sys.stderr.write("No such color")
        sys.exit()
