#!/usr/bin/env python
# -.- coding: utf-8 -.-
# Author  : Avaris
# Created : 31.10.2012

import sys
import random
from collections import Counter
from PyQt4 import QtGui, QtCore


class Row(QtGui.QWidget):
    rowComplete = QtCore.pyqtSignal(bool)

    def __init__(self, colors=None, parent=None):
        super(Row, self).__init__(parent)
        self.setFixedSize(120, 30)

        if colors is None:
            self.colors = [None]*4
        else:
            self.colors = colors[:]

    def appendColor(self, new_color):
        for i, color in enumerate(self.colors):
            if color is None:
                self.colors[i] = new_color
                break
        self.rowComplete.emit(all(color is not None for color in self.colors))
        self.update()

    def clearLastColor(self):
        for i in reversed(range(4)):
            if self.colors[i] is not None:
                self.colors[i] = None
                break
        self.rowComplete.emit(False)
        self.update()

    def clear(self):
        self.colors = [None]*4
        self.rowComplete.emit(False)
        self.update()

    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        for i, color in enumerate(self.colors):
            if color is None:
                painter.setBrush(QtGui.QBrush(QtCore.Qt.black))
                painter.drawEllipse(i*30+13, 13, 4, 4)
            else:
                gradient = QtGui.QRadialGradient(i*30+15, 15, 15, i*30+12, 12)
                gradient.setColorAt(0, QtCore.Qt.white)
                gradient.setColorAt(0.2, color)
                gradient.setColorAt(1, QtCore.Qt.black)
                painter.setBrush(gradient)
                painter.drawEllipse(i*30+5, 5, 20, 20)
        painter.end()

class Result(QtGui.QWidget):
    def __init__(self, result, parent=None):
        super(Result, self).__init__(parent)
        self.result = result
        self.setFixedSize(30, 30)

    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        for i, color in enumerate(self.result):
            row, column = divmod(i, 2)
            gradient = QtGui.QRadialGradient(column*15+7, row*15+7, 5, column*15+5, row*15+5)
            gradient.setColorAt(0, QtCore.Qt.white)
            gradient.setColorAt(0.5, color)
            gradient.setColorAt(1, QtCore.Qt.black)
            painter.setBrush(gradient)
            painter.drawEllipse(column*15+2, row*15+2, 10, 10)
        painter.end()

class History(QtGui.QScrollArea):
    def __init__(self, parent=None):
        super(History, self).__init__(parent)

        self.layout = QtGui.QVBoxLayout()
        self.layout.setSpacing(3)
        self.setWidgetResizable(True)

        widget = QtGui.QWidget()
        widgetLayout = QtGui.QVBoxLayout()
        widgetLayout.addLayout(self.layout)
        widgetLayout.addStretch()
        widget.setLayout(widgetLayout)
        self.setWidget(widget)

    def addRow(self, colors, result):
        row = Row(colors)
        result = Result(result)
        container = QtGui.QWidget()
        containerLayout = QtGui.QHBoxLayout()
        container.setLayout(containerLayout)
        containerLayout.addWidget(row)
        containerLayout.addWidget(result)
        self.layout.addWidget(container)

    def clear(self):
        while self.layout.count():
            item = self.layout.takeAt(0)
            item.widget().deleteLater()

class ColorButton(QtGui.QWidget):
    clicked = QtCore.pyqtSignal(QtCore.Qt.GlobalColor)

    def __init__(self, color, parent=None):
        super(ColorButton, self).__init__(parent)
        self.color = color
        self.setFixedSize(30, 30)
        self.pressed = False

    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        if self.pressed:
            gradient = QtGui.QRadialGradient(15, 15, 10, 12, 12)
        else:
            gradient = QtGui.QRadialGradient(15, 15, 15, 12, 12)
        gradient.setColorAt(0, QtCore.Qt.white)
        gradient.setColorAt(0.2, self.color)
        gradient.setColorAt(1, QtCore.Qt.black)
        painter.setBrush(gradient)
        painter.drawEllipse(5, 5, 20, 20)

    def mousePressEvent(self, event):
        self.pressed = True
        self.update()

    def mouseReleaseEvent(self, event):
        self.clicked.emit(self.color)
        self.pressed = False
        self.update()

    def animateClick(self):
        self.clicked.emit(self.color)

