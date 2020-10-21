from PyQt5 import QtWidgets, uic
from PyQt5.QtWidgets import *
import os, sys
import pickle
import hashlib
import win32con
import win32api

# SYSTEM ---

path_program = os.path.dirname(os.path.abspath(sys.argv[0]))   # find out the current program address

app = QtWidgets.QApplication([])
dlg = uic.loadUi("FileSorted_1.3_des.ui")

# open/create "data.pickle" with dic_name and dic_tag (library)
file = open(path_program + '\lib' + '\data.pickle', 'rb')
try:
    dic_name = pickle.load(file)
    dic_tag = pickle.load(file)
except EOFError:
    dic_name = {}
    dic_tag = {}

print("test")

# objects for 1 directory
local_dir = ''  # dir with icon
file_location = ''  # location of sel dir
dic_name_in_dir = {}  # hash_name = tag, in 1 dir
dic_tag_in_dir = {}  # tag = hash_name, in 1 dir
dic_orig_name = {}  # original name file = hash_name (dic_name)
list_tag = []  # list with tags in dir
list_sel_tag = []  # list with selected tags in listWidget
sel_files_names = []  # list with full path for selected files
sel_name_hash = []  # list with hash_name for selected files
but_clicked = 0

# FUNCTIONS  ---
def cl_but_mes(i):
    global but_clicked
    if i.text() == "Cancel":
       but_clicked = 0
    else:
        but_clicked = 1

def messag_box(title, text, option):
    # QMessageBox.information(None, title, text)
    mes_box = QMessageBox()
    mes_box.setWindowTitle(title)
    mes_box.setText(text)

    if option == 1:
        mes_box.setIcon(QMessageBox.Information)

    elif option == 2:
        mes_box.setIcon(QMessageBox.Question)
        mes_box.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
        mes_box.setDefaultButton(QMessageBox.Cancel)
        mes_box.buttonClicked.connect(cl_but_mes)

    x = mes_box.exec_()

def find_list_sel_tag():
    # find selected tag in listWidgets
    global list_sel_tag
    items = dlg.listWidget.selectedItems()
    x = []
    for i in range(len(items)):
        x.append(str(dlg.listWidget.selectedItems()[i].text()))
    list_sel_tag = x

def find_name_in_tag():
    # find h_name file for selected tag
    list_name_with_sel_tag = []
    for x in list_sel_tag:
        if x in dic_tag_in_dir:
            for y in dic_tag_in_dir[x]:
                if y not in list_name_with_sel_tag:
                    list_name_with_sel_tag.append(y)
    return list_name_with_sel_tag

def hide_or_show_file(file_name, operation):
    if operation == "hide":
        win32api.SetFileAttributes(file_name, win32con.FILE_ATTRIBUTE_HIDDEN)  # hide file
    else:
        win32api.SetFileAttributes(file_name, win32con.FILE_ATTRIBUTE_NORMAL)  # show file

def hide_all():
    for x in dic_orig_name:
        file_full_loc = file_location + "/" + dic_orig_name[x]
        hide_or_show_file(file_full_loc, "hide")

def show_all():
    for x in dic_orig_name:
        file_full_loc = file_location + "/" + dic_orig_name[x]
        hide_or_show_file(file_full_loc, "show")

def hide_sel():
    show_all()
    find_list_sel_tag()
    list_with_name_sel_tags = []  # list with full_name with sel Tags
    for x in dic_tag_in_dir:
        if x in list_sel_tag:
            for y in dic_tag_in_dir[x]:
                if y not in list_with_name_sel_tags:
                    list_with_name_sel_tags.append(dic_orig_name[y])
    for x in list_with_name_sel_tags:
        file_full_loc = file_location + "/" + x
        hide_or_show_file(file_full_loc, "hide")

def show_sel():
    show_all()
    find_list_sel_tag()
    list_with_name_sel_tags = []  # list with hash_name with sel Tags
    list_with_name_not_sel_tags = []  # list with full_name with not sel Tags
    for x in dic_tag_in_dir:
        if x in list_sel_tag:
            for y in dic_tag_in_dir[x]:
                if y not in list_with_name_sel_tags:
                    list_with_name_sel_tags.append(y)

    for x in dic_orig_name:
        if x not in list_with_name_sel_tags:
            list_with_name_not_sel_tags.append(dic_orig_name[x])
    for x in list_with_name_not_sel_tags:
        file_full_loc = file_location + "/" + x
        hide_or_show_file(file_full_loc, "hide")

def hash_file(filename):
    # takes full path for file and return hash_name
    h = hashlib.sha1()
    with open(filename, 'rb') as file:
        chunk = 0
        while chunk != b'':
            chunk = file.read(1024)
            h.update(chunk)
        return h.hexdigest()

def add_in_list(item):
    if item not in list_tag:
        dlg.listWidget.addItem(item)
        list_tag.append(item)
        dic_tag_in_dir[item]=[]

def create_tag():
    if dlg.lineEdit.text() != "":
        add_in_list(dlg.lineEdit.text())
        dlg.lineEdit.setText("")


