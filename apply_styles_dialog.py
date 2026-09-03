# -*- coding: utf-8 -*-
"""Dialog that lets the user pick one or more target layers to receive a style."""

from qgis.PyQt.QtCore import Qt
from qgis.PyQt.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QDialogButtonBox,
    QLabel,
    QCheckBox,
)


class ApplyStylesDialog(QDialog):
    """Dialog showing a filterable, checkable list of candidate layers."""

    def __init__(self, source_layer, candidate_layers, parent=None):
        """
        :param source_layer: the layer whose style will be copied.
        :param candidate_layers: list of (display_name, QgsVectorLayer) tuples,
            where display_name is the layer name prefixed with its group
            path (e.g. "GroupName1/GroupName2/LayerName").
        :param parent: parent widget (typically iface.mainWindow()).
        """
        super().__init__(parent)
        self.source_layer = source_layer
        self.candidate_layers = candidate_layers

        self.setWindowTitle(self.tr('Apply Styles - "{}"').format(source_layer.name()))
        self.resize(380, 460)

        layout = QVBoxLayout(self)

        info_label = QLabel(
            self.tr('Apply the style of "{}" to the selected layer(s):').format(
                source_layer.name()
            )
        )
        info_label.setWordWrap(True)
        layout.addWidget(info_label)

        self.filter_edit = QLineEdit(self)
        self.filter_edit.setPlaceholderText(self.tr("Filter layers by name..."))
        self.filter_edit.textChanged.connect(self._filter_layers)
        layout.addWidget(self.filter_edit)

        self.list_widget = QListWidget(self)
        layout.addWidget(self.list_widget)

        for display_name, layer in self.candidate_layers:
            item = QListWidgetItem(display_name)
            item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
            item.setCheckState(Qt.Unchecked)
            item.setData(Qt.UserRole, layer.id())
            self.list_widget.addItem(item)

        self.select_all_checkbox = QCheckBox(self.tr("Select All/None"), self)
        self.select_all_checkbox.setTristate(False)
        self.select_all_checkbox.stateChanged.connect(self._toggle_select_all)
        layout.addWidget(self.select_all_checkbox)

        self.button_box = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel, self
        )
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        layout.addWidget(self.button_box)

        self.filter_edit.setFocus()

    def _filter_layers(self, text):
        """Hide list items whose name doesn't contain the filter text."""
        text = text.strip().lower()
        for i in range(self.list_widget.count()):
            item = self.list_widget.item(i)
            item.setHidden(bool(text) and text not in item.text().lower())

    def _toggle_select_all(self, state):
        """Check/uncheck every currently visible (non-filtered-out) item."""
        check_state = Qt.Checked if state == Qt.Checked else Qt.Unchecked
        for i in range(self.list_widget.count()):
            item = self.list_widget.item(i)
            if not item.isHidden():
                item.setCheckState(check_state)

    def selected_layer_ids(self):
        """Return the layer ids of every checked item, regardless of filter state."""
        ids = []
        for i in range(self.list_widget.count()):
            item = self.list_widget.item(i)
            if item.checkState() == Qt.Checked:
                ids.append(item.data(Qt.UserRole))
        return ids
