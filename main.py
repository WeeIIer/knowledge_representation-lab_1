import matplotlib.pyplot
import matplotlib.pyplot as plt

from settings import *
from objects import Events, Tempors


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
        self.tempors = Tempors(self.table_tempors, self.events)

        self.splitter.restoreState(SETTINGS.value("splitterSizes"))

        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.starting)
        self.button_start.clicked.connect(self.on_click_button_start)
        self.list_events.itemClicked.connect(self.on_item_clicked_list_events)
        self.list_events.doubleClicked.connect(self.on_double_clicked_list_events)

        self.edit_add_event.returnPressed.connect(self.on_return_pressed_edit_add_event)

        #self.resize_table()

    def on_return_pressed_edit_add_event(self):
        new_event = self.edit_add_event.text().strip()
        if new_event:
            self.events.add(new_event)
            self.tempors.update()

            splits = new_event.split()
            if splits[-1].isdigit():
                splits.append(str(int(splits.pop()) + 1))
                self.edit_add_event.setText(' '.join(splits))

    def on_item_clicked_list_events(self, item: QtWidgets.QListWidgetItem):
        self.list_events.setCurrentItem(item)
        self.events.states[self.list_events.currentRow()] = item.checkState()

    def on_double_clicked_list_events(self):
        self.events.discard(self.list_events.currentRow())
        self.tempors.update()

    def plot_timeline(self):
        titles = [data.title for data in self.events.plots]
        y_axis = range(1, self.events.amount + 1)

        plt.rc("font", size=8)
        plt.rcParams["font.family"] = "Calibri"

        fig: matplotlib.pyplot.Figure
        ax: matplotlib.pyplot.Axes
        fig, ax = plt.subplots(figsize=(9, 6))
        #plt.setp(ax, yticks=[*y_axis], yticklabels=repeat('', len(y_axis)))
        plt.setp(ax, yticks=[*y_axis], yticklabels=titles)

        ticks_count, now = 20, self.events.now
        past = now - ticks_count if now > ticks_count else 0

        ax.set(xlim=(past, now), ylim=(0, self.events.amount + 1))
        ax.locator_params(axis="x", nbins=now - past)

        slider = self.slider_user_time
        slider.setMinimum(0)
        slider.setMaximum(now - past)

        user_time = now - (now - past - slider.value())
        self.events.pos(self.slider_user_time.value())


        self.edit_current_time.setText(str(now))
        self.edit_user_time.setText(str(user_time))

        for i, data in enumerate(self.events.plots):
            _, rgb, x_axis, _ = data
            y = y_axis[i]
            for x in x_axis:
                x_begin, x_end = x[0], x[-1]
                ax.plot([x_begin, x_end], [y, y], linewidth=10, color=rgb)

        ax.plot([*repeat(int(self.edit_user_time.text()), 2)], [0, self.events.amount + 1], linewidth=3, color="red")

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