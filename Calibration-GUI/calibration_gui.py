import sys
from PyQt6.QtWidgets import (QApplication, QWidget, QStackedWidget, QPushButton,
QHBoxLayout, QGridLayout, QFileDialog, QVBoxLayout, QMainWindow, QGraphicsView,
QGraphicsScene)
from PyQt6.QtGui import QPixmap, QImage, QColor, QPainter
from PyQt6.QtCore import Qt, pyqtSignal, QRectF
import numpy as np
import calibrationDataManager as cdm

class mainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # Create the central widget
        self.centralwidget = QWidget()

        # Create the widgets
        self.buttonsWidget = buttonsWidget()
        self.imageWidget = imageWidget()
        self.stackedWidget = stackedWidget()

        # Connect signal from undistortImage widget with image widget
        self.stackedWidget.undistortWidget.imageLoaded.connect(self.imageWidget.setImage)

        # Connect signal from undistortImage widget with image widget
        self.stackedWidget.undistortWidget.imageUndistorted.connect(self.imageWidget.setUndistortedImage)

        # Connect signal from button widget to stacked widget
        self.buttonsWidget.previousNextClicked.connect(self.stackedWidget.changeIndex)

        # Connect signal from calibrations point widget to image widget
        self.stackedWidget.calibrationPointsWidget.savePointsButtonClicked.connect(self.imageWidget.writePointsToFile)

        self.stackedWidget.checkResultWidget.calibrationChecked.connect(self.imageWidget.setCheckImage)

        # self.stackedWidget.undistortWidget.signal.connect(self.imageWidget.setImage)

        # Create the layout an add the widgets
        centralLayout = QGridLayout()
        centralLayout.addWidget(self.buttonsWidget, 1, 0, 2, 1)
        centralLayout.addWidget(self.imageWidget, 0, 0, 1, 1)
        centralLayout.setColumnStretch(0, 1)
        centralLayout.addWidget(self.stackedWidget, 0, 1, 1, 1)
        centralLayout.setColumnStretch(1, 0)
        self.centralwidget.setLayout(centralLayout)
        self.setCentralWidget(self.centralwidget)

class calibrationPointsWidget(QWidget):
    def __init__(self):
        super().__init__()

        self.savePointsButton = QPushButton("Save Points")
        self.savePointsButton.clicked.connect(self.sendSignal)

        # Create a layout and add the button
        layout = QVBoxLayout()
        layout.addWidget(self.savePointsButton)
        self.setLayout(layout)

    savePointsButtonClicked = pyqtSignal()

    def sendSignal(self):
        self.savePointsButtonClicked.emit()

class undistortWidget(QWidget):
    def __init__(self):
        super().__init__()

        self.loadImageButton = QPushButton("Load Image")
        self.loadImageButton.clicked.connect(self.loadImage)
        
        self.loadCalibrationButton = QPushButton("Load Calibration File")
        self.loadCalibrationButton.clicked.connect(self.loadCalibration)

        self.undistortButton = QPushButton("Undistort Image")
        self.undistortButton.clicked.connect(self.undistortImage)

        #self.undistortButton = QPushButton("Undistort Image")

        # Create a layout and add the button
        layout = QVBoxLayout()
        layout.addWidget(self.loadImageButton)
        layout.addWidget(self.loadCalibrationButton)
        layout.addWidget(self.undistortButton)
        self.setLayout(layout)

    imageLoaded = pyqtSignal()
    imageUndistorted = pyqtSignal()

    def loadImage(self):
        # Show a file dialog to choose an image file
        fileName, _ = QFileDialog.getOpenFileName(self, 'Open Image', '', 'Images (*.jpg *.png);;All Files (*)')

        # Load the image and set it as the pixmap for the label
        if fileName:
            self.imageFile = fileName
            cdm.set_image_file(fileName)
            self.imageLoaded.emit()

    def loadCalibration(self):
        # Show a file dialog to choose a calibration file
        fileName, _ = QFileDialog.getOpenFileName(self, 'Open Calibration File', '', 'All Files (*)')

        # Load the image and set it as the pixmap for the label
        if fileName:
            self.calibrationFile = fileName
            cdm.set_calibration_file(fileName)

    def undistortImage(self):
        # Undistort image and send signal
        cdm.undistort_image()
        self.imageUndistorted.emit()

