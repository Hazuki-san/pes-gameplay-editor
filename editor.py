import math
import os
import struct
import sys

from PySide6.QtCore import *
from PySide6.QtWidgets import *

from pes_ai.eighteen.team import *
from pes_ai.ui import Ui_Editor
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

        match type(value).__name__:
            case "int":
                self.ui_value = QSpinBox()
                self.ui_value.setMaximum(65535)
                self.ui_value.setValue(self.value)
            case "float":
                self.ui_value = QDoubleSpinBox()
                self.ui_value.setMaximum(9999.99)
                self.ui_value.setMinimum(-9999.99)
                self.ui_value.setValue(self.value)
            case "bool":
                self.ui_value = QCheckBox()
                self.ui_value.setChecked(self.value)
            case _:
                self.ui_value = QSpinBox()
                self.ui_value.setValue(0)
                self.ui_value.setReadOnly(True)
                self.ui_value.setEnabled(False)

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
                self.ui_value.valueChanged.connect(self.update_value)

    def update_value(self, value):
        self.value = value


class Editor(QMainWindow, Ui_Editor):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)

        self.actionLoad_18_files.triggered.connect(self.load_18_bin)
        self.actionSave.triggered.connect(self.save_bin)
        self.SectionList.currentItemChanged.connect(self.load_section)

        self.buffer: io.BytesIO | None = None
        self.filename: str = ""
        self.head_len: int = 0
        self.idx_len: int = 0
        self.subsections: dict = {}

    def get_filename(self):
        f = QFileDialog.getOpenFileName(self, "CPK File")
        self.filename = f[0].replace(" ", "")

    def load_bin(self):
        self.SectionList.clear()
        if self.filename != "":
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
                self.SectionList.addItem(item)

    def load_18_bin(self):
        self.get_filename()
        if "constant_team" in self.filename:
            self.head_len = 200
            self.idx_len = 218
        if self.head_len != 0 and self.idx_len != 0:
            self.load_bin()

    def save_changed_value(self, sect: SectionItem):
        val_count = self.ValueList.count()
        if val_count != 1:
            self.buffer.seek(sect.offset)
            for i in range(val_count):
                val = self.ValueList.itemWidget(self.ValueList.item(i))
                if "null" in val.name and val.value == 0:
                    data = conv_to_bytes(None)
                else:
                    data = conv_to_bytes(val.value)
                self.buffer.write(data)

    def save_bin(self):
        self.save_changed_value(self.SectionList.currentItem())
        with open(self.filename, "wb") as f:
            self.buffer.seek(0)
            f.write(self.buffer.read())

    def add_value_widget(self, name: str, value: float | int | bool, disabled=False):
        item = QListWidgetItem()
        widget = ValueWidget(name, value, disabled)
        self.ValueList.insertItem(self.ValueList.count(), item)
        self.ValueList.setItemWidget(item, widget)
        item.setSizeHint(widget.sizeHint())

    def load_section(self, curr: SectionItem, prev: SectionItem | None):
        if prev:
            self.save_changed_value(prev)
        self.ValueList.clear()
        try:
            vals = globals()[f"map_{curr.text()[:-2]}"](
                self.buffer, curr.offset, curr.length
            )
            for k, v in vals.items():
                self.add_value_widget(k, v)
        except KeyError:
            self.add_value_widget(str(curr.length), curr.offset, True)


if __name__ == "__main__":
    p = QApplication(sys.argv)
    w = Editor()
    w.show()
    sys.exit(p.exec())
