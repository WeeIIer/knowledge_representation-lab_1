from settings import *


class Events:
    def __init__(self, list_events: QtWidgets.QListWidget):
        self.widget = list_events
        self.titles = list()
        self.states = list()


    def update_widget_events(self, titles):
        self.widget.clear()
        self.titles = list(titles)
        self.states.clear()

        for i, name in enumerate(self.titles):
            self.widget.addItem(name)
            self.widget.item(i).setCheckState(0)
            self.states.append(1)
