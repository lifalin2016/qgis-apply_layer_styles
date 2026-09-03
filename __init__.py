# -*- coding: utf-8 -*-
"""Apply Layer Styles - QGIS plugin entry point."""


def classFactory(iface):
    """Load ApplyLayerStyles class.

    :param iface: A QGIS interface instance.
    :type iface: qgis.gui.QgisInterface
    """
    from .apply_layer_styles import ApplyLayerStyles
    return ApplyLayerStyles(iface)
