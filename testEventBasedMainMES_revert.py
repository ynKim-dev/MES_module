import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QStackedWidget, QDialog, QTableWidgetItem, QGridLayout, QCheckBox, QWidget, QVBoxLayout, QGraphicsItem, QGraphicsScene, QPushButton, QGraphicsPixmapItem, QLabel, QGraphicsRectItem, QMessageBox
from PyQt5.QtCore import pyqtSlot, pyqtSignal, Qt
from PyQt5.QtGui import QColor, QPalette, QPixmap, QPainter
from PyQt5 import uic
from PyQt5.QtSvg import QGraphicsSvgItem
import mariadb
import sowingQuery
import buddingQuery
import subFormQuery
import paho.mqtt.client as mqtt
import json
import random
from PyQt5.QtCore import QTimer
import os
from PyQt5.QtWidgets import QOpenGLWidget
from PyQt5.QtCore import pyqtSignal, Qt
from datetime import datetime
import xml.etree.ElementTree as ET

# 예외를 출력하는 함수 정의
def exception_hook(exctype, value, traceback):
    print("Exception:", exctype, value)
    sys.__excepthook__(exctype, value, traceback)

# sys.excepthook을 재정의
sys.excepthook = exception_hook

# UI 파일 연결
form_class = uic.loadUiType("sowingScreen.ui")[0]
budding_form_class = uic.loadUiType("buddingScreen.ui")[0]
sub_form_class = uic.loadUiType("selectStoreForm.ui")[0]
raising_form_class = uic.loadUiType("raisingScreen.ui")[0]
grafting_form_class = uic.loadUiType("graftingScreen.ui")[0]
taking_form_class = uic.loadUiType("takingScreen.ui")[0]
monitoring_form_class = uic.loadUiType("renewMonitoringScreen.ui")[0]

# MQTT 설정
# broker_address = "localhost" 
# broker_port = 1883

broker_address =  'mqtt.iobot.co.kr'
broker_port =  1883
client_id = 'KETI-System'
username = 'user'
password = '1111'

# 전역 변수 배열
temp_arr = []

# 시간 지연 변수 설정
ROBOT_MOVE_INTERVAL = 1000  # 로봇 이동 간격 (밀리초)
PANEL_MOVE_INTERVAL = 2000  # 패널 이동 간격 (밀리초)

# 로봇 도형 위치 지정 (태그 ID: 도형 타입)
ROBOT_SHAPES = {
    'tag2': 'ellipse',
    'tag1': 'rectangle',
    'tag0': 'triangle'
}

# 태그 사각형의 크기 
TAG_RECT_SIZE = 20


#패널 데이터 하드코딩 
PANEL_DATA = {
    'panel1': {'과실': '사과', '수량': 100, '기타1': '신선도 높음', '기타2': '유기농 인증', '기타3': '경북 영주산'},
    'panel2': {'과실': '배', '수량': 80, '기타1': '당도 14브릭스', '기타2': '크기 대과', '기타3': '충남 나주산'},
    'panel3': {'과실': '복숭아', '수량': 60, '기타1': '백도품종', '기타2': '과즙 풍부', '기타3': '경북 청도산'},
    'panel4': {'과실': '포도', '수량': 50, '기타1': '씨없는 품종', '기타2': '항산화 물질 풍부', '기타3': '경기 안성산'},
    'panel5': {'과실': '상추', '수량': 70, '기타1': '잎이 부드러움', '기타2': '수경재배', '기타3': '충북 청주산'},
    'panel6': {'과실': '키위', '수량': 45, '기타1': '비타민C 풍부', '기타2': '제주도 특산품', '기타3': '껍질째 먹기 가능'},
    'panel7': {'과실': '오렌지', '수량': 85, '기타1': '수입과일', '기타2': '과즙 많음', '기타3': '캘리포니아산'},
    'panel8': {'과실': '망고', '수량': 30, '기타1': '열대과일', '기타2': '당도 높음', '기타3': '필리핀산'},
    'panel9': {'과실': '없음', '수량': 0, '기타1': '재고 소진', '기타2': '다음 주 입고 예정', '기타3': '예약 가능'},
    'panel10': {'과실': '토마토', '수량': 120, '기타1': '방울토마토', '기타2': '샐러드용', '기타3': '강원도 화천산'},
    'panel11': {'과실': '상추', '수량': 90, '기타1': '로메인 품종', '기타2': '샌드위치용', '기타3': '전북 김제산'},
    'panel12': {'과실': '딸기', '수량': 40, '기타1': '설향 품종', '기타2': '과육이 단단함', '기타3': '충남 논산산'},
    'panel13': {'과실': '바나나', '수량': 150, '기타1': '수입과일', '기타2': '후숙 과일', '기타3': '필리핀산'},
    'panel14': {'과실': '블루베리', '수량': 25, '기타1': '안토시아닌 풍부', '기타2': '냉동보관', '기타3': '미국산'},
    'panel15': {'과실': '없음', '수량': 0, '기타1': '품절', '기타2': '수요 과다', '기타3': '재입고 미정'},
    'panel16': {'과실': '파인애플', '수량': 35, '기타1': '열대과일', '기타2': '비타민 풍부', '기타3': '필리핀산'},
    'panel17': {'과실': '수박', '수량': 20, '기타1': '씨없는 수박', '기타2': '당도 12브릭스', '기타3': '전남 함평산'},
    'panel18': {'과실': '귤', '수량': 200, '기타1': '제주 특산품', '기타2': '비타민C 풍부', '기타3': '제주도산'},
    'panel19': {'과실': '상추', '수량': 80, '기타1': '버터헤드 품종', '기타2': '유기농 재배', '기타3': '강원도 평창산'},
    'panel20': {'과실': '참외', '수량': 70, '기타1': '성주 참외', '기타2': '당도 높음', '기타3': '경북 성주산'},
    'panel21': {'과실': '자두', '수량': 55, '기타1': '과즙 풍부', '기타2': '식이섬유 풍부', '기타3': '충북 옥천산'},
    'panel22': {'과실': '체리', '수량': 40, '기타1': '수입과일', '기타2': '안토시아닌 풍부', '기타3': '미국 워싱턴주산'},
    'panel23': {'과실': '없음', '수량': 0, '기타1': '계절 외 품목', '기타2': '내년 봄 입고 예정', '기타3': '사전 예약 가능'},
    'panel24': {'과실': '멜론', '수량': 30, '기타1': '네트멜론', '기타2': '아삭한 식감', '기타3': '충남 서산산'},
    'panel25': {'과실': '석류', '수량': 25, '기타1': '항산화 물질 풍부', '기타2': '씨까지 섭취 가능', '기타3': '터키산'},
    'panel26': {'과실': '무화과', '수량': 15, '기타1': '식이섬유 풍부', '기타2': '부드러운 식감', '기타3': '전남 영암산'},
    'panel27': {'과실': '레몬', '수량': 60, '기타1': '신맛 강함', '기타2': '비타민C 풍부', '기타3': '미국 캘리포니아산'},
    'panel28': {'과실': '상추', '수량': 100, '기타1': '청상추', '기타2': '쌈용', '기타3': '전북 완주산'},
    'panel29': {'과실': '아보카도', '수량': 40, '기타1': '건강한 지방 함유', '기타2': '부드러운 식감', '기타3': '멕시코산'},
    'panel30': {'과실': '포도', '수량': 75, '기타1': '거봉 품종', '기타2': '과립이 큼', '기타3': '경북 김천산'},
    'panel31': {'과실': '감', '수량': 50, '기타1': '단감', '기타2': '비타민A 풍부', '기타3': '경남 창원산'},
    'panel32': {'과실': '라임', '수량': 30, '기타1': '신맛 강함', '기타2': '칵테일용', '기타3': '멕시코산'},
    'panel33': {'과실': '수박', '수량': 30, '기타1': '흑수박', '기타2': '당도 11브릭스', '기타3': '전북 고창산'},
    'panel34': {'과실': '없음', '수량': 0, '기타1': '수요 조사 중', '기타2': '신규 품목 검토', '기타3': '고객 의견 수렴'}
}

