from settings import *

Plot = namedtuple("Plot", ["title", "rgb", "x_axis"])


class Events:
    def __init__(self, list_events: QtWidgets.QListWidget):
        self.widget = list_events

        self.plots: list[Plot]
        self.states: list[int]
        self.now: int

    def update_widget_events(self, titles):
        rgb = lambda: (random.random(), random.random(), random.random())

        self.widget.clear()
        self.plots = [Plot(title, rgb(), []) for title in titles]
        self.states = []
        self.now = 0

        for i, data in enumerate(self.plots):
            self.widget.addItem(data.title)
            self.widget.item(i).setCheckState(0)
            self.states.append(0)

    def next(self):
        self.now += 1

        for i, data in enumerate(self.plots):
            _, _, x_axis = data
            if self.states[i]:
                if x_axis and self.now - x_axis[-1][-1] == 1:
                    x_axis[-1].append(self.now)
                else:
                    x_axis.append([self.now])

        #print(self.plots.values())
