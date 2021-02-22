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
        self.graph.recompute_edges()

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
            self.graph.recompute_edges()
        return super(HandlePoint, self).itemChange(change, value)

    def center(self):
        itemBR = self.boundingRect()
        sceneBR = self.mapRectToParent(itemBR)
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
        self.prepareGeometryChange()
        br = self.boundingRect()
        center = br.center()
        new_rect = QtCore.QRectF(center.x() - size.width() / 2, center.y() - size.height() / 2, size.width(),
                                 size.height())
        self.setRect(new_rect)
        self.graph.recompute_edges()

    def moveTo(self, position):
        self.prepareGeometryChange()
        size = self.getSize()
        new_rect = QtCore.QRectF(position.x() - (size.width() - 1) / 2,
                                 position.y() - (size.height() - 1) / 2,
                                 size.width() - 1,
                                 size.height() - 1)
        self.setRect(new_rect)
        self.recompute_edges()

    def hoverEnterEvent(self, evt):
        self.setTransformOriginPoint(self.mapFromParent(self.center()))
        self.setScale(1.2)
        super(HandlePoint, self).hoverEnterEvent(evt)

    def hoverLeaveEvent(self, evt):
        self.setTransformOriginPoint(self.mapFromParent(self.center()))
        self.setScale(1.0)
        super(HandlePoint, self).hoverEnterEvent(evt)

    def delete_point(self):
        for e in self.edges:
            self.scene().removeItem(e)
        self.scene().removeItem(self)
