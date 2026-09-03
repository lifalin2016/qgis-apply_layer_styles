# Apply Layer Styles (QGIS plugin)

Adds an **Apply Styles...** entry to the bottom of a vector layer's
**Styles** submenu (right-click a layer in the Layers panel → Styles →
Apply Styles...).

## What it does

1. You right-click a vector layer and open **Styles → Apply Styles...**
2. A dialog opens listing every *other* vector layer in the project that
   has the same geometry type (point / line / polygon) as the layer you
   clicked. Each entry is prefixed with its layer-tree group path, e.g.
   `GroupName1/GroupName2/LayerName`, so layers in different groups are
   easy to tell apart. A text box above the list lets you filter it by
   name as you type.
3. Below the list, a **Select All/None** checkbox checks or unchecks
   every currently visible (non-filtered-out) layer in one click.
4. Check one or more layers and click **OK**.
5. The plugin copies the full style (symbology, labeling, opacity, etc.)
   from the source layer onto every checked layer and repaints the map.

"Same topology" is interpreted as **same geometry type** (point, line,
or polygon), since that's what determines whether a style can validly be
applied — it ignores incidental differences like single- vs.
multi-part or Z/M dimensionality.

## Installation

1. Zip the `apply_layer_styles` folder (or use the provided zip) so that
   `metadata.txt` is at the top level of the archive.
2. In QGIS: **Plugins → Manage and Install Plugins → Install from ZIP**,
   select the zip file, and click **Install Plugin**.
3. Enable **Apply Layer Styles** in the plugin list if it isn't enabled
   automatically.

Alternatively, copy the `apply_layer_styles` folder directly into your
QGIS profile's `python/plugins` directory (find it via **Settings →
User Profiles → Open Active Profile Folder**, then `python/plugins/`),
then enable the plugin from the Plugin Manager.

## Files

- `metadata.txt` — plugin metadata read by the QGIS Plugin Manager.
- `__init__.py` — plugin entry point (`classFactory`).
- `apply_layer_styles.py` — main plugin logic: hooks the layer tree
  context menu, finds candidate layers, and copies styles.
- `apply_styles_dialog.py` — the filterable, multi-select layer picker
  dialog.

## Notes

- Requires QGIS 3.16+.
- Works on any vector layer type (memory, file-based, PostGIS, etc.)
  since it uses QGIS's standard named-style (QML) export/import
  mechanism — the same one used by "Copy Style" / "Paste Style".
