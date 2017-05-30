import serial

from PyQt5.QtWidgets import * #QApplication, QWidget, QPushButton, QLineEdit, QListView
from PyQt5.QtGui import * #QFont, QStandardItemModel, QStandardItem
from PyQt5.QtCore import *

import sqlite3

import sys, argparse

def log(description):
	print(description)


txt = {
	'inpserial': '시리얼 포트',
	'title': 'CRUX-170HD Controller',
	'connect': '연결',
	'message': '메시지',
	'quit': '종료하시겠습니까?',
	'catsearch': '카탈로그 검색',
	'slew': '선택한 대상으로 GOTO',
	'stopslew': '적도의 정지',
	'mountra': '적도의 적경',
	'mountdec': '적도의 적위',
	'objectname': '대상 이름',
	'objectra': '대상 적경',
	'objectdec': '대상 적위',
	'constellation': '별자리',
	'commonname': '다른 이름',
	'type': '종류',
	'magnitude': '등급',
	'connected': '연결됨',
	'nc': '연결 안 됨',
	'status': '상태',
	'connectfailed': '연결 실패',
	'speed': '속도',
	'nightmodeon': '야간 모드 켜기',
	'nightmodeoff': '야간 모드 끄기'
}

db = 'dso.db'
dbc = sqlite3.connect(db, check_same_thread=False)
dbc.text_factory = str
c = dbc.cursor()

ser = serial.Serial()
ser.baudrate = 9600
ser.timeout = 0.1

dsodata = []
selectedDSO = None

status = False

def getDSOName(dso):
	return dso[7] + ' ' + str(dso[8])

def convRA(RA):
	RAH = int(RA)
	RAM = int((RA-RAH)*60)
	RAS = int(((RA-RAH)*60-RAM)*60)
	return [RAH, RAM, RAS]

def convDEC(DEC):
	sign = 1 if abs(DEC) == DEC else -1
	dectmp = abs(DEC)
	DECD = int(dectmp)
	DECM = int((dectmp-DECD)*60)
	DECS = int(((dectmp-DECD)*60-DECM)*60)
	return [sign, DECD, DECM, DECS]

def serialwrite(data):
	global ser
	print(data)
	#ser.write(data.encode())

def serialread(length):
	global ser
	if length == 9:
		return '04:54:23#'
	else:
		return "-32*34'23#"
	#return ser.read(length).decode('utf-8')

def makestatus(status):
	return '<b>' + txt['status'] + ' </b>' + status


