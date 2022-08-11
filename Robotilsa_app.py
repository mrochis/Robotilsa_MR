import sys
import urllib.request, json
import random
import datetime

from PyQt5.QtWidgets import QMenu, QWidget, QApplication, QMainWindow, QVBoxLayout
from PyQt5.QtCore import QTime, QTimer, pyqtSignal, QObject, QThread, QEvent 
from Robotilsa_GUI import Ui_Robotilsa_HMI
from Robotilsa_GUI_2ndW import Ui_SecondaryWindow

request_list = []
request_num = []

class Request_data(QObject):
    resultChanged = pyqtSignal()
    resultProgress = pyqtSignal(int)

    def request_data(self):
        global request_list
        global request_num

        request_list.clear()
        request_num.clear()

        url = 'https://swapi.dev/api/people/{}/?format=json'
        itt_num = 0

        for a in range (10):
            itt_num+=1
            num = random.randint(1,83)

            try:
                with urllib.request.urlopen(url.format(num)) as page:
                    data = json.loads(page.read().decode())
            except:
                with urllib.request.urlopen(url.format(1)) as page:
                    data = json.loads(page.read().decode())

            request_num.append(num)
            request_list.append(data)

            self.resultProgress.emit(itt_num*10)

        self.resultChanged.emit()
    

class RobotilsaApp(QMainWindow):
    def __init__ (self, parent=None):
        super(RobotilsaApp, self).__init__(parent=parent) #contrsuctor de la clase padre

        self.ui = Ui_Robotilsa_HMI()
        self.ui.setupUi(self)

        self.ui.LoadingBar.setValue(0)
        self.ui.LoadingBar.setVisible(False)
        #Event hanldrer for the button
        self.ui.btn_request.clicked.connect(self.request_thread_act)

        #Time and date handling
        time_refresh = QTimer(self)
        time_refresh.timeout.connect(self.displayTime)
        time_refresh.start(1000)

        date = datetime.datetime.now()
        self.ui.lbl_date.setText('{} / {} / {}'.format(date.day,date.month,date.year))
        self.show()

    def eventFilter(self, source, event):
        global request_list

        if event.type() == QEvent.ContextMenu and source == self.ui.lst_SearchResult:
            list_menu = QMenu()
            list_menu.addAction('Información del personaje')
            
            if (list_menu.exec_(event.globalPos())):
                item = source.itemAt(event.pos())

                self.window = QMainWindow()
                self.ui2nd = Ui_SecondaryWindow()
                self.ui2nd.setupUi(self.window)
                self.window.show()

                selected_number = item.text()
                selected_int = int(selected_number[0:1])
                self.ui2nd.lst_info.addItem('height:\t\t'+ request_list[selected_int]['height']+'\n')
                self.ui2nd.lst_info.addItem('mass:\t\t'+ request_list[selected_int]['mass']+'\n')
                self.ui2nd.lst_info.addItem('hair_color:\t'+ request_list[selected_int]['hair_color']+'\n')
                self.ui2nd.lst_info.addItem('skin_color:\t'+ request_list[selected_int]['skin_color']+'\n')
                self.ui2nd.lst_info.addItem('eye_color:\t\t'+ request_list[selected_int]['eye_color']+'\n')
                self.ui2nd.lst_info.addItem('birth_year:\t'+ request_list[selected_int]['birth_year']+'\n')
                self.ui2nd.lst_info.addItem('gender:\t\t'+ request_list[selected_int]['gender']+'\n')
            return True
        
        return super().eventFilter(source,event)
        

    def request_thread_act (self):
        #Reqeuest thread handling
        self.ui.lst_SearchResult.clear()
        self.ui.btn_request.setDisabled(True)
        self.ui.LoadingBar.setVisible(True)

        self.thread = QThread(self)

        self.request_ex = Request_data()
        self.request_ex.moveToThread(self.thread)

        self.thread.started.connect(self.request_ex.request_data)
        self.request_ex.resultChanged.connect(self.display_names)  
        self.request_ex.resultProgress.connect(self.report_request_progress)
        self.request_ex.resultChanged.connect(self.thread.quit) 

        self.thread.start()

    def report_request_progress(self, progress):
        self.ui.LoadingBar.setValue(progress)

    def display_names(self):
        global request_list
        global request_num

        self.ui.LoadingBar.setValue(0)
        self.ui.btn_request.setDisabled(False)
        self.ui.LoadingBar.setVisible(False)
         
        itt_num=0

        for element in request_list:
            lst_str = '{}) '.format(itt_num+1) + element['name'] +' ({})'.format(request_num[itt_num])
            self.ui.lst_SearchResult.addItem(lst_str)
            itt_num+=1

        self.ui.lst_SearchResult.installEventFilter(self)

    def displayTime (self):
        currentTime = QTime.currentTime()
        displayTime = currentTime.toString('hh:mm:ss')

        self.ui.lbl_time.display(displayTime)

if __name__ == '__main__':
    app = QApplication(sys.argv)

    MainWindow = RobotilsaApp()
    MainWindow.show()

    sys.exit(app.exec_())