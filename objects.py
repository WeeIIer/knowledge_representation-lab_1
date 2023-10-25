from settings import *

Plot = namedtuple("Plot", ["title", "rgb", "x_axis"])


class Events:
    def __init__(self, list_events: QtWidgets.QListWidget):
        self.widget = list_events

        self.plots: list[Plot]
        self.states: list[int]
        self.now: int

        self.clear()

    def clear(self):
        self.widget.clear()
        self.plots: list[Plot] = []
        self.states: list[int] = []
        self.now = 0

    def add(self, title: str):
        rgb = lambda: (random.random(), random.random(), random.random())

        self.plots.append(Plot(title, rgb(), []))
        self.widget.addItem(title)
        self.widget.item(len(self.plots) - 1).setCheckState(0)
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


# class Legend:
#     def __init__(self, layout: QtWidgets.QVBoxLayout, titles: Iterable):
#         self.layout = layout
#         self.titles = titles
#
#         self.update()
#
#     def update(self):
#         for title in self.titles:
#             label = QtWidgets.QLabel()
#             label.setText(title)
#             label.setWordWrap(True)
#             self.layout.addWidget(label)
#
#             print(label.width())