class Input(QtGui.QWidget):
    inputSubmitted = QtCore.pyqtSignal(list)

    def __init__(self, colors, parent=None):
        super(Input, self).__init__(parent)

        self.row = Row()
        self.back = QtGui.QToolButton()
        self.back.setArrowType(QtCore.Qt.LeftArrow)
        self.back.clicked.connect(self.row.clearLastColor)
        self.back.setFixedSize(30, 30)
        self.submit = QtGui.QToolButton()
        self.submit.setText(u'\u2713')
        self.submit.setStyleSheet('font-size: 18px;')
        self.submit.setEnabled(False)
        self.submit.setFixedSize(30, 30)
        self.submit.clicked.connect(self.submitInput)
        self.row.rowComplete.connect(self.submit.setEnabled)

        topLayout=QtGui.QHBoxLayout()
        topLayout.addWidget(self.row)
        topLayout.addStretch(1)
        topLayout.addWidget(self.back)
        topLayout.addWidget(self.submit)

        self.colors = colors
        self.colorButtons = []
        colorLayout = QtGui.QHBoxLayout()
        for color in self.colors:
            button = ColorButton(color)
            self.colorButtons.append(button)
            colorLayout.addWidget(button)
            button.clicked.connect(self.row.appendColor)

        layout = QtGui.QVBoxLayout()
        layout.addLayout(topLayout)
        layout.addLayout(colorLayout)
        self.setLayout(layout)

    def submitInput(self):
        self.inputSubmitted.emit(self.row.colors)
        self.row.clear()

    def keyPressEvent(self, event):
        key = event.key()
        if 49 <= key <= 54: # 1..6
            self.colorButtons[key-49].animateClick()
        elif key == QtCore.Qt.Key_Backspace:
            self.row.clearLastColor()
        elif key == QtCore.Qt.Key_Return:
            self.submit.animateClick()

class Mastermind(QtGui.QWidget):
    def __init__(self, parent=None):
        super(Mastermind, self).__init__(parent)

        self.setWindowTitle(u'Mastermind (\u2184) Avaris')
        self.setWindowIcon()
        self.setMinimumHeight(500)

        self.colors = [QtCore.Qt.red, QtCore.Qt.green, QtCore.Qt.blue, QtCore.Qt.yellow, QtCore.Qt.magenta, QtCore.Qt.cyan]

        self.history = History()

        self.input = Input(self.colors)
        self.input.inputSubmitted.connect(self.checkInput)

        layout = QtGui.QVBoxLayout()
        layout.addWidget(self.history)
        layout.addWidget(self.input)
        self.setLayout(layout)
        self.initialize()

    def setWindowIcon(self):
        pixmap = QtGui.QPixmap(16, 16)
        pixmap.fill(QtCore.Qt.transparent)
        painter = QtGui.QPainter(pixmap)
        gradient = QtGui.QRadialGradient(8, 8, 8, 6, 6)
        gradient.setColorAt(0, QtCore.Qt.white)
        gradient.setColorAt(0.2, QtCore.Qt.red)
        gradient.setColorAt(1, QtCore.Qt.black)
        painter.setBrush(gradient)
        painter.drawEllipse(0, 0, 14, 14)
        painter.end()
        super(Mastermind, self).setWindowIcon(QtGui.QIcon(pixmap))

    def initialize(self):
        self.history.clear()
        self.count = 0
        self.target = [random.choice(self.colors) for _ in range(4)]

    def checkInput(self, guess):
        self.count += 1
        inPlace = sum(t==g for t, g in zip(self.target, guess))
        total = 4 - sum((Counter(guess) - Counter(self.target)).values())
        result = [QtCore.Qt.black]*(total-inPlace) + [QtCore.Qt.white]*inPlace
        self.history.addRow(guess, result)
        if inPlace == 4:
            question = QtGui.QMessageBox(QtGui.QMessageBox.Information,
                                         'Congratulations',
                                         'Yay! You solved it in %d tries.\nAnother game?' % self.count,
                                         QtGui.QMessageBox.Yes | QtGui.QMessageBox.No)
            question.setWindowIcon(self.windowIcon())
            if question.exec_() == QtGui.QMessageBox.Yes:
                self.initialize()
            else:
                self.close()

    def keyPressEvent(self, event):
        self.input.keyPressEvent(event)

if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)

    w = Mastermind()
    w.show()

    sys.exit(app.exec_())