class PanelItem(QGraphicsRectItem):
    def __init__(self, panel_id, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.panel_id = panel_id
        self.setAcceptHoverEvents(True)

    def mousePressEvent(self, event):
        # 패널 클릭 시 해당 패널의 데이터 표시
        data = PANEL_DATA.get(self.panel_id, {})
        info = f"패널 ID: {self.panel_id}\n"
        for key, value in data.items():
            info += f"{key}: {value}\n"
        QMessageBox.information(None, "패널 정보", info)

# 데이터베이스 연결 함수
def connect_to_db():
    try:
        conn = mariadb.connect(
            user="root",
            password="keti1147!",
            host="1.214.32.67",
            port=11474,
            database="system"
        )
        return conn
    except mariadb.Error as e:
        print(f"Error connecting to MariaDB: {e}")
        return None

# 서브 폼 클래스
class SubForm(QDialog):

    # 창고 정보 전달 시그널 07_15
    store_selected = pyqtSignal(str, list)

    def __init__(self):
        super().__init__()
        self.ui = sub_form_class()
        self.ui.setupUi(self)

        # DB 연결
        self.db_connection = connect_to_db()

        # 전역 변수 초기화
        store_list = subFormQuery.get_store(self.db_connection)
        self.temp_store_list = []  # Make sure this is an instance variable
        self.checkbox_states = [] # 리스트 초기화 0716
       

        # 콤보 박스에 아이템 추가
        if store_list:
            for i, store_dict in enumerate(store_list):
                for key, value in store_dict.items():
                    if key != 'Column2':
                        self.ui.formStoreComboBox.addItem(str(value))
                    else:
                        self.temp_store_list.append(str(value))
        
        print(self.temp_store_list)

        # 콤보 박스에서 아이템이 선택될 때마다 이벤트 핸들러 연결
        self.ui.formStoreComboBox.currentIndexChanged.connect(self.update_store_label)

        # 창고 맵 그리기 이벤트 핸들러 연결
        self.ui.formCallStorePushButton.clicked.connect(self.call_store_and_populate_grid)

        # 저장 버튼 클릭 이벤트 핸들러 연결 07_15
        self.ui.formClearPushButton.clicked.connect(self.save_and_close)


    def update_store_label(self, index):
        if index >= 0 and index < len(self.temp_store_list):
            selected_value = self.temp_store_list[index]
            self.ui.formStoreNameLabel.setText(selected_value)
        else:
            self.ui.formStoreNameLabel.setText("")
            
    def call_store_and_populate_grid(self):
        selected_index = self.ui.formStoreComboBox.currentIndex()
        if selected_index >= 0:
            selected_store_id = self.ui.formStoreComboBox.itemText(selected_index)
            print(f"parameter : {selected_store_id}")
            self.populate_grid(selected_store_id)


    def create_checkbox_container(self, state):
        # Create a QWidget to hold the checkbox
        container = QWidget()
        checkbox = QCheckBox(state)
        
        # Set layout for the container
        layout = QVBoxLayout(container)
        layout.addWidget(checkbox)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)  # Center the checkbox
        
        # Set the background color and border
        container.setAutoFillBackground(True)
        palette = container.palette()
        palette.setColor(QPalette.ColorRole.Window, QColor("lightgray"))
        container.setPalette(palette)
        container.setStyleSheet("border: 1px solid black;")
        
        # Disable the checkbox if state is "적재"
        if state == "적재":
            checkbox.setEnabled(False)

        container.checkbox = checkbox # 컨테이너에 추가 0716
        return container



    def populate_grid(self, store_id):
        print(f"check Elements : {store_id}")
        details = subFormQuery.get_detail_store(self.db_connection, store_id)
        if not details:
            print(f"No details found for StoreId: {store_id}")
            return

        max_row = max(detail['Row'] for detail in details)
        max_column = max(detail['Column'] for detail in details)

        # Clear the previous grid layout
        for i in reversed(range(self.ui.gridLayout.count())):
            widget = self.ui.gridLayout.itemAt(i).widget()
            if widget is not None:
                widget.setParent(None)

        self.checkbox_states = [] # 추가 0716

        # Add custom widgets to the grid layout based on details
        for detail in details:
            row = detail['Row']
            column = detail['Column']
            state = detail['State']

            # Create a custom widget containing the checkbox
            container = self.create_checkbox_container(state)
            self.ui.gridLayout.addWidget(container, row, column)

            # Save the state of each checkbox
            self.checkbox_states.append((row, column, state, container.checkbox.isChecked()))  # 추가된 부분 0716



    def print_combo_box_items(self):
        count = self.ui.formStoreComboBox.count()
        print(f"ComboBox has {count} items:")
        for index in range(count):
            text = self.ui.formStoreComboBox.itemText(index)
            data = self.ui.formStoreComboBox.itemData(index)
            print(f"Index {index}: Text='{text}', Data='{data}'")

    # 추가 07_15_창고 요소 전달
    def save_and_close(self):
        selected_store_id = self.ui.formStoreComboBox.currentText()

        # Update checkbox states before emitting the signal 추가 0716
        self.checkbox_states = []
        for i in range(self.ui.gridLayout.count()):
            widget = self.ui.gridLayout.itemAt(i).widget()
            if widget is not None and isinstance(widget, QWidget) and hasattr(widget, 'checkbox'):
                checkbox = widget.checkbox
                self.checkbox_states.append((self.ui.gridLayout.getItemPosition(i)[0], self.ui.gridLayout.getItemPosition(i)[1], checkbox.text(), checkbox.isChecked()))

        self.store_selected.emit(selected_store_id, self.checkbox_states)
        self.accept()


