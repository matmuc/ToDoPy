
import json
import datetime
import sys, io
from os.path import exists

import tkinter
from tkinter import *
from tkinter import ttk
from tkinter.font import Font, nametofont
from tkcalendar import DateEntry


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
    json.dump(obj, newFile, sort_keys=False, indent=2 )
    newFile.close()
    return fname

class Window(Tk):
    def __init__(self):
        super().__init__()

        self.title("myToDos")
        self.minsize(600,400)
        self.geometry('1600x600')
        self['bg'] = '#AC99F2'

        #default_font = nametofont("TkDefaultFont")
        #default_font = nametofont("TkFixedFont")
        default_font = Font(family='Verdana')
        default_font.configure(size=10) #9 is default
        self.option_add("*Font", default_font)

        self.topFrame = Frame(self, width=850, height=60)
        self.topFrame.pack(expand=False, fill='x')

        self.text = Label(self.topFrame, text="Nothing will work unless you do.")
        self.text['bg'] = '#99FF99'
        self.text.grid(row=1, column=4)
        #self.text.pack()

        self.NewToDoButton = Button(self.topFrame, text="NewToDo", command= self.handle_NewToDoButton_press)
        #self.NewToDoButton.bind("", self.handle_NewToDoButton_press)
        self.NewToDoButton.grid(row=1, column=1)
        #self.NewToDoButton.pack()

        self.showDone = IntVar()
        self.showDone.set(0)
        self.DoneCB = Checkbutton(self.topFrame, text='DONE', variable=self.showDone, onvalue=1, offvalue=0, command=self.onDoneCB)
        self.DoneCB.grid(row=1, column=2)

        self.reloadFileButton = Button(self.topFrame, text="reload", command=reloadFile)
        self.reloadFileButton.grid(row=1, column=5)

        self.catSel = StringVar()
        self.categoriesCB = ttk.Combobox(self.topFrame, textvariable=self.catSel)
        self.categoriesCB.grid(row=1, column=3)
        self.categoriesCB['values'] = categories
        self.categoriesCB.set('ALL')
        self.categoriesCB.bind("<<ComboboxSelected>>", self.OnCatCbSel)

        self.tableFrame = Frame(self, width=850, height=500)
        self.tableFrame.pack(expand=True, fill='both')
        #self.tableFrame.grid(row=3, column=1, columnspan=9, sticky="nsew")

        self.scroll = Scrollbar(self.tableFrame)
        self.scroll.pack(side=RIGHT, fill=Y)
        self.scroll = Scrollbar(self.tableFrame, orient='horizontal')
        self.scroll.pack(side=BOTTOM, fill=X)

        self.todoTable = tkinter.ttk.Treeview(self.tableFrame)
        #self.todoTable.place(relx=0.01, rely=0.1, width=850, height=500)

        self.scroll.config(command=self.todoTable.yview)
        self.scroll.config(command=self.todoTable.xview)

        self.todoTable['columns'] = ('ID', 'Category', 'Title', 'Description', 'Priority', 'Date', 'DueDate', 'Status', 'Done')

        self.todoTable.column("#0", width=0, stretch=NO)
        self.todoTable.column("ID", anchor=CENTER, width=15)
        self.todoTable.column("Category", anchor=CENTER, width=50)
        self.todoTable.column("Title", anchor=CENTER, width=250)
        self.todoTable.column("Description", anchor=CENTER, width=500)
        self.todoTable.column("Priority", anchor=CENTER, width=15)
        self.todoTable.column("Date", anchor=CENTER, width=60)
        self.todoTable.column("DueDate", anchor=CENTER, width=60)
        self.todoTable.column("Status", anchor=CENTER, width=60)
        self.todoTable.column("Done", anchor=CENTER, width=60)

        self.todoTable.heading("#0", text="", anchor=CENTER)
        self.todoTable.heading("ID", text="ID", anchor=CENTER)
        self.todoTable.heading("Category", text="Category", anchor=CENTER)
        self.todoTable.heading("Title", text="Title", anchor=CENTER)
        self.todoTable.heading("Description", text="Description", anchor=CENTER)
        self.todoTable.heading("Priority", text="Priority", anchor=CENTER)
        self.todoTable.heading("Date", text="Date", anchor=CENTER)
        self.todoTable.heading("DueDate", text="DueDate", anchor=CENTER)
        self.todoTable.heading("Status", text="Status", anchor=CENTER)
        self.todoTable.heading("Done", text="Done", anchor=CENTER)

        self.todoTable.tag_configure('urgent', background='#f9f995')
        self.todoTable.tag_configure('overdue', background='#f9c795')

        #self.todoTable.pack()
        self.todoTable.pack(expand=True, fill='both')
        self.showItems()

        self.todoTable.bind("<Double-1>", self.OnDoubleClick)

        self.statusText = Label(self, text=toDoFile, height=1)
        self.statusText['bg'] = '#CCC'
        self.statusText.pack(expand=False, fill='x')

    def OnDoubleClick(self,event):
        #row = self.todoTable.selection()[0]
        #print("you clicked on row", row)
        item = self.todoTable.identify('item',event.x,event.y)
        #print(self.todoTable.item(item))
        rowItem = self.todoTable.item(item)
        #print("you clicked on", self.todoTable.item(item, "text"))
        #print(rowItem["values"][0])
        print("you clicked on", rowItem["text"])
        EditToDo(self, getToDoItem(rowItem["values"][0]))

    def OnCatCbSel(self,event):
        self.catSel.set(self.categoriesCB.get())
        print("Filter: "+self.catSel.get())
        self.reload()

    def handle_NewToDoButton_press(self):
        print("New")
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
        mbox = EditToDo(self, newObj)

    def showItems(self):
        global ItemsObject
        print("Filter: " + self.catSel.get())
        for item in ItemsObject:
            if item['Status'].lower() == "deleted":
                itemDeleted = True
            else:
                itemDeleted = False
            if item['Status'].lower() == "done" or item['Status'].lower() == "obsolet":
                itemDone = True
            else:
                itemDone = False

            if (self.showDone.get() == 1 and itemDone) or (self.showDone.get() == 0 and not itemDone) and not itemDeleted:
                tag = ''
                try:
                    itemdate = datetime.datetime.strptime(item['DueDate'], '%Y-%m-%d').date()
                    today = datetime.date.today()
                    deltaDays = (today - itemdate).days
                    if  deltaDays > 0 and not itemDone:
                        tag = 'overdue'
                    elif  deltaDays > -7 and not itemDone:
                        tag = 'urgent'
                except:
                    None
                if self.catSel.get() =='ALL' or self.catSel.get() == item['Category']: # or len(self.catSel.get())<2
                    self.todoTable.insert(parent='', index='end', iid=str(item['ID'])   , text='ID'+str(item['ID']), tags=(tag,),
                                values=(item['ID'],item['Category'], item['Title'], item['Description'], item['Priority'], item['Date'], item['DueDate'], item['Status'], item['DoneDate']))

    def onDoneCB(self):
        print("onDoneCB: ", self.showDone.get())
        self.reload()

    def reload(self):
        x = self.todoTable.get_children()
        for item in x:  ## Changing all children from root item
            self.todoTable.delete(item)
        self.showItems()
        self.categoriesCB['values'] = categories

