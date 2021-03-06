# coding: utf-8
# Copyright (c) 2018  Shotaro Ishigami
# 画像を合成します。
from UnionKit import *
import csv
import cv2


#bak：背景画像
#tar：前景画像（ターゲット）
#これより下の引数は省略できます。
#SharpBackground：背景を鮮鋭化するか
#Brightness_mode：明るさを変更する方法を選択(No,PIL,OpenCV)
#Extraction_mode : 前景抽出方法を選択(No,Color,Binary)
#dilate,erode：クロージング時の拡大率と縮小率
#X,Y：前景画像の貼り付け位置（途中の処理で前景画像をリサイズするのでその後の貼り付け位置）
#Random_rotation : 画像をランダムで回転させるか
#resize：前景画像を倍数指定でリサイズします
#R,G,B：切り抜かれる色を指定(0〜255）
#Threshold：２値化のの際の閾値（輪郭抽出）
#brightness：明るさ。
#BilateralFilter：バイラテラルフィルタ
#GausianFilter：ガウシアンフィルタ
#HideNum：遮蔽物の数
#x1_Ho,y1_Ho,x2_Ho,y2_Ho=,x3_Ho,y3_Ho,x4_Ho,y4_Ho：射影変換。
#flips : 反転(0:上下反転, 1:左右反転, -1:上下左右反転)
#amount : ソルト&ペッパにおける画像の中のノイズの割合
#sp_ratio : ソルト&ペッパの塩と胡椒の割合
#mean : ガウシアンフィルタにおける平均
#sigma : ガウシアンフィルタにおける分散
#kernel : 量子化するときのくくりの数値(つまりは何色で表示にするか)
#perspective : 中心にいくほどどれだけ縮小させるか(例:perspectiveが2ならば1/2まで縮小)

