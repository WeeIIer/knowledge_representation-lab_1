from settings import *

Plot = namedtuple("Plot", ["title", "rgb", "x_axis", "timeline"])


class Events:
    def __init__(self, list_events: QtWidgets.QListWidget):
        self.widget = list_events

        self.plots: list[Plot]
        self.states: list[int]
        self.now: int
        self.amount: int

        self.clear()

    def clear(self):
        self.widget.clear()
        self.plots: list[Plot] = []
        self.states: list[int] = []
        self.now = 0
        self.amount = 0

    def add(self, title: str):
        rgb = lambda: (random.random(), random.random(), random.random())

        self.plots.append(Plot(title, rgb(), [], [*repeat(0, self.now), 0]))
        self.widget.addItem(title)
        self.widget.item(self.amount).setCheckState(0)
        self.states.append(0)
        self.amount += 1

    def discard(self, index: int):
        del self.plots[index]
        self.widget.takeItem(index)
        del self.states[index]
        self.amount -= 1

    def next(self):
        self.now += 1

        for i, data in enumerate(self.plots):
            y, _, x_axis, timeline = data
            if self.states[i]:
                if x_axis and self.now - x_axis[-1][-1] == 1:
                    new_points = [self.now]
                    x_axis[-1].extend(new_points)
                else:
                    new_points = [self.now - 1, self.now]
                    x_axis.append(new_points)
                    del timeline[-1]
                timeline.extend(new_points)
            else:
                timeline.append(0)

    def pos(self, user_time: int):
        for i, data in enumerate(self.plots):
            title, _, _, timeline = data
            timeline, chart = timeline[-21:], None

            if timeline[user_time]:
                chart = "-+-"
            elif any(timeline[user_time + 1:]):
                chart = "--+"
            elif any(timeline[: user_time]):
                chart = "+--"
            else:
                chart = "--+"

            self.widget.item(i).setText(f"[{chart}] {title}")



class Tempors:
    def __init__(self, table_tempors: QtWidgets.QTableWidget, events: Events):
        self.widget = table_tempors
        self.widget.clear()
        self.events = events

        self.update()

    def resize_table(self):
        h_header = self.widget.horizontalHeader()
        v_header = self.widget.verticalHeader()

        [h_header.setSectionResizeMode(i, QHeaderView.Stretch) for i in range(self.events.amount)]
        [v_header.setSectionResizeMode(i, QHeaderView.Stretch) for i in range(self.events.amount)]

    def update(self):
        titles = [data.title for data in self.events.plots]

        self.widget.setRowCount(self.events.amount)
        self.widget.setColumnCount(self.events.amount)

        self.widget.setHorizontalHeaderLabels(titles)
        self.widget.setVerticalHeaderLabels(titles)

        self.resize_table()
