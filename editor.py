import importlib
import io
import math
import os
import struct
import sys

from PySide6.QtCore import QCoreApplication, QMetaObject, QRect, QSize, Qt
from PySide6.QtGui import QAction
from PySide6.QtWidgets import (
    QAbstractItemView,
    QApplication,
    QCheckBox,
    QComboBox,
    QDoubleSpinBox,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QListView,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QMenu,
    QMenuBar,
    QSpinBox,
    QWidget,
)

from pes_ai.utils import conv_to_bytes


class SectionItem(QListWidgetItem):
    def __init__(self, offset=None, length=None):
        super().__init__()
        self.offset = offset
        self.length = length


class ValueWidget(QWidget):
    def __init__(self, name: str, value: int | float | bool, disabled=False):
        super().__init__()
        self.name = name
        self.value = value

        self.resize(512, 64)
        self.setMinimumSize(QSize(512, 64))
        self.setMaximumSize(QSize(512, 64))

        self.ui_name = QLabel()
        self.ui_name.setText(self.name)

        match type(self.value).__name__:
            case "int":
                self.ui_value = QSpinBox()
                self.ui_value.setMaximum(65535)
                self.ui_value.setValue(self.value)
            case "float":
                self.ui_value = QDoubleSpinBox()
                self.ui_value.setMaximum(9999.99)
                self.ui_value.setMinimum(-9999.99)
                self.ui_value.setValue(self.value)
                if math.isnan(self.value):
                    disabled = True
            case "bool":
                self.ui_value = QCheckBox()
                self.ui_value.setChecked(self.value)
            case _:
                self.ui_value = QSpinBox()
                self.ui_value.setValue(0)
                disabled = True

        if disabled:
            self.ui_value.setReadOnly(True)
            self.ui_value.setEnabled(False)

        layout = QHBoxLayout()
        layout.addWidget(self.ui_name)
        layout.addStretch()
        layout.addWidget(self.ui_value)
        self.setLayout(layout)

        match type(value).__name__:
            case "bool":
                self.ui_value.toggled.connect(self.update_value)
            case _:
                self.ui_value.setFixedSize(QSize(75, 22))
                self.ui_value.valueChanged.connect(self.update_value)

    def update_value(self, value):
        self.value = value


