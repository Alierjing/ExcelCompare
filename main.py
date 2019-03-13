# -*- coding: UTF-8 -*-

import sys
import getopt
import json

from functools import partial

import tkinter as tk
from tkinter import filedialog
from tkinter import ttk
from tkinter.ttk import *

from differ import ExcelDiffer, ExcelHelper

import tktable


class ScrollDummy(object):
    def __init__(self, table):
        self.table = table

    def xview(self, *args):
        if args[0] == 'scroll':
            self.table.xview_scroll(*args[1:])
        if args[0] == 'moveto':
            self.table.xview_moveto(*args[1:])

    def yview(self, *args):
        if args[0] == 'scroll':
            self.table.yview_scroll(*args[1:])
        if args[0] == 'moveto':
            self.table.yview_moveto(*args[1:])


class MyApp(tk.Tk):
    def __init__(self, srcPath=None, dstPath=None):
        super().__init__()

        self.srcPath = srcPath
        self.dstPath = dstPath
        self.diffResults = {}
        self.lastSelectCells = None

        self.InitFrame()

        self.InitTableTitleFlame(srcPath, dstPath)

        self.InitTableFlame(srcPath, dstPath)

        self.InitButtonFlame()

        self.InitTabFlame()

    def InitFrame(self):
        self.title("Excel Compare")

        w, h = self.maxsize()
        self.geometry("{}x{}".format(w, h))

        #self.columnconfigure(0, weight=1)
        #self.rowconfigure(0, weight=1)


    def InitTableTitleFlame(self, srcPath, dstPath):
        if srcPath is None:
            srcPath = ""
        if dstPath is None:
            dstPath = ""

        tableTitleFrame = Frame(self)

        srcPathLabel = Label(tableTitleFrame, text=srcPath)
        srcPathLabel.grid(row=0, column=0)

        dstPathLabel = Label(tableTitleFrame, text=dstPath)
        dstPathLabel.grid(row=0, column=1)

        tableTitleFrame.columnconfigure(0, weight=1)

        tableTitleFrame.columnconfigure(1, weight=1)

        tableTitleFrame.grid(sticky=tk.W + tk.E + tk.N + tk.S, row=0, column=0)

    def InitTableFlame(self, srcPath, dstPath):
        if not srcPath or not dstPath:
            tableFrame = Frame(self)
            tableFrame.grid(sticky=tk.W + tk.E + tk.N + tk.S, row=1, column=0)
            return

        srcExcel = ExcelHelper.OpenExcel(srcPath)

        dstExcel = ExcelHelper.OpenExcel(dstPath)

        tableFrame = Frame(self)

        maxRows = srcExcel.GetMaxRow() if srcExcel.GetMaxRow(
        ) >= dstExcel.GetMaxRow() else dstExcel.GetMaxRow()
        maxCols = srcExcel.GetMaxColumn() if srcExcel.GetMaxColumn(
        ) >= dstExcel.GetMaxColumn() else dstExcel.GetMaxColumn()

        maxRows += 1
        maxCols += 1

        self.maxRows = maxRows
        self.maxCols = maxCols

        self.table1, self.var1 = self.setTable(
            tableFrame, gridRow=0, gridColumn=0, rows=maxRows, cols=maxCols, excel=srcExcel)

        self.table2, self.var2 = self.setTable(
            tableFrame, gridRow=0, gridColumn=1, rows=maxRows, cols=maxCols, excel=dstExcel)

        tableFrame.grid(sticky="nsew", row=1, column=0)

        diffResults = ExcelDiffer.Diff2(srcExcel, dstExcel)

        self.SetDiffColor(diffResults)

        self.diffResults = diffResults

    def InitButtonFlame(self):
        buttonFrame = Frame(self)

        uploadFile1Button = tk.Button(
            buttonFrame,
            text="选择原文件",
            width=15,
            height=2,
            relief='groove',
            font=("13"),
            bg='DeepSkyBlue', fg='white',
            command=partial(self.UploadFile, "srcFile"))
        uploadFile1Button.grid(row=0, column=0,padx=5,pady=10)
        uploadFile1Button = tk.Button(
            buttonFrame,
            text="选择目标文件",
            width=15,
            height=2,
            relief='groove',
            font=("13"),
            bg='DeepSkyBlue', fg='white',
            command=partial(self.UploadFile, "dstFile"))
        uploadFile1Button.grid(row=0, column=2,padx=5,pady=10)

        buttonFrame.grid(sticky=tk.W + tk.E + tk.N + tk.S, row=2, column=0)

    def UploadFile(self, whitchFile):
        fileName = filedialog.askopenfilename()
        if whitchFile == "srcFile":
            self.srcPath = fileName
        if whitchFile == "dstFile":
            self.dstPath = fileName
        self.InitTableTitleFlame(self.srcPath, self.dstPath)
        self.InitTableFlame(self.srcPath, self.dstPath)
        self.InitTabFlame()

    def setTable(self, tableFrame, gridRow, gridColumn, rows, cols, excel):
        tb = tktable.Table(
            tableFrame,
            selectmode="browse",
            state='disabled',
            width=8,
            height=16,
            font=(8),
            exportselection=0,
            titlerows=1,
            titlecols=1,
            rows=rows+1,
            cols=cols+1,
            colwidth=9)

        #### LIST OF LISTS DEFINING THE ROWS AND VALUES IN THOSE ROWS ####
        #### SETS THE DOGS INTO THE TABLE ####
        #DEFINING THE VAR TO USE AS DATA IN TABLE
        var = tktable.ArrayVar(tableFrame)

        row_count = 0
        col_count = 1
        #SETTING COLUMNS
        for col in range(0, cols):
            index = "%i,%i" % (row_count, col_count)
            var[index] = ExcelDiffer.GetColumnLeter(col)
            col_count += 1

        #SETTING ROWS
        row_count = 1
        col_count = 0
        for row in range(0, rows):
            index = "%i,%i" % (row_count, col_count)
            var[index] = row + 1
            row_count += 1

        #SETTING DATA IN ROWS
        row_count = 1
        col_count = 1
        for row in excel.data:
            for item in row:
                index = "%i,%i" % (row_count, col_count)
                ## PLACING THE VALUE IN THE INDEX CELL POSITION ##
                if item is None:
                    var[index] = ""
                else:
                    var[index] = item
                col_count += 1
            col_count = 1
            row_count += 1
        #### ABOVE CODE SETS THE DOG INTO THE TABLE ####
        ################################################
        #### VARIABLE PARAMETER SET BELOW ON THE 'TB' USES THE DATA DEFINED ABOVE ####
        tb['variable'] = var
        tb.tag_configure(
            'title',
            relief='raised',
            anchor='center',
            background='#D3D3D3',
            fg='BLACK',
            state='disabled')

        tb.width(**{"0": 5})

        xScrollbar = Scrollbar(tableFrame, orient='horizontal')
        xScrollbar.grid(row=gridRow + 1, column=gridColumn, sticky="ew")
        xScrollbar.config(command=tb.xview_scroll)
        tb.config(xscrollcommand=xScrollbar.set)

        yScrollbar = Scrollbar(tableFrame)
        yScrollbar.grid(row=gridRow, column=gridColumn * 2 + 1, sticky="ns")
        yScrollbar.config(command=ScrollDummy(tb).yview)
        tb.config(yscrollcommand=yScrollbar.set)

        tb.grid(sticky="nsew", row=gridRow, column=gridColumn)

        return tb, var

    def _SetCommonHeader(self, tabControl, title, tabText, headers):
        tab = ttk.Frame(tabControl)

        tabControl.add(tab, text=title,pad=5)

        monty = tk.LabelFrame(tab, text=tabText,font=(8))
        monty.grid(sticky=tk.W + tk.E + tk.N + tk.S, column=0, row=0,padx=5,pady=5)

        row, col = 1, 0
        for header in headers:
            l = Label(tab, text=header,font=('',15,'bold'))
            l.grid(sticky=tk.W + tk.E + tk.N + tk.S, row=row, column=col,padx=10,pady=5)
            col += 1

        return tab

    def _SetRowTab(self, tabControl, title, tabText, headers, data=None):

        tabFrame = self._SetCommonHeader(tabControl, title, tabText, headers)

        if not data:
            return

        row = 2
        for _data in data["new"]:
            l = Label(tabFrame, text="新增",font=(8))
            l.grid(sticky=tk.W + tk.E + tk.N + tk.S, row=row, column=0,pady=5)

            first = "%i,%i" % (_data, 0)
            last = "%i,%i" % (_data, 10)
            l = tk.Button(
                tabFrame,
                text=_data,
                bg='white',
                relief='groove',
                command=partial(self.SelectCells, first, last))

            l.grid(sticky=tk.W + tk.E + tk.N + tk.S, row=row, column=1,pady=5)
            row += 1

        for _data in data["del"]:
            l = Label(tabFrame, text="删除",font=(8))
            l.grid(sticky=tk.W + tk.E + tk.N + tk.S, row=row, column=0,pady=5)

            first = "%i,%i" % (_data, 0)
            last = "%i,%i" % (_data, 10)
            l = tk.Button(
                tabFrame,
                text=_data,
                bg='white',
                relief='groove',
                width=8,
                command=partial(self.SelectCells, first, last))
            l.grid(sticky=tk.W + tk.E + tk.N + tk.S, row=row, column=1,pady=5)
            row += 1

    def _SetColumnTab(self, frame, title, tabText, headers, data=None):

        tabFrame = self._SetCommonHeader(frame, title, tabText, headers)

        if not data:
            return

        row = 2
        for _data in data["new"]:
            l = Label(tabFrame, text="新增",font=(8))
            l.grid(sticky=tk.W + tk.E + tk.N + tk.S, row=row, column=0,pady=5)

            first = "%i,%i" % (0, ExcelHelper.ColumnIndexFromStr(_data))
            last = "%i,%i" % (10, ExcelHelper.ColumnIndexFromStr(_data))
            l = tk.Button(
                tabFrame,
                text=_data,
                bg='white',
                relief='groove',
                width=8,
                command=partial(self.SelectCells, first, last))

            l.grid(sticky=tk.W + tk.E + tk.N + tk.S, row=row, column=1,pady=5)
            row += 1
        for _data in data["del"]:
            l = Label(tabFrame, text="删除",font=(8))
            l.grid(sticky=tk.W + tk.E + tk.N + tk.S, row=row, column=0,pady=5)

            first = "%i,%i" % (0, ExcelHelper.ColumnIndexFromStr(_data))
            last = "%i,%i" % (10, ExcelHelper.ColumnIndexFromStr(_data))
            l = tk.Button(
                tabFrame,
                text=_data,
                bg='white',
                relief='groove',
                command=partial(self.SelectCells, first, last))

            l.grid(sticky=tk.W + tk.E + tk.N + tk.S, row=row, column=1,pady=5)
            row += 1

    def _SetCellTab(self, tabControl, title, tabText, headers, data=None):

        tabFrame = self._SetCommonHeader(tabControl, title, tabText, headers)

        if not data:
            return

        row = 2
        for key, _data in list(data.items()):
            coordinate = ExcelHelper.CoordinateFromStr(key)
            first = "%i,%i" % (coordinate[1],
                               ExcelHelper.ColumnIndexFromStr(coordinate[0]))

            l = tk.Button(
                tabFrame, text=key, bg='white',
                relief='groove',width=8,command=partial(self.SelectCells, first))

            l.grid(sticky=tk.W + tk.E + tk.N + tk.S, row=row, column=0)
            l = Label(tabFrame, text=_data[0],font=(8))
            l.grid(sticky=tk.W + tk.E + tk.N + tk.S, row=row, column=1,padx=8)
            l = Label(tabFrame, text=_data[1],font=(8))
            l.grid(sticky=tk.W + tk.E + tk.N + tk.S, row=row, column=2,padx=8)
            row += 1

    def InitTabFlame(self):
        tabControl = ttk.Notebook(self)

        self._SetRowTab(tabControl, "行增删", "共计新增1行, 删除1行", ["改动", "行号"],
                        self.diffResults.get("rows"))
        self._SetColumnTab(tabControl, "列增删", "共计新增1列, 删除1列", ["改动", "列号"],
                           self.diffResults.get("columns"))
        self._SetCellTab(tabControl, "单元格改动", "共计2个单元格", ["坐标", "旧值", "新值"],
                         self.diffResults.get("cells"))

        tabControl.grid(sticky=tk.W + tk.E + tk.N + tk.S, row=3, column=0)

    def SetDiffColor(self, diffResults):
        for row in diffResults["rows"]["new"]:
            for col in range(0, self.maxCols+1):
                index = "%i,%i" % (row, col)
                self.table1.tag_cell("new", index)
                self.table2.tag_cell("new", index)

        for row in diffResults["rows"]["del"]:
            for col in range(0, self.maxCols+1):
                index = "%i,%i" % (row, col)
                self.table1.tag_cell("del", index)
                self.table2.tag_cell("del", index)

        for strCol in diffResults["columns"]["new"]:
            col = ExcelHelper.ColumnIndexFromStr(strCol)
            for row in range(0, self.maxRows+1):
                index = "%i,%i" % (row, col)
                self.table1.tag_cell("new", index)
                self.table2.tag_cell("new", index)

        for strCol in diffResults["columns"]["del"]:
            col = ExcelHelper.ColumnIndexFromStr(strCol)
            for row in range(0, self.maxRows+1):
                index = "%i,%i" % (row, col)
                self.table1.tag_cell("del", index)
                self.table2.tag_cell("del", index)

        for k, v in list(diffResults["cells"].items()):
            coordinate = ExcelHelper.CoordinateFromStr(k)
            index = "%i,%i" % (coordinate[1],
                               ExcelHelper.ColumnIndexFromStr(coordinate[0]))
            self.table1.tag_cell("mod", index)
            self.table2.tag_cell("mod", index)

        self.table1.tag_configure('new', background='green')
        self.table2.tag_configure('new', background='green')
        self.table1.tag_configure('del', background='red')
        self.table2.tag_configure('del', background='red')
        self.table1.tag_configure('mod', background='yellow')
        self.table2.tag_configure('mod', background='yellow')

    def SelectCells(self, first, last=None):
        if self.lastSelectCells:
            self.table1.selection_clear(self.lastSelectCells[0],
                                        self.lastSelectCells[1])
            self.table2.selection_clear(self.lastSelectCells[0],
                                        self.lastSelectCells[1])

        self.table1.selection_set(first, last)

        self.table2.selection_set(first, last)

        self.lastSelectCells = (first, last)


def Usage():
    print('''
-h/--help print this usage
-s/--src src excel path
-d/--dst dst excel path
    ''')
    return 0


def ParseArgv(argv):

    params = {}

    argvMap = {
        "h": "help",
        "s:": "src=",
        "d:": "dst=",
    }

    try:
        options, args = getopt.getopt(sys.argv[1:], "".join(
            list(argvMap.keys())), list(argvMap.values()))

        for name, value in options:
            if name in ('-h', '--help'):
                return Usage()
            elif name in ('-s', '--src'):
                params['srcPath'] = value
            elif name in ('-d', '--dst'):
                params['dstPath'] = value
        if not params:
            raise getopt.GetoptError("need path for excel")

    except getopt.GetoptError:
        return {}
        #return Usage()

    return params


if __name__ == '__main__':
    params = ParseArgv(sys.argv)

    if isinstance(params, int):
        sys.exit(params)

    if not params:
        MyApp().mainloop()
    else:
        MyApp(params["srcPath"], params["dstPath"]).mainloop()
