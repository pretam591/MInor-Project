from PyQt5.QtWidgets import QWidget, QLabel, QApplication, QPushButton, QRadioButton, QFileDialog
from PyQt5 import QtGui
import sys
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtCore import *
from PIL import Image, ImageDraw
from PIL.ImageQt import ImageQt
import numpy as np
from copy import deepcopy
import torchvision.transforms as transforms
import torch
import torch.nn as nn
#import torch.nn.functional as F
import torch.optim as optim

class App(QWidget):

    def __init__(self):
        super().__init__()
        self.title = 'Image Manipulator'
        self.left = 50 #xposition
        self.top = 50  #yposition
        self.width = 1200
        self.height = 650
        self.crop_image_resize = None
        self.initUI()
        self.show()
    
    def initUI(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height) #x,y,width,height
        
        self.label = QLabel('developed by Pretam &',self)
        self.label.setGeometry(50, 50, 512, 512)
        self.label1 = QLabel('Swarnendu Sir',self)
        self.label1.setGeometry(650, 50, 512, 512)
        
        self.load_button = QPushButton("Load Image", self)
        self.load_button.setGeometry(50, 20, 100, 25)
        self.load_button.clicked.connect(self.load_image)
        
        self.sharp_button = QPushButton("Sharpen", self)
        self.sharp_button.setGeometry(850, 575, 90, 40)
        self.sharp_button.clicked.connect(self.sharpen_image)
        
        self.sharp_button = QPushButton("Deep Sharpen", self)
        self.sharp_button.setGeometry(950, 575, 90, 40)
        #self.sharp_button.clicked.connect(self.deep_sharpen_image)
        
        # creating a "2.5x" radio button
        self.radio_2_5x = QRadioButton('2.5x', self)
        self.radio_2_5x.setGeometry(180, 560, 120, 40)
        self.radio_2_5x.clicked.connect(self.radio_2_5x_clicked)

        # creating a "10x" radio button
        self.radio_10x = QRadioButton('10x', self)
        self.radio_10x.setGeometry(350, 560, 120, 40)
        self.radio_10x.clicked.connect(self.radio_10x_clicked)
        
    def radio_2_5x_clicked(self):
        print('2.5x clicked')
        self.rh = 512/2.5
        self.rw = 512/2.5

    def radio_10x_clicked(self):
        print('10x clicked')
        self.rh = 512/10
        self.rw = 512/10

    def load_image(self):
        filename, _ = QFileDialog.getOpenFileName(self, "Open Image", "", "Image Files (*.png *.jpg *.jpeg)")
        if filename:
            image = image = Image.open(filename)
            print(image.size)
            skImg = image.resize((512, 512))
            self.ori_img = deepcopy(skImg)
            self.backup_img = deepcopy(self.ori_img)
            height, width = skImg.size# (512, 512, 3)
            bytesPerLine = 3 * width
            qim = ImageQt(skImg)
            #qImg = QtGui.QImage(qim, width, height, bytesPerLine, QtGui.QImage.Format_ARGB32)
            pixmap = QtGui.QPixmap.fromImage(qim)
            
            self.label.setPixmap(pixmap)
            self.radio_2_5x.setChecked(True)
            self.label.mousePressEvent = self.getPos
            return(self.label)
            
    def display_image(self, image, flag):
        #height, width = image.size
        #bytes_per_line = 3 * width
        #qimage = QImage(image.data, width, height, bytes_per_line, QImage.Format_BGR888)
        qim = ImageQt(image)
        pixmap = QPixmap.fromImage(qim)
        if flag == 0:
            self.label.setPixmap(pixmap)
        if flag == 1:
            self.label1.setPixmap(pixmap)
            

    def sharpen_image(self):
        self.label1.update()
        print("p1")
        kernel = np.array([[0, -1, 0],
                   [-1, 5,-1],
                   [0, -1, 0]])
        
        #self.crop_image_resize = cv2.filter2D(src=self.crop_image_resize, ddepth=-1, kernel=kernel)
        
        self.display_image(self.crop_image_resize, 1)
        
                  
    def getPos(self,event):
        cx, cy = event.pos().x(),event.pos().y()
        print(cx,cy) #prints the coordinates of the point clicked over the image
        start_point = (cx-int(self.rh/2), cy-int(self.rw/2)) #left topmost starting point of rectangle
        end_point = (cx+int(self.rh/2), cy+int(self.rw/2)) #right lowermost end-point of rectangle
        color = (255, 0 , 0)
        print(start_point,end_point)
        y = start_point[1]
        h = end_point[1]
        x = start_point[0]
        w = end_point[0]
        print(y,h,x,w)
        if cx > int(self.rh/2) and cx < (512-int(self.rh/2)) and cy > int(self.rh/2) and cy < (512-int(self.rh/2)): #safe-space creation
            #safe_coordinates = (102.4,102.4) -- (409.6,102.4)
                                #(102.4,409.6) -- (409.6,409.6)
            self.ori_img = deepcopy(self.backup_img)
            img = ImageDraw.Draw(self.ori_img)  
            img.rectangle([start_point , end_point], outline ="white")
            
            qim = ImageQt(self.ori_img)
            pixmap = QPixmap.fromImage(qim)
            self.label1.setPixmap(pixmap)
            #self.display_image(img,0)
            
            crop_image = img[y+1:h, x+1:w]
            self.crop_image_resize = crop_image.resize((512, 512))
            #self.display_image(self.crop_image_resize,1)
            qim = ImageQt(img)
            pixmap = QPixmap.fromImage(qim)
            self.label1.setPixmap(pixmap)

    
if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = App()
    sys.exit(app.exec_())