class Editor(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("Editor")
        self.resize(1280, 720)
        self.setMinimumSize(QSize(1280, 720))
        self.setMaximumSize(QSize(1280, 720))
        self.act_load_17 = QAction()
        self.act_load_17.setObjectName("act_load_17")
        self.act_load_18 = QAction()
        self.act_load_18.setObjectName("act_load_18")
        self.act_save = QAction()
        self.act_save.setObjectName("act_save")
        self.act_save_as = QAction()
        self.act_save_as.setObjectName("act_save_as")
        self.central_widget = QWidget()
        self.central_widget.setObjectName("central_widget")
        self.section_list = QListWidget(self.central_widget)
        self.section_list.setObjectName("section_list")
        self.section_list.setGeometry(QRect(10, 45, 200, 640))
        self.value_list = QListWidget(self.central_widget)
        self.value_list.setObjectName("value_list")
        self.value_list.setGeometry(QRect(220, 10, 1050, 675))
        self.value_list.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.value_list.setSelectionMode(QAbstractItemView.SelectionMode.NoSelection)
        self.value_list.setFlow(QListView.Flow.LeftToRight)
        self.value_list.setProperty("isWrapping", True)
        self.value_list.setGridSize(QSize(512, 64))
        self.file_list = QComboBox(self.central_widget)
        self.file_list.setObjectName("file_list")
        self.file_list.setGeometry(QRect(10, 10, 200, 25))
        self.setCentralWidget(self.central_widget)
        self.menu_bar = QMenuBar()
        self.menu_bar.setObjectName("menu_bar")
        self.menu_bar.setGeometry(QRect(0, 0, 1280, 22))
        self.menu_load = QMenu(self.menu_bar)
        self.menu_load.setObjectName("menu_load")
        self.menu_save = QMenu(self.menu_bar)
        self.menu_save.setObjectName("menu_save")
        self.setMenuBar(self.menu_bar)

        self.menu_bar.addAction(self.menu_load.menuAction())
        self.menu_bar.addAction(self.menu_save.menuAction())
        self.menu_load.addAction(self.act_load_17)
        self.menu_load.addAction(self.act_load_18)
        self.menu_save.addAction(self.act_save)
        self.menu_save.addAction(self.act_save_as)

        self.re_translate_ui()

        QMetaObject.connectSlotsByName(self)

        self.act_load_17.triggered.connect(self.load_17_bin)
        self.act_load_18.triggered.connect(self.load_18_bin)
        self.act_save.triggered.connect(self.save_bin)
        self.section_list.currentItemChanged.connect(self.load_section)

        self.buffer: io.BytesIO | None = None
        self.filename: str = ""
        self.module = None
        self.head_len: int = 0
        self.idx_len: int = 0
        self.subsections: dict = {}

    def re_translate_ui(self):
        window_title = QCoreApplication.translate("Editor", "PES Gameplay Editor", None)
        self.setWindowTitle(window_title)
        load_17_text = QCoreApplication.translate("Editor", "Load 17 files", None)
        self.act_load_17.setText(load_17_text)
        load_18_text = QCoreApplication.translate("Editor", "Load 18 files", None)
        self.act_load_18.setText(load_18_text)
        save_text = QCoreApplication.translate("Editor", "Save", None)
        self.act_save.setText(save_text)
        save_as_text = QCoreApplication.translate("Editor", "Save As...", None)
        self.act_save_as.setText(save_as_text)
        menu_load_title = QCoreApplication.translate("Editor", "Load", None)
        self.menu_load.setTitle(menu_load_title)
        menu_save_title = QCoreApplication.translate("Editor", "Save", None)
        self.menu_save.setTitle(menu_save_title)

    def get_filename(self):
        self.filename = QFileDialog.getOpenFileName(self, "CPK File")[0]

    def load_bin(self):
        self.section_list.clear()
        if self.filename.replace(" ", "") != "":
            with open(self.filename, "rb") as f:
                self.buffer = io.BytesIO(f.read())
                sect_offs = []
                sect_lens = []
                for i in range(math.ceil(self.head_len / 12) - 1):
                    sect_len, _, sect_off = struct.unpack("<3i", self.buffer.read(12))
                    sect_lens.append(sect_len)
                    sect_offs.append(sect_off)

                del sect_lens[0]
                sect_lens.append(os.fstat(f.fileno()).st_size - sect_offs[-1])

                self.buffer.seek(self.head_len)
                i = 0
                for enc_str in self.buffer.read(self.idx_len).split(b"\x00"):
                    if enc_str != b"":
                        sect_name = enc_str.decode("utf-8")
                        sect_dict = {"offset": sect_offs[i], "length": sect_lens[i]}
                        self.subsections[sect_name] = sect_dict
                        i += 1

            for k, v in self.subsections.items():
                item = SectionItem(offset=v["offset"], length=v["length"])
                item.setText(k)
                self.section_list.addItem(item)

    def load_17_bin(self):
        self.get_filename()
        if "constant_team" in self.filename:
            self.module = importlib.import_module("pes_ai.seventeen.team")
            self.head_len = 200
            self.idx_len = 218
        if self.head_len != 0 and self.idx_len != 0:
            self.load_bin()

    def load_18_bin(self):
        self.get_filename()
        if "constant_team" in self.filename:
            self.module = importlib.import_module("pes_ai.eighteen.team")
            self.head_len = 200
            self.idx_len = 218
        if self.head_len != 0 and self.idx_len != 0:
            self.load_bin()

    def save_changed_value(self, sect: SectionItem):
        val_count = self.value_list.count()
        if val_count != 1:
            self.buffer.seek(sect.offset)
            for i in range(val_count):
                val = self.value_list.itemWidget(self.value_list.item(i))
                name = getattr(val, "name")
                value = getattr(val, "value")
                if "null" in name and value == 0:
                    data = conv_to_bytes(None)
                else:
                    bool_list = getattr(self.module, "one_byte_bools")
                    if isinstance(value, bool) and name not in bool_list:
                        data = conv_to_bytes(int(value))
                    else:
                        data = conv_to_bytes(value)
                self.buffer.write(data)

    def save_bin(self):
        # noinspection PyTypeChecker
        self.save_changed_value(self.section_list.currentItem())
        with open(self.filename, "wb") as f:
            self.buffer.seek(0)
            f.write(self.buffer.read())

    def add_value_widget(self, name: str, value: float | int | bool, disabled=False):
        item = QListWidgetItem()
        widget = ValueWidget(name, value, disabled)
        self.value_list.insertItem(self.value_list.count(), item)
        self.value_list.setItemWidget(item, widget)
        item.setSizeHint(widget.sizeHint())

    def load_section(self, curr: SectionItem | None, prev: SectionItem | None):
        if prev:
            self.save_changed_value(prev)
        self.value_list.clear()
        if curr:
            try:
                func = getattr(self.module, f"map_{curr.text()[:-2]}")
                vals = func(self.buffer, curr.offset, curr.length)
                for k, v in vals.items():
                    self.add_value_widget(k, v)
            except AttributeError:
                self.add_value_widget(str(curr.length), curr.offset, True)


if __name__ == "__main__":
    p = QApplication(sys.argv)
    w = Editor()
    w.show()
    sys.exit(p.exec())
