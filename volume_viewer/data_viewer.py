# -*- coding: utf-8 -*-

import numpy as np
from pyqtgraph.Qt import QtCore, QtGui


class HandlePoint(QtGui.QGraphicsEllipseItem):
    def __init__(self, graph, *args, **kwargs):
        self.edges = []

        super(HandlePoint, self).__init__(*args, **kwargs)
        self.graph = graph
        self.active = False
        self.setFlag(self.ItemIsMovable)
        self.setFlag(self.ItemSendsGeometryChanges)
        self.setCacheMode(self.DeviceCoordinateCache);
        self.setZValue(-1)
        self.setAcceptHoverEvents(True)
        self.size = 1
        self.bd_pt1 = QtCore.QPoint()
        self.bd_pt2 = QtCore.QPoint()
        self.size_state = self.getSize()

    def add_edge(self, edge):
        self.edges.append(edge)
        self.recompute_edges()

    def paint(self, painter, option, widget):
        painter.setPen(QtCore.Qt.NoPen)
        if self.active:
            painter.setBrush(QtGui.QColor(200, 200, 200, 125))
        else:
            painter.setBrush(QtGui.QColor(0, 0, 0, 125))
        painter.drawEllipse(self.boundingRect())

    def getSize(self):
        return self.boundingRect().size()

    def register_size_state(self):
        self.size_state = self.getSize()

    def recompute_edges(self):
        if self.edges:
            angles = [e.get_orientation() for e in self.edges]
            angle = np.mean(angles)
            x, y = self.get_xy()
            size = self.getSize().width() / 3
            self.bd_pt1.setX(int(np.cos(angle + np.pi / 2) * size) + x)
            self.bd_pt1.setY(int(np.sin(angle + np.pi / 2) * size) + y)
            self.bd_pt2.setX(int(np.cos(angle - np.pi / 2) * size) + x)
            self.bd_pt2.setY(int(np.sin(angle - np.pi / 2) * size) + y)
            for e in self.edges:
                e.update_polygon()

    def itemChange(self, change, value):
        if change == self.ItemPositionHasChanged:
            self.recompute_edges()
        return super(HandlePoint, self).itemChange(change, value)

    def center(self):
        itemBR = self.boundingRect()
        sceneBR = self.mapRectToScene(itemBR)
        return sceneBR.center()

    def get_xy(self):
        center = self.center()
        return center.x(), center.y()

    def mousePressEvent(self, evt):
        self.graph.deactivate_all()
        self.active = True
        self.graph.active_point = self
        super(HandlePoint, self).mousePressEvent(evt)
        self.update()

    def setSize(self, size):
        size = QtCore.QSizeF(max(2, size.width() - 1), max(2, size.height() - 1))
        # self.prepareGeometryChange()
        br = self.boundingRect()
        center = br.center()
        new_rect = QtCore.QRectF(center.x() - size.width() / 2, center.y() - size.height() / 2, size.width(),
                                 size.height())
        self.setRect(new_rect)
        self.recompute_edges()

    def moveTo(self, position):
        self.prepareGeometryChange()
        size = self.getSize()
        new_rect = QtCore.QRectF(position.x() - (size.width() - 1) / 2,
                                 position.y() - (size.height() - 1) / 2,
                                 size.width() - 1,
                                 size.height() - 1)
        self.setRect(new_rect)
        self.recompute_edges()
        self.update()

    def mouseReleaseEvent(self, evt):
        super(HandlePoint, self).mouseReleaseEvent(evt)

    def hoverEnterEvent(self, evt):
        self.setTransformOriginPoint(self.mapFromScene(self.center()))
        self.setScale(1.2)
        super(HandlePoint, self).hoverEnterEvent(evt)

    def hoverLeaveEvent(self, evt):
        self.setTransformOriginPoint(self.mapFromScene(self.center()))
        self.setScale(1.0)
        super(HandlePoint, self).hoverEnterEvent(evt)

    def delete_point(self):
        for e in self.edges:
            self.scene().removeItem(e)
        self.scene().removeItem(self)


