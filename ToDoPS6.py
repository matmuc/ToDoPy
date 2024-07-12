'''
Small Utility to track ToDo Items using PySide6

https://github.com/matmuc/ToDoPy

Copyright (C) 2024  Matthias Vogt

This program is free software; you can redistribute it and/or
modify it under the terms of the GNU General Public License
as published by the Free Software Foundation version 3

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA
'''

import json
import datetime
import sys, io
from os.path import exists

from PySide6.QtCore import Qt, QAbstractTableModel, QDate
from PySide6.QtGui import QBrush, QGuiApplication
from PySide6.QtWidgets import QApplication, QWidget, QMainWindow, QPushButton, \
    QVBoxLayout, QHBoxLayout, QCheckBox, QLabel, QTableView, QComboBox, QHeaderView, QSizePolicy, QSpacerItem, \
    QDialog, QLineEdit, QDateEdit, QTextEdit, QStyle

showDone = False
CatSel = 'ALL'

def qDateFromStr(dStr):
    try:
        tmpD = datetime.datetime.strptime(dStr, '%Y-%m-%d')
        qDate = QDate(tmpD.year, tmpD.month, tmpD.day)
        return qDate
    except:
        return None

def qDateToDateStr(qDate):
    if qDate.month() == 1 and qDate.year() == 2000 and qDate.day() == 1:
        return ""
    date = datetime.datetime(qDate.year(), qDate.month(), qDate.day())
    return date.strftime("%Y-%m-%d")

def getFilteredItems():
    global showDone
    global CatSel
    filteredItems=[]
    for item in ItemsObject:
        if item['Status'].lower() == "deleted":
            itemDeleted = True
        else:
            itemDeleted = False
        if item['Status'].lower() == "done" or item['Status'].lower() == "obsolet":
            itemDone = True
        else:
            itemDone = False
        if CatSel == "ALL" or item['Category'] == CatSel:
            itemCat = True
        else:
            itemCat = False
        if itemDeleted:
            None
        elif showDone and itemDone and itemCat:
            filteredItems.append(item)
        elif not showDone and not itemDone and itemCat:
            filteredItems.append(item)
        #if (showDone and itemDone) or (not showDone and not itemDone) and not itemDeleted and itemCat:
        #    filteredItems.append(item)
    return filteredItems

class TableModel(QAbstractTableModel):
    def __init__(self):
        super(TableModel, self).__init__()
        self.filteredItems = getFilteredItems()
        #print(self.filteredItems)
        self.columns= { 0: 'Category', 1: 'Priority', 2: 'Status', 3: 'Title', 4: 'Description', 5: 'Date', 6: 'DueDate', 7: 'DoneDate'}


    def data(self, index, role):
        global showDone
        global darkScheme

        item = self.filteredItems[index.row()]
        if item['Status'].lower() == "done":
            itemDone = True
        else:
            itemDone = False

        urgent = False
        overdue = False
        
        try:
            itemdate = datetime.datetime.strptime(item['DueDate'],'%Y-%m-%d').date()
            today = datetime.date.today()
            deltaDays = (today-itemdate).days
            if deltaDays > 0 and not itemDone:
                overdue = True
            elif deltaDays > - 7 and not itemDone:
                urgent = True
        except:
            None


        if role == Qt.DisplayRole:
            text = item[self.columns[index.column()]]
            #if index.column() == 1: # titel
            #    text = '  '+text+'   '
            return text
        elif role == Qt.FontRole:
            if not darkScheme:
                return QBrush('#000')
        elif role == Qt.ForegroundRole:
            if darkScheme:
                return QBrush('#000')
            else:
                return QBrush('#000')
        elif role == Qt.BackgroundRole:
            print("urgent: ",urgent," overdue: ",overdue )
            if index.row()%2 > 0:
                if darkScheme:
                    col = QBrush('#4452ac')
                else:      
                    col = QBrush('#f2f2ff')
            else:
                if darkScheme:
                    col = QBrush('#ddd')
                else:      
                    col = QBrush('#fff')
            if overdue and not itemDone:
                return QBrush('#f9c090') # red: '#f9c795'
            elif urgent and not itemDone:
                return QBrush('#f9f995') # yellow: '#f9f995'
            else:
                return col


    def rowCount(self, index):
        return len(self.filteredItems)

    def columnCount(self, index):
        return len(self.columns)

    def headerData(self, section: int, orientation: Qt.Orientation, role: int = ...):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return self.columns[section]

        if orientation == Qt.Vertical and role == Qt.DisplayRole:
            #print("get Vertical "+str(section)+": "+str(self.filteredItems[section]['ID'])+" "+self.filteredItems[section]['Title'])
            return f"{self.filteredItems[section]['ID']}"