def sel_dir():

    messag_box("sel_dir", "Select directory with files", 1)
    global dic_name_in_dir, dic_name, dic_tag, dic_orig_name, dic_tag_in_dir, file_location

    # add Files name in dic_name_in_dir
    file_location = QFileDialog.getExistingDirectory()
    if file_location == "":
        pass
    else:
        dlg.LineEd_directory.setText(file_location)  # add file_location in UI

        for x in os.listdir(file_location):

            file_full_loc = file_location + "\\" + x
            if os.path.isdir(file_full_loc):  # checking file or directory
                pass
            else:
                x1 = hash_file(file_full_loc)  # create hash_name for files
                dic_orig_name[x1] = x
                if x1 not in dic_name_in_dir:
                    dic_name_in_dir[x1] = []
        # add tag for Name (if they in Library)
        for x in dic_name_in_dir:
            if x in dic_name:
                dic_name_in_dir[x] = dic_name[x]
                # add tag for dic_tag_in_dir
                if len(dic_name_in_dir[x]):
                    for y in dic_name_in_dir[x]:
                        if y not in dic_tag_in_dir:
                            add_in_list(y)
                            dic_tag_in_dir[y] = [x]
                            add_in_list(y)
                        elif y in dic_tag_in_dir:
                            if x not in dic_tag_in_dir[y]:
                                dic_tag_in_dir[y].append(x)

def sel_files():
    global sel_files_names, sel_name_hash
    files_names = QFileDialog.getOpenFileNames(dlg, "select files", file_location)
    first_list = files_names[0]
    for x in first_list:
        sel_files_names.append(x)
    # find hash_name for sel files
    for x in sel_files_names:
        y = hash_file(x)
        sel_name_hash.append(y)

def add_tag_in_files():
    global list_sel_tag, sel_name_hash, dic_name_in_dir, dic_tag_in_dir

    find_list_sel_tag()  # find sel tags

    sel_files()  # sel/choose Files on dir

    # add Key for Name in dic_name_in_dir
    for x in sel_name_hash:
        for y in list_sel_tag:
            if y not in dic_name_in_dir[x]:
                dic_name_in_dir[x].append(y)

    # add  Name  for tag in dic_key_in_dir
    for x in list_sel_tag:
         for y in sel_name_hash:
            if y not in dic_tag_in_dir[x]:
                dic_tag_in_dir[x].append(y)

def save():

    # update dic_tag and dic_name
    for x in dic_tag_in_dir:
        dic_tag[x] = dic_tag_in_dir[x]
    for x in dic_name_in_dir:
        dic_name[x] = dic_name_in_dir[x]

    # save lib with new files name and tags
    file = open(path_program + '\lib' + '\data.pickle', 'wb')
    pickle.dump(dic_name, file)
    pickle.dump(dic_tag, file)
    file.close()

def del_tag_in_f(dic):  # dic - dic with files where you need to remove tags
    list_names_with_tegs = []

    # find sel tags
    find_list_sel_tag()

    # del sel tags from dic_name_in_dir
    for x in dic:
        for y in list_sel_tag:
            if y in dic_name_in_dir[x]:
                dic_name_in_dir[x].remove(y)
                list_names_with_tegs.append(x)

    # del sel tags from dic_tag_in_dir
    for x in dic_tag_in_dir:
        for y in list_names_with_tegs:
            if y in dic_tag_in_dir[x]:
                dic_tag_in_dir[x].remove(y)

def del_sel_tags_in_sel_files(): # del sel tags in sel Files
    sel_files()
    del_tag_in_f(sel_name_hash)

def del_sel_tags_in_dir(): # del sel tags in all files in dir and listWidgets
    messag_box("Delete Tags", "Delete selected Tags in all files in Directory?", 2)
    if but_clicked == 0:
        pass
    elif but_clicked == 1:
        del_tag_in_f(dic_name_in_dir)

        # find sel tags
        find_list_sel_tag()

        for item in list_sel_tag:
            if item in list_tag:
                dlg.listWidget.takeItem(dlg.listWidget.currentRow())
                list_tag.remove(item)
                if len(dic_tag_in_dir[item]) == 0:
                    del dic_tag_in_dir[item]


# BUTTONS  ---

dlg.but_sel_dir.clicked.connect(sel_dir)
dlg.but_create_tag.clicked.connect(create_tag)
dlg.but_ShowAll.clicked.connect(show_all)
dlg.but_HideAll.clicked.connect(hide_all)
dlg.but_add_teg_files.clicked.connect(add_tag_in_files)
dlg.but_save.clicked.connect(save)
dlg.but_HideSel.clicked.connect(hide_sel)
dlg.but_ShowSel.clicked.connect(show_sel)
dlg.but_del_sel_Tags_sel_files.clicked.connect(del_sel_tags_in_sel_files)
dlg.but_del_sel_Tags.clicked.connect(del_sel_tags_in_dir)

# SYSTEM ---

dlg.show()
app.exec()
