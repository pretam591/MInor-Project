from PyQt6.QtWidgets import QWidget, QLabel, QApplication, QPushButton, QRadioButton, QFileDialog
from PyQt6 import QtGui
import sys
from PyQt6.QtGui import QPixmap, QImage
from PyQt6.QtCore import *
from PIL import Image, ImageDraw, ImageFilter
from PIL.ImageQt import ImageQt
import numpy as np
from numpy import asarray
from copy import deepcopy
import torchvision.transforms as transforms
import torch
import torch.nn as nn
#import torch.nn.functional as F
import torch.optim as optim
import torchvision.models as models

class ConvBlock(nn.Module):
  def __init__(self,IC,OC,K,S,P):
    super(ConvBlock, self).__init__()
    self.conv = nn.Conv2d(IC,OC,K,S,P)
    self.bn = nn.BatchNorm2d(OC)
    self.relu = nn.LeakyReLU()
    self.conv1 = nn.Conv2d(OC,OC,K,S,P)
    self.bn1 = nn.BatchNorm2d(OC)
    self.relu1 = nn.LeakyReLU()
  def forward(self, x):
    return(self.relu1(self.bn1(self.conv1(self.relu(self.bn(self.conv(x)))))))

class Generator(nn.Module):
  def __init__(self):
    super(Generator, self).__init__()
    self.conv1 = ConvBlock(3,8,3,1,1)
    self.mp1 = nn.MaxPool2d(2,2)
    self.conv2 = ConvBlock(8,16,3,1,1)
    self.mp2 = nn.MaxPool2d(2,2)
    self.conv3 = ConvBlock(16,32,3,1,1)
    self.mp3 = nn.MaxPool2d(2,2)
    self.conv4 = ConvBlock(32,64,3,1,1)
    self.mp4 = nn.MaxPool2d(2,2)
    self.conv5 = ConvBlock(64,128,3,1,1)
    self.up1 = nn.UpsamplingBilinear2d(scale_factor=2)
    self.conv6 = ConvBlock(128,64,3,1,1)
    self.up2 = nn.UpsamplingBilinear2d(scale_factor=2)
    self.squeeze1 = ConvBlock(128,64,3,1,1)
    self.conv7 = ConvBlock(64,32,3,1,1)
    self.up3 = nn.UpsamplingBilinear2d(scale_factor=2)
    self.squeeze2 = ConvBlock(64,32,3,1,1)
    self.conv8 = ConvBlock(32,16,3,1,1)
    self.up4 = nn.UpsamplingBilinear2d(scale_factor=2)
    self.squeeze3 = ConvBlock(32,16,3,1,1)
    self.conv9 = ConvBlock(16,8,3,1,1)
    self.out = nn.Conv2d(8,3,3,1,1)

  def forward(self,x):                                    # 3 * 256 * 256
    c1=self.conv1(x)                                      # 8 * 256 * 256
    cm1=self.mp1(c1)                                      # 8 * 128 * 128
    c2=self.conv2(cm1)                                    # 16 * 128 * 128
    cm2 =self.mp2(c2)                                     # 16 * 64 * 64
    c3=self.conv3(cm2)                                    # 32 * 64 * 64
    cm3 = self.mp3(c3)                                    # 32 * 32 * 32
    c4=self.conv4(cm3)                                    # 64 * 32 * 32
    cm4 = self.mp4(c4)                                    # 64 * 16 * 16
    mid = self.conv5(cm4)                                 # 128 * 16 * 16
    u1 = self.up1(mid)                                    # 128 * 32 * 32
    uc1 = torch.cat((self.conv6(u1),c4), dim=1)           # 128 * 32 * 32
    uc1s = self.squeeze1(uc1)                             # 64 * 32 * 32
    u2 = self.up2(uc1s)                                   # 64 * 64 * 64
    uc2 = torch.cat((self.conv7(u2), c3), dim=1)          # 64 * 64 * 64
    uc2s = self.squeeze2(uc2)                             # 32 * 64 * 64
    u3 = self.up3(uc2s)                                   # 32 * 128 * 128
    uc3 = torch.cat((self.conv8(u3), c2), dim=1)          # 32 * 128 * 128
    uc3s = self.squeeze3(uc3)                             # 16 * 128 * 128
    u4 = self.up4(uc3s)                                   # 16 * 256 * 256
    uc4 = self.conv9(u4)                                  # 8 * 256 * 256
    ucfinal = self.out(uc4)                               # 3 * 256 * 256
    #norm = ucfinal.pow(2).sum(dim=1, keepdim=True).sqrt()
    #out = (ucfinal/norm)
    return(torch.tanh(ucfinal))

