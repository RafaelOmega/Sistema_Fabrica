# -*- coding: utf-8 -*-

################################################################################
# Form generated from reading UI file 'carregamentonzAvUi.ui'
##
# Created by: Qt User Interface Compiler version 6.11.2
##
# WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
                            QMetaObject, QObject, QPoint, QRect,
                            QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
                           QFont, QFontDatabase, QGradient, QIcon,
                           QImage, QKeySequence, QLinearGradient, QPainter,
                           QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QDialog, QFrame, QHBoxLayout,
                               QLabel, QProgressBar, QSizePolicy, QVBoxLayout,
                               QWidget)


class Ui_Carregamento(object):
    def setupUi(self, Carregamento):
        if not Carregamento.objectName():
            Carregamento.setObjectName(u"Carregamento")
        Carregamento.resize(707, 132)
        font = QFont()
        font.setFamilies([u"Segoe UI Semibold"])
        font.setPointSize(20)
        font.setBold(True)
        Carregamento.setFont(font)
        self.verticalLayout = QVBoxLayout(Carregamento)
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.frm_Texto = QFrame(Carregamento)
        self.frm_Texto.setObjectName(u"frm_Texto")
        self.frm_Texto.setFrameShape(QFrame.Shape.StyledPanel)
        self.frm_Texto.setFrameShadow(QFrame.Shadow.Raised)
        self.horizontalLayout = QHBoxLayout(self.frm_Texto)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.lb_Carregamento = QLabel(self.frm_Texto)
        self.lb_Carregamento.setObjectName(u"lb_Carregamento")

        self.horizontalLayout.addWidget(
            self.lb_Carregamento, 0, Qt.AlignmentFlag.AlignHCenter)

        self.verticalLayout.addWidget(self.frm_Texto)

        self.frm_Barra_Progresso = QFrame(Carregamento)
        self.frm_Barra_Progresso.setObjectName(u"frm_Barra_Progresso")
        self.frm_Barra_Progresso.setFrameShape(QFrame.Shape.StyledPanel)
        self.frm_Barra_Progresso.setFrameShadow(QFrame.Shadow.Raised)
        self.horizontalLayout_2 = QHBoxLayout(self.frm_Barra_Progresso)
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.progressBar = QProgressBar(self.frm_Barra_Progresso)
        self.progressBar.setObjectName(u"progressBar")
        self.progressBar.setValue(24)

        self.horizontalLayout_2.addWidget(self.progressBar)

        self.verticalLayout.addWidget(self.frm_Barra_Progresso)

        self.retranslateUi(Carregamento)

        QMetaObject.connectSlotsByName(Carregamento)
    # setupUi

    def retranslateUi(self, Carregamento):
        Carregamento.setWindowTitle(QCoreApplication.translate(
            "Carregamento", u"Carregando o sistema", None))
        self.lb_Carregamento.setText(QCoreApplication.translate(
            "Carregamento", u"Carregando....", None))
    # retranslateUi
