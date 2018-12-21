# coding: utf-8
#Copyright (c) 2018  Shotaro Ishigami

import cv2
import numpy as np
import random
from PIL import Image, ImageDraw, ImageFilter

#ターゲット切り取り
def ImageTrim(img):

    th1=Binarize(245,img)
    # 輪郭を抽出
      #   contours : [領域][Point No][0][x=0, y=1]
      #   cv2.CHAIN_APPROX_NONE: 中間点も保持する
      #   cv2.CHAIN_APPROX_SIMPLE: 中間点は保持しない
    _,contours, hierarchy = cv2.findContours(th1, cv2.RETR_LIST, cv2.CHAIN_APPROX_NONE)
    
    
    h,w,_=img.shape[:3]
    img_area=h*w
    
    maxContour = 0

    # 各輪郭に対する処理
    for i in range(0, len(contours)):

        # 輪郭の領域を計算
        area = cv2.contourArea(contours[i])

        # ノイズ（小さすぎる領域）と画像全体の輪郭を除外
        if area < 1e3 or area>=img_area-100000:
              continue

        # 外接矩形
        if len(contours[i]) > 0:
            if(area>maxContour):
                rect = contours[i]
                x, y, w, h = cv2.boundingRect(rect)
                # cv2.rectangle(img, (x, y), (x + w, y + h), (255, 0,0 ), 1)
                # 外接矩形毎に画像を保存
                img_pe=img[y:y + h, x:x + w]
                maxContour=area
        
    try:
        return img_pe
    except NameError:
        return None

# 抽出モードによって抽出手法を変更します。
def Extraction(Extraction_mode=None,
                        Threshold=None,
                        tar=None,
                        dilate=None,
                        erode=None,
                        B=None,G=None,R=None,
              ):
    
    if(Extraction_mode=="Binary"):
        #2値化による輪郭抽出
        th1=Binarize(Threshold,tar)
        MakeMask(th1,dilate,erode)
        mask=Image.open("./tmp/mask.png")
        tar=Image.fromarray(tar)
        tar.putalpha(mask)
        tar=np.asarray(tar)
       
    elif Extraction_mode=="Color":
        tar=Extraction_color(B,G,R,tar,dilate=dilate,erode=erode)#　色指定による輪郭抽出（BGR)
    
    return tar

#輪郭抽出（色）
def Extraction_color(B,G,R,tar,dilate=0,erode=0):
    B_thres_type=cv2.THRESH_BINARY_INV
    B_thres=B
    G_thres_type=cv2.THRESH_BINARY_INV
    G_thres=G
    R_thres_type=cv2.THRESH_BINARY_INV
    R_thres=R
    BGR = cv2.split(tar) #BGRに分離
    _, B_mask = cv2.threshold(BGR[0], B_thres, 1, B_thres_type)
    _, G_mask = cv2.threshold(BGR[1], G_thres, 1, G_thres_type)
    _, R_mask = cv2.threshold(BGR[2], R_thres, 1, R_thres_type)
    background_mask = B_mask * G_mask * R_mask
    result = cv2.merge(BGR + [255 * background_mask])
    result=Closing(result,dilate=dilate,erode=erode)
    return result

#画像を２値化します。
def Binarize(gray,im):
   
    im_gray=cv2.cvtColor(im,cv2.COLOR_BGR2GRAY)#画像の読み込み
    #ガウスフィルタ
    im_gray_smooth=cv2.GaussianBlur(im_gray,(11,11),0)
    #2値化
    _,th1 = cv2.threshold(im_gray_smooth,gray,255,cv2.THRESH_BINARY)
    
    return th1

#２値化した情報からマスクを作成します。
def MakeMask(th1,dilate=0,erode=0):
    #マスク画像作成
    mask_img=255-th1
    mask_img=Closing(mask_img,dilate=dilate,erode=erode)
    cv2.imwrite("./tmp/mask.png",mask_img)

    
def PasteTarget(x=0,y=0,background=None,mask=None):
    target=Image.open("./tmp/tmp.png").convert("RGBA")
    #マスク画像が指定された時(Extractionが呼ばれてる時)はmask処理をする
    if mask is None:
        background.paste(target,(x,y),target)
    else:
        mask_img=Image.open(mask)#.convert("RGBA")
        background.paste(target,(x,y),mask_img)
    return background
    
