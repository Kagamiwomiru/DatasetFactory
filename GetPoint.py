# coding: utf-8
#クリックした場所の座標を表示します。
import matplotlib
matplotlib.use('TkAgg')
import numpy as np
import pylab
from PIL import Image
import matplotlib.pyplot as plt
import glob
import sys

args=sys.argv

if(len(args) != 2):
    print "ディレクトリを指定してください。"
    print "例:~/Background/"
    sys.exit()

def onclick(event):
    print 'event.button=%d,  event.x=%d, event.y=%d, event.xdata=%f, \
    event.ydata=%f'%(event.button, event.x, event.y, event.xdata, event.ydata)


for images in glob.glob(args[1]+"*"):
    image=Image.open(images)
    image_list=np.asarray(image)

    plt.figure()
    plt.title(images)
    plt.imshow(image_list)
    plt.connect('button_press_event', onclick)     # マウスを押した時
    plt.show()
