import numpy as np
from pyqtgraph.Qt import QtCore, QtGui


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
        sceneBR = self.mapRectToParent(itemBR)
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