class App(QWidget):

    def __init__(self):
        super().__init__()
        self.title = 'Deep Neural Network Image Manipulator Application'
        self.setStyleSheet("background-color: pink;")
        self.left = 50 #xposition
        self.top = 50  #yposition
        self.width = 1200
        self.height = 650
        self.crop_image_resize = None
        self.model_path = None
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
        
        self.deep_sharp_button = QPushButton("Deep Sharpen", self)
        self.deep_sharp_button.setGeometry(950, 575, 90, 40)
        self.deep_sharp_button.clicked.connect(self.deep_sharpen_image)
        
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
        self.model_path = None

    def radio_10x_clicked(self):
        print('10x clicked')
        self.rh = 512/10
        self.rw = 512/10
        self.model_path = None

    def load_image(self):
        # Loading the input image with PIL and resizing it to (512, 512)
        filename, _ = QFileDialog.getOpenFileName(self, "Open Image", "", "Image Files (*.png *.jpg *.jpeg)")
        if filename:
            image = Image.open(filename)
            print(image.size)
            pilImg = image.resize((512, 512))
             # Convert the PIL image to a QPixmap and set it as the input label's pixmap
            pixmap = QPixmap.fromImage(ImageQt(pilImg.convert('RGBA')))
            self.label.setPixmap(pixmap)
            
            self.ori_img = deepcopy(pilImg)
            self.backup_img = deepcopy(self.ori_img)
            
            self.radio_2_5x.setChecked(True)
            self.label.mousePressEvent = self.getPos
            return(self.label)
            
    def display_image(self, image, flag):
        # Displaying an image via converting it to a pixmap
        pixmap = QPixmap.fromImage(ImageQt(image.convert('RGBA')))

        if flag == 0:
            self.label.setPixmap(pixmap)
        if flag == 1:
            self.label1.setPixmap(pixmap)
            
     
    def sharpen_image(self):
        
        # Applying a sharp filter
        sharpened1 = self.crop_image_resize.filter(ImageFilter.SHARPEN);
        sharpened2 = sharpened1.filter(ImageFilter.SHARPEN);
        
        self.display_image(sharpened2, 1)
        
    def deep_sharpen_image(self):
        # Loading the neural network model with torch
        if self.model_path == None:
            self.model_path, _ = QFileDialog.getOpenFileName(self, 'Open Model', '', 'Model (*.pt)')
            sd = torch.load(self.model_path, map_location=torch.device('cpu'))
            print(sd.keys())
            model = gen.load_state_dict(sd)
            print("done3")
            #print(model.input_shape)
            #print(model.input_dtype)
        
        print("done4")
        # Defining a transform while converting PIL image to a Torch tensor & Resizing the tensor to match the input size of our DL model
        transform = transforms.Compose([
            transforms.Resize(size=(256, 256)),
            transforms.PILToTensor()])
        img_tensor = transform(self.crop_image_resize).unsqueeze(0)
        print(img_tensor)
        print("done5")
        # Passing the tensor through the model
        print(img_tensor.shape)
        output_tensor = model(img_tensor)
        print("done7")
        # Converting the output tensor back to an image
        output_img = transforms.ToPILImage()(output_tensor.squeeze().detach().cpu())
        print("done8")
        pixmap = QPixmap.fromImage(output_img)
        self.label1.setPixmap(pixmap)
        print("done9")
        #print(output_img)
        print("done10")
        # Convert the output PIL image to a QPixmap and set it as the output label's pixmap
        #self.display_image(output_image,1)
        print("done11")
        
        
    def getPos(self,event):
        cx, cy = event.pos().x(),event.pos().y()
        print(cx,cy) #prints the coordinates of the point clicked over the image
        start_point = (cx-int(self.rh/2), cy-int(self.rw/2)) #left topmost starting point of rectangle
        end_point = (cx+int(self.rh/2), cy+int(self.rw/2)) #right lowermost end-point of rectangle
        
        if cx > int(self.rh/2) and cx < (512-int(self.rh/2)) and cy > int(self.rh/2) and cy < (512-int(self.rh/2)): #safe-space creation
            #safe_coordinates = (102.4,102.4) -- (409.6,102.4)
                                #(102.4,409.6) -- (409.6,409.6)
            self.ori_img = deepcopy(self.backup_img)
            img = ImageDraw.Draw(self.ori_img)  
            img.rectangle([start_point , end_point], outline ="blue")
            
            self.display_image(self.ori_img,0)
        
            crop_image = self.ori_img.crop((start_point[0]+1, start_point[1]+1, end_point[0], end_point[1]))
            self.crop_image_resize = crop_image.resize((512, 512))
            self.display_image(self.crop_image_resize,1)
            
    
if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = App()
    gen = Generator()
    sys.exit(app.exec())