class WMain(QWidget):
	def __init__(self):
		super().__init__()
		self.initUI()

	def initUI(self):
		self.inpSerial = QLineEdit(self)
		self.inpSerial.setPlaceholderText(txt['inpserial'])
		self.inpSerial.resize(100, 20)
		self.inpSerial.move(15, 15)

		self.btnSerial = QPushButton(txt['connect'], self)
		self.btnSerial.resize(70, 20)
		self.btnSerial.move(125, 15)
		self.btnSerial.clicked.connect(self.click_btnSerial)

		self.inpCat = QLineEdit(self)
		self.inpCat.setPlaceholderText(txt['catsearch'])
		self.inpCat.resize(120, 20)
		self.inpCat.move(15, 60)
		self.inpCat.textChanged.connect(self.searchCat)

		self.listCat = QListView(self)
		self.listCat.resize(120, 150)
		self.listCat.move(15, 85)
		self.listCat.setEditTriggers(QAbstractItemView.NoEditTriggers)
		self.searchCat()

		self.labelCat = QLabel(self)
		self.labelCat.resize(200, 150)
		self.labelCat.move(150, 60)
		self.labelCat.setAlignment(Qt.AlignTop | Qt.AlignLeft)

		self.btnSlew = QPushButton(txt['slew'], self)
		self.btnSlew.resize(200, 30)
		self.btnSlew.move(70, 250)
		self.btnSlew.clicked.connect(self.click_btnSlew)

		self.btnStopSlew = QPushButton(txt['stopslew'], self)
		self.btnStopSlew.resize(200, 30)
		self.btnStopSlew.move(70, 285)
		self.btnStopSlew.clicked.connect(self.click_btnStopSlew)

		self.labelMount = QLabel(self)
		self.labelMount.resize(300, 150)
		self.labelMount.move(20, 330)
		self.labelMount.setAlignment(Qt.AlignTop | Qt.AlignLeft)

		self.labelStatus = QLabel(self)
		self.labelStatus.resize(300, 30)
		self.labelStatus.move(230, 15)
		self.labelStatus.setAlignment(Qt.AlignTop | Qt.AlignLeft)
		self.labelStatus.setText(makestatus(txt['nc']))

		self.timerMount = QTimer(self)
		self.timerMount.timeout.connect(self.runTimerMount)
		self.timerMount.start(250)

		font = QFont()
		font.setPointSize(18)

		self.btnMoveUp = QPushButton('▲', self)
		self.btnMoveUp.resize(70, 50)
		self.btnMoveUp.move(135, 380)
		self.btnMoveUp.clicked.connect(self.click_btnMoveUp)
		self.btnMoveUp.setFont(font)
		
		self.btnMoveDown = QPushButton('▼', self)
		self.btnMoveDown.resize(70, 50)
		self.btnMoveDown.move(135, 440)
		self.btnMoveDown.clicked.connect(self.click_btnMoveDown)
		self.btnMoveDown.setFont(font)
		
		self.btnMoveLeft = QPushButton('◀', self)
		self.btnMoveLeft.resize(70, 50)
		self.btnMoveLeft.move(50, 410)
		self.btnMoveLeft.clicked.connect(self.click_btnMoveLeft)
		self.btnMoveLeft.setFont(font)
		
		self.btnMoveRight = QPushButton('▶', self)
		self.btnMoveRight.resize(70, 50)
		self.btnMoveRight.move(220, 410)
		self.btnMoveRight.clicked.connect(self.click_btnMoveRight)
		self.btnMoveRight.setFont(font)

		self.labelSpeed = QLabel(self)
		self.labelSpeed.resize(100, 20)
		self.labelSpeed.move(215, 380)
		self.labelSpeed.setAlignment(Qt.AlignTop | Qt.AlignLeft)
		self.labelSpeed.setText('<b>' + txt['speed'] + '</b>')

		self.cmbSpeed = QComboBox(self)
		self.cmbSpeed.addItems(["Guide", "Center", "Find", "Slew"])
		self.cmbSpeed.currentIndexChanged.connect(self.changeSpeed)
		self.cmbSpeed.resize(85, 25)
		self.cmbSpeed.move(250, 370)
		self.cmbSpeed.setCurrentIndex(3)


		self.btnNightMode = QPushButton(txt['nightmodeon'], self)
		self.btnNightMode.resize(100, 25)
		self.btnNightMode.move(20, 480)
		self.btnNightMode.clicked.connect(self.setNightMode)
		self.nightmode = False
		
		self.moving = [0, 0, 0, 0]

		self.MountRA = 0.
		self.MountDEC = 0.
		self.toggleTimer = 1

		self.setFixedSize(340, 520)
		self.setWindowTitle(txt['title'])
		self.setStyle(QStyleFactory.create('Fusion'))
		self.show()

	def closeEvent(self, event):
		result = QMessageBox.question(self, txt['message'], txt['quit'], QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

		if result == QMessageBox.Yes:
			event.accept()
		else:
			event.ignore() 

	def click_btnSerial(self):
		global ser
		try:
			ser.port = self.inpSerial.text()
			ser.open()
			status = True
			self.labelStatus.setText(makestatus(txt['connected']))
			serialwrite(':RS#')
		except:
			status = False
			self.labelStatus.setText(makestatus(txt['connectfailed']))
		serialwrite(':Sr00:00:00#')
		#serialwrite(':U#')

	def searchCat(self):
		global c
		c.execute("SELECT * FROM DSO WHERE catalogue || cid LIKE ? ORDER BY catalogue, cid", ('%' + self.inpCat.text().replace(' ', '') + '%',))
		#print(c.fetchall())
		global dsodata
		dsodata = c.fetchall()
		model = QStandardItemModel(self.listCat)
		for i in dsodata:
			item = QStandardItem(getDSOName(i))
			model.appendRow(item)
		self.listCat.setModel(model)
		self.listCat.selectionModel().selectionChanged.connect(self.selectCat)

	def selectCat(self, selected):
		global dsodata, selectedDSO
		selected = selected.indexes()[0].data()
		for i in dsodata:
			if getDSOName(i) == selected:
				selectedDSO = i
				RA = convRA(selectedDSO[2])
				DEC = convDEC(selectedDSO[3])
				RA = str(RA[0]) + "h " + str(RA[1]) + "m " + str(RA[2]) + "s"
				DEC = ("-" if DEC[0] < 0 else "") + str(DEC[1]) + "° " + str(DEC[2]) + "m " + str(DEC[3]) + "s"

				self.labelCat.setText(
					"<b>" + txt['objectname'] + " </b>" + selected  + "<br />" +
					"<b>" + txt['objectra'] + " </b>" + RA + "<br />" +
					"<b>" + txt['objectdec'] + " </b>" + DEC + "<br />" +
					"<b>" + txt['commonname'] + " </b>" + i[1] + "<br />" +
					"<b>" + txt['constellation'] + " </b>" + i[5] + "<br />" +
					"<b>" + txt['magnitude'] + " </b>" + str(i[6]) + "<br />" +
					"<b>" + txt['type'] + " </b>" + i[4]
					)
				break


	def Mmove(self, direction):
		global moving
		if direction == 0:
			if self.moving[direction] == 0:
				serialwrite(':Mn#')
				self.btnMoveUp.setText('■')
				self.moving[direction] = 1
			else:
				serialwrite(':Qn#')
				self.btnMoveUp.setText('▲')
				self.moving[direction] = 0
		elif direction == 1:
			if self.moving[direction] == 0:
				serialwrite(':Ms#')
				self.btnMoveDown.setText('■')
				self.moving[direction] = 1
			else:
				serialwrite(':Qs#')
				self.btnMoveDown.setText('▼')
				self.moving[direction] = 0
		elif direction == 2:
			if self.moving[direction] == 0:
				serialwrite(':Mw#')
				self.btnMoveLeft.setText('■')
				self.moving[direction] = 1
			else:
				serialwrite(':Qw#')
				self.btnMoveLeft.setText('◀')
				self.moving[direction] = 0
		elif direction == 3:
			if self.moving[direction] == 0:
				serialwrite(':Me#')
				self.btnMoveRight.setText('■')
				self.moving[direction] = 1
			else:
				serialwrite(':Qe#')
				self.btnMoveRight.setText('▶')
				self.moving[direction] = 0

	def click_btnSlew(self):
		if selectedDSO != None:
			DEC = convDEC(selectedDSO[3])
			sign = "-" if DEC[0] < 0 else "+"
			for i in range(1, 4):
				if DEC[i] < 10:
					DEC[i] = '0' + str(DEC[i])
				else:
					DEC[i] = str(DEC[i])

			RA = convRA(selectedDSO[2])
			for i in range(0, 3):
				if RA[i] < 10:
					RA[i] = '0' + str(RA[i])
				else:
					RA[i] = str(RA[i])
			serialwrite(':Sd' + sign + DEC[1] + '*' + DEC[2] + ':' + DEC[3] + '#')
			serialwrite(':Sr' + RA[0] + ':' + RA[1] + ':' + RA[2] + '#')
			serialwrite(':MS#')

	def click_btnStopSlew(self):
		serialwrite(':Q#')
		serialwrite(':RC#')

	def runTimerMount(self):
		if status == True and self.toggleTimer == -1:
			serialwrite(':GR#')
			RAtmp = serialread(9)
			RAtmp = RAtmp.split(':')
			RAtmp[2] = RAtmp[2].replace('#', '')
			self.MountRA = int(RAtmp[0]) + int(RAtmp[1]) / 60. + int(RAtmp[2]) / 60. / 60.
		elif status == True:
			serialwrite(':GD#')
			DECtmp = serialread(10)
			DECsign = -1 if DECtmp[0] == "-" else 1
			DECD = int(DECtmp[1:3])
			DECM = int(DECtmp[4:6])
			DECS = int(DECtmp[7:9])
			self.MountDEC = (int(DECD) + int(DECM) / 60. + int(DECS) / 60. / 60.) * DECsign
		self.toggleTimer *= -1

		RA = convRA(self.MountRA)
		DEC = convDEC(self.MountDEC)

		RA = str(RA[0]) + "h " + str(RA[1]) + "m " + str(RA[2]) + "s"
		DEC = ("-" if DEC[0] < 0 else "") + str(DEC[1]) + "° " + str(DEC[2]) + "m " + str(DEC[3]) + "s"

		self.labelMount.setText(
			"<b>" + txt['mountra'] + " </b>" + RA + "<br />"
			"<b>" + txt['mountdec'] + " </b>" + DEC + "<br />"
			)

	def click_btnMoveUp(self):
		self.Mmove(0)

	def click_btnMoveDown(self):
		self.Mmove(1)

	def click_btnMoveLeft(self):
		self.Mmove(2)

	def click_btnMoveRight(self):
		self.Mmove(3)

	def changeSpeed(self, item):
		if item == 0:
			serialwrite(':RG#')
		elif item == 1:
			serialwrite(':RC#')
		elif item == 2:
			serialwrite(':RM#')
		elif item == 3:
			serialwrite(':RS#')

	def setNightMode(self):
		if self.nightmode == True:
			self.nightmode = False
			self.setStyleSheet('')
			self.btnNightMode.setText(txt['nightmodeon'])
		else:
			self.nightmode = True
			self.setStyleSheet('background-color: red;')
			self.btnNightMode.setText(txt['nightmodeoff'])




if __name__ == '__main__':
	app = QApplication(sys.argv)
	window = WMain()
	sys.exit(app.exec_())