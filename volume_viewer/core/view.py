import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtGui
from pyqtgraph.graphicsItems import ImageItem

from core.edge import Edge
from core.point import HandlePoint


class Label:
    def __init__(self, parent, scene):
        self.parent = parent
        self.scene = scene
        self.list_points = []
        self.minimum_distance_between_points = 10
        self.default_point_size = 10
        self.path = QtGui.QPainterPath()
        self.selected = True
        self.active_point = None

    def recompute_edges(self, reversed=True):
        order = -1 if reversed else 1
        for pt in self.list_points[::order]:
            pt.recompute_edges()

    def add_point(self, point, ignore_limit=False):
        x, y = point.x(), point.y()
        new_handle = HandlePoint(self, x - self.default_point_size / 2, y - self.default_point_size / 2,
                                 self.default_point_size, self.default_point_size, self.parent)
        if ignore_limit or self.outside_min_radius(new_handle):
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
        self.active_point = self.list_points[-1]

    def resize_event(self, steps):
        old_size = self.active_point.size_state
        new_size = QtCore.QSizeF(old_size.width() + steps, old_size.height() + steps)
        self.active_point.setSize(new_size)

    def active_point_to_position(self, position):
        self.active_point.moveTo(position)

    def start_extrude(self):
        self.active_point.setAcceptHoverEvents(False)
        self.add_point(self.active_point.center(), True)
        self.active_point.setAcceptedMouseButtons(QtCore.Qt.NoButton)

    def end_extrude(self):
        self.active_point.setAcceptHoverEvents(True)
        self.active_point.setAcceptedMouseButtons(QtCore.Qt.AllButtons)
        self.recompute_edges()

    def start_resize(self):
        self.active_point.register_size_state()
        self.active_point.setAcceptedMouseButtons(QtCore.Qt.NoButton)

    def end_resize(self):
        self.active_point.setAcceptedMouseButtons(QtCore.Qt.AllButtons)

    def get_active_point(self):
        return self.active_point

    def add_edge(self, start_pt, end_pt):
        new_edge = Edge(start_pt, end_pt, self.parent)
        new_edge.update()

    def outside_min_radius(self, handle):
        return all([(
                            other_handle.center() - handle.center()).manhattanLength() > other_handle.getSize().width() + self.minimum_distance_between_points
                    for other_handle in self.list_points])


modeDefault = -1
modeAdd = 0
modeExtrude = 1
modeResize = 2


class DrawableImageItem(ImageItem.ImageItem):
    def __init__(self, *args, **kwargs):
        super(DrawableImageItem, self).__init__(*args, **kwargs)

        self.current_mode = modeAdd
        self.enteredResizeMousePos = QtCore.QPointF()
        self.mousePos = QtCore.QPointF()

    def setScene(self, scene):
        self.item_path = Label(self, scene)
        self.scene = scene

    def mousePressEvent(self, evt):
        super(DrawableImageItem, self).mousePressEvent(evt)

    def mousePressed(self, evt):
        if evt.button() == QtCore.Qt.LeftButton:

            if self.current_mode == modeAdd:
                mousePoint = self.mapFromScene(evt.pos())
                self.item_path.add_point(mousePoint)
            if self.current_mode == modeResize:
                self.current_mode = modeDefault
                self.item_path.end_resize()
            if self.current_mode == modeExtrude:
                self.item_path.end_extrude()
                self.current_mode = modeDefault

    def keyEvent(self, evt):
        if evt.key() == QtCore.Qt.Key_Escape:

            if self.current_mode == modeResize:
                self.item_path.resize_event(0)
                self.item_path.end_resize()
                self.current_mode = modeAdd

            if self.current_mode == modeExtrude:
                self.item_path.delete_active_point()
        elif evt.key() == QtCore.Qt.Key_X:
            self.item_path.delete_active_point()

        elif evt.key() == QtCore.Qt.Key_S:
            self.enteredResizeMousePos = self.mousePos
            self.item_path.start_resize()
            self.current_mode = modeResize

        elif evt.key() == QtCore.Qt.Key_E:
            if self.current_mode == modeExtrude: self.item_path.end_extrude()
            self.current_mode = modeExtrude
            self.item_path.start_extrude()
        else:
            super(DrawableImageItem, self).keyPressEvent(evt)

    def mouseMoved(self, pos):
        self.mousePos = self.mapFromScene(pos)
        if self.current_mode == modeResize:
            factor = -1 if self.mousePos.x() < self.enteredResizeMousePos.x() else 1
            steps = (self.enteredResizeMousePos - self.mousePos).manhattanLength()
            self.item_path.resize_event(factor * steps)

        elif self.current_mode == modeExtrude:
            self.item_path.active_point_to_position(self.mousePos)


class DrawableImage(pg.ImageView):
    def __init__(self, *args, **kwargs):
        img_item = DrawableImageItem()
        super(DrawableImage, self).__init__(imageItem=img_item, *args, **kwargs)
        img_item.setScene(self.scene)
        # self.imageItem.scene.mouseMoveEvent = self.mouseMove
        self.scene.sigMouseMoved.connect(self.getImageItem().mouseMoved)
        self.scene.sigMouseClicked.connect(self.getImageItem().mousePressed)

    def keyPressEvent(self, evt):
        self.imageItem.keyEvent(evt)

    # def mousePressEvent(self, evt):
    #     super(DrawableImage, self).mousePressEvent(evt)
