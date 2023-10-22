from settings import *

BUFFER = list()
SENSORS = (
    "Температура в основании ПЭД",
    "Давление на приёме",
    "Состояние насоса (вкл/выкл)",
    "Давление устьевое",
    "Подача жидкости",
    "Перегруз",
    "Недогруз",
    "Низкое сопротивление изоляции",
    "Отсутствие напряжения",
    "Блокировка",
    "Деблокировка",
    "Включение насоса",
    "Выключение насоса"
)

DB = sqlite3.connect("sensors.db")  # Подключение БД
DB_cursor = DB.cursor()

DB_cursor.execute("DELETE FROM 'values'")  # Удаление записей в таблице БД
DB.commit()


def normal_law(begin: float, end: float, amount: int):
    scale = end - begin
    values = [random.random() for _ in range(amount)]
    return round(sum(values) / amount * scale + begin, 1)


def uniform_law(begin: float, end: float):
    scale = end - begin
    return round(random.random() * scale + begin, 1)


def logic_signal(event_chance: float):
    return 1 if random.random() <= event_chance else 0


def generation():
    values = [
        normal_law(5, 55, 12),      # 1
        uniform_law(0, 2),          # 2
        logic_signal(0.8),          # 3
        uniform_law(0, 1.5),        # 4
        normal_law(0, 400, 12),     # 5
        logic_signal(0.7),          # 6
        logic_signal(0.8),          # 7
        logic_signal(0.8),          # 8
        logic_signal(0.8),          # 9
        logic_signal(0.8),          # 10
        logic_signal(0.8),          # 11
        logic_signal(0.7),          # 12
        logic_signal(0.7)           # 13
    ]
    return values


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

        self.button_start.clicked.connect(self.on_click_button_start)
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.starting)
        self.button_connection.clicked.connect(self.on_click_button_connection)

        self.on_click_button_connection()
        self.text_log.clear()
        self.resize_table()

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
        current_header = self.table_current.horizontalHeader()
        buffer_header = self.table_buffer.horizontalHeader()

        [current_header.setSectionResizeMode(i, QHeaderView.Stretch) for i in range(2)]
        [buffer_header.setSectionResizeMode(i, QHeaderView.Stretch) for i in range(10)]

    def on_click_button_connection(self):
        if self.connection:
            self.connection = False
            self.button_connection.setText("Вкл. связь")
            self.text_log.append("УСТАНОВЛЕН ПРИНУДИТЕЛЬНЫЙ ОБРЫВ СВЯЗИ.")
        else:
            self.connection = True
            self.button_connection.setText("Выкл. связь")
            self.text_log.append("ПРИНУДИТЕЛЬНЫЙ ОБРЫВ СВЯЗИ УБРАН.")

    def on_click_button_start(self):
        if self.timer.isActive():
            self.timer.stop()
            self.button_start.setText("Старт")

            self.text_log.append("За время работы:")
            self.text_log.append(f"{self.packets['sent']} пакетов было передано.")
            self.text_log.append(f"{self.packets['unsent']} пакетов было утеряно.")
            self.text_log.append(f"{round(self.times['connected'], 2)} минут была связь.")
            self.text_log.append(f"{round(self.times['unconnected'], 2)} минут связь отсутствовала.")
        else:
            self.button_start.setText("Стоп")
            self.timer.start(1000)

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