# Sowing 폼 클래스
class SowingForm(QMainWindow):
    def __init__(self, event_manager, mqtt_client):
        super().__init__()
        self.ui = form_class()
        self.ui.setupUi(self)
        self.event_manager = event_manager
        self.mqtt_client = mqtt_client


        # Stacked Widget 생성
        self.stackedWidget = QStackedWidget()

        # 버튼에 클릭 이벤트 핸들러 연결
        self.ui.selectStorePushButton.clicked.connect(self.showSubForm)
        self.ui.buddingButtonLabel.mousePressEvent = self.showBuddingForm
        self.ui.raisingButtonLabel.mousePressEvent = self.showRaisingForm
        self.ui.graftingButtonLabel.mousePressEvent = self.showGraftingForm
        self.ui.takingButtonLabel.mousePressEvent = self.showTakingForm
        self.ui.monitoringButtonLabel.mousePressEvent = self.showMonitoringForm
        # 다른 버튼에 대한 클릭 이벤트 핸들러도 동일하게 추가

        # clearPushButton 클릭 시 이벤트 핸들러 연결
        self.ui.clearPushButton.clicked.connect(self.handle_clear_button_click)

        # 로봇 호출 버튼 클릭 이벤트 핸들러 연결 07_15
        self.ui.callRobotPushButton.clicked.connect(self.call_to_robot)

        # DB 연결
        self.db_connection = connect_to_db()

        # 전역변수 초기화
        temp_arr = []

        # 레이아웃 설정 0716
        self.ui.contentStoreBackgroundLabel3.setLayout(QGridLayout())  # 추가된 부분

        # 데이터 표시
        self.display_data()

        # 감추기 기능 테스트 07_15
        SowingForm.hide_ui_elements(self)

    # 서브 폼 보여주기
    @pyqtSlot()
    def showSubForm(self):
        subForm = SubForm()
        # 추가된 기능 start_0716
        subForm.store_selected.connect(self.update_store_info)
        # 추가 기능 end
        subForm.exec_()


    @pyqtSlot(str, list)  # 추가된 메서드 0716
    def update_store_info(self, store_id, checkbox_states):
        self.ui.guideStoreInfoInputLabel3.setText(store_id)
        self.populate_store_grid(checkbox_states)

    def populate_store_grid(self, checkbox_states):  # 추가된 메서드 0716
        # Clear the previous grid layout
        layout = self.ui.contentStoreBackgroundLabel3.layout()
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.setParent(None)

        for row, column, state, checked in checkbox_states:
            container = self.create_checkbox_container(state, checked)
            layout.addWidget(container, row, column)

    def create_checkbox_container(self, state, checked):  # 추가된 메서드 0716
        container = QWidget()
        checkbox = QCheckBox(state)
        checkbox.setChecked(checked)

        layout = QVBoxLayout(container)
        layout.addWidget(checkbox)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        container.setAutoFillBackground(True)
        palette = container.palette()
        palette.setColor(QPalette.ColorRole.Window, QColor("lightgray"))
        container.setPalette(palette)
        container.setStyleSheet("border: 1px solid black;")

        if state == "적재":
            checkbox.setEnabled(False)

        return container



    # budding 폼 보여주기
    @pyqtSlot()
    def showBuddingForm(self, event):
        self.event_manager.change_to_budding_form()

    # raising 폼 보여주기
    @pyqtSlot()
    def showRaisingForm(self, event):
        self.event_manager.change_to_raising_form()

    # grafting 폼 보여주기
    @pyqtSlot()
    def showGraftingForm(self, event):
        self.event_manager.change_to_grafting_form()

    # taking 폼 보여주기
    @pyqtSlot()
    def showTakingForm(self, event):
        self.event_manager.change_to_taking_form()

    # monitoring 폼 보여주기
    @pyqtSlot()
    def showMonitoringForm(self, event):
        self.event_manager.change_to_monitoring_form()    

    # 데이터 표시 메소드
    def display_data(self):

        try:
            self.ui.presentSowingTableWidget.clearContents()

            rows = sowingQuery.get_sowing(self.db_connection)

            if rows:
                self.ui.presentSowingTableWidget.setRowCount(len(rows))
                self.ui.presentSowingTableWidget.setColumnCount(len(rows[0]) - 1) 


                for i, row in enumerate(rows):
                    for j, (key, value) in enumerate(row.items()):
                        
                        if key != 'Column7':
                            item = QTableWidgetItem(str(value))
                            self.ui.presentSowingTableWidget.setItem(i, j, item)
                        else: 
                            temp_arr.append(str(value))    
                        # self.ui.presentSowingTableWidget.setItem(i, j, QTableWidgetItem(str(value)))

                self.ui.presentSowingTableWidget.cellClicked.connect(self.handle_row_click)
 
            else:
                self.ui.presentSowingTableWidget.setRowCount(0)
                self.ui.presentSowingTableWidget.setColumnCount(0)

            
        except Exception as e:
            print(f"Error displaying data: {e}")

    # 행 클릭 이벤트 핸들러 정의
    def handle_row_click(self, row, column):
        try:
           
           print(f"row : {row}")
           print(temp_arr[row])

           # 초기화 추가 0716
           SowingForm.clear_store_grid(self)
           SowingForm.clear_input_label(self)

           json_data = json.loads(temp_arr[row])

           
           info1 = json_data.get("Seed", "")

           print(info1)

           if(self.ui.presentSowingTableWidget.item(row, 2).text() == "재료투입"):

                SowingForm.hide_ui_elements(self)
                self.ui.guideInfoInputLabel.setText(json_data.get("Seed", ""))
                self.ui.guideInfoInputLabel_2.setText(str(int(json_data.get("TrayStandard", "")) * int(json_data.get("TrayQuantity", ""))))
                self.ui.guideInfoInputLabel_3.setText(self.ui.presentSowingTableWidget.item(row, 3).text())
                self.ui.guideInfoInputLabel_4.setText(self.ui.presentSowingTableWidget.item(row, 4).text())
                self.ui.guideInfoInputLabel_5.setText(json_data.get("TrayStandard", ""))
                self.ui.guideInfoInputLabel_6.setText(json_data.get("WaterQuantity", ""))
                self.ui.guideInfoInputLabel_7.setText(json_data.get("Soil", ""))
                self.ui.guideInfoInputLabel_8.setText(json_data.get("SoilQuantity", ""))
                self.ui.guideInfoInputLabel_9.setText(json_data.get("OtherMaterial1", ""))
                self.ui.guideInfoInputLabel_10.setText(json_data.get("OtherMaterialQuantity1", ""))
                self.ui.guideInfoInputLabel_11.setText(json_data.get("OtherMaterial2", ""))
                self.ui.guideInfoInputLabel_12.setText(json_data.get("OtherMaterialQuantity2", ""))
           
           elif(self.ui.presentSowingTableWidget.item(row, 2).text() == "이동작업"):
                
                SowingForm.show_ui_elements(self)
                self.ui.guideStoreInfoInputLabel.setText(json_data.get("Store", ""))
                self.ui.guideStoreInfoInputLabel4.setText(json_data.get("DetailStore", ""))
               

        except Exception as e:
            print(f"Error handling row click: {e}")

    # clearPushButton 클릭 시 실행될 함수
    def handle_clear_button_click(self, row):
        # lineEdit1 ~ lineEdit9의 텍스트 값 가져오기

        missionNumber = self.ui.presentSowingTableWidget.item(row, 5).text()
        seedValue = self.ui.lineEdit.text()
        trayStandardValue = self.ui.lineEdit_2.text()
        trayQuantityValue = self.ui.lineEdit_3.text()
        soilValue = self.ui.lineEdit_4.text()
        soilQunatityValue = self.ui.lineEdit_5.text()
        otherMaterial1Value = self.ui.lineEdit_6.text()
        otherMaterialQunatity1Value = self.ui.lineEdit_7.text()
        otherMaterial2Value = self.ui.lineEdit_8.text()
        otherMaterialQuantity2Value = self.ui.lineEdit_9.text()
        noteValue = self.ui.lineEdit_10.text()

        # 가져온 값들을 insert_sowing 함수에 전달
        sowingQuery.insert_sowing(self.db_connection, seedValue, trayStandardValue, trayQuantityValue, soilValue, soilQunatityValue, otherMaterial1Value, otherMaterialQunatity1Value, otherMaterial2Value, otherMaterialQuantity2Value, noteValue, str(missionNumber))

    # 기능별 감추기 07_15
    def hide_ui_elements(self):
        self.ui.contentStoreBackgroundLabel.setVisible(False)
        self.ui.guideStoreInfoLabel.setVisible(False)
        self.ui.guideStoreInfoInputLabel.setVisible(False)
        self.ui.contentStoreBackgroundLabel2.setVisible(False)
        self.ui.guideStoreInfoLabel2.setVisible(False)
        self.ui.guideStoreInfoInputLabel2.setVisible(False)
        self.ui.contentStoreBackgroundLabel3.setVisible(False)
        self.ui.guideStoreInfoLabel3.setVisible(False)
        self.ui.guideStoreInfoInputLabel3.setVisible(False)
        self.ui.guideStoreInfoLabel4.setVisible(False)
        self.ui.guideStoreInfoInputLabel4.setVisible(False)

    # 기능별 보여주기 07_15
    def show_ui_elements(self):
        self.ui.contentStoreBackgroundLabel.setVisible(True)
        self.ui.guideStoreInfoLabel.setVisible(True)
        self.ui.guideStoreInfoInputLabel.setVisible(True)
        self.ui.contentStoreBackgroundLabel2.setVisible(True)
        self.ui.guideStoreInfoLabel2.setVisible(True)
        self.ui.guideStoreInfoInputLabel2.setVisible(True)
        self.ui.contentStoreBackgroundLabel3.setVisible(True)
        self.ui.guideStoreInfoLabel3.setVisible(True)
        self.ui.guideStoreInfoInputLabel3.setVisible(True)
        self.ui.guideStoreInfoLabel4.setVisible(True)
        self.ui.guideStoreInfoInputLabel4.setVisible(True)

    # 로봇 호출 버튼 메소드 07_15
    def call_to_robot(self):
        message = "파종실"
        self.mqtt_client.publish("demo/axis", message)
        print(f"Published: {message}")


    # 입력란 초기화 0715
    def clear_input_label(self):
        self.ui.lineEdit.setText("")
        self.ui.lineEdit_2.setText("")
        self.ui.lineEdit_3.setText("")
        self.ui.lineEdit_4.setText("")
        self.ui.lineEdit_5.setText("")
        self.ui.lineEdit_6.setText("")
        self.ui.lineEdit_7.setText("")
        self.ui.lineEdit_8.setText("")
        self.ui.lineEdit_9.setText("")
        self.ui.lineEdit_10.setText("")


    # 창고 초기화 0715     
    def clear_store_grid(self):
        layout = self.ui.contentStoreBackgroundLabel3.layout()
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.setParent(None)


