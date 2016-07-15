from PyQt5.QtWidgets import QUndoCommand


class DragOperation(QUndoCommand):
    """
    Class representing a drag operation on a widget.
    Adjusting the position through the apply method.
    """

    def __init__(self, widget, event):
        super(DragOperation, self).__init__()
        self.widget = widget  # type: QWidget
        self.widgetStartPos = self.widget.pos()
        self.dragStartPos = self.__getEventPos__(event)
        self.undone = False
        self.changed = False

    def apply(self, event):
        self.changed = True
        eventPos = self.__getEventPos__(event)
        self.latestEventDiff = eventDiff = eventPos - self.dragStartPos
        self.latestDragPosition = self.widgetStartPos + eventDiff
        self.widget.move(self.latestDragPosition)

    def __getEventPos__(self, event):
        return event.globalPos()

    def undo(self):
        self.undone = True
        self.widget.move(self.widgetStartPos)

    def redo(self):
        if not hasattr(self, "latestDragPosition"):
            return
        if (self.undone):
            self.widget.move(self.widget.pos() + self.latestEventDiff)
        else:
            self.widget.move(self.latestDragPosition)
