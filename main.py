import matplotlib.pyplot
import matplotlib.pyplot as plt

from settings import *
from objects import Events


# DB = sqlite3.connect("sensors.db")  # Подключение БД
# DB_cursor = DB.cursor()
#
# DB_cursor.execute("DELETE FROM 'values'")  # Удаление записей в таблице БД
# DB.commit()


class MainWindow(QWidget, main_window_form.Ui_main_window):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.setupUi(self)

        self.events = Events(self.list_events)
        self.events.update_widget_events(f"Событие {i}" for i in range(1, 6))

        self.splitter.restoreState(SETTINGS.value("splitterSizes"))

        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.starting)
        self.button_start.clicked.connect(self.on_click_button_start)
        self.list_events.itemClicked.connect(self.on_selection_changed_list_events)

        self.resize_table()

    def on_selection_changed_list_events(self, item: QtWidgets.QListWidgetItem):
        self.list_events.setCurrentItem(item)
        self.events.states[self.list_events.currentRow()] = item.checkState()

    def plot_timeline(self):
        titles = [data.title for data in self.events.plots]
        y_axis = range(1, len(titles) + 1)

        plt.rc("font", size=8)
        plt.rcParams["font.family"] = "Calibri"

        fig: matplotlib.pyplot.Figure
        ax: matplotlib.pyplot.Axes
        fig, ax = plt.subplots(figsize=(9, 6))
        #plt.setp(ax, yticks=[*y_axis], yticklabels=repeat('', len(y_axis)))
        plt.setp(ax, yticks=[*y_axis], yticklabels=titles)

        ticks_count, now = 20, self.events.now
        past = now - ticks_count if now > ticks_count else 0

        ax.set(xlim=(past, now), ylim=(0, len(titles) + 1))
        ax.locator_params(axis="x", nbins=now - past)

        user_time = self.slider_user_time
        user_time.setMinimum(0)
        user_time.setMaximum(now - past)

        self.edit_current_time.setText(str(now))
        self.edit_user_time.setText(str(now - (now - past - user_time.value())))

        for i, data in enumerate(self.events.plots):
            _, rgb, x_axis = data
            y = y_axis[i]
            for x in x_axis:
                x_begin, x_end = x[0], x[-1]
                ax.plot([x_begin, x_end], [y, y], linewidth=10, color=rgb)

        ax.plot([*repeat(int(self.edit_user_time.text()), 2)], [0, len(titles) + 1], linewidth=3, color="red")

        #ax.yaxis.set_label_position("right")
        ax.yaxis.tick_right()
        #ax.spines[['right', 'left']].set_visible(False)
        #ax.xaxis.set_visible(False)
        #ax.yaxis.set_visible(False)

        ax.grid(which="major", color="k", linestyle="--")

        # ax.bar_label(bars, y, padding=0, color='white',
        #              fontsize=12, label_type='center', fmt='%.1f%%',
        #              fontweight='bold')

        plt.tight_layout()
        plt.savefig("fig.png", transparent=True)
        plt.close()
        self.label_plot.clear()
        self.label_plot.setPixmap(QPixmap("fig.png"))


    def write_to_table(self, table: QTableWidget, values: list):
        table_name = table.objectName()

        if table_name == "table_current":
            for i, value in enumerate(values, 0):
                table.setItem(i, 1, QTableWidgetItem(str(value)))

        elif table_name == "table_buffer":
            self.table_buffer.clear()
            for j, row in enumerate(values, 0):
                j = 9 - j
                for i, value in enumerate(row, 0):
                    table.setItem(i, j, QTableWidgetItem(str(value)))

    def resize_table(self):
        #current_header = self.table_current.horizontalHeader()
        buffer_header = self.table_buffer.horizontalHeader()

        #[current_header.setSectionResizeMode(i, QHeaderView.Stretch) for i in range(2)]
        [buffer_header.setSectionResizeMode(i, QHeaderView.Stretch) for i in range(10)]


    def on_click_button_start(self):
        if self.timer.isActive():
            self.label_indicator.setStyleSheet("background-color: red;")
            self.timer.stop()
            self.button_start.setText("Старт")
        else:
            self.label_indicator.setStyleSheet("background-color: green;")
            self.button_start.setText("Стоп")
            self.timer.start(1000)

    def starting(self):
        self.events.next()

        self.plot_timeline()

    def closeEvent(self, a0):
        super(MainWindow, self).closeEvent(a0)

        SETTINGS.setValue("splitterSizes", self.splitter.saveState())

    def show(self):
        super(MainWindow, self).show()
        self.showMaximized()


app = QApplication(sys.argv)
app.setStyle("fusion")
app.setPalette(palette())
#app.setWindowIcon(QIcon(":/logos/icons/program.png"))

main_window = MainWindow()

main_window.show()
app.exec_()