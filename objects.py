from settings import *

Plot = namedtuple("Plot", ["title", "rgb", "x_axis"])
Rates = namedtuple("Rates", ["left_border", "right_border", "length"])


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
        rgb = lambda: (round(random.random(), 2), round(random.random(), 2), round(random.random(), 2))

        self.plots.append(Plot(title, rgb(), []))
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
            y, _, x_axis = data
            if self.states[i]:
                if x_axis and self.now - x_axis[-1][-1] == 1:
                    new_points = [self.now]
                    x_axis[-1].extend(new_points)
                else:
                    new_points = [self.now - 1, self.now]
                    x_axis.append(new_points)

        # print(*self.plots, sep="\n", end="\n\n")

    def pos(self, user_time: int):
        for i, data in enumerate(self.plots):
            title, _, x_axis = data
            event = get_available_event(self.now, x_axis)

            if event is None:
                chart = "--+"
            elif user_time in event:
                chart = "-+-"
            elif user_time < event[-1]:
                chart = "--+"
            else:
                chart = "+--"

            self.widget.item(i).setText(f"[{chart}] {title}")


class Tempors:
    def __init__(self, table_tempors: QtWidgets.QTableWidget, events: Events):
        self.widget = table_tempors
        self.widget.clear()
        self.events = events

        self.update_structure()

    def resize_table(self):
        h_header = self.widget.horizontalHeader()
        v_header = self.widget.verticalHeader()

        [h_header.setSectionResizeMode(i, QHeaderView.Stretch) for i in range(self.events.amount)]
        [v_header.setSectionResizeMode(i, QHeaderView.Stretch) for i in range(self.events.amount)]

    def update_structure(self):
        titles = [data.title for data in self.events.plots]

        self.widget.setRowCount(self.events.amount)
        self.widget.setColumnCount(self.events.amount)

        self.widget.setHorizontalHeaderLabels(titles)
        self.widget.setVerticalHeaderLabels(titles)

        self.resize_table()

    def update_values(self):
        if self.events.plots:
            for i, first_data in enumerate(self.events.plots):
                first_event = get_available_event(self.events.now, first_data.x_axis)

                for j, second_data in enumerate(self.events.plots):
                    second_event = get_available_event(self.events.now, second_data.x_axis)

                    if first_event is None or second_event is None or first_data is second_data:
                        item = QTableWidgetItem("")
                    else:
                        item = QTableWidgetItem(self.__get_relation(first_event, second_event))

                    self.widget.setItem(i, j, item)

    def __get_rates(self, event: list) -> Rates:
        return Rates(event[0], event[-1], len(event))

    def __get_relation(self, first_event: list, second_event: list) -> str:
        first_rates, second_rates = self.__get_rates(first_event), self.__get_rates(second_event)

        types = ("rts", "rtsn", "rtes", "rtel", "rter", "rte")
        pos = 1 if first_rates.left_border < second_rates.left_border else 2

        conditions = (
            any(  # rts
                (
                    first_rates.right_border < second_rates.left_border,
                    second_rates.right_border < first_rates.left_border
                )
            ),
            any(  # rtsn
                (
                    first_rates.right_border == second_rates.left_border,
                    second_rates.right_border == first_rates.left_border
                )
            ),
            any(  # rtes
                (
                    all(
                        (
                            first_rates.left_border < second_rates.left_border,
                            first_rates.right_border < second_rates.right_border
                        )
                    ),
                    all(
                        (
                            first_rates.left_border > second_rates.left_border,
                            first_rates.right_border > second_rates.right_border
                        )
                    ),
                    all(
                        (
                            first_rates.left_border == second_rates.left_border,
                            first_rates.right_border == second_rates.right_border
                        )
                    )
                )
            ),
            all(  # rtel
                (
                    first_rates.left_border == second_rates.left_border,
                    first_rates.length != second_rates.length
                )
            ),
            all(  # rter
                (
                    first_rates.right_border == second_rates.right_border,
                    first_rates.length != second_rates.length
                )
            ),
            any(  # rte
                (
                    all(
                        (
                            first_rates.left_border > second_rates.left_border,
                            first_rates.right_border < second_rates.right_border
                        )
                    ),
                    all(
                        (
                            first_rates.left_border < second_rates.left_border,
                            first_rates.right_border > second_rates.right_border
                        )
                    )
                )
            )
        )

        try:
            return f"{types[conditions.index(True)]}{pos}"
        except ValueError:
            return f"rtu{pos}"


def get_available_event(now: int, x_axis: list) -> list | None:
    left_border = now - 20 if now > 20 else 0

    if x_axis:
        event = x_axis[-1]
        if event[0] >= left_border:
            return event
        else:
            try:
                return event[event.index(left_border):]
            except ValueError:
                return None
    return None
