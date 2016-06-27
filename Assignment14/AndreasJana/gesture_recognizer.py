from PyQt5 import Qt, QtGui, QtCore, QtWidgets
import sys


app = QtWidgets.QApplication(sys.argv)

class QDrawWidget(QtWidgets.QWidget):

    
    
    def __init__(self, width=800, height=800):
        super().__init__()
        self.resize(width, height)
        self.setFocusPolicy(QtCore.Qt.StrongFocus)
        self.drawing = False
        self.points = []
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

dw = QDrawWidget()

def distance(p1,p2):

    dx = p1[0] - p2[0]

    dy = p1[1] - p2[1]

    return sqrt(dx*dx+dy*dy)

 

def total_length(point_list):

    p1 = point_list[0]

    length = 0.0

    for i in range(1,len(point_list)):

        length += distance(p1,point_list[i])

        p1 = point_list[i]

    return length

def resample(point_list,step_count=64):
    newpoints = []
    length = total_length(point_list)
    stepsize = length/step_count
    curpos = 0
    newpoints.append(point_list[0])
    i = 1
    while i < len(point_list):
        p1 = point_list[i-1]
        d = distance(p1,point_list[i])
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

def transform(points):
    center = (400,400)
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

def custom_filter(points):
    return(transform(points))