# budding 폼 클래스
class BuddingForm(QMainWindow):
    goToMainWindow = pyqtSignal()
    
    def __init__(self, event_manager):
        super().__init__()
        self.ui = budding_form_class()
        self.ui.setupUi(self)
        self.event_manager = event_manager

        # Stacked Widget 생성
        self.stackedWidget = QStackedWidget()

        # 버튼에 클릭 이벤트 핸들러 연결
        self.ui.selectStorePushButton.clicked.connect(self.showSubForm)
        self.ui.sowingButtonLabel.mousePressEvent = self.showSowingForm
        self.ui.raisingButtonLabel.mousePressEvent = self.showRaisingForm
        self.ui.graftingButtonLabel.mousePressEvent = self.showGraftingForm
        self.ui.takingButtonLabel.mousePressEvent = self.showTakingForm
        self.ui.monitoringButtonLabel.mousePressEvent = self.showMonitoringForm
        # 다른 버튼에 대한 클릭 이벤트 핸들러도 동일하게 추가

        # DB 연결
        self.db_connection = connect_to_db()

        # 전역 변수 초기화
        temp_arr = []

        # 데이터 표시
        self.display_data()

        # # QTimer를 사용하여 주기적으로 값을 업데이트
        # self.timer = QTimer(self)
        # self.timer.timeout.connect(self.update_temperature_and_humidity)
        # self.timer.start(10000)  # 10초마다 호출
        

    # 서브 폼 보여주기
    @pyqtSlot()
    def showSubForm(self):
        subForm = SubForm()
        subForm.exec_()

    # sowing 폼 보여주기
    @pyqtSlot()
    def showSowingForm(self, event):
        self.event_manager.change_to_sowing_form()

    # raising 폼 보여주기
    @pyqtSlot()
    def showRaisingForm(self, event):
        self.event_manager.change_to_raising_form() 

    # grafting 폼 보여주기
    @pyqtSlot()
    def showGraftingForm(self, event):
        self.event_manager.change_to_grafting_form() 
    
    # taking 폼 보여주기
    @pyqtSlot()
    def showTakingForm(self, event):
        self.event_manager.change_to_taking_form()   

    # taking 폼 보여주기
    @pyqtSlot()
    def showMonitoringForm(self, event):
        self.event_manager.change_to_monitoring_form()    

    # 데이터 표시 메소드
    def display_data(self):

        try:
            self.ui.presentJobTableWidget.clearContents()

            rows = buddingQuery.get_budding(self.db_connection)

            if rows:
                self.ui.presentJobTableWidget.setRowCount(len(rows))
                self.ui.presentJobTableWidget.setColumnCount(len(rows[0]) - 1) 


                for i, row in enumerate(rows):
                    for j, (key, value) in enumerate(row.items()):
                        
                        if key != 'Column7':
                            item = QTableWidgetItem(str(value))
                            self.ui.presentJobTableWidget.setItem(i, j, item)
                        else: 
                            temp_arr.append(str(value))    
                        # self.ui.presentSowingTableWidget.setItem(i, j, QTableWidgetItem(str(value)))

                self.ui.presentJobTableWidget.cellClicked.connect(self.handle_row_click)
 
            else:
                self.ui.presentJobTableWidget.setRowCount(0)
                self.ui.presentJobTableWidget.setColumnCount(0)

            
        except Exception as e:
            print(f"Error displaying data: {e}")

    # 행 클릭 이벤트 핸들러 정의
    def handle_row_click(self, row, column):
        try:
           
           print(f"row : {row}")
           print(temp_arr[row])
           json_data = json.loads(temp_arr[row])

           
           info1 = json_data.get("Seed", "")

           print(info1)

         
           self.ui.guideInfoInputLabel.setText(json_data.get("Seed", ""))
           self.ui.guideInfoInputLabel_2.setText(str(int(json_data.get("TrayStandard", "")) * int(json_data.get("TrayQuantity", ""))))
           self.ui.guideInfoInputLabel_3.setText(self.ui.presentJobTableWidget.item(row, 4).text())
           self.ui.guideInfoInputLabel_4.setText(self.ui.presentJobTableWidget.item(row, 5).text())
           self.ui.guideInfoInputLabel_5.setText(json_data.get("TrayStandard", ""))
           self.ui.guideInfoInputLabel_6.setText(json_data.get("WaterQuantity", ""))
           self.ui.guideInfoInputLabel_7.setText(json_data.get("Soil", ""))
           self.ui.guideInfoInputLabel_8.setText(json_data.get("SoilQuantity", ""))
           self.ui.guideInfoInputLabel_9.setText(json_data.get("OtherMaterial1", ""))
           self.ui.guideInfoInputLabel_10.setText(json_data.get("OtherMaterialQuantity1", ""))
           self.ui.guideInfoInputLabel_11.setText(json_data.get("OtherMaterial2", ""))
           self.ui.guideInfoInputLabel_12.setText(json_data.get("OtherMaterialQuantity2", ""))

        except Exception as e:
            print(f"Error handling row click: {e}")

    def update_temperature_display(self, temperature):
        self.ui.currentTemperatureInfoInputLabel.setText(f"{temperature:.1f} ℃")

    def update_humidity_display(self, humidity):
        self.ui.currentHumidityInfoInputLabel.setText(f"{humidity:.1f} %")



# raising 폼 클래스
class RaisingForm(QMainWindow):
    goToMainWindow = pyqtSignal()
    
    def __init__(self, event_manager, mqtt_client):
        super().__init__()
        self.ui = raising_form_class()
        self.ui.setupUi(self)
        self.event_manager = event_manager
        self.mqtt_client = mqtt_client

        # Stacked Widget 생성
        self.stackedWidget = QStackedWidget()

        # 버튼에 클릭 이벤트 핸들러 연결
        self.ui.selectStorePushButton.clicked.connect(self.showSubForm)
        self.ui.sowingButtonLabel.mousePressEvent = self.showSowingForm
        self.ui.buddingButtonLabel.mousePressEvent = self.showBuddingForm
        self.ui.graftingButtonLabel.mousePressEvent = self.showGraftingForm
        self.ui.takingButtonLabel.mousePressEvent = self.showTakingForm
        self.ui.monitoringButtonLabel.mousePressEvent = self.showMonitoringForm
        # 다른 버튼에 대한 클릭 이벤트 핸들러도 동일하게 추가

        self.ui.settingGatePushButton.clicked.connect(self.click_test_store_button)
       # self.ui.settingStoreButton.clicked.connect(self.call_to_robot)

        self.ui.settingStoreButton.clicked.connect(self.call_to_loader_shelf)
       # self.ui.selectStorePushButton.clicked.connect(self.call_to_gentry)
        self.ui.selectStorePushButton.clicked.connect(self.call_to_loader_gentry)
        


        # DB 연결
        self.db_connection = connect_to_db()

        RaisingForm.hide_ui_element(self)

