import sys
from PyQt4 import QtGui, QtCore
from functools import partial

import parse_game_config
import parse_stage_config

class Window(QtGui.QMainWindow):
    def __init__(self):
        super(Window, self).__init__()

        if not self.open_file_dlg():
            sys.exit()

        self.setGeometry(50, 50, 530, 580)
        self.setWindowTitle("Sonic Mania Palette Editor")
        #self.setWindowIcon(QtGui.QIcon('pythonlogo.png'))

        openAction = QtGui.QAction("&Open", self)
        openAction.setShortcut("Ctrl+S")
        openAction.triggered.connect(self.open)

        saveAction = QtGui.QAction("&Save", self)
        saveAction.setShortcut("Ctrl+S")
        saveAction.triggered.connect(self.save)

        exitAction = QtGui.QAction("&Exit", self)
        exitAction.setShortcut("Ctrl+Q")
        exitAction.triggered.connect(self.close_application)

        self.statusBar()

        mainMenu = self.menuBar()
        fileMenu = mainMenu.addMenu('&File')
        fileMenu.addAction(openAction)
        fileMenu.addAction(saveAction)
        fileMenu.addAction(exitAction)

        self.toolBar = self.addToolBar("Toolbar")
        self.toolBar.setMovable(False)
        self.toolBar.addAction(openAction)
        self.toolBar.addAction(saveAction)

        self.checkboxs = []
        for i in xrange(16):
            checkBox = QtGui.QCheckBox("", self)
            checkBox.move(10, 90 + i * 30)
            checkBox.stateChanged.connect(partial(self.click_checkbox, i))
            self.checkboxs.append(checkBox)

        self.columns = []
        for i in xrange(16):
            pixels = []
            self.columns.append(pixels)
            for j in xrange(16):
                pixel = QtGui.QPushButton("", self)
                pixels.append(pixel)
                pixel.resize(25, 25)
                self.update_pixel_color(i, j, None)
                pixel.move(34 + j * 30, 92 + i * 30)
                pixel.clicked.connect(partial(self.set_color, i, j))

        self.palette_buttons = []
        for i in xrange(8):
            palette = QtGui.QPushButton("#%d" % i, self)
            palette.resize(60, palette.height())
            palette.move(15 + i * 63, 52)
            palette.setCheckable(True)
            palette.clicked.connect(partial(self.load_palette, i))
            self.palette_buttons.append(palette)

        self.current_palette = 0
        self.changes = False
        self.load_palette(0)

        self.show()

    def open_file_dlg(self):
        settings = QtCore.QSettings()
        choose_file = QtGui.QFileDialog.getOpenFileName(self, "Open Config File", settings.value("default_dir").toString(), "Sonic Mania Config File (GameConfig.bin; StageConfig.bin)");

        if not choose_file:
            return False
        settings.setValue("default_dir", QtCore.QDir().absoluteFilePath(choose_file))

        self.filename = str(choose_file)
        try:
            if self.filename.endswith("GameConfig.bin"):
                self.cfg = parse_game_config.CFG.parse(open(self.filename, "rb").read())
            else:
                self.cfg = parse_stage_config.CFG.parse(open(self.filename, "rb").read())
        except:
            self._error_message("Failed to load configuration file")
            return False
        return True

    def _error_message(self, text):
        msg = QtGui.QMessageBox()
        msg.setIcon(QtGui.QMessageBox.Critical)

        msg.setText(text)
        msg.setWindowTitle("Error")
        msg.setStandardButtons(QtGui.QMessageBox.Close)

        msg.exec_()

    def open(self):
        if not self.changes or self._save_changes_dlg():
            if self.open_file_dlg():
                self.load_palette(0)

    def save(self):
        if self.changes:
            try:
                if self.filename.endswith("GameConfig.bin"):
                    open(self.filename, "wb").write(parse_game_config.CFG.build(self.cfg))
                else:
                    open(self.filename, "wb").write(parse_stage_config.CFG.build(self.cfg))
                self.changes = False
            except:
                self._error_message("Failed to save configuration file")
                return False
        return True

    def update_pixel_color(self, col, row, color):
        if color is None:
            self.columns[col][row].setStyleSheet("QWidget { background-color: rgb(220,220,220); border-color: rgb(150,150,150); border-width: 1; border-style: outset; }")
        else:
            self.columns[col][row].setStyleSheet("QWidget { background-color: rgb(%d,%d,%d); border-color: black; border-width: 1; border-style: outset; }" % (color["R"], color["G"], color["B"]))

    def update_column_colors(self, col, pixels):
        for i in xrange(16):
            if pixels:
                self.update_pixel_color(col, i, pixels[i])
            else:
                self.update_pixel_color(col, i, None)

    def load_palette(self, index):
        before_changes = self.changes
        self.palette_buttons[self.current_palette].setChecked(False)
        self.current_palette = index
        self.palette_buttons[self.current_palette].setChecked(True)
        for i in xrange(16):
            if self.cfg.Palettes[index].Bitmap & (1 << i):
                self.checkboxs[i].setChecked(True)
                self.update_column_colors(i, self.cfg.Palettes[index].Columns[i].Pixels)
            else:
                self.checkboxs[i].setChecked(False)
                self.update_column_colors(i, None)
        self.changes = before_changes

    def click_checkbox(self, col, state):
        if state == QtCore.Qt.Checked:
            if not self.cfg.Palettes[self.current_palette].Columns[col].Pixels:
                pixels = [{"R":0,"G":0,"B":0} for i in xrange(16)]
                self.cfg.Palettes[self.current_palette].Columns[col].Pixels = pixels
            self.cfg.Palettes[self.current_palette].Bitmap |= 1 << col
            self.update_column_colors(col, self.cfg.Palettes[self.current_palette].Columns[col].Pixels)
        else:
            self.cfg.Palettes[self.current_palette].Bitmap &= ~(1 << col)
            self.update_column_colors(col, None)
        self.changes = True

    def set_color(self, col, row):
        if self.checkboxs[col].isChecked():
            dlg = QtGui.QColorDialog(self)
            current_pixel = self.cfg.Palettes[self.current_palette].Columns[col].Pixels[row]
            dlg.setCurrentColor(QtGui.QColor(current_pixel["R"], current_pixel["G"], current_pixel["B"]))
            if dlg.exec_():
                color = dlg.selectedColor()
                self.changes = True
                pixel = {"R": color.red(), "G": color.green(), "B": color.blue()}
                self.cfg.Palettes[self.current_palette].Columns[col].Pixels[row] = pixel
                self.update_pixel_color(col, row, pixel)

    def _save_changes_dlg(self):
        choice = QtGui.QMessageBox.question(self, 'Warning',
                                                  "Are you want to save the changes?",
                                                  QtGui.QMessageBox.Yes | QtGui.QMessageBox.No | QtGui.QMessageBox.Cancel)
        if choice == QtGui.QMessageBox.No:
            return True
        elif choice == QtGui.QMessageBox.Yes:
            return self.save()
        else:
            return False

    def close_application(self):
        if not self.changes:
            sys.exit()
        if self._save_changes_dlg():
            sys.exit()
        else:
            pass

    def closeEvent(self, event):
        if self.changes:
            if self._save_changes_dlg():
                event.accept()
            else:
                event.ignore()
        else:
            event.accept()

def run():
    app = QtGui.QApplication(sys.argv)
    app.setApplicationName("Sonic Mania Palette Editor")
    app.setOrganizationName("koolkdev")
    app.setOrganizationDomain("github.com/koolkdev")
    GUI = Window()
    sys.exit(app.exec_())

run()