def Union(label_name="?",
         bak=None,
         tar=None,
         SharpBackground=False,
         SepiaAll=False,
         Brightness_mode="No",
         Extraction_mode="No",
         dilate=0,erode=0,
         X=0,Y=0,
         Random_rotation=False,
         angle=0,
         resize=1,
         R=248,G=248,B=248,
         Threshold=200,
         brightness=1.0,
         BilateralFilter=1,
         GausianFilter=1,
         HideNum=0,
         x1_Ho=0,y1_Ho=0,x2_Ho=0,y2_Ho=0,x3_Ho=0,y3_Ho=0,x4_Ho=0,y4_Ho=0,
         flips=2,
         amount=0.,
         sp_ratio=0.5,
         mean=0,
         sigma=0,
         kernel=-1,
	 perspective=2
         ):
    
    if(SharpBackground is True):
        # 背景画像の鮮鋭化
        cv2.imwrite("./tmp/background.jpg", Sharp(cv2.imread(bak)))
        background = Image.open("./tmp/background.jpg")
    else:
        background = Image.open(bak)

    target = Image.open(tar)

    w, h = background.size
    tar_w, tar_h = target.size

    # 前景画像を拡張
    target = img_expansion(target, resize, w, h)
    # target.save("./tmp/tmp_ex.png")
    # PILからOpenCVへ変換
    target = cv2.cvtColor(np.array(target), cv2.COLOR_BGR2RGB)

    # ターゲットを反転
    target = flip_img(tar=target, flips=flips)

    # バイラテラルぼかし
    target = BilateralBlur(img=target, cnt=BilateralFilter)
    cv2.imwrite("./tmp/tmp.png", target)

    # 前景抽出選択
    target = Extraction(tar=target, dilate=dilate, erode=erode, B=B,
                        G=G, R=R, Threshold=Threshold, Extraction_mode=Extraction_mode)
    cv2.imwrite("./tmp/tmp.png", target)

    # ホモグラフィー変換

    target = Homography(cv2.imread("./tmp/tmp.png", -1), tar_w=tar_w, tar_h=tar_h,
                        x1=x1_Ho, y1=y1_Ho, x2=x2_Ho, y2=y2_Ho, x3=x3_Ho, y3=y3_Ho, x4=x4_Ho, y4=y4_Ho)

    # アフィン回転(ランダムで回転させるか)
    if Random_rotation:
        target=Affine(target,random.randint(0,359))
    else:
        target = Affine(target, angle)

    # トリミング
    target = ImageTrim(target)
    cv2.imwrite("./tmp/tmp.png", target)

    try:
        tar_h, tar_w, _ = target.shape[:3]
        org_w = tar_w
        org_h = tar_h
    except AttributeError:
        print("エラー:"+tar)
        sys.exit(1)

    target = HideTarget(target, HideNum)
    target.save("./tmp/tmp.png")

    # ターゲット全体にガウシアンぼかし
    target = TargetSmoothingBlur(cv2.imread(
        "./tmp/tmp.png", -1), Blur=GausianFilter)

    cv2.imwrite("./tmp/tmp.png", target)
    tar_h, tar_w, _ = target.shape[:3]

    # リサイズ
    # tar_raito=float(resize)/org_w 
    
    # target=cv2.resize(target,(resize,int(tar_h*tar_raito)))
    target=cv2.resize(target,(int(tar_w*resize),int(tar_h*resize)))
    cv2.imwrite("./tmp/tmp.png",target)
    tar_h,tar_w,_=target.shape[:3]
    
    #遠近による大きさの変化
    if perspective>1:
    	target=Perspective(tar=cv2.imread("./tmp/tmp.png",-1),bak=background,x=X,y=Y,perspective=perspective)
    	cv2.imwrite("./tmp/tmp.png",target)
    	tar_h,tar_w,_=target.shape[:3] 

    #背景に溶け込ませる
    target=Nature_Target(tar=cv2.imread("./tmp/tmp.png",-1),bak=background,x=X,y=Y)
    cv2.imwrite("./tmp/tmp.png",target)
    

    # OpenCVで明度変換
    if (Brightness_mode == "OpenCV"):
        target = OpenCV_gamma(brightness, cv2.imread("./tmp/tmp.png", -1))
        cv2.imwrite("./tmp/tmp.png", target)

    # PILで明度変換
    if (Brightness_mode == "PIL"):
        target = PIL_point(brightness, Image.open("./tmp/tmp.png"))
        target.save("./tmp/tmp.png")

    out_image = PasteTarget(x=X, y=Y, background=background)  # 画像の貼り付け
    out_image.save("./tmp/result.png")

    # 量子化クラスタリング
    if not (kernel == -1):
        cluster_img = cluster(tar=cv2.imread(
            "./tmp/result.png"), kernel=kernel)
        cv2.imwrite("./tmp/result.png", cluster_img)

    # ソルト&ペッパー
    if not (amount == 0):
        sp_image = salt_and_pepper(tar=cv2.imread(
            "./tmp/result.png"), amount=amount, sp_ratio=sp_ratio)
        cv2.imwrite("./tmp/result.png", sp_image)

    # ガウシアンノイズ
    gauss_image = gauss_noise(tar=cv2.imread(
        "./tmp/result.png"), mean=mean, sigma=sigma)
    cv2.imwrite("./tmp/result.png", gauss_image)

    if(SepiaAll is True):
        SepiaImage = Sepia(cv2.imread("./tmp/result.png"))
        cv2.imwrite("./tmp/result.png", SepiaImage)

    out_image = Image.open("./tmp/result.png")
    # return plt.imshow(out_image)
    return out_image, tar_h, tar_w

# CSVから情報を取り出す


def csv_read(RECIPE, encoding):
    with open(RECIPE, "r") as f:
        recipe = csv.reader(f)
        rows = [[c.decode(encoding) for c in r] for r in recipe]
        return rows

# 定義済みのカラー設定を取り出す


def ColorPalet(color):
    if(color == "White"):
        return 244, 248, 243
    elif(color == "Red"):
        return 255, 0, 0
    elif(color == "Green"):
        return 0, 255, 0
    elif(color == "Blue"):
        return 0, 0, 255
    else:
        sys.stderr.write("No such color")
        sys.exit()