## 테스트 기능 추가 start

    # 행 클릭 이벤트 핸들러 정의
    def click_test_store_button(self):

        is_visible = self.ui.contentTestBackgroundLabel.isVisible()

        if is_visible:
            RaisingForm.hide_ui_element(self)
            self.ui.guideInfoInputLabel.setText("")
            self.ui.guideInfoInputLabel_2.setText("")
            self.ui.guideInfoInputLabel_3.setText("")
            self.ui.guideInfoInputLabel_4.setText("")
            self.ui.guideInfoInputLabel_5.setText("")
            self.ui.guideInfoInputLabel_6.setText("")
            self.ui.guideInfoInputLabel_7.setText("")
            self.ui.guideInfoInputLabel_8.setText("")

            self.graphicsView.scene().clear()

        else:
            RaisingForm.show_ui_element(self)    
            self.ui.guideTestInfoInputLabel.setText("")
            self.ui.guideTestInfoInputLabel_2.setText("")
        
    # 로봇 호출 버튼 메소드 07_15
    def call_to_robot(self):

        current_time = datetime.now().strftime("%Y%m%d%H%M%S")
        storeid = self.ui.guideTestInfoInputLabel.text()
        message = {
            "id": current_time,
            "storeid": storeid,
            "robotid": "1"
        }

        json_message = json.dumps(message, ensure_ascii=False)  # JSON 형식으로 변환
        self.mqtt_client.publish("kitech/test", json_message)
        print(f"Published: {message}")

        self.ui.guideTestInfoInputLabel.setText("")
        self.ui.guideTestInfoInputLabel_2.setText("")

    def hide_ui_element(self):
        self.ui.contentTestBackgroundLabel.setVisible(False)
        self.ui.guideTestInfoLabel.setVisible(False)
        self.ui.guideTestInfoInputLabel.setVisible(False)
        self.ui.guideTestInfoLabel_2.setVisible(False)
        self.ui.guideTestInfoInputLabel_2.setVisible(False)
        self.ui.guideTestInfoLabel_3.setVisible(False)
        self.ui.comboBox.setVisible(False)
        self.ui.graphicsView.setVisible(False)

    def show_ui_element(self):
        self.ui.contentTestBackgroundLabel.setVisible(True)
        self.ui.guideTestInfoLabel.setVisible(True)
        self.ui.guideTestInfoInputLabel.setVisible(True)
        self.ui.guideTestInfoLabel_2.setVisible(True)
        self.ui.guideTestInfoInputLabel_2.setVisible(True)
        self.ui.guideTestInfoLabel_3.setVisible(True)
        self.ui.comboBox.setVisible(True)
        self.ui.graphicsView.setVisible(True)

    # 로봇 호출 버튼 메소드 07_15
    def call_to_gentry(self):

        current_time = datetime.now().strftime("%Y%m%d%H%M%S")
        storeid = self.ui.guideTestInfoInputLabel.text()
        message = {
            "gentry": {
                "command": "control",
                "x_position": 500,
                "y_position": 500,
                "pump": "on",
                "processingtime": 10000,
                "datatime": current_time
            }
        }

        json_message = json.dumps(message, ensure_ascii=False)  # JSON 형식으로 변환
        self.mqtt_client.publish("farm/gentry", json_message)
        print(f"Published: {message}")

     # 로봇 호출 버튼 메소드 07_15

    def call_to_loader_shelf(self):

        current_time = datetime.now().strftime("%Y%m%d%H%M%S")
        storeid = self.ui.guideTestInfoInputLabel.text()
        message = {
            "loader": {
                "command": "shelf",
                "shelf_floor": "5",
                "shelf_column": "2",
                "gentry_column": "1",
                "oper": "unload",
                "processingtime": 10000,
                "datatime": current_time
            }
        }

        json_message = json.dumps(message, ensure_ascii=False)  # JSON 형식으로 변환
        self.mqtt_client.publish("farm/loader", json_message)
        print(f"Published: {message}")

        self.ui.guideTestInfoInputLabel.setText("")
        self.ui.guideTestInfoInputLabel_2.setText("")


    def call_to_loader_gentry(self):

        current_time = datetime.now().strftime("%Y%m%d%H%M%S")
        storeid = self.ui.guideTestInfoInputLabel.text()
        message = {
            "loader": {
                "command": "gentry",
                "shelf_floor": "none",
                "shelf_column": "none",
                "gentry_column": "1",
                "oper": "unload",
                "processingtime": 20000,
                "datatime": current_time
            }
        }

        json_message = json.dumps(message, ensure_ascii=False)  # JSON 형식으로 변환
        self.mqtt_client.publish("farm/loader", json_message)
        print(f"Published: {message}")


## 테스트 기능 추가 end

    # 서브 폼 보여주기
    @pyqtSlot()
    def showSubForm(self):
        subForm = SubForm()
        subForm.exec_()

    # sowing 폼 보여주기
    @pyqtSlot()
    def showSowingForm(self, event):
        self.event_manager.change_to_sowing_form()

    # raising 폼 보여주기
    @pyqtSlot()
    def showBuddingForm(self, event):
        self.event_manager.change_to_budding_form()

    # grafting 폼 보여주기
    @pyqtSlot()
    def showGraftingForm(self, event):
        self.event_manager.change_to_grafting_form()

    # taking 폼 보여주기
    @pyqtSlot()
    def showTakingForm(self, event):
        self.event_manager.change_to_taking_form()

    # taking 폼 보여주기
    @pyqtSlot()
    def showMonitoringForm(self, event):
        self.event_manager.change_to_monitoring_form()

# grafting 폼 클래스
class GraftingForm(QMainWindow):
    goToMainWindow = pyqtSignal()
    
    def __init__(self, event_manager):
        super().__init__()
        self.ui = grafting_form_class()
        self.ui.setupUi(self)
        self.event_manager = event_manager

        # Stacked Widget 생성
        self.stackedWidget = QStackedWidget()

        # 버튼에 클릭 이벤트 핸들러 연결
        self.ui.selectStorePushButton.clicked.connect(self.showSubForm)
        self.ui.sowingButtonLabel.mousePressEvent = self.showSowingForm
        self.ui.buddingButtonLabel.mousePressEvent = self.showBuddingForm
        self.ui.raisingButtonLabel.mousePressEvent = self.showRaisingForm
        self.ui.takingButtonLabel.mousePressEvent = self.showTakingForm
        self.ui.monitoringButtonLabel.mousePressEvent = self.showMonitoringForm
        # 다른 버튼에 대한 클릭 이벤트 핸들러도 동일하게 추가

        # DB 연결
        self.db_connection = connect_to_db()

    # 서브 폼 보여주기
    @pyqtSlot()
    def showSubForm(self):
        subForm = SubForm()
        subForm.exec_()

    # sowing 폼 보여주기
    @pyqtSlot()
    def showSowingForm(self, event):
        self.event_manager.change_to_sowing_form()

    # budding 폼 보여주기
    @pyqtSlot()
    def showBuddingForm(self, event):
        self.event_manager.change_to_budding_form()

    # raising 폼 보여주기
    @pyqtSlot()
    def showRaisingForm(self, event):
        self.event_manager.change_to_raising_form()

    # taking 폼 보여주기
    @pyqtSlot()
    def showTakingForm(self, event):
        self.event_manager.change_to_taking_form()

    # taking 폼 보여주기
    @pyqtSlot()
    def showMonitoringForm(self, event):
        self.event_manager.change_to_monitoring_form()

# taking 폼 클래스
class TakingForm(QMainWindow):
    goToMainWindow = pyqtSignal()
    
    def __init__(self, event_manager):
        super().__init__()
        self.ui = taking_form_class()
        self.ui.setupUi(self)
        self.event_manager = event_manager

        # Stacked Widget 생성
        self.stackedWidget = QStackedWidget()

        # 버튼에 클릭 이벤트 핸들러 연결
        self.ui.selectStorePushButton.clicked.connect(self.showSubForm)
        self.ui.sowingButtonLabel.mousePressEvent = self.showSowingForm
        self.ui.buddingButtonLabel.mousePressEvent = self.showBuddingForm
        self.ui.raisingButtonLabel.mousePressEvent = self.showRaisingForm
        self.ui.graftingButtonLabel.mousePressEvent = self.showGraftingForm
        self.ui.monitoringButtonLabel.mousePressEvent = self.showMonitoringForm
        # 다른 버튼에 대한 클릭 이벤트 핸들러도 동일하게 추가

        # DB 연결
        self.db_connection = connect_to_db()

    # 서브 폼 보여주기
    @pyqtSlot()
    def showSubForm(self):
        subForm = SubForm()
        subForm.exec_()

    # sowing 폼 보여주기
    @pyqtSlot()
    def showSowingForm(self, event):
        self.event_manager.change_to_sowing_form()

    # budding 폼 보여주기
    @pyqtSlot()
    def showBuddingForm(self, event):
        self.event_manager.change_to_budding_form()

    # raising 폼 보여주기
    @pyqtSlot()
    def showRaisingForm(self, event):
        self.event_manager.change_to_raising_form()

    # grafting 폼 보여주기
    @pyqtSlot()
    def showGraftingForm(self, event):
        self.event_manager.change_to_grafting_form()

    # grafting 폼 보여주기
    @pyqtSlot()
    def showMonitoringForm(self, event):
        self.event_manager.change_to_monitoring_form()