class EditDialog(QDialog):
    item = None
    def __init__(self, item):
        super().__init__()
        self.item = item

        self.setWindowTitle("Edit Todo "+item['Title'])
        self.setMinimumSize(800,100)

        self.mainLayout = QVBoxLayout()
        self.setLayout(self.mainLayout)
        #self.setAttribute(QWA_DeleteOnClose)


        titLayout = QHBoxLayout()
        self.mainLayout.addLayout(titLayout)
        self.catSelCB = QComboBox()
        self.catSelCB.addItems(categories)
        self.catSelCB.setCurrentText(item['Category'])
        def onSelCategoryCB():
            print (self.catSelCB.currentText())
            newCatEdit.setText("")
        self.catSelCB.currentTextChanged.connect(onSelCategoryCB)
        titLayout.addWidget(self.catSelCB)
        titLayout.addWidget(QLabel("New Category:"))
        def onNewCat():
            newItem = newCatEdit.text()
            if len(newItem):
                if not newItem in categories:
                    self.catSelCB.addItem(newItem)
                self.catSelCB.setCurrentText(newItem)
                newCatEdit.setText("")
        newCatEdit = QLineEdit('', parent=self)
        titLayout.addWidget(newCatEdit)
        newCatEdit.setMaximumWidth(80)
        newCatEdit.editingFinished.connect(onNewCat)
        titLayout.addWidget(QLabel("Title"))
        self.titleEdit = QLineEdit(item['Title'], parent=self)
        titLayout.addWidget(self.titleEdit)


        descLayout = QHBoxLayout()
        descLayout.addWidget(QLabel("Description"))
        self.descriptionEdit = QLineEdit(item['Description'], parent=self)
        descLayout.addWidget(self.descriptionEdit)
        self.mainLayout.addLayout(descLayout)

        prioLayout = QHBoxLayout()
        prioLayout.addWidget(QLabel("Priority"))
        self.prioEdit = QLineEdit(item['Priority'], parent=self)
        self.prioEdit.setMaximumWidth(50)
        prioLayout.addWidget(self.prioEdit)
        self.mainLayout.addLayout(prioLayout)

        #statusLayout = QHBoxLayout()
        prioLayout.addWidget(QLabel("Status"))
        self.statusEdit = QLineEdit(item['Status'], parent=self)
        prioLayout.addWidget(self.statusEdit)
        #self.mainLayout.addLayout(statusLayout)

        dateLayout = QHBoxLayout()
        dlabel = QLabel("Date")
        dlabel.setAlignment(Qt.AlignRight)
        dateLayout.addWidget(dlabel)
        self.dateEdit = QDateEdit()
        self.dateEdit.setDisplayFormat("dd.MM.yyyy")
        self.dateEdit.setDate(qDateFromStr(item['Date']))
        dateLayout.addWidget(self.dateEdit)
        dulabel = QLabel("DueDate")
        dulabel.setAlignment(Qt.AlignRight)
        dateLayout.addWidget(dulabel)
        self.dueDateEdit = QDateEdit()
        self.dueDateEdit.setDisplayFormat("dd.MM.yyyy")
        self.dueDateEdit.setDate(qDateFromStr(item['DueDate']))
        dateLayout.addWidget(self.dueDateEdit)
        def onCDuBtn():
            self.dueDateEdit.setDate(qDateFromStr('2000-01-01'))
        clearDuDButton = QPushButton(self.tr("X"), default=False, autoDefault=False)
        clearDuDButton.setMaximumWidth(30)
        clearDuDButton.pressed.connect(onCDuBtn)
        dateLayout.addWidget(clearDuDButton)
        dolabel = QLabel("DoneDate")
        dolabel.setAlignment(Qt.AlignRight)
        dateLayout.addWidget(dolabel)
        self.doneDateEdit = QDateEdit()
        self.doneDateEdit.setDisplayFormat("dd.MM.yyyy")
        self.doneDateEdit.setDate(qDateFromStr(item['DoneDate']))
        dateLayout.addWidget(self.doneDateEdit)
        def onCDoBtn():
            self.doneDateEdit.setDate(qDateFromStr('2000-01-01'))
        clearDoDButton = QPushButton(self.tr("X"), default=False, autoDefault=False)
        clearDoDButton.setMaximumWidth(30)
        clearDoDButton.pressed.connect(onCDoBtn)
        dateLayout.addWidget(clearDoDButton)
        def onDoNowBtn():
            self.doneDateEdit.setDate(qDateFromStr(datetime.date.today().strftime("%Y-%m-%d")))
        doDNowButton = QPushButton(self.tr("NOW"), default=False, autoDefault=False)
        doDNowButton.setMaximumWidth(37)
        doDNowButton.pressed.connect(onDoNowBtn)
        dateLayout.addWidget(doDNowButton)

        self.mainLayout.addLayout(dateLayout)

        self.progTextEdit = QTextEdit()
        addProgLayout = QHBoxLayout()
        self.mainLayout.addLayout(addProgLayout)
        addProgLayout.addWidget(QLabel("Add new Progress"))
        self.addProgEdit = QLineEdit('', parent=self)
        self.addProgEdit.editingFinished.connect(self.onAddProg)
        addProgLayout.addWidget(self.addProgEdit)
        self.mainLayout.addWidget(self.progTextEdit)
        for line in item['Progress']:
            self.progTextEdit.append(line)

        doneButton = QPushButton(self.tr("&Done"), default=False, autoDefault=False)
        doneButton.setObjectName("Done")
        doneButton.setCheckable(True)
        doneButton.setStyleSheet("""* {background-color: #6f6; color: #000} *:hover { background-color: #7d7; color: #000 }""");
        doneButton.clicked.connect(self.onDoneBtn)
        delButton = QPushButton(self.tr("&Delete"), default=False, autoDefault=False)
        delButton.setCheckable(True)
        delButton.setStyleSheet("""* {background-color: #f66; color: #000} *:hover { background-color: #d77; color: #000 }""");
        delButton.clicked.connect(self.onDelBtn)
        BtnLayout1 = QHBoxLayout()
        BtnLayout1.addWidget(delButton)
        BtnLayout1.addWidget(doneButton)
        verticalSpacer = QSpacerItem(800, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)
        BtnLayout1.addItem(verticalSpacer)
        self.mainLayout.addLayout(BtnLayout1)

        okButton = QPushButton(self.tr("&OK"), default=False, autoDefault=False)
        okButton.setCheckable(True)
        okButton.setStyleSheet("""* {background-color: #afa; color: #000} *:hover { background-color: #8d8; color: #000 }""");
        okButton.clicked.connect(self.save)
        cancelButton = QPushButton(self.tr("&Cancel"), default=False, autoDefault=False)
        cancelButton.setCheckable(True)
        cancelButton.setStyleSheet("""* {background-color: #faa; color: #000} *:hover { background-color: #d88; color: #000 }""");
        cancelButton.clicked.connect(self.cancel)
        BtnLayout2 = QHBoxLayout()
        verticalSpacer = QSpacerItem(800, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)
        BtnLayout2.addItem(verticalSpacer)
        BtnLayout2.addWidget(cancelButton)
        BtnLayout2.addWidget(okButton)
        self.mainLayout.addLayout(BtnLayout2)

    def onAddProg(self):
        if len(self.addProgEdit.text()):
            newText = datetime.datetime.now().strftime("%y%m%d-%H%M%S ") + self.addProgEdit.text()
            self.progTextEdit.append(newText)
            self.addProgEdit.setText('')

    def save(self):
        print('save')
        self.onAddProg() #falls noch etwas in der Eingabezeile für Progess steht
        self.item['Title'] = self.titleEdit.text()
        cat = self.catSelCB.currentText()
        if cat =='ALL':
            cat = ''
        self.item['Category'] = cat
        self.item['Description'] = self.descriptionEdit.text()
        self.item["Priority"] =  self.prioEdit.text()
        self.item["Status"] = self.statusEdit.text()
        self.item["Date"] = qDateToDateStr(self.dateEdit.date())
        self.item["DueDate"] = qDateToDateStr(self.dueDateEdit.date())
        self.item["DoneDate"] = qDateToDateStr(self.doneDateEdit.date())

        self.item["Progress"] = []
        #text = self.progTextEdit.toPlainText().split('\n')
        #print(text)
        for line in self.progTextEdit.toPlainText().splitlines():
            self.item["Progress"].append(line)

        writeToDos()
        reloadFile()
        self.accept()

    def cancel(self):
        print('cancel')
        self.reject()


    def onDoneBtn(self):
        print('done')
        self.doneDateEdit.setDate(qDateFromStr(datetime.date.today().strftime("%Y-%m-%d")))
        self.statusEdit.setText("DONE")
        self.save()

    def onDelBtn(self):
        print('del')
        self.doneDateEdit.setDate(qDateFromStr(datetime.date.today().strftime("%Y-%m-%d")))
        self.statusEdit.setText("DELETED")
        self.save()


