# -*- coding: utf-8 -*-
"""Apply Layer Styles plugin.

Adds an "Apply Styles" entry to the bottom of a vector layer's "Styles"
context-menu submenu in the Layers panel. Choosing it opens a dialog
listing every other vector layer in the project with the same geometry
type, with a name filter box. Checked layers receive a full copy of the
source layer's style.
"""

from qgis.PyQt.QtCore import QCoreApplication
from qgis.PyQt.QtXml import QDomDocument
from qgis.core import (
    QgsProject,
    QgsVectorLayer,
    QgsWkbTypes,
    QgsReadWriteContext,
)

from .apply_styles_dialog import ApplyStylesDialog


class ApplyLayerStyles:
    """Main plugin class."""

    def __init__(self, iface):
        self.iface = iface
        self.layer_tree_view = None
        # Keep references to dynamically-created actions so PyQt does not
        # garbage-collect them (and their signal connections) between clicks.
        self._added_actions = []

    # ------------------------------------------------------------------
    # QGIS plugin lifecycle
    # ------------------------------------------------------------------
    def initGui(self):
        self.layer_tree_view = self.iface.layerTreeView()
        self.layer_tree_view.contextMenuAboutToShow.connect(self._on_context_menu)

    def unload(self):
        if self.layer_tree_view is not None:
            try:
                self.layer_tree_view.contextMenuAboutToShow.disconnect(
                    self._on_context_menu
                )
            except (TypeError, RuntimeError):
                pass
        self._added_actions = []

    # ------------------------------------------------------------------
    # Context menu handling
    # ------------------------------------------------------------------
    def _on_context_menu(self, menu):
        """Called just before the layer tree context menu is shown."""
        layer = self.iface.layerTreeView().currentLayer()
        if not isinstance(layer, QgsVectorLayer):
            return

        styles_menu = self._find_styles_submenu(menu)
        if styles_menu is None:
            return

        styles_menu.addSeparator()
        action = styles_menu.addAction(self.tr("Apply Styles..."))
        action.triggered.connect(lambda checked=False, l=layer: self._show_dialog(l))
        self._added_actions.append(action)

    @staticmethod
    def _find_styles_submenu(menu):
        """Locate the built-in "Styles" submenu inside the layer context menu."""
        target_title = QCoreApplication.translate(
            "QgsMapLayerStyleManagerWidget", "Styles"
        ).replace("&", "").strip().lower()

        for action in menu.actions():
            submenu = action.menu()
            if submenu is None:
                continue
            title = submenu.title().replace("&", "").strip().lower()
            if title == target_title or title == "styles":
                return submenu
        return None

    @staticmethod
    def _layer_display_path(root, layer):
        """Build 'GroupName1/GroupName2/LayerName' for a layer's position
        in the layer tree. Layers not inside any group just return their
        own name."""
        node = root.findLayer(layer.id())
        if node is None:
            return layer.name()

        group_names = []
        parent = node.parent()
        while parent is not None and parent != root:
            name = parent.name()
            if name:
                group_names.insert(0, name)
            parent = parent.parent()

        if group_names:
            return "/".join(group_names) + "/" + layer.name()
        return layer.name()

    # ------------------------------------------------------------------
    # Dialog / style application
    # ------------------------------------------------------------------
    def _show_dialog(self, source_layer):
        source_geom_type = QgsWkbTypes.geometryType(source_layer.wkbType())
        root = QgsProject.instance().layerTreeRoot()

        candidates = []
        for layer in QgsProject.instance().mapLayers().values():
            if layer.id() == source_layer.id():
                continue
            if not isinstance(layer, QgsVectorLayer):
                continue
            if QgsWkbTypes.geometryType(layer.wkbType()) != source_geom_type:
                continue
            display_name = self._layer_display_path(root, layer)
            candidates.append((display_name, layer))

        candidates.sort(key=lambda pair: pair[0].lower())

        if not candidates:
            self.iface.messageBar().pushInfo(
                self.tr("Apply Styles"),
                self.tr(
                    'No other layers with the same geometry type as "{}" were found.'
                ).format(source_layer.name()),
            )
            return

        dialog = ApplyStylesDialog(source_layer, candidates, self.iface.mainWindow())
        if dialog.exec_():
            target_ids = dialog.selected_layer_ids()
            if target_ids:
                self._apply_style(source_layer, target_ids)

    def _apply_style(self, source_layer, target_ids):
        doc = QDomDocument()
        context = QgsReadWriteContext()

        # exportNamedStyle's signature changed across QGIS versions; support both.
        try:
            error_msg = source_layer.exportNamedStyle(doc, context)
        except TypeError:
            error_msg = source_layer.exportNamedStyle(doc)

        if error_msg:
            self.iface.messageBar().pushWarning(
                self.tr("Apply Styles"),
                self.tr("Could not read style from source layer: {}").format(error_msg),
            )
            return

        applied = 0
        failed = []
        project = QgsProject.instance()

        for layer_id in target_ids:
            layer = project.mapLayer(layer_id)
            if layer is None:
                continue
            # Each layer needs its own copy of the DOM document.
            style_doc = doc.cloneNode(True).toDocument()
            success, err = layer.importNamedStyle(style_doc)
            if success:
                layer.triggerRepaint()
                layer.emitStyleChanged()
                applied += 1
            else:
                failed.append("{}: {}".format(layer.name(), err))

        if applied:
            self.iface.messageBar().pushSuccess(
                self.tr("Apply Styles"),
                self.tr('Style from "{}" applied to {} layer(s).').format(
                    source_layer.name(), applied
                ),
            )
        if failed:
            self.iface.messageBar().pushWarning(
                self.tr("Apply Styles"),
                self.tr("Failed to apply style to: {}").format("; ".join(failed)),
            )

    def tr(self, message):
        return QCoreApplication.translate("ApplyLayerStyles", message)
