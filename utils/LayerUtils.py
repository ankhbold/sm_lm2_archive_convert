#!/usr/bin/python
# -*- coding: utf-8
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4.QtSql import QSqlDatabase
from qgis.core import *

from SessionHandler import SessionHandler
from ..model import SettingsConstants
from ..model import Constants
from ..model.LM2Exception import LM2Exception

class LayerUtils(object):

    @staticmethod
    def layer_by_name(layer_name):
        layers = QgsMapLayerRegistry.instance().mapLayers()

        for id, layer in layers.iteritems():
            if layer.name() == layer_name:
                return layer

        return None

    @staticmethod
    def layer_by_data_source(schema_name, table_name):

        layers = QgsMapLayerRegistry.instance().mapLayers()

        for id, layer in layers.iteritems():
            if layer.type() == QgsMapLayer.VectorLayer:
                uri_string = layer.dataProvider().dataSourceUri()
                uri = QgsDataSourceURI(uri_string)
                if uri.table() == table_name:
                    if uri.schema() == schema_name:
                        return layer

    @staticmethod
    def load_layer_by_name(layer_name, id, restrictions=[]):

        restrictions = restrictions.split(",")

        if len(restrictions) > 0:
            for restriction in restrictions:
                restriction = restriction.strip()
                uri = QgsDataSourceURI()
                user = QSettings().value(SettingsConstants.USER)
                db = QSettings().value(SettingsConstants.DATABASE_NAME)
                host = QSettings().value(SettingsConstants.HOST)
                port = QSettings().value(SettingsConstants.PORT, "5432")
                pwd = SessionHandler().current_password()

                uri.setConnection(host, port, db, user, pwd)
                uri.setDataSource("s" + restriction, layer_name, "geometry", "", id)

                vlayer = QgsVectorLayer(uri.uri(), "s" + restriction + "_" + layer_name, "postgres")
                QgsMapLayerRegistry.instance().addMapLayer(vlayer)
                return vlayer

        else:
            uri = QgsDataSourceURI()
            user = QSettings().value(SettingsConstants.USER)
            db = QSettings().value(SettingsConstants.DATABASE_NAME)
            host = QSettings().value(SettingsConstants.HOST)
            port = QSettings().value(SettingsConstants.PORT, "5432")
            pwd = SessionHandler().current_password()

            uri.setConnection(host, port, db, user, pwd)
            uri.setDataSource(layer_name, "geometry", "", id)

            vlayer = QgsVectorLayer(uri.uri(), layer_name, "postgres")
            QgsMapLayerRegistry.instance().addMapLayer(vlayer)
            return vlayer

    @staticmethod
    def where(layer, exp):

        exp = QgsExpression(exp)

        if exp.hasParserError():
            raise LM2Exception("Error", "Wrong Expression")

        exp.prepare(layer.pendingFields())
        for feature in layer.getFeatures():
            value = exp.evaluate(feature)
            if exp.hasEvalError():
                raise ValueError(exp.evalErrorString())
            if bool(value):
                yield feature

    @staticmethod
    def deselect_all():

        layers = QgsMapLayerRegistry.instance().mapLayers()

        for id, layer in layers.iteritems():
            if layer.type() == QgsMapLayer.VectorLayer:
                layer.removeSelection()