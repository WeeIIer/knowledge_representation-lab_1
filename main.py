import matplotlib.pyplot
import matplotlib.pyplot as plt

from settings import *
from objects import Events


DB = sqlite3.connect("sensors.db")  # Подключение БД
DB_cursor = DB.cursor()

DB_cursor.execute("DELETE FROM 'values'")  # Удаление записей в таблице БД
DB.commit()


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

        self.sec = 1
        self.time = datetime.datetime.today()
        self.x = list()
        self.y = list()
        self.connection = False
        self.packets = {'sent': 0, 'unsent': 0}
        self.times = {'connected': 0, "unconnected": 0}

        self.events = Events(self.list_events)

        self.button_start.clicked.connect(self.on_click_button_start)
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.starting)

        self.list_events.itemClicked.connect(self.on_selection_changed_list_events)

        self.resize_table()

    def on_selection_changed_list_events(self, item: QtWidgets.QListWidgetItem):
        self.list_events.setCurrentItem(item)
        self.events.states[self.list_events.currentRow()] = item.checkState()

        self.plot_timeline()


    def plot_timeline(self):
        titles = self.events.titles
        x = self.events.states
        y = range(1, len(x) + 1)

        plt.rc('font', size=8)

        fig: matplotlib.pyplot.Figure
        ax: matplotlib.pyplot.Axes
        fig, ax = plt.subplots(1)

        plt.setp(ax, yticks=[*range(1, len(titles) + 1)], yticklabels=titles)

        ax.set(xlim=(0, 20), ylim=(0, len(x) + 1))
        ax.locator_params(axis="x", nbins=20)

        for point_x, point_y, title in zip(x, y, titles):
            ax.plot([0, point_x], [point_y, point_y], label=title, linewidth=10)

        #ax.yaxis.set_label_position("right")
        ax.yaxis.tick_right()
        ax.spines[['right', 'left']].set_visible(False)
        #ax.xaxis.set_visible(False)
        #ax.yaxis.set_visible(False)

        ax.grid(which='major', color='k', linestyle='--')

        # ax.bar_label(bars, y, padding=0, color='white',
        #              fontsize=12, label_type='center', fmt='%.1f%%',
        #              fontweight='bold')

        plt.tight_layout()
        plt.savefig(f"fig.png")
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
        self.events.update_widget_events(f"Событие {i}" for i in range(1, 6))



        # if self.timer.isActive():
        #     self.timer.stop()
        #     self.button_start.setText("Старт")
        #
        #     self.text_log.append("За время работы:")
        #     self.text_log.append(f"{self.packets['sent']} пакетов было передано.")
        #     self.text_log.append(f"{self.packets['unsent']} пакетов было утеряно.")
        #     self.text_log.append(f"{round(self.times['connected'], 2)} минут была связь.")
        #     self.text_log.append(f"{round(self.times['unconnected'], 2)} минут связь отсутствовала.")
        # else:
        #     self.button_start.setText("Стоп")
        #     self.timer.start(1000)

    def starting(self):
        global BUFFER

        time_step = self.double_time_step.value() * 100  # Перевод минут в секунды
        connection_quality = self.double_connection_quality.value()
        current_connection = random.random()
        current_time = (self.time + datetime.timedelta(seconds=self.sec)).strftime("%H:%M:%S")
        packet = generation() + [current_time]
        print(packet)

        if (current_connection <= connection_quality) and self.connection:  # Проверка связи
            self.times["connected"] += self.double_time_step.value()
            self.packets["sent"] += 1
            if BUFFER:
                insert_to_database(BUFFER)
                self.packets["sent"] += len(BUFFER)
                self.text_log.append("Буфер очищен.\nПериод восстановлен.")
                BUFFER.clear()
            insert_to_database([packet])
            self.text_log.append(f"{current_time}: Данные отправлены в БД.")
            self.label_indicator.setStyleSheet("background-color: green;")
        else:
            self.times["unconnected"] += self.double_time_step.value()
            BUFFER.append(packet)
            self.text_log.append(f"{current_time}: Данные отправлены в буфер.")
            self.label_indicator.setStyleSheet("background-color: red;")

        self.write_to_table(self.table_current, packet)  # Запись пакета в таблицы
        self.write_to_table(self.table_buffer, BUFFER)

        if len(BUFFER) == 10:  # Прореживание буфера
            self.packets["unsent"] += 5
            BUFFER = [row for i, row in enumerate(BUFFER, 0) if i % 2 == 0]
            BUFFER.append(packet)

        if len(self.x) > 10:  # Формирование списков для построения графиков
            del self.x[0]
            del self.y[0]
        self.x.append(current_time)
        self.y.append(packet[:-1])

        plot(self.x, self.y)  # Отрисовка графиков
        self.label_plot.clear()
        self.label_plot.setPixmap(QPixmap(f"fig.png"))

        self.sec += time_step  # Увеличение общего времени работы

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