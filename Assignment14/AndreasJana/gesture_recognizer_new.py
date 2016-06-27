from PyQt5 import QtGui, QtCore, QtWidgets, uic
from functools import partial
import sys

class GestureRecognizer(QtWidgets.QWidget):
    def __init__(self, width=800, height=800):
        super().__init__()
        self.resize(width, height)
        self.setFocusPolicy(QtCore.Qt.StrongFocus)
        self.drawing = False
        self.points = []
        self.Unistrokes = []
        #QtGui.QCursor.setPos(self.mapToGlobal(QtCore.QPoint(*self.start_pos)))
        self.setMouseTracking(True) # only get events when button is pressed
        self.initUI()

    def initUI(self):      
        self.text = "Please click on the target"
        self.setWindowTitle('Drawable')
        self.show()

    def mousePressEvent(self, ev):
        if ev.button() == QtCore.Qt.LeftButton:
            self.drawing = True
            self.points = []
            self.update()
        elif ev.button() == QtCore.Qt.RightButton:
            self.points = custom_filter(self.points)
            self.update()
            
    def mouseReleaseEvent(self, ev):
        if ev.button() == QtCore.Qt.LeftButton:
            self.drawing = False
            self.update() 

    def mouseMoveEvent(self, ev):
        if self.drawing:
            self.points.append((ev.x(), ev.y()))
            self.update() 
    
    def poly(self, pts):
        return QtGui.QPolygonF(map(lambda p: QtCore.QPointF(*p), pts))

    def paintEvent(self, ev):
        qp = QtGui.QPainter()
        qp.begin(self)
        qp.setBrush(QtGui.QColor(0, 0, 0))
        qp.drawRect(ev.rect())
        qp.setBrush(QtGui.QColor(20, 255, 190))
        qp.setPen(QtGui.QColor(0, 155, 0))
        qp.drawPolyline(self.poly(self.points))
        for point in self.points:
            qp.drawEllipse(point[0]-1, point[1] - 1, 2, 2)
        qp.end()

    def Recognize(points, useProtractor):
		points = Resample(points, NumPoints)
		radians = IndicativeAngle(points)
		points = RotateBy(points, -radians)
		points = ScaleTo(points, SquareSize)
		points = TranslateTo(points, Origin)
		vector = Vectorize(points); # for Protractor

		b = +Infinity;
		u = -1;
		for i in range(0,len(self.Unistrokes)): # for each unistroke
			d;
			if (useProtractor):# for Protractor
				d = OptimalCosineDistance(this.Unistrokes[i].Vector, vector)
			else: # Golden Section Search (original $1)
				d = DistanceAtBestAngle(points, this.Unistrokes[i], -AngleRange, +AngleRange, AnglePrecision)
			if (d < b):
				b = d # best (least) distance
				u = i # unistroke
            i +=1
		return (u == -1) ? new Result("No match.", 0.0) : new Result(this.Unistrokes[u].Name, useProtractor ? 1.0 / b : 1.0 - b / HalfDiagonal)


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = GestureRecognizer()
    window.show()

    sys.exit(app.exec_())