# Subclass QMainWindow to customize your application's main window
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        global darkScheme

        shints = QGuiApplication.styleHints()
        darkScheme = shints.colorScheme() == Qt.ColorScheme.Dark

        self.setWindowTitle("ToOdPs6")
        self.setMinimumSize(1600,700)

        pixmapi = getattr(QStyle, 'SP_ArrowForward')
        icon = self.style().standardIcon(pixmapi)
        self.setWindowIcon(icon)

        mainLayout = QVBoxLayout()
        topLayout = QHBoxLayout()

        mainWidget = QWidget()
        mainWidget.setLayout(mainLayout)
        self.setCentralWidget(mainWidget)

        topWidget = QWidget()
        topWidget.setLayout(topLayout)
        mainLayout.addWidget(topWidget)
        topWidget.setMaximumHeight(40);

        ToDoButton = QPushButton("AddToDo")
        ToDoButton.clicked.connect(self.onAddToDoButton)
        topLayout.addWidget(ToDoButton)

        self.DoneCheckBox = QCheckBox('Done')
        self.DoneCheckBox.clicked.connect(self.onDoneCB)
        self.DoneCheckBox.setMaximumWidth(60);
        topLayout.addWidget(self.DoneCheckBox)

        self.categoriesCB = QComboBox()
        self.categoriesCB.addItems(categories)
        self.categoriesCB.currentTextChanged.connect(self.onCategoriesCB)
        topLayout.addWidget(self.categoriesCB)

        label = QLabel('Nothing will work unless you do.')
        label.setMaximumHeight(30);
        label.setAlignment(Qt.AlignCenter)
        label.setStyleSheet("""
               background-color: #99FF99;
               color: #000;
               font-family: Titillium;
               font-size: 12px;
               """)
        topLayout.addWidget(label)

        ReloadButton = QPushButton("Reload")
        ReloadButton.clicked.connect(self.onReloadButton)
        topLayout.addWidget(ReloadButton)
        verticalSpacer = QSpacerItem(400, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)
        topLayout.addItem(verticalSpacer)

        self.todoTable = QTableView()
        mainLayout.addWidget(self.todoTable)
        self.model = TableModel()
        self.todoTable.setModel(self.model)
        self.todoTable.setShowGrid(False)
        self.todoTable.verticalHeader().setStyleSheet("""font-weight: 800; font-size: 11px; """)
        self.todoTable.horizontalHeader().setStyleSheet("""font-weight: 800;""")
        self.todoTable.doubleClicked.connect(self.onSelTableItem)
        self.todoTable.verticalHeader().setDefaultSectionSize(9); # Row height
        #Category
        self.todoTable.horizontalHeader().setSectionResizeMode(0, QHeaderView.Fixed)
        self.todoTable.horizontalHeader().resizeSection(0, 100)
        #Prio
        self.todoTable.horizontalHeader().setSectionResizeMode(1, QHeaderView.Fixed)
        self.todoTable.horizontalHeader().resizeSection(1, 60)
        #Status
        self.todoTable.horizontalHeader().setSectionResizeMode(2, QHeaderView.Fixed)
        self.todoTable.horizontalHeader().resizeSection(2, 80)
        #Title
        #self.todoTable.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.todoTable.horizontalHeader().setSectionResizeMode(3, QHeaderView.Fixed)
        self.todoTable.horizontalHeader().resizeSection(3, 300)
        # Description
        self.todoTable.horizontalHeader().setSectionResizeMode(4, QHeaderView.Stretch)
        #Date
        self.todoTable.horizontalHeader().setSectionResizeMode(5, QHeaderView.Fixed)
        self.todoTable.horizontalHeader().resizeSection(5, 70)
        #DueDate
        self.todoTable.horizontalHeader().setSectionResizeMode(6, QHeaderView.Fixed)
        self.todoTable.horizontalHeader().resizeSection(6, 70)
        #DoneDate
        self.todoTable.horizontalHeader().setSectionResizeMode(7, QHeaderView.Fixed)
        self.todoTable.horizontalHeader().resizeSection(7, 70)

        self.statusText = QLabel(toDoFile)
        self.statusText.setMaximumHeight(20);
        self.statusText.setStyleSheet("""
               background-color: #ddd;
               color: #000;
               font-family: Titillium;
               font-size: 11px;
               """)
        mainLayout.addWidget(self.statusText)

    def onAddToDoButton(self):
        print ('click onAddToDoButton')
        newObj = {
            'ID': getNewID(),
            'Category':'',
            'Title':'',
            'Description': '',
            'Priority': '',
            'Date': datetime.date.today().strftime("%Y-%m-%d"),
            'DueDate': '',
            'Status': "New",
            'DoneDate': '',
            'Progress': []
        }
        ItemsObject.append(newObj)
        self.EditToDo(newObj)

    def onDoneCB(self, evt):
        global showDone
        showDone = evt
        reloadFile()
        print ('click onDoneCB: '+str(evt))

    def onReloadButton(self):
        reloadFile()

    def onCategoriesCB(self, Text):
        global CatSel
        CatSel = Text
        print("Selected Category: "+CatSel)
        reloadFile()

    def reloadTable(self):
        print("window.reloadTable()")
        self.model = TableModel()
        self.todoTable.setModel(self.model)

    def onSelTableItem(self, evt):
        item = self.model.filteredItems[evt.row()]
        self.EditToDo(item)

    def EditToDo(self, item):
        print(item)
        dlg = EditDialog(item)
        dlg.exec()