# monitoring 폼 클래스
class MonitoringForm(QMainWindow):
    goToMainWindow = pyqtSignal()

    def __init__(self, event_manager, mqtt_client):
        super().__init__()
        self.ui = monitoring_form_class()
        self.ui.setupUi(self)
        self.event_manager = event_manager
        self.mqtt_client = mqtt_client


        # Connect buttons to their respective methods
        self.ui.sowingButtonLabel.mousePressEvent = self.showSowingForm
        self.ui.buddingButtonLabel.mousePressEvent = self.showBuddingForm
        self.ui.raisingButtonLabel.mousePressEvent = self.showRaisingForm
        self.ui.graftingButtonLabel.mousePressEvent = self.showGraftingForm
        self.ui.takingButtonLabel.mousePressEvent = self.showTakingForm

        # DB 연결
        self.db_connection = connect_to_db()

        # SVG 파일 로드 및 표시
        self.load_svg("renew_monitoring_map.svg")

        # 태그 위치 저장
        self.tag_positions = self.get_tag_positions("renew_monitoring_map.svg")

        # 패널 위치 저장
        self.panel_positions = self.get_panel_positions("renew_monitoring_map.svg")

        # 로봇 시나리오 설정
        self.robot_scenarios = [
            [2,3,4,5,6,7,8,9,10,11,12, 13, 14, 15, 16, 16, 17, 18, 22, 23, 24, 25, 26, 27, 28, 28, 27, 26, 25, 24, 23],
            [1,2,3,4,5,6,7,8,9,10, 11, 12, 13, 14, 15, 15, 16, 17, 18, 22, 23, 24, 25, 26, 27,30,29,29,30,27,26],
            [0,1,2,3,4,5,6,7,8,9,10, 11, 11, 12, 13, 14, 15, 16, 17, 18, 22, 23, 36, 37, 38, 39, 40, 40, 39, 38, 37]
        ]

        # 로봇 상태 초기화
        self.robot_states = ["대기장소", "대기장소", "대기장소"]
        
        # 로봇 도형 추가
        self.robot_shapes = self.add_robot_shapes()

        # 패널 아이템 추가
        self.panel_items = self.add_panel_items()

        # 타이머 설정
        self.timer = QTimer()
        self.timer.timeout.connect(self.move_robots)
        self.timer.start(ROBOT_MOVE_INTERVAL)  # 로봇 이동 간격

        # 패널 이동을 위한 타이머 설정
        self.panel_timer = QTimer()
        self.panel_timer.timeout.connect(self.move_panels)
        self.panel_timer.start(PANEL_MOVE_INTERVAL)  # 패널 이동 간격

        self.current_index = [0, 0, 0]  # 각 로봇의 현재 위치 인덱스

    def load_svg(self, svg_file):
        """SVG 파일을 로드하여 QGraphicsView에 표시"""
        svg_path = os.path.join(os.getcwd(), 'images', svg_file)

        # 경로가 존재하는지 확인
        if not os.path.exists(svg_path):
            print(f"File not found: {svg_path}")
            return

        # QGraphicsScene과 QGraphicsSvgItem을 사용하여 SVG 파일 로드
        self.scene = QGraphicsScene()
        self.svg_item = QGraphicsSvgItem(svg_path)
        self.scene.addItem(self.svg_item)

        # SVG 아이템이 마우스 이벤트를 받지 않도록 설정
        self.svg_item.setAcceptedMouseButtons(Qt.NoButton)
        self.svg_item.setZValue(-1)  # SVG 아이템을 가장 뒤로 보냄

        # QGraphicsView에 Scene 설정
        self.ui.dynamicGraphicsView.setScene(self.scene)

        # SVG의 실제 크기를 확인하기 위해 경계값 출력 (디버깅용)
        svg_rect = self.svg_item.boundingRect()
        print(f"SVG Rect: {svg_rect}")

        # SVG의 viewBox 속성 확인 (좌표계 변환을 위해)
        svg_element = ET.parse(svg_path).getroot()
        viewBox = svg_element.get("viewBox")
        if viewBox:
            self.viewBox_values = [float(v) for v in viewBox.split()]
            print(f"SVG viewBox: {self.viewBox_values}")
        else:
            self.viewBox_values = [0, 0, svg_rect.width(), svg_rect.height()]
            print(f"viewBox가 없습니다. 기본값 사용: {self.viewBox_values}")

        # 뷰포트 스케일을 맞추기 위해 스케일을 직접 계산하여 설정
        view_rect = self.ui.dynamicGraphicsView.viewport().rect()  # 뷰포트 크기
        scale_x = view_rect.width() / svg_rect.width()  # X축 스케일 비율
        scale_y = view_rect.height() / svg_rect.height()  # Y축 스케일 비율

        # Y축 스케일을 X축 스케일과 동일하게 맞춤
        print(f"뷰포트 스케일 - X축: {scale_x}, Y축: {scale_y}")
        scale = scale_x  # X축 스케일에 맞추어 Y축을 강제 동일하게 맞춤

        # SVG 크기에 맞춰 스케일 설정
        self.ui.dynamicGraphicsView.resetTransform()  # 기존 스케일 초기화
        self.ui.dynamicGraphicsView.scale(scale, scale)  # 동일한 비율로 스케일 적용

        # QPainter의 Antialiasing 적용
        self.ui.dynamicGraphicsView.setRenderHint(QPainter.Antialiasing)

    def resizeEvent(self, event):
        """윈도우 크기 변경 시 SVG 크기를 맞추기"""
        self.ui.dynamicGraphicsView.fitInView(self.ui.dynamicGraphicsView.sceneRect(), Qt.KeepAspectRatio)
        super().resizeEvent(event)

    def get_tag_positions(self, svg_file):
        """SVG 파일에서 태그 위치 파싱하여 좌표 반환"""
        svg_path = os.path.join(os.getcwd(), 'images', svg_file)
        tree = ET.parse(svg_path)
        root = tree.getroot()

        namespaces = {'svg': 'http://www.w3.org/2000/svg'}

        # 태그 위치 저장
        tag_positions = {}
        for i in range(43):
            tag_id = f"tag{i}"
            elem = root.find(f".//svg:rect[@id='{tag_id}']", namespaces)
            if elem is not None:
                x = float(elem.get('x'))
                y = float(elem.get('y'))
                width = float(elem.get('width'))
                height = float(elem.get('height'))

                # 사각형의 중심 좌표 계산
                center_x = x + width / 2
                center_y = y + height / 2

                center_x, center_y = self.convert_svg_to_view_coordinates(center_x, center_y)
                tag_positions[tag_id] = (center_x, center_y)
                print(f"{tag_id} 위치: ({center_x}, {center_y})")
            else:
                print(f"{tag_id}를 찾을 수 없습니다.")

        return tag_positions

    def get_panel_positions(self, svg_file):
        """SVG 파일에서 패널 위치 파싱하여 좌표 반환"""
        svg_path = os.path.join(os.getcwd(), 'images', svg_file)
        tree = ET.parse(svg_path)
        root = tree.getroot()

        namespaces = {'svg': 'http://www.w3.org/2000/svg'}

        # 패널 위치 저장
        panel_positions = []
        for i in range(1, 35):  # 패널 번호는 1부터 34까지
            panel_id = f"panel{i}"
            elem = root.find(f".//svg:rect[@id='{panel_id}']", namespaces)
            if elem is not None:
                x = float(elem.get('x'))
                y = float(elem.get('y'))
                width = float(elem.get('width'))
                height = float(elem.get('height'))

                # 사각형의 중심 좌표 계산
                center_x = x + width / 2
                center_y = y + height / 2

                # 좌표 및 크기 변환
                center_x, center_y, width_scaled, height_scaled = self.convert_svg_to_view_coordinates(
                    center_x, center_y, width, height
                )

                panel_positions.append({
                    'id': panel_id,
                    'position': (center_x, center_y),
                    'width': width_scaled,
                    'height': height_scaled
                })
                print(f"{panel_id} 위치: ({center_x}, {center_y}), 크기: ({width_scaled}, {height_scaled})")
            else:
                print(f"{panel_id}를 찾을 수 없습니다.")

        return panel_positions

    def convert_svg_to_view_coordinates(self, x, y, width=None, height=None):
        """SVG 좌표를 QGraphicsView 좌표로 변환"""
        # viewBox에 따른 변환
        viewBox_x, viewBox_y, viewBox_width, viewBox_height = self.viewBox_values

        # 좌표를 viewBox 기준으로 변환
        x_transformed = (x - viewBox_x) / viewBox_width * self.svg_item.boundingRect().width()
        y_transformed = (y - viewBox_y) / viewBox_height * self.svg_item.boundingRect().height()

        if width is not None and height is not None:
            # 사이즈 변환
            width_transformed = width / viewBox_width * self.svg_item.boundingRect().width()
            height_transformed = height / viewBox_height * self.svg_item.boundingRect().height()
            return x_transformed, y_transformed, width_transformed, height_transformed
        else:
            return x_transformed, y_transformed

    def add_robot_shape(self, tag_id, shape_type):
        """로봇 아이콘을 지정된 색상으로 칠하여 Scene에 추가"""
        image_path = os.path.join(os.getcwd(), 'images', 'agv-robot.png')  # 로봇 아이콘 이미지 경로
        pixmap = QPixmap(image_path)
        
        # 이미지 크기 조정 (도형 크기 20x20에 맞춤)
        scaled_pixmap = pixmap.scaled(TAG_RECT_SIZE, TAG_RECT_SIZE, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        
        # QPainter를 사용하여 색상 덮어쓰기
        colored_pixmap = QPixmap(scaled_pixmap.size())
        colored_pixmap.fill(Qt.transparent)  # 투명한 배경
        painter = QPainter(colored_pixmap)
        painter.drawPixmap(0, 0, scaled_pixmap)  # 원래 이미지 그리기

        # 도형 타입에 따른 색상 지정
        if shape_type == 'ellipse':  # 빨간색
            painter.setCompositionMode(QPainter.CompositionMode_SourceIn)
            painter.fillRect(colored_pixmap.rect(), QColor(Qt.red))
        elif shape_type == 'rectangle':  # 초록색
            painter.setCompositionMode(QPainter.CompositionMode_SourceIn)
            painter.fillRect(colored_pixmap.rect(), QColor(Qt.green))
        elif shape_type == 'triangle':  # 파란색
            painter.setCompositionMode(QPainter.CompositionMode_SourceIn)
            painter.fillRect(colored_pixmap.rect(), QColor(Qt.blue))
        
        painter.end()

        # 이미지의 위치 계산
        x, y = self.tag_positions[tag_id]
        x_centered = x - TAG_RECT_SIZE / 2
        y_centered = y - TAG_RECT_SIZE / 2
        
        # QGraphicsPixmapItem 생성 및 설정
        shape = QGraphicsPixmapItem(colored_pixmap)
        shape.setPos(x_centered, y_centered)
        shape.setZValue(2)  # 로봇 아이콘을 가장 위로 설정
        self.scene.addItem(shape)
        return shape

    def add_robot_shapes(self):
        """모든 로봇 도형 추가"""
        robot_shapes = []
        for tag_id, shape_type in ROBOT_SHAPES.items():
            shape = self.add_robot_shape(tag_id, shape_type)
            robot_shapes.append(shape)
        return robot_shapes

    def add_panel_items(self):
        """패널 아이템들을 Scene에 추가"""
        panel_items = []
        for panel_info in self.panel_positions:
            panel_id = panel_info['id']
            x, y = panel_info['position']
            width = panel_info['width']
            height = panel_info['height']

            # 패널 아이템 생성
            rect_item = PanelItem(panel_id, -width / 2, -height / 2, width, height)
            rect_item.setPos(x, y)
            rect_item.setPen(QColor(Qt.black))
            rect_item.setFlag(QGraphicsItem.ItemIsSelectable, True)
            rect_item.setZValue(1)  # 패널을 SVG 위에 표시

            # 패널 데이터에 따른 색상 설정
            data = PANEL_DATA.get(panel_id, {})
            fruit = data.get('과실', '')
            if panel_id == 'panel1':
                rect_item.setBrush(QColor(Qt.yellow))  # 패널1은 노란색
            elif panel_id == 'panel34':
                rect_item.setBrush(QColor(Qt.green))  # 패널34는 초록색
            elif fruit == '상추':
                rect_item.setBrush(QColor(Qt.red))  # 과실이 '상추'인 경우 빨간색
            elif fruit == '없음' or fruit == '과실없음':
                rect_item.setBrush(QColor(Qt.black))  # 과실이 '없음'인 경우 검은색
            else:
                rect_item.setBrush(QColor(Qt.lightGray))  # 그 외의 경우 기본 색상

            self.scene.addItem(rect_item)
            panel_items.append(rect_item)
        return panel_items

    def move_robots(self):
        """로봇들을 시나리오에 따라 이동"""
        for i in range(3):
            # 이전 도형 제거
            self.scene.removeItem(self.robot_shapes[i])

            # 현재 위치 인덱스 업데이트
            self.current_index[i] += 1
            if self.current_index[i] >= len(self.robot_scenarios[i]):
                self.current_index[i] = 0

            # 현재 위치의 태그 ID
            tag_id = f"tag{self.robot_scenarios[i][self.current_index[i]]}"
            
            # 로봇 도형 다시 추가
            shape_type = list(ROBOT_SHAPES.values())[i]
            self.robot_shapes[i] = self.add_robot_shape(tag_id, shape_type)

            # 로봇 도형의 좌표 출력
            x, y = self.tag_positions[tag_id]
            shape_size = 20
            x_centered = x - shape_size / 2
            y_centered = y - shape_size / 2
            #print(f"로봇 {i+1} 도형 위치: (x: {x_centered}, y: {y_centered})")

            # 특정 장소에 2번 연속으로 있는 경우 상태 변경
            if self.current_index[i] > 0 and self.robot_scenarios[i][self.current_index[i]] == self.robot_scenarios[i][self.current_index[i]-1]:
                tag_num = self.robot_scenarios[i][self.current_index[i]]
                if tag_num == 11:
                    self.robot_states[i] = "본상 하역"
                elif tag_num == 17:
                    self.robot_states[i] = "파종 대기"
                elif tag_num == 19:
                    self.robot_states[i] = "본상 적재"
                elif 27 <= tag_num <= 30:
                    self.robot_states[i] = "발아실 적재"
                elif 32 <= tag_num <= 35:
                    self.robot_states[i] = "접목실 적재"
                elif 39 <= tag_num <= 42:
                    self.robot_states[i] = "활착실 적재"
            else:
                self.robot_states[i] = "이동 진행"

            # 로봇 상태 업데이트 (라벨 업데이트 부분은 실제 UI에 맞게 수정 필요)
            if i == 0:
                self.ui.currentPositionLabel1.setText(self.robot_states[i])
            elif i == 1:
                self.ui.currentPositionLabel2.setText(self.robot_states[i])
            elif i == 2:
                self.ui.currentPositionLabel3.setText(self.robot_states[i])

    def move_panels(self):
        """패널들을 시계방향으로 한 칸씩 이동"""
        # 패널 위치 리스트를 시계방향으로 한 칸씩 회전
        first_position = self.panel_positions[0]['position']
        first_width = self.panel_positions[0]['width']
        first_height = self.panel_positions[0]['height']
        for i in range(len(self.panel_positions)-1):
            self.panel_positions[i]['position'] = self.panel_positions[i+1]['position']
            self.panel_positions[i]['width'] = self.panel_positions[i+1]['width']
            self.panel_positions[i]['height'] = self.panel_positions[i+1]['height']
        self.panel_positions[-1]['position'] = first_position
        self.panel_positions[-1]['width'] = first_width
        self.panel_positions[-1]['height'] = first_height

        # 패널 아이템들의 위치 업데이트
        for idx, panel_item in enumerate(self.panel_items):
            panel_id = self.panel_positions[idx]['id']
            x, y = self.panel_positions[idx]['position']
            panel_item.setPos(x, y)

            # 패널 데이터에 따른 색상 설정
            data = PANEL_DATA.get(panel_id, {})
            fruit = data.get('과실', '')
            if panel_id == 'panel1':
                panel_item.setBrush(QColor(Qt.yellow))  # 패널1은 노란색
            elif panel_id == 'panel34':
                panel_item.setBrush(QColor(Qt.green))  # 패널34는 초록색
            elif fruit == '상추':
                panel_item.setBrush(QColor(Qt.red))  # 과실이 '상추'인 경우 빨간색
            elif fruit == '없음' or fruit == '과실없음':
                panel_item.setBrush(QColor(Qt.black))  # 과실이 '없음'인 경우 검은색
            else:
                panel_item.setBrush(QColor(Qt.lightGray))  # 그 외의 경우 기본 색상

    def showEvent(self, event):
        """창이 처음 표시될 때 SVG 크기를 맞추기"""
        super().showEvent(event)
        self.ui.dynamicGraphicsView.fitInView(self.ui.dynamicGraphicsView.sceneRect(), Qt.KeepAspectRatio)

    def closeEvent(self, event):
        """프로그램 종료 시 타이머 정지"""
        self.timer.stop()
        self.panel_timer.stop()
        super().closeEvent(event)

    def showMainWindow(self):
        self.stackedWidget.setCurrentWidget(self)


    @pyqtSlot()
    def showSubForm(self):
        subForm = SubForm()
        subForm.exec_()

    @pyqtSlot()
    def showSowingForm(self, event):
        self.event_manager.change_to_sowing_form()

    @pyqtSlot()
    def showBuddingForm(self, event):
        self.event_manager.change_to_budding_form()

    @pyqtSlot()
    def showRaisingForm(self, event):
        self.event_manager.change_to_raising_form()

    @pyqtSlot()
    def showGraftingForm(self, event):
        self.event_manager.change_to_grafting_form()

    @pyqtSlot()
    def showTakingForm(self, event):
        self.event_manager.change_to_taking_form()

    def update_position_label(self, position):
        self.ui.currentPositionLabel1.setText(position)


# 본상 내 버튼 이벤트 정의
class ButtonPopup(QDialog):
    def __init__(self, button_index, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"Button {button_index + 1} Clicked")
        self.setGeometry(100, 100, 200, 100)

        layout = QVBoxLayout()

        label = QLabel(f"You clicked button {button_index + 1}", self)
        layout.addWidget(label)

        close_button = QPushButton("Close", self)
        close_button.clicked.connect(self.close)
        layout.addWidget(close_button)

        self.setLayout(layout)

# MainWindow 클래스
class MainWindow(QMainWindow):
    mqtt_connected = pyqtSignal()
    temperature_update = pyqtSignal(float)
    humidity_update = pyqtSignal(float)
    position_update = pyqtSignal(str)

    def __init__(self):
        super().__init__()

        self.ui = form_class()
        self.ui.setupUi(self)

        self.stackedWidget = QStackedWidget()

        self.mqtt_client = mqtt.Client(client_id) # 클라이언트 아이디 요소 추가
        self.mqtt_client.username_pw_set(username, password) # 추가 설정
        self.mqtt_client.on_connect = self.on_mqtt_connect
        self.mqtt_client.on_message = self.on_mqtt_message
        self.mqtt_client.connect(broker_address, broker_port)
        self.mqtt_client.loop_start()

        self.sowingForm = SowingForm(self, self.mqtt_client)
        self.buddingForm = BuddingForm(self)
        self.raisingForm = RaisingForm(self, self.mqtt_client)
        self.graftingForm = GraftingForm(self)
        self.takingForm = TakingForm(self)
        self.monitoringForm = MonitoringForm(self, self.mqtt_client)

        self.stackedWidget.addWidget(self.sowingForm)
        self.stackedWidget.addWidget(self.buddingForm)
        self.stackedWidget.addWidget(self.raisingForm)
        self.stackedWidget.addWidget(self.graftingForm)
        self.stackedWidget.addWidget(self.takingForm)
        self.stackedWidget.addWidget(self.monitoringForm)

        self.setCentralWidget(self.stackedWidget)

        self.event_manager = EventManager()
        self.event_manager.register_main_window(self)

        self.connect_signals()

        # 메인 윈도우에게 이벤트 관리자를 등록
        self.register_event_manager()

    def connect_signals(self):
        self.temperature_update.connect(self.buddingForm.update_temperature_display)
        self.humidity_update.connect(self.buddingForm.update_humidity_display)
        self.position_update.connect(self.monitoringForm.update_position_label)

    def closeEvent(self, event):
        self.mqtt_client.loop_stop()
        self.mqtt_client.disconnect()
        event.accept()


    def change_to_monitoring_form(self):
        self.stackedWidget.setCurrentWidget(self.monitoringForm)  # 모니터링 폼으로 전환


    def on_mqtt_connect(self, client, userdata, flags, rc):
        if rc == 0:
            print("MQTT 브로커에 연결되었습니다.")
            self.mqtt_client.subscribe("demo/sensors")
            self.mqtt_client.subscribe("demo/position")
            self.mqtt_client.subscribe("demo/move")  # 추가: 큐브 이동을 위한 토픽 구독
            self.mqtt_client.subscribe("farm/QR")
            self.mqtt_client.subscribe("farm/gentry_status")
            self.mqtt_client.subscribe("farm/loader_status")
        else:
            print("MQTT 브로커에 연결하는 데 실패했습니다.")

    def on_mqtt_message(self, client, userdata, message):
        try:
            payload = json.loads(message.payload.decode())
            if message.topic == "demo/sensors":
                temperature = payload.get('temperature')
                humidity = payload.get('humidity')

                if temperature is not None:
                    self.temperature_update.emit(temperature)
                if humidity is not None:
                    self.humidity_update.emit(humidity)

            elif message.topic == "demo/move":
                try:
                    command = int(payload)
                    self.monitoringForm.opengl_widget.update_cube_position(command)
                except ValueError:
                    print(f"메시지 파싱 오류: 정수로 변환할 수 없습니다 - {payload}")

            elif message.topic == "farm/QR":
                print(f"메시지 파싱: {payload}")

            elif message.topic == "farm/gentry_status":
                print(f"메시지 파싱: {payload}")

                payload_data = json.loads(payload)
                
                x_position = payload_data.get('x_position')
                y_position = payload_data.get('y_position')
                pump = payload_data.get('pump')
                datatime = payload_data.get('datatime')

                MainWindow.show_popup(f"본상 상태\nx_position: {x_position}\ny_position: {y_position}\npump: {pump}\ndatatime: {datatime}")
            
            elif message.topic == "farm/loader_status":
                print(f"메시지 파싱: {payload}")
                tray = payload_data.get('tray')
                status = payload_data.get('status')
                error = payload_data.get('error')
                datatime = payload_data.get('datatime')

                MainWindow.show_popup(f"로더 상태\ntray: {tray}\nstatus: {status}\nerror: {error}\ndatatime :{datatime}")
            
        except Exception as e:
            print(f"메시지 파싱 오류: {str(e)}")

    # 추가 1016_start
    def show_popup(message):
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Information)
        msg_box.setWindowTitle("MQTT 메시지")
        msg_box.setText(message)
        msg_box.setStandardButtons(QMessageBox.Ok)
        msg_box.exec_()
    # 추가 1016_end

    # 이벤트 관리자를 등록하는 메서드
    def register_event_manager(self):
        self.sowingForm.event_manager = self.event_manager
        self.buddingForm.event_manager = self.event_manager
        self.raisingForm.event_manager = self.event_manager
        self.graftingForm.event_manager = self.event_manager
        self.takingForm.event_manager = self.event_manager
        self.monitoringForm.event_manager = self.event_manager

