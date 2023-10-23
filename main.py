import matplotlib.pyplot
import matplotlib.pyplot as plt

from settings import *
from objects import Events


# DB = sqlite3.connect("sensors.db")  # Подключение БД
# DB_cursor = DB.cursor()
#
# DB_cursor.execute("DELETE FROM 'values'")  # Удаление записей в таблице БД
# DB.commit()


def insert_to_database(rows: list[list]):
    for row in rows:
        sql_request = "INSERT INTO 'values' VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"
        DB_cursor.execute(sql_request, row)
        DB.commit()


def plot(x: list, y: list):
    lims = [
        (5, 55),
        (0, 2),
        (0, 1),
        (0, 1.5),
        (0, 400),
        (0, 1),
        (0, 1),
        (0, 1),
        (0, 1),
        (0, 1),
        (0, 1),
        (0, 1),
        (0, 1)
    ]

    figure, axis = plt.subplots(13, 1)
    figure.set_figwidth(10)
    figure.set_figheight(12)
    figure.set_dpi(100)

    for i in range(13):
        axis[i].plot(x, [col[i] for col in y], color="red", linewidth=2)
        axis[i].set_ylim(lims[i][0] - 0.1, lims[i][1] + 0.1)
        axis[i].set_title(i + 1, x=-0.05, y=0.25)
        axis[i].xaxis.set_tick_params(labelsize=8)
        if i < 12:
            axis[i].set_xticklabels([])
        #axis[i].margins(x=0)
        #axis[i].get_xaxis().set_visible(False)
        axis[i].get_yaxis().set_visible(False)
        axis[i].grid(which='major', color='k', linestyle='-')
        #axis[i].grid(axis="x", linewidth=1)

        #axis[i].spines["top"].set_color("k")
        #axis[i].spines["top"].set_linestyle(":")
        #axis[i].spines["bottom"].set_color("k")
        #axis[i].spines["bottom"].set_linestyle(":")
        axis[i].spines["left"].set_visible(False)
        axis[i].spines["right"].set_visible(False)

    plt.subplots_adjust(wspace=0, hspace=0)
    plt.savefig(f"fig.png", bbox_inches='tight', pad_inches=0, transparent=True)
    #plt.show()


class MainWindow(QWidget, main_window_form.Ui_main_window):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.setupUi(self)

        self.events = Events(self.list_events)
        self.events.update_widget_events(f"Событие {i}" for i in range(1, 6))

        self.button_start.clicked.connect(self.on_click_button_start)
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.starting)
        self.list_events.itemClicked.connect(self.on_selection_changed_list_events)

        self.resize_table()

    def on_selection_changed_list_events(self, item: QtWidgets.QListWidgetItem):
        self.list_events.setCurrentItem(item)
        self.events.states[self.list_events.currentRow()] = item.checkState()

    def plot_timeline(self):
        titles = [data.title for data in self.events.plots]
        y_axis = range(1, len(titles) + 1)

        plt.rc('font', size=8)
        fig: matplotlib.pyplot.Figure
        ax: matplotlib.pyplot.Axes
        fig, ax = plt.subplots(1)
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

        #ax.yaxis.set_label_position("right")
        ax.yaxis.tick_right()
        #ax.spines[['right', 'left']].set_visible(False)
        #ax.xaxis.set_visible(False)
        #ax.yaxis.set_visible(False)

        ax.grid(which='major', color='k', linestyle='--')

        # ax.bar_label(bars, y, padding=0, color='white',
        #              fontsize=12, label_type='center', fmt='%.1f%%',
        #              fontweight='bold')

        plt.tight_layout()
        plt.savefig(f"fig.png")
        plt.close()
        self.label_plot.clear()
        self.label_plot.setPixmap(QPixmap(f"fig.png"))


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