class stackedWidget(QWidget):
    def __init__(self):
        super().__init__()

        self.stackedW = QStackedWidget()

        self.undistortWidget = undistortWidget()
        self.calibrationPointsWidget = calibrationPointsWidget()
        self.convertWidget = convertWidget()
        self.checkResultWidget = checkResultWidget()

        self.stackedW.addWidget(self.undistortWidget)
        self.stackedW.addWidget(self.calibrationPointsWidget)
        self.stackedW.addWidget(self.convertWidget)
        self.stackedW.addWidget(self.checkResultWidget)

        layout = QVBoxLayout()
        layout.addWidget(self.stackedW)
        self.setLayout(layout)

    def changeIndex(self, change):
        self.stackedW.setCurrentIndex(self.stackedW.currentIndex() + change)
        
class customScene(QGraphicsScene):
    def __init__(self):
        super().__init__()

    pointAdded = pyqtSignal(float, float)
    pointDeleted = pyqtSignal()
        
    def mousePressEvent(self, event):
        # Check if the left mouse button was clicked
        if event.button() == Qt.MouseButton.LeftButton:
            position = event.scenePos()
            # Draw a cross at the clicked point
            self.addLine(position.x() - 5, position.y(), position.x() + 5, position.y(), pen=QColor(255, 0, 0))
            self.addLine(position.x(), position.y() - 5, position.x(), position.y() + 5, pen=QColor(255, 0, 0))
            self.pointAdded.emit(position.x(), position.y())        

        if event.button() == Qt.MouseButton.RightButton:
            self.pointDeleted.emit()

class imageWidget(QWidget):
    def __init__(self):
        super().__init__()

        self.pixmap = QPixmap()
        self.view = QGraphicsView()
        self.scene = customScene()
        self.view.setScene(self.scene)
        # Create a layout and add the label
        wLayout = QHBoxLayout()
        wLayout.addWidget(self.view)
        self.setLayout(wLayout)

        self.scene.pointAdded.connect(self.addPoint)
        self.scene.pointDeleted.connect(self.deletePoint)
        self.imageStorage =[]

    def setImage(self):
        # Load the image and display it in the label, the image is scaled to the size of the label
        self.pixmap = QPixmap(cdm.get_image_file())
        self.scene.addPixmap(self.pixmap)
        if len(self.imageStorage) == 0:
            self.imageStorage.append(self.pixmap)
        else:
            self.imageStorage[0] = self.pixmap

    def setUndistortedImage(self):
        # Load the image and display it in the label, the image is scaled to the size of the label
        self.pixmap = QPixmap(cdm.get_undistorted_image_file())
        self.scene.clear()
        self.scene.addPixmap(self.pixmap)
        self.imageStorage.append(self.pixmap)

    def saveScene(self):
        self.scene.clearSelection()
        self.scene.setSceneRect(self.scene.itemsBoundingRect())
        image = QImage(self.scene.sceneRect().size().toSize(), QImage.Format.Format_ARGB32)
        image.fill(Qt.GlobalColor.transparent)
        painter = QPainter(image)
        self.scene.render(painter)
        image.save("saveSceneTest.jpg", "JPG")

    def getSceneAsImage(self):
        # Get the size of your graphicsview
        rect = self.scene.sceneRect()
        pixmap = QPixmap(rect.size().toSize())
        painter = QPainter(pixmap)
        self.scene.render(painter, QRectF(), rect)
        pixmap.save("testAgain.png")
        painter.end()
        return pixmap
    
    def getSceneAsNPArray(self):
        image = self.getSceneAsImage()
        image = image.toImage()
        image = image.convertToFormat(QImage.Format.Format_RGB32)

        width = image.width()
        height = image.height()

        ptr = image.constBits()
        ptr.setsize(height * width * 4)
        image_array = np.frombuffer(ptr, np.uint8).reshape(height, width, 4)
        return image_array

    def addPoint(self, xCoord, yCoord):
        point = np.array([int(xCoord), int(yCoord)])
        print("added point: (" + str(int(xCoord)) + ", " + str(int(yCoord)) + ")")
        #image = self.getSceneAsNPArray()
        cdm.storage.add_points(point)
        pixmap = self.getSceneAsImage()
        self.imageStorage.append(pixmap)
        print("total points: " + str(len(cdm.storage.obj_pts)))

    def deletePoint(self):
        cdm.storage.delete_point()
        self.imageStorage.pop()
        self.scene.clear()
        self.scene.addPixmap(self.imageStorage[-1])
        print("deleted last point")
        print("total points: " + str(len(cdm.storage.obj_pts)))
        
    def writePointsToFile(self):
        cdm.saveStorageToFile()

    def setCheckImage(self):
        self.pixmap = QPixmap(cdm.get_check_image_file())
        self.scene.clear()
        self.scene.addPixmap(self.pixmap)