# 이벤트 관리자 클래스
class EventManager:
    def __init__(self):
        self.main_window = None

    # 메인 윈도우를 등록하는 메서드
    def register_main_window(self, main_window):
        self.main_window = main_window

    # budding 폼으로 변경하는 메서드
    def change_to_budding_form(self):
        print("Switching to Budding Form")  # 디버그 출력 추가
        print(f"MainWindow: {self.main_window}")  # MainWindow가 올바르게 설정되었는지 확인
        self.main_window.stackedWidget.setCurrentWidget(self.main_window.buddingForm)


    # sowing 폼으로 변경하는 메서드
    def change_to_sowing_form(self):
        self.main_window.stackedWidget.setCurrentWidget(self.main_window.sowingForm)

    # raising 폼으로 변경하는 메서드
    def change_to_raising_form(self):
        self.main_window.stackedWidget.setCurrentWidget(self.main_window.raisingForm)

    # grafting 폼으로 변경하는 메서드
    def change_to_grafting_form(self):
        try:
            self.main_window.stackedWidget.setCurrentWidget(self.main_window.graftingForm)
        except Exception as e:
            print(f"Error while changing to grafting form: {e}")
        # self.main_window.stackedWidget.setCurrentWidget(self.main_window.graftingForm)

    # raising 폼으로 변경하는 메서드
    def change_to_taking_form(self):
        self.main_window.stackedWidget.setCurrentWidget(self.main_window.takingForm)

    def change_to_monitoring_form(self):
        self.main_window.stackedWidget.setCurrentWidget(self.main_window.monitoringForm)


# 메인 프로그램
if __name__ == "__main__":
    app = QApplication(sys.argv)
    mainWindow = MainWindow()
    mainWindow.show()
    sys.exit(app.exec_())