class Edge(QtGui.QGraphicsPolygonItem):
    def __init__(self, pt1, pt2, *args, **kwargs):
        super(Edge, self).__init__(*args, **kwargs)
        self.setFlag(self.ItemSendsGeometryChanges)
        self.pt1 = pt1
        self.pt2 = pt2
        self.pt1.add_edge(self)
        self.pt2.add_edge(self)
        self.size = 1
        self.setZValue(-2)

        self.update_polygon()

    def update_polygon(self):
        # Todo makes some check to assert the polygon does not intersect himself. Currently solution isnt very pretty
        #  (just does the union of the two possible polygons)
        self.setPolygon(QtGui.QPolygonF([self.pt1.bd_pt1,
                                         self.pt2.bd_pt1,
                                         self.pt2.bd_pt2,
                                         self.pt1.bd_pt2]).united(
            QtGui.QPolygonF([self.pt1.bd_pt2, self.pt2.bd_pt1, self.pt2.bd_pt2, self.pt1.bd_pt1])))

    def center(self):
        itemBR = self.boundingRect()
        sceneBR = self.mapRectToScene(itemBR)
        return sceneBR.center()

    def paint(self, painter, option, widget):
        painter.setPen(QtCore.Qt.NoPen)
        painter.setBrush(QtCore.Qt.blue)
        painter.drawPolygon(self.polygon(), QtCore.Qt.WindingFill)
        # super(Edge, self).paint(painter, option, widget)

    def get_orientation(self):
        vector_dir = self.pt2.center() - self.pt1.center()
        return np.arctan2(vector_dir.y(), vector_dir.x())

    def itemChange(self, change, value):
        return super(Edge, self).itemChange(change, value)


class Label:
    def __init__(self, scene):
        self.scene = scene
        self.list_points = []
        self.minimum_distance_between_points = 10
        self.default_point_size = 10
        self.path = QtGui.QPainterPath()
        self.selected = True
        self.active_point = None

    def add_point(self, point, ignore_limit=False):
        x, y = point.x(), point.y()
        new_handle = HandlePoint(self, x - self.default_point_size / 2, y - self.default_point_size / 2,
                                 self.default_point_size, self.default_point_size)
        if ignore_limit or self.outside_min_radius(new_handle):
            self.scene.addItem(new_handle)
            self.list_points.append(new_handle)
            if len(self.list_points) > 1:
                selected_point = self.get_active_point()
                new_handle.setSize(selected_point.getSize())
                self.add_edge(selected_point, new_handle)
                selected_point.recompute_edges()
            self.deactivate_all()
            new_handle.active = True
            self.active_point = new_handle

    def deactivate_all(self):
        if self.active_point is not None:
            self.active_point.active = False
            self.active_point.update()

    def delete_active_point(self):

        self.active_point.delete_point()
        del self.active_point
        self.active_point = None

    def resize_event(self, steps):
        old_size = self.active_point.size_state
        new_size = QtCore.QSizeF(old_size.width() + steps, old_size.height() + steps)
        self.active_point.setSize(new_size)

    def active_point_to_position(self, position):

        self.active_point.moveTo(position)

    def start_extrude(self):
        self.active_point.setAcceptHoverEvents(False)
        self.add_point(self.active_point.center(), True)

    def end_extrude(self):
        self.active_point.setAcceptHoverEvents(True)

    def register_resize_event(self):
        for pt in self.list_points:
            if pt.active:
                pt.register_size_state()

    def get_active_point(self):
        for pt in self.list_points:
            if pt.active: return pt

    def add_edge(self, start_pt, end_pt):
        new_edge = Edge(start_pt, end_pt)
        self.scene.addItem(new_edge)
        new_edge.update()

    def outside_min_radius(self, handle):
        return all([(
                            other_handle.center() - handle.center()).manhattanLength() > other_handle.getSize().width() + self.minimum_distance_between_points
                    for other_handle in self.list_points])

    # def update_line(self):
    #     self.setPath(self.path)


modeDefault = 0
modeAdd = 0
modeExtrude = 1
modeResize = 2


