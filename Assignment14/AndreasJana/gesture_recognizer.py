from PyQt5 import QtGui, QtCore, QtWidgets, uic
import sys
from pylab import *

class GestureRecognizer(QtWidgets.QWidget):
    def __init__(self, width=800, height=800):
        super().__init__()
        self.resize(width, height)
        self.setFocusPolicy(QtCore.Qt.StrongFocus)
        self.drawing = False
        self.points = []
        self.uniStrokes = []
        #QtGui.QCursor.setPos(self.mapToGlobal(QtCore.QPoint(*self.start_pos)))
        self.setMouseTracking(True) # only get events when button is pressed
        self.initUI()

    def initUI(self): 
        palette = QtGui.QPalette()     
        palette.setColor(QtGui.QPalette.Foreground, QtCore.Qt.red)
        self.text = "Press N to add a new gesture; press R to recognize your gesture"
        self.setWindowTitle('Drawable')
        self.show()

    def mousePressEvent(self, ev):
        if ev.button() == QtCore.Qt.LeftButton:
            self.drawing = True
            self.points = []
            self.update()
        elif ev.button() == QtCore.Qt.RightButton:
            self.points = self.resample(self.points)
            self.points = self.rotateBy(self.points)
            self.points = self.scaleTo(self.points)
            self.points = self.translateToCenter(self.points)
            
            self.update()
            
    def mouseReleaseEvent(self, ev):
        if ev.button() == QtCore.Qt.LeftButton:
            self.drawing = False
            self.update() 

    def mouseMoveEvent(self, ev):
        if self.drawing:
            self.points.append((ev.x(), ev.y()))
            self.update() 

    def keyPressEvent(self, ev):
        if ev.text() == 'n':
            self.points = self.resample(self.points)
            self.points = self.rotateBy(self.points)
            self.points = self.scaleTo(self.points)
            self.points = self.translateToCenter(self.points)
            self.addGesture(self.points, len(self.uniStrokes))
        elif ev.text() == 'r':
            self.recognize(self.points)
    
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
        self.drawText(ev, qp)
        for point in self.points:
            qp.drawEllipse(point[0]-1, point[1] - 1, 2, 2)
        qp.end()

    def drawText(self, ev, qp):
        qp.setPen(QtGui.QColor(0, 155, 0))
        qp.setFont(QtGui.QFont('Decorative', 20))
        qp.drawText(ev.rect(), QtCore.Qt.AlignTop, self.text)
     
    def distance(self, p1,p2):
        dx = p1[0] - p2[0]
        dy = p1[1] - p2[1]
        return sqrt(dx*dx+dy*dy)

    def total_length(self, point_list):
        p1 = point_list[0]
        length = 0.0
        for i in range(1,len(point_list)):
            length += self.distance(p1,point_list[i])
            p1 = point_list[i]
        return length

    def resample(self, point_list,step_count=64):
        newpoints = []
        length = self.total_length(point_list)
        stepsize = length/step_count
        curpos = 0
        newpoints.append(point_list[0])
        i = 1
        while i < len(point_list):
            p1 = point_list[i-1]
            d = self.distance(p1,point_list[i])
            if curpos+d >= stepsize:
                nx = p1[0] + ((stepsize-curpos)/d)*(point_list[i][0]-p1[0])
                ny = p1[1] + ((stepsize-curpos)/d)*(point_list[i][1]-p1[1])
                newpoints.append([nx,ny])
                point_list.insert(i,[nx,ny])
                curpos = 0
            else:
                curpos += d
            i += 1
        return newpoints
    
    def translateToCenter(self, points):
        center = (400, 400)
        cur_center = self.findCentroid(points)
        new_points = []
        for i in range(len(points)):
            qx = points[i][0] + center[0] - cur_center[0]
            qy = points[i][1] + center[1] - cur_center[1]
            new_points.append((qx, qy))
        return new_points

    def rotateBy(self, points):
        center = self.findCentroid(points)
        radians = arctan2(center[1] - points[0][1], center[0] - points[0][0]) * (-1)
        cur_cos = cos(radians)
        cur_sin = sin(radians)
        newpoints = []
        for i in range(len(points)):
            qx = (points[i][0] - center[0]) * cur_cos - (points[i][1] - center[1]) * cur_sin + center[0]
            qy = (points[i][0] - center[0]) * cur_sin + (points[i][1] - center[1]) * cur_cos + center[1];
            newpoints.append((qx, qy))
        return newpoints

    def boundingBox(self, points):
        minX = float('inf')
        maxX = -1 * float('inf')
        minY = float('inf')
        maxY = -1 * float('inf')
        for i in range(len(points)):
            minX = minimum(minX, points[i][0])
            minY = minimum(minY, points[i][1])
            maxX = maximum(maxX, points[i][0])
            maxY = maximum(maxY, points[i][1])
        return QtCore.QRect(minX, minY, maxX - minX, maxY - minY)

    def scaleTo(self, points):
        b = self.boundingBox(points)
        size = 100
        newpoints = []
        for i in range(len(points)):
            qx = points[i][0] * (size / b.width())
            qy = points[i][1] * (size / b.height())
            newpoints.append((qx, qy))
        return newpoints

    def transform(self, points):
        # center = (400,400)
        center = self.findCentroid(points)
        new_points = []
        r = 5 * (pi / 180)# degrees multmat
        rot_matrix = matrix([[cos(r), -sin(r), 0], # clockwise
                         [sin(r),  cos(r), 0], 
                         [     0,       0, 1]])
        t1 = matrix([[1,0,-center[0]],[0,1,-center[1]],[0,0,1]])
        t2 = matrix([[1,0,center[0]],[0,1,center[1]],[0,0,1]])  

        for point in points:
            hom_point = matrix([[point[0]], [point[1]], [1]])
            transform = t2  @ rot_matrix @ t1
            rotated_point = transform @ hom_point
            new_points.append((int(rotated_point[0]),int(rotated_point[1])))
        return new_points 

    def findCentroid(self, points):
        x = 0.0
        y = 0.0
        for i in range(len(points)):
            x += points[i][0]
            y += points[i][1]
	
        x /= len(points)
        y /= len(points)
        return (x, y)

    def addGesture(self, points, name):
        stroke = (name, points)
        self.uniStrokes.append(stroke)

    def recognize(self, points):
        points = self.resample(points)
        points = self.rotateBy(points)
        points = self.scaleTo(points)
        points = self.translateToCenter(points)
        match = False
        for i in range(len(self.uniStrokes)):
            length, name = self.calculateDistance(self.uniStrokes[i], points)
            if length <= 600.0:
                match = True
                print("Length: ",length)
                print(" Name: ",name)
        if not match:
            print("No matches found!")

        

    def calculateDistance(self, uniStroke, points):
        template = uniStroke[1] 
        length = 0.0
        for i in range(64):
            length += self.distance(template[i], points[i])
        return length, uniStroke[0]


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = GestureRecognizer()
    window.show()

    sys.exit(app.exec_())
