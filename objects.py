from settings import *
from itertools import repeat


class Events:
    def __init__(self, list_events: QtWidgets.QListWidget):
        self.widget = list_events
        self.plots: dict[str:list[list[int]]]
        self.states: list[int]
        self.now: int

    def update_widget_events(self, titles):
        rgb = lambda: (random.random(), random.random(), random.random())

        self.widget.clear()
        self.plots = dict(((i, title, rgb()), []) for i, title in enumerate(titles, 0))
        self.states = []
        self.now = 0

        for i, title, _ in self.plots.keys():
            self.widget.addItem(title)
            self.widget.item(i).setCheckState(0)
            self.states.append(0)

    def next(self):
        self.now += 1

        for data, plots in self.plots.items():
            i, title, _ = data
            if self.states[i]:
                if plots and self.now - plots[-1][-1] == 1:
                    plots[-1].append(self.now)
                else:
                    plots.append([self.now])

        #print(self.plots.values())