class convertWidget(QWidget):
    def __init__(self):
        super().__init__()

        self.loadCoordsButton = QPushButton("Load Coordinates File")
        self.loadCoordsButton.clicked.connect(self.loadCoords)
        
        self.convertButton = QPushButton("Convert Coordinates")
        self.convertButton.clicked.connect(self.convertCoords)

        # Create a layout and add the button
        layout = QVBoxLayout()
        layout.addWidget(self.loadCoordsButton)
        layout.addWidget(self.convertButton)
        self.setLayout(layout)

    def loadCoords(self):
        # Show a file dialog to choose an image file
        fileName, _ = QFileDialog.getOpenFileName(self, 'Open Coordinate File', '', 'Coordinate Files (*.csv *.geojson);;All Files (*)')

        # Load the image and set it as the pixmap for the label
        if fileName:
            self.imageFile = fileName
            cdm.set_original_coordinates_file(fileName)

    def convertCoords(self):
        cdm.convert_to_opencv()

class checkResultWidget(QWidget):
    def __init__(self):
        super().__init__()

        self.loadConfigButton = QPushButton("Check Results")
        self.loadConfigButton.clicked.connect(self.checkResults)
        
        self.updateConfigButton = QPushButton("Update Config")
        self.updateConfigButton.clicked.connect(self.updateConfig)

        # Create a layout and add the buttons
        layout = QVBoxLayout()
        layout.addWidget(self.updateConfigButton)
        layout.addWidget(self.loadConfigButton)
        self.setLayout(layout)

    calibrationChecked = pyqtSignal()

    def checkResults(self):
        cdm.check_calibration()
        self.calibrationChecked.emit()

    def updateConfig(self):
        fileName, _ = QFileDialog.getOpenFileName(self, 'Open Coordinate File', '', 'Config Files (*.ini);;All Files (*)')
        if fileName:
            cdm.updateConfig(fileName)
        cdm.set_config_file(fileName)

class buttonsWidget(QWidget):
    def __init__(self):
        super().__init__()

        self.buttonNext = QPushButton("Next")
        self.buttonNext.clicked.connect(self.gotoNext)
        self.buttonPrevious = QPushButton("Previous")
        self.buttonPrevious.clicked.connect(self.gotoPrevious)
        buttonLayout = QHBoxLayout()
        buttonLayout.addWidget(self.buttonPrevious)
        buttonLayout.addWidget(self.buttonNext)
        self.setLayout(buttonLayout)

    previousNextClicked = pyqtSignal(int)

    def gotoNext(self):
       self.previousNextClicked.emit(1)
        
    def gotoPrevious(self):
       self.previousNextClicked.emit(-1)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    widget = mainWindow()
    widget.showMaximized()
    # widget.show()
    sys.exit(app.exec())