class EditToDo(object):
    root = None
    ToDoObj = None
    frame = None

    def __init__(self, root, ToDoObj):
        global categories
        self.root = root
        self.top = Toplevel(root)
        self.top.wm_title = "Edit ToDo"
        self.ToDoObj = ToDoObj

        frm = Frame(self.top, borderwidth=4, relief='ridge')
        frm.pack(fill='both', expand=True)
        self.frame = frm


        hlabel = Label(frm, text="Edit \""+ToDoObj['Title']+"\"")
        hlabel.grid(row=0, column=1, columnspan=5, sticky="w")

        self.teTitle = StringVar()
        self.teTitle.set(ToDoObj["Title"])
        Label(frm, text="Title").grid(row=2, column=1, sticky="e")
        Entry(frm, width=50, textvariable=self.teTitle).grid(row=2, column=2, padx=5, sticky="w")

        self.teCategory = StringVar()
        self.teCategory.set(ToDoObj["Category"])
        Label(frm, text="Category").grid(row=3, column=1, sticky="e")
        frmCat = Frame(frm, width=200, height=25)
        frmCat.grid(row=3, column=2, padx=5, sticky="w")
        Entry(frmCat, width=30, textvariable=self.teCategory).grid(row=1, column=2, padx=5, sticky="w")
        def OnDCatCbSel(event):
            self.teCategory.set(self.categoriesCB.get())
        self.catSel = StringVar()
        self.categoriesCB = ttk.Combobox(frmCat, textvariable=self.catSel)
        self.categoriesCB.grid(row=1, column=1, sticky="w", padx=5)
        self.categoriesCB['values'] = categories
        self.categoriesCB.set(self.teCategory.get())
        self.categoriesCB.bind("<<ComboboxSelected>>", OnDCatCbSel)

        self.teDescription = StringVar()
        self.teDescription.set(ToDoObj["Description"])
        Label(frm, text="Description").grid(row=4, column=1, sticky="e")
        Entry(frm, width=90, textvariable=self.teDescription).grid(row=4, column=2, padx=5, sticky="w")

        self.tePriority = StringVar()
        self.tePriority.set(ToDoObj["Priority"])
        Label(frm, text="Priority").grid(row=5, column=1, sticky="e")
        Entry(frm, width=10, textvariable=self.tePriority).grid(row=5, column=2, padx=5, sticky="w")

        #Date (CreationDate)
        self.teDate = StringVar()
        self.teDate.set(datetime.date.today().strftime("%Y-%m-%d"))
        self.teDate.set(ToDoObj["Date"])
        Label(frm, text="Date").grid(row=6, column=1, sticky="e")
        frmD = Frame(frm, background='#aaa', width=80, height=25)
        frmD.grid(row=6, column=2, padx=5, sticky="w")
        def selD(e):
            self.teDate.set(calD.get_date())
        calD = DateEntry(frmD, date_pattern="yyyy-mm-dd")
        calD.bind("<<DateEntrySelected>>", selD)
        if len((self.teDate.get())) > 1:
            calD.set_date(self.teDate.get())
        calD.pack(padx=1, pady=1)

        #Due-Date
        self.teDueDate = StringVar()
        self.teDueDate.set(ToDoObj["DueDate"])
        Label(frm, text="DueDate").grid(row=7, column=1, sticky="e")
        frmDD = Frame(frm, background='#aaa', width=80, height=25)
        frmDD.grid(row=7, column=2, padx=5, sticky="w")
        def selDD(e):
            self.teDueDate.set(calDD.get_date())
        calDD = DateEntry(frmDD, date_pattern="yyyy-mm-dd")
        calDD.bind("<<DateEntrySelected>>", selDD)
        if len((self.teDueDate.get())) > 1:
            calDD.set_date(self.teDueDate.get())
        calDD.pack(padx=1, pady=1)


        self.teStatus = StringVar()
        if ToDoObj is not None:
            self.teStatus.set(ToDoObj["Status"])
        Label(frm, text="Status").grid(row=8, column=1, sticky="e")
        Entry(frm, width=40, textvariable=self.teStatus).grid(row=8, column=2, padx=5, sticky="w")

        self.teDoneDate = StringVar()
        self.teDoneDate.set(ToDoObj["DoneDate"])
        Label(frm, text="DoneDate").grid(row=9, column=1, sticky="e")
        frmDoneD = Frame(frm, background='#aaa', width=80, height=25)
        frmDoneD.grid(row=9, column=2, padx=5, sticky="w")
        def selDoneD(e):
            self.teDoneDate.set(calDoneD.get_date())
        calDoneD = DateEntry(frmDoneD, date_pattern="yyyy-mm-dd")
        calDoneD.bind("<<DateEntrySelected>>", selDoneD)
        if len((self.teDoneDate.get())) > 1:
            calDoneD.set_date(self.teDoneDate.get())
        calDoneD.pack(padx=1, pady=1)


        Label(frm, text="Progress").grid(row=11, column=1, sticky="e")
        self.ProgText = Text(frm, width=80, height=8)
        for elem in ToDoObj["Progress"]:
            self.ProgText.insert(self.ProgText.index('end'), elem+'\n')
        self.ProgText.grid(row=11, column=2, columnspan=4, padx=5, sticky="w")
        self.teProgress = StringVar()
        self.progEntry = Entry(frm, width=80, textvariable=self.teProgress)
        Button(frm, text="+", padx=15, bg="#BFB", command=lambda: self.AddProgress(ToDoObj)).grid(row=12, column=1)
        self.progEntry.grid(row=12, column=2, padx=5, sticky="w", columnspan=2)

        frmBtn1 = Frame(frm, background='#aaa', width=80, height=25)
        frmBtn1.grid(row=14, column=2, padx=5)
        b_ok = Button(frmBtn1, text='OK', padx=35, bg="#05CC05", command= lambda: self.save(ToDoObj))
        b_ok.grid(row=1, column=2)
        b_cancel = Button(frmBtn1, text='Cancel', bg="#D11", command= self.top.destroy)
        b_cancel.grid(row=1, column=1)

        b_done = Button(frm, text='DONE', bg="#99f", command= lambda: self.done(ToDoObj))
        b_done.grid(row=14, column=4)
        b_delete = Button(frm, text='delete', bg="#FF3333", command= lambda: self.delete(ToDoObj))
        b_delete.grid(row=14, column=1)

    def done(self, obj):
        obj["DoneDate"] = datetime.date.today().strftime("%Y-%m-%d")
        obj["Status"] = "DONE"
        writeToDos()
        self.top.destroy()
        window.reload()

    def delete(self, obj):
        obj["DoneDate"] = datetime.date.today().strftime("%Y-%m-%d")
        obj["Status"] = "DELETED"
        writeToDos()
        self.top.destroy()
        window.reload()

    def save(self,ToDoObj):
        print("save existing ToDo "+str(ToDoObj['ID']))
        ToDoObj["Title"] = self.teTitle.get()
        ToDoObj["Category"] = self.teCategory.get()
        if self.teCategory.get() not in categories:
            categories.append(self.teCategory.get())
            window.reload()
        ToDoObj["Description"] = self.teDescription.get()
        ToDoObj["Priority"] = self.tePriority.get()
        ToDoObj["Date"] = self.teDate.get()
        ToDoObj["DueDate"] = self.teDueDate.get()
        ToDoObj["Status"] = self.teStatus.get()
        ToDoObj["DoneDate"] = self.teDoneDate.get()

        self.AddProgress(ToDoObj) # Falls noch was im Eingabefeld steht!

        ToDoObj["Progress"] = []
        for line in self.ProgText.get('1.0', 'end-1c').splitlines():
            ToDoObj["Progress"].append(line)

        writeToDos()
        self.top.destroy()
        window.reload()

    def AddProgress(self,ToDoObj):
        if len(self.teProgress.get()) < 2:
            return
        newText = datetime.datetime.now().strftime("%y%m%d-%H%M%S ")+self.teProgress.get()
        if 'Progress' not in ToDoObj:
            ToDoObj['Progress'] = []
        ToDoObj['Progress'].append(newText)
        self.teProgress.set('')
        self.ProgText.insert(self.ProgText.index('end'), newText+'\n')


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
    loadToDoFile()
    window.reload()

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

    # Start the event loop.
    window = Window()
    window.mainloop()