class MyGraphicsView(QtGui.QGraphicsView):

    def __init__(self, *args, **kwargs):
        super(MyGraphicsView, self).__init__(*args, **kwargs)
        self.list_points = []
        self.item_path = Label(self.scene())
        self.setRenderHint(QtGui.QPainter.Antialiasing)
        self.current_mode = modeDefault
        self.enteredResizeMousePos = QtCore.QPointF()
        self.mousePos = QtCore.QPointF()

    def mousePressEvent(self, evt):
        if evt.button() == QtCore.Qt.LeftButton:
            if self.current_mode == modeAdd:
                mousePoint = self.mapToScene(evt.pos())
                self.item_path.add_point(mousePoint)
            if self.current_mode == modeResize:
                self.current_mode = modeAdd
            if self.current_mode == modeExtrude:
                self.item_path.end_extrude()
                self.current_mode = modeAdd
        super(MyGraphicsView, self).mousePressEvent(evt)

    def keyPressEvent(self, evt):
        if evt.key() == QtCore.Qt.Key_Escape:

            if self.current_mode == modeResize:
                self.item_path.resize_event(0)
                self.current_mode = modeAdd
            if self.current_mode == modeExtrude:
                self.item_path.delete_active_point()
        elif evt.key() == QtCore.Qt.Key_X:
            self.item_path.delete_active_point()

        elif evt.key() == QtCore.Qt.Key_S:
            self.enteredResizeMousePos = self.mousePos
            self.item_path.register_resize_event()
            self.current_mode = modeResize

        elif evt.key() == QtCore.Qt.Key_E:
            self.current_mode = modeExtrude
            self.item_path.start_extrude()

        super(MyGraphicsView, self).keyPressEvent(evt)

    def wheelEvent(self, evt):
        super(MyGraphicsView, self).wheelEvent(evt)

    def mouseReleaseEvent(self, evt):
        super(MyGraphicsView, self).mouseReleaseEvent(evt)

    def mouseMoveEvent(self, evt):
        self.mousePos = self.mapToScene(evt.pos())
        if self.current_mode == modeResize:
            factor = -1 if self.mousePos.x() < self.enteredResizeMousePos.x() else 1
            steps = (self.enteredResizeMousePos - self.mousePos).manhattanLength()
            self.item_path.resize_event(factor * steps)

        elif self.current_mode == modeExtrude:
            self.item_path.active_point_to_position(self.mousePos)
        else:
            super(MyGraphicsView, self).mouseMoveEvent(evt)


app = QtGui.QApplication([])

## Create window with two ImageView widgets
win = QtGui.QMainWindow()
win.resize(1200, 800)
win.show()

win.setWindowTitle('pyqtgraph example: DataSlicing')

cw = QtGui.QWidget()
win.setCentralWidget(cw)
l = QtGui.QGridLayout()
cw.setLayout(l)

scene = QtGui.QGraphicsScene(0, 0, 1000, 800)
scene.setSceneRect(0, 0, 512, 512)
view = MyGraphicsView(scene)
l.addWidget(view)
view.resize(512, 512);

# imv1 = pg.ImageView()
# imv2 = pg.ImageView()
# w = gl.GLViewWidget()
#
# l.addWidget(imv1, 0, 0)
# l.addWidget(imv2, 1, 0)
# l.addWidget(w, 0, 1)
# win.show()
#
# g = gl.GLGridItem()
# g.scale(100, 100, 100)
# w.addItem(g)
#
# roi = pg.LineSegmentROI([[10, 64], [120, 64]], pen='r')
# imv1.addItem(roi)
# path = '/media/clement/SAMSUNG/AMD/data/patients/1554268 FILLION, CHARLES-HENRI/2020-02-18/OD/structural_oct_6mmx6mm/'
# data = read_images_to_np(path)
# data = data.transpose((0,2,1))

# def update():
#     global data, imv1, imv2
#     d2 = roi.getArrayRegion(data, imv1.imageItem, axes=(1, 2))
#     imv2.setImage(d2)
#
# roi.sigRegionChanged.connect(update)

## Display the data
# imv1.setImage(data/255.)
# imv1.setHistogramRange(0, 1)
# imv1.setLevels(0, 1)
# data = np.expand_dims(data, 3)
# data = np.repeat(data, 4, axis=3)
# v = gl.GLVolumeItem(data[:,: ,::-1])
# v.translate(-50,-250,-1536//2)
# w.addItem(v)
# ax = gl.GLAxisItem()
# w.addItem(ax)
# update()

## Start Qt event loop unless running in interactive mode.
if __name__ == '__main__':
    import sys

    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QApplication.instance().exec_()
