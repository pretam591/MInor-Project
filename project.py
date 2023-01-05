from PyQt5.QtWidgets import *
import sys
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtGui import QPainter, QBrush, QPen
from PyQt5.QtCore import Qt
from PyQt5 import QtCore, QtGui
import cv2
from copy import deepcopy
class App(QWidget):

    def __init__(self):
        super().__init__()
        self.title = 'PyQt5 image'
        self.left = -10
        self.top = -10
        self.width = 640
        self.height = 480
        self.initUI()
        self.radio()
        self.show()
        self.rh = 512/2.5
        self.rw = 512/2.5
    
    def radio(self):
        
        # creating a radio button
        radio_button = QRadioButton(self)
        radio_button_2 = QRadioButton(self)
        # setting geometry of radio button
        radio_button.setGeometry(100, 410, 120, 40)
        radio_button_2.setGeometry(200, 410, 120, 40)
  
        # setting text to radio button
        radio_button.setText("2.5x")
        radio_button_2.setText("10x")
        
        radio_button.toggled.connect(self.onClicked)
        radio_button_2.toggled.connect(self.onClicked)
        
    def onClicked(self):
        radio_button = self.sender()
        radio_button_2 = self.sender()
        
        if radio_button.isChecked():
            self.rh = 512/2.5
            self.rw = 512/2.5
            #self.initUI(self.rh,self.rw)
            
        elif radio_button_2.isChecked():
            self.rh = 512/10
            self.rw = 512/10
            #self.getPos(self.rh,self.rw)
    '''
    def paintEvent1(self, e):
        painter = QPainter(self)
        painter.drawRect(100, 15, 400,200)
        painter.setOpacity(0.2)
        painter.setBrush(Qt.black)       #ACTUAL BACKGROUDN
        painter.setPen(QPen(Qt.white))   #BORDER OF THE RECTANGLE
        painter.drawRect(self.rect())
    '''
    def initUI(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)
    
        cvImg = cv2.imread("./1.0.0.png")
        cvImg = cv2.resize(cvImg, (512,512))
        self.ori_img = deepcopy(cvImg)
        height, width, channel = cvImg.shape
        bytesPerLine = 3 * width
        qImg = QtGui.QImage(cvImg.data, width, height, bytesPerLine, QtGui.QImage.Format_BGR888)
        pixmap = QtGui.QPixmap.fromImage(qImg)
        self.label = QLabel('window',self)
        
        self.label.setPixmap(pixmap)
        self.label.mousePressEvent = self.getPos
        return(self.label)

        
    def getPos(self,event):
        cx, cy = event.pos().x(),event.pos().y()
        print(1)
        start_point = (int(cx-(self.rh/2)), int(cy-(self.rw/2)))
        print(1)
        end_point = (int(cx+(self.rh/2)), int(cy+(self.rw/2)))
        print(1)
        color = (255, 0, 0)
        print(1)
        thickness = 2
        print(1)
              
        img = cv2.rectangle(self.ori_img, start_point, end_point, color, thickness)
        print(1)
        height, width, channel = img.shape
        print(1)
        bytesPerLine = 3 * width
        print(1)
        qImg = QtGui.QImage(img.data, width, height, bytesPerLine, QtGui.QImage.Format_BGR888)
        print(1)
        pixmap = QtGui.QPixmap.fromImage(qImg)
        print(1)
        self.label.setPixmap(pixmap)
        print(1)
        
        
        #cv2.imshow('window',self.img)

    
if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = App()
    sys.exit(app.exec_())
