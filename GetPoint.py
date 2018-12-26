# coding: utf-8
#Copyright (c) 2018  Shotaro Ishigami
#クリックした場所の座標を表示します。
import matplotlib
matplotlib.use('TkAgg')
import numpy as np
import pylab
from PIL import Image
import matplotlib.pyplot as plt
import glob
import sys,csv,os

args=sys.argv

FLAG=False
resize_width=600 #横幅600pxにリサイズ

if(len(args) != 2):
    print( "ディレクトリを指定してください。")
    print ("例:~/Background/")
    sys.exit()



files=glob.glob(args[1]+"*.jpg")
print("全ての背景画像を"+str(resize_width)+"pxにリサイズ中...")
for f in files:
    img=Image.open(f)
    resize_rate=float(resize_width)/img.width
    # print(resize_rate) 

    img_resize = img.resize((int(img.width*resize_rate), int(img.height*resize_rate)))
    img_resize.save(f)


with open('./GetPoint.csv', 'w') as f:
        writer = csv.writer(f)
        writer.writerow(['filename','xmin','ymin','xmax','ymax'])   

def onclick(event):
    global x1,y1,FLAG
    print("click")
    try:
        FLAG=True
        x1=int(round(event.xdata))
        y1=int(round(event.ydata))
    except:
        return
    

def ondrag(event):
    global x1,x2,y1,y2,x,y,FLAG
    if FLAG==False:
        return
    try:
        x2=int(round(event.xdata))
        y2=int(round(event.ydata))
        drawRect()
        plt.draw()
    except:
        return

def onkey(event):
    global x1,y1,x2,y2
    
    if event.key=='e':
        print("データを保存します")
        x1, x2 = sorted([x1,x2])
        y1, y2 = sorted([y1,y2])
        data.append([base,x1,y1,x2,y2])
        #print(data)

    if event.key=='q':
        print('現在の画像を終了します')
        if data :
            with open('./GetPoint.csv', 'a') as f:
                writer = csv.writer(f)
                for i in data:
                    writer.writerow(i)   
        plt.close()


def onrelease(event):
    global FLAG
    FLAG=False


def drawRect():
    global x1,y1,x2,y2
    Rect = [ [ [x1,x2], [y1,y1] ],
             [ [x2,x2], [y1,y2] ],
             [ [x1,x2], [y2,y2] ],
             [ [x1,x1], [y1,y2] ] ]
    for i, rect in enumerate(Rect):  
        lns[i].set_data(rect[0],rect[1])


for images in glob.glob(args[1]+"*"):
    x1=0
    y1=0
    x2=0
    y2=0
    data=[]
    base=os.path.basename(images)  
    image=Image.open(images)  
    image_list=np.asarray(image)

   

    plt.figure()
    plt.subplot(1,1,1)

    Rect = [ [ [x1,x2], [y1,y1] ],
            [ [x2,x2], [y1,y2] ],
            [ [x1,x2], [y2,y2] ],
            [ [x1,x1], [y1,y2] ] ]

    lns = []
    for rect in Rect:
        ln, = plt.plot(rect[0],rect[1],color='r',lw=2)
        lns.append(ln)
        
    plt.connect('button_press_event', onclick)     
    plt.connect('motion_notify_event',ondrag)
    plt.connect('button_release_event',onrelease)
    plt.connect('key_press_event',onkey)
    
    plt.title(images)
    im=plt.imshow(image_list)
    plt.clim(im.get_clim())
    plt.axis('off')

    plt.show()
