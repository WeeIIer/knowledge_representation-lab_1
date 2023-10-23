from settings import *


class Events:
    def __init__(self, list_events: QtWidgets.QListWidget):
        self.widget = list_events
        self.titles = list()
        self.states = list()
        self.now = int()


    def update_widget_events(self, titles):
        self.widget.clear()
        self.titles = list(titles)
        self.states.clear()
        self.now = 1

        for i, name in enumerate(self.titles):
            self.widget.addItem(name)
            self.widget.item(i).setCheckState(0)
            self.states.append(0)

    def next(self):
        self.now += 1
