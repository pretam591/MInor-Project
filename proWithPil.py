import sys
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QImage, QPixmap, QPainter, QPen
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QPushButton, QGraphicsScene, QGraphicsView
from PIL import Image
from PIL.ImageQt import ImageQt


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setGeometry(50, 50, 1200, 650)
        self.image_label = QLabel(self)
        self.image_label.setGeometry(0, 0, 1200, 650)
        self.load_button = QPushButton('Load Image', self)
        self.load_button.setGeometry(10, 10, 100, 30)
        self.load_button.clicked.connect(self.load_image)
        self.crop_button = QPushButton('Crop Image', self)
        self.crop_button.setGeometry(120, 10, 100, 30)
        self.crop_button.clicked.connect(self.crop_image)
        self.image = None
        self.scene = QGraphicsScene(self)
        self.view = QGraphicsView(self.scene, self)
        self.view.setGeometry(0, 0, 1200, 650)
        self.view.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.view.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.view.setRenderHint(QPainter.Antialiasing)

    def load_image(self):
        file_name, _ = QFileDialog.getOpenFileName(self, 'Open Image', '', 'Image Files (*.png *.jpg *.bmp)')
        if file_name:
            self.image = Image.open(file_name)
            qimage = ImageQt(self.image).copy()
            pixmap = QPixmap.fromImage(qimage)
            self.image_label.setPixmap(pixmap)
            self.scene.clear()

    def crop_image(self):
        if self.image is not None:
            self.scene.clear()
            self.scene.addPixmap(QPixmap.fromImage(ImageQt(self.image)))
            self.view.show()
            rect = self.scene.addRect(0, 0, 0, 0, pen=QPen(Qt.red))
            self.view.setDragMode(QGraphicsView.RubberBandDrag)
            rect.setFlag(rect.ItemIsMovable)
            rect.setFlag(rect.ItemIsSelectable)
            rect.setFlag(rect.ItemIsFocusable)
            self.view.setScene(self.scene)
            self.view.viewport().update()
            self.view.show()
            self.view.scene().selectionChanged.connect(lambda: self.crop(rect))

    def crop(self, rect):
        if self.image is not None:
            x = int(rect.pos().x())
            y = int(rect.pos().y())
            width = int(rect.rect().width())
            height = int(rect.rect().height())
            cropped_image = self.image.crop((x, y, x + width, y + height))
            qimage = ImageQt(cropped_image).copy()
            pixmap = QPixmap.fromImage(qimage)
            self.image_label.setPixmap(pixmap)
            self.scene.clear()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())