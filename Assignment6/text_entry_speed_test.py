#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
from PyQt5 import QtCore, QtWidgets
import re


class SuperText(QtWidgets.QTextEdit):

    def __init__(self, example_text):
        super(SuperText, self).__init__()
        self.numbers = []
        self.template_doc = ""
        self.setHtml(example_text)
        self.prev_content = ""
        self.generateTemplate()
        self.renderTemplate()
        self.initUI()

    def initUI(self):
        self.setGeometry(100, 100, 400, 400)
        self.setWindowTitle('Text Entry Speed Test')
        self.setFocusPolicy(QtCore.Qt.StrongFocus)
        self.setMouseTracking(True)
        self.show()

    def wheelEvent(self, ev):
        super(SuperText, self).wheelEvent(ev)
        self.generateTemplate()
        self.renderTemplate()
        anc = self.anchorAt(ev.pos())
        if (anc):
            self.changeValue(anc, ev.angleDelta().y())

    def changeValue(self, val_id, amount):
        self.numbers[int(str(val_id))] += amount / 120
        self.renderTemplate()

    def renderTemplate(self):
        cur = self.textCursor()
        doc = self.template_doc
        for num_id, num in enumerate(self.numbers):
            doc = doc.replace('$' + str(num_id) + '$', '%d' % (num))
        self.setHtml(doc)
        self.setTextCursor(cur)

    def generateTemplate(self):
        content = str(self.toPlainText())
        numbers = list(re.finditer(" -?[0-9]+", content))
        numbers = [int(n.group()) for n in numbers]
        self.numbers = numbers
        if len(numbers) == 0:
            self.template_doc = content
            return
        for num_id in range(len(numbers)):
            content = re.sub(
                " " + str(numbers[num_id]), " <a href='%d'>$%d$</a>" % (num_id, num_id), content, count=1)
        self.template_doc = content


def main():
    app = QtWidgets.QApplication(sys.argv)
    super_text = SuperText("An 123 Tagen kamen 1342 Personen.")
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