# ターゲット画像を背景の２倍の大きさにします。
def img_expansion(img,resize,width=1900,height=1080):
    scale=2 #背景の何倍に拡張するか
    img.thumbnail((width/scale,height/scale))
    # img.thumbnail((width/scale*resize,height/scale*resize))
    # 透明に塗りつぶす用の背景画像を作成
    bg = Image.new("RGBA",[width,height],(255,255,255,0))
    # 元の画像を、背景画像のセンターに配置
    bg.paste(img,(int((width-img.size[0])/2),int((height-img.size[1])/2)))
#     bg.paste(img,(0,0))
    return bg

#クロージングをします（拡大縮小率を変えられる）
def Closing(img,kernel=np.ones((5,5),np.uint8),dilate=0,erode=0):
    img_dilate=cv2.dilate(img,np.ones((5,5),np.uint8),iterations = dilate)
    img_dilate_erode = cv2.erode(img_dilate,np.ones((5,5),np.uint8),iterations = erode)
    return img_dilate_erode

# PILで明度調整
def PIL_point(point,img):
    img_dw=img.point(lambda x:x*point)
    return img_dw

#OpenCVで明度調整
def OpenCV_gamma(gamma,img):
    gamma_cvt=np.zeros((256,1),dtype='uint8')
    for i in range(256):
        gamma_cvt[i][0]=255*(float(i)/255)**(1.0/gamma)
    img_gamma=cv2.LUT(img,gamma_cvt)
    return img_gamma



#射影変換(ホモグラフィー変換)
def Homography(img,tar_w=None,tar_h=None,x1=0,y1=0,x2=0,y2=1080,x3=1900,y3=1080,x4=1900,y4=0):
    tar_h,tar_w,_=img.shape[:3]

    pts1 = np.float32([[0,0],[0,tar_h],[tar_w,tar_h],[tar_w,0]])#4隅を指定
    pts2 = np.float32([[x1,y1],[x2,y2+tar_h],[x3+tar_w,y3+tar_h],[x4+tar_w,y4]])#変換後
    M = cv2.getPerspectiveTransform(pts1,pts2)
    return cv2.warpPerspective(img,M,(tar_w,tar_h),borderValue=(255,255,255))



#ぼかし（ターゲット全体）
def TargetSmoothingBlur(img=None,Blur=None):
    if(Blur>0 and Blur%2!=0):
        dst=cv2.blur(img,ksize=(Blur,Blur))
        return dst
    else:
        print("ぼかしに使うカーネルは１以上で奇数の値を指定してください。")
        return img



 #バイラテラルフィルタ
def BilateralBlur(img=None,cnt=1):
    if(cnt>1):
        dst=cv2.bilateralFilter(img,15,20,20)
        for i in range(cnt-1):
            dst=cv2.bilateralFilter(dst,15,20,20)
        return dst
    else:
        return img       

# アフィン変換
def Affine(img,angle):
    h,w,c=img.shape
    M=cv2.getRotationMatrix2D(center=(w/2,h/2),angle=angle,scale=1.)
    dst=cv2.warpAffine(img,M,dsize=(w*2,h*2),borderValue=(255,255,255))
    return dst

#レンズフィルタ（指定した色だけにします）
def LensFilter(img,color,scale):
    b,g,r=img[:,:,0],img[:,:,1],img[:,:,2]
    if(color=="red"):
        img[:,:,0]=0
        img[:,:,1]=0
        img[:,:,2]=r//scale
    elif(color=="green"):
        img[:,:,0]=0
        img[:,:,1]=g//scale
        img[:,:,2]=0
    elif(color=="blue"):
        img[:,:,0]=b//scale
        img[:,:,1]=0
        img[:,:,2]=0
    
    return img


# セピア変換
def Sepia(im):
    b, g, r = im[:,:,0],im[:,:,1], im[:,:,2]
    gray = 0.2989 * r + 0.5870 * g + 0.1140 * b 
    r=gray*240/255
    g=gray*200/255
    b=gray*145/255
    im[:,:,0],im[:,:,1], im[:,:,2]=b, g, r
     
    return im



#鮮鋭化
def Sharp(img=None):
    kernel=np.array([[-1,-1,-1],
                     [-1,9,-1],
                     [-1,-1,-1]],np.float32)
    dst=cv2.filter2D(img,-1,kernel)
    return dst


