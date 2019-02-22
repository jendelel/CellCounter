from PyQt5 import QtWidgets, uic
from PyQt5.QtWidgets import QGraphicsView, QRubberBand, QGraphicsScene, QGraphicsPixmapItem, QLabel, QFileDialog
from PyQt5.QtCore import (QPoint, QRect, pyqtSignal, QSize, Qt, pyqtSlot)
from PyQt5.QtGui import (QPixmap, QImage, QPainter, QColor, QPalette, QBrush)

from skimage.io import imread
import qimage2ndarray
from analysis import segment_image
import numpy as np

class PictureBox(QLabel):
    changedNumberRegions = pyqtSignal(int)
    def __init__(self, image, regions, parent = None):
    
        QLabel.__init__(self, parent)
        self.rubberBand = QRubberBand(QRubberBand.Rectangle, self)
        self.origin = QPoint()
        self.regions = None
        self.image = image
        def region_to_rect(region):
            y1, x1, y2, x2 = region.bbox
            return QRect(x1, y1, x2-x1, y2-y1)
        self.regions = list(map(region_to_rect, regions))
        self._update_picture()
    
    def mousePressEvent(self, event):
        pal = QPalette()
        if event.button() == Qt.LeftButton:
            pal.setBrush(QPalette.Highlight, QBrush(Qt.blue))
        elif event.button() == Qt.RightButton:
            pal.setBrush(QPalette.Highlight, QBrush(Qt.green))
        self.rubberBand.setPalette(pal)
        self.origin = QPoint(event.pos())
        self.rubberBand.setGeometry(QRect(self.origin, QSize()))
        self.rubberBand.show()

    def mouseMoveEvent(self, event):
        if not self.origin.isNull():
            self.rubberBand.setGeometry(QRect(self.origin, event.pos()).normalized())

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            drawnRect = QRect(self.origin, event.pos()).normalized()
            for region in self.getIntersectedRegions(drawnRect):
                self.regions.remove(region)
        elif event.button() == Qt.RightButton:
            drawnRect = QRect(self.origin, event.pos()).normalized()
            meanArea = np.mean([r.width() * r.height() for r in self.regions])
            meanHeight = np.mean([r.height() for r in self.regions])
            meanWidth = np.mean([r.width() for r in self.regions])
            if drawnRect.width() * drawnRect.height() * 2 < meanArea:
                rect = QRect(self.origin.x() - meanWidth/2, self.origin.y() - meanHeight/2, meanWidth, meanHeight)
                self.regions.append(rect)
            else:
                self.regions.append(drawnRect)
        self.rubberBand.hide()
        self._update_picture()

    def getIntersectedRegions(self, drawnRect):
        result = []
        for region in self.regions:
            if region.intersects(drawnRect):
                result.append(region)
        return result

    def _update_regions(self):
        pixmap = self._get_pixmap()
        paint = QPainter(pixmap)
        paint.setPen(QColor("green"))
        for region in self.regions:
            paint.drawRect(region)
            # rect = mpatches.Rectangle((minc, minr), maxc - minc, maxr - minr,
            #                          fill=False, edgecolor='green', linewidth=2)
        del paint
        return pixmap
    
    def savePicture(self, fname):
        pixmap = self._update_regions()
        return pixmap.save(fname)

    def _update_picture(self):
        pixmap = self._update_regions()
        self.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        self.setPixmap(pixmap)
        self.changedNumberRegions.emit(len(self.regions))

    def _get_pixmap(self):
        # Convert image to QImage
        qimg = qimage2ndarray.array2qimage(self.image, True)
        return QPixmap(qimg)

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        QtWidgets.QMainWindow.__init__(self)
        with open('main.ui') as f:
            uic.loadUi(f, self)
        
        self.butAnalyze.clicked.connect(self.loadImage)
        self.butSave.clicked.connect(self.saveImage)
        self.picBox = None

        # image = imread('pokus.tif')
        # regions = segment_image(image)

        # picture_box = PictureBox(image, regions)

    @pyqtSlot(int)
    def updateLabel(self, numRegions):
        self.txtNumRegions.setText("Number of\nregions: %d" % numRegions)

    @pyqtSlot()
    def loadImage(self):
        fileName = self.openFileDialog()
        if fileName:
            if self.picBox:
                self.picBox.changedNumberRegions.disconnect()
            image = imread(fileName)
            regions = segment_image(image, scale=self.spinScale.value(), sigma=self.spinSigma.value(),
                                    min_size=self.spinMinSize.value(), min_area=self.spinMinArea.value())
            self.picBox = PictureBox(image, regions)
            self.scrollArea.setWidget(self.picBox)
            self.picBox.changedNumberRegions.connect(self.updateLabel)

    @pyqtSlot()
    def saveImage(self):
        if self.picBox:
            fname = self.saveFileDialog()
            if fname:
                self.picBox.savePicture(fname)

    def openFileDialog(self):
        options = QFileDialog.Options()
        # options |= QFileDialog.DontUseNativeDialog
        fileName, _ = QFileDialog.getOpenFileName(self,"Open image file", "","All Files (*);;Tif Files (*.tif)", options=options)
        return fileName

    def saveFileDialog(self):
        options = QFileDialog.Options()
        # options |= QFileDialog.DontUseNativeDialog
        fileName, _ = QFileDialog.getSaveFileName(self,"Save file","","All Files (*);;Tif File (*.tif)", options=options)
        return fileName

def main():
    app = QtWidgets.QApplication([])
    mainWindow = MainWindow()
    mainWindow.show()

    return app.exec()

main()