def getToDoItem(ID):
    for item in ItemsObject:
        if item['ID'] == ID:
            print("getToDoItem("+str(ID)+")",item)
            return item
    return None

def getNewID():
    maxId = 0
    for i in ItemsObject:
        if i['ID'] > maxId:
            maxId = i['ID']
    return maxId+1

def writeToDos():
    global toDoFile
    print('writing ToDos to '+toDoFile)
    toDoFO = io.open(toDoFile, mode="w", encoding="utf-8")
    json.dump(ItemsObject, toDoFO, sort_keys=False, ensure_ascii=False, indent=2 )
    toDoFO.close()

def loadToDoFile():
    global ItemsObject
    global toDoFile
    global categories
    toDoFO = io.open(toDoFile, mode="r", encoding="utf-8")
    ItemsObject = json.load(toDoFO)
    toDoFO.close()
    categories = ['ALL']
    IDs = []
    FixIdsNeeded = False
    for item in ItemsObject:
        if not "DoneDate" in item:
            item["DoneDate"] = ""
        if not "Category" in item:
            item["Category"] = ""
        else:
            if item["Category"] not in categories:
                categories.append(item["Category"])
        if item['ID'] not in IDs:
            IDs.append(item['ID'])
        else:
            print("item "+item['Title'] +' has duplicate ID'+str(item['ID'])+', reset to -1 ! ')
            FixIdsNeeded = True
            item['ID'] = -1
    if FixIdsNeeded:
        #reassign IDs
        for item in ItemsObject:
            if item['ID'] == -1:
                item['ID'] = getNewID()
        writeToDos()

def reloadFile():
    print("reloadFile()")
    loadToDoFile()
    window.reloadTable()


def createNewEmptyJson():
    obj = [
        {
           'ID': 1,
           'Title':'Test1',
           'Description': 'Nur ein Test',
           'Priority': 1,
           'Date': '2024-07-01',
           'DueDate': '',
           'Status': "New",
           'Category': 'Test',
           'Progress': [],
           'DoneDate': ''
        }
    ]
    fname = "ToDo.json"
    newFile = io.open(fname, mode="w", encoding="utf-8")
    json.dump(obj, newFile, sort_keys=False, ensure_ascii=False, indent=2 )
    newFile.close()
    return fname

if __name__ == '__main__':
    global ItemsObject
    global toDoFile
    global window
    global categories

    toDoFile = "ToDo.json"

    if len(sys.argv) > 1:
        print('using File: '+sys.argv[1])
        toDoFile = sys.argv[1]
    else:
        if not exists(toDoFile):
            toDoFile = createNewEmptyJson()

    loadToDoFile()

    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    app.exec()