#彩度を下げる
def ModChroma(img,chroma):
    a=cv2.cvtColor(img,cv2.COLOR_BGR2HSV)
    hsv=cv2.split(a)
    hsv[1]=hsv[1]//chroma
    img=cv2.merge((hsv[0],hsv[1],hsv[2]))
    img=cv2.cvtColor(img,cv2.COLOR_HSV2BGR)
    return img


#擬似遮蔽
#簡単な図形をランダムで生成し、遮蔽物を再現します。作成する個数は設定でき、初期値は０です。
#ターゲット周辺に生成されます。
def HideTarget(img,num):
    cv2.imwrite("./tmp/Shield.png",MakeShield(img,num))
    
    target=Image.open("./tmp/tmp.png").convert("RGBA")
    shield=Image.open("./tmp/Shield.png").convert("RGBA")
    target.paste(shield,(0,0),shield)
    return target

# 図形生成
def MakeShield(img,num=0):
    h,w,_=img.shape
    Shield=np.full((h,w,3),255,np.uint8)
    
    
    for i in range(num):
    
    #   描画設定
        ShieldType,FillOption,startX,startY,ColorR,ColorG,ColorB=Dise(w,h)

        if(ShieldType==0):#四角形    
            endX=random.randint(0,w)
            endY=random.randint(0,h)
            cv2.rectangle(Shield,(startX,startY),
                          (endX,endY),
                          (ColorB,ColorG,ColorR),FillOption)
        elif(ShieldType==1):#円
            min_len=min(h,w)
            radius=random.randint(1,min_len/2)
            cv2.circle(Shield,(startX,startY),
                       radius,(ColorB,ColorG,ColorR),FillOption)
        elif(ShieldType==2):#楕円
            radiusX=random.randint(1,w)
            radiusY=random.randint(1,h)
            angle=random.randint(1,359)
            cv2.ellipse(Shield,((startX,startY),
                                    (radiusX,radiusY),angle),
                                    (ColorB,ColorG,ColorR),FillOption)
    
    Shield=Extraction_color(B=254,G=254,R=254,tar=Shield)
    return Shield



def Dise(w,h):
    ShieldType=random.randint(0,2)
    FillOption=random.choice([-1,5])
    startX=random.randint(0,w)
    startY=random.randint(0,h)
    ColorR=random.randint(0,254)
    ColorG=random.randint(0,254)
    ColorB=random.randint(0,254)
    return ShieldType,FillOption,startX,startY,ColorR,ColorG,ColorB  

# 画像反転
def flip_img(tar=None,flips=2):
    if not flips in [1,0,-1]:
        return tar
    img = cv2.flip(tar, flips)    
    return img


# ガウシアンノイズ
def gauss_noise(tar=None,mean=0,sigma=15):
    row,col,ch= tar.shape
    gauss = np.random.normal(mean,sigma,(row,col,ch))
    gauss = gauss.reshape(row,col,ch)
    gauss_img = tar + gauss
    
    gauss_img=gauss_img.astype("int")
    gauss_img=np.asarray(gauss_img)
    return gauss_img

# ソルト&ペッパノイズ
def salt_and_pepper(tar=None, amount=0.,sp_ratio=0.5):
    #tar=np.asarray(tar)
    sp_img = tar.copy()
    #print(tar)
    # 塩モード
    num_salt = np.ceil(amount * tar.size * sp_ratio)
    coords = [np.random.randint(0, i-1 , int(num_salt)) for i in tar.shape]
    #print(coords[:-1])
    sp_img[coords[:-1]] = (255,255,255)

    # 胡椒モード
    num_pepper = np.ceil(amount* tar.size * (1. - sp_ratio))
    coords = [np.random.randint(0, i-1 , int(num_pepper)) for i in tar.shape]
    sp_img[coords[:-1]] = (0,0,0)
    
    return sp_img

# 量子化クラスタリング
def cluster(tar=None,kernel=256):
    cluster_img = tar.reshape((-1,3))
    # convert to np.float32
    cluster_img = np.float32(cluster_img)

    # define criteria, number of clusters(K) and apply kmeans()
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 10, 1.0)
    ret,label,center=cv2.kmeans(cluster_img,kernel,None,criteria,10,cv2.KMEANS_RANDOM_CENTERS)

    # Now convert back into uint8, and make original image
    center = np.uint8(center)
    result = center[label.flatten()]
    result = result.reshape((tar.shape))
    return result

