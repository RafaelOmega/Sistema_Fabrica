# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'estoqueKuOzKF.ui'
##
## Created by: Qt User Interface Compiler version 6.11.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QCheckBox, QDateEdit, QFrame,
    QHBoxLayout, QHeaderView, QLabel, QPushButton,
    QSizePolicy, QSpacerItem, QTableView, QVBoxLayout,
    QWidget)

class Ui_Estoque_Tab(object):
    def setupUi(self, Estoque_Tab):
        if not Estoque_Tab.objectName():
            Estoque_Tab.setObjectName(u"Estoque_Tab")
        Estoque_Tab.resize(806, 548)
        font = QFont()
        font.setFamilies([u"Segoe UI Semibold"])
        font.setPointSize(10)
        font.setBold(True)
        Estoque_Tab.setFont(font)
        self.verticalLayout = QVBoxLayout(Estoque_Tab)
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.frm_Sequencia = QFrame(Estoque_Tab)
        self.frm_Sequencia.setObjectName(u"frm_Sequencia")
        self.frm_Sequencia.setFrameShape(QFrame.Shape.StyledPanel)
        self.frm_Sequencia.setFrameShadow(QFrame.Shadow.Raised)
        self.horizontalLayout_2 = QHBoxLayout(self.frm_Sequencia)
        self.horizontalLayout_2.setSpacing(5)
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.horizontalLayout_2.setContentsMargins(5, 5, 5, 5)
        self.lb_Saldo_Data = QLabel(self.frm_Sequencia)
        self.lb_Saldo_Data.setObjectName(u"lb_Saldo_Data")
        self.lb_Saldo_Data.setMinimumSize(QSize(0, 30))
        self.lb_Saldo_Data.setMaximumSize(QSize(16777215, 30))

        self.horizontalLayout_2.addWidget(self.lb_Saldo_Data)

        self.dt_Filtro = QDateEdit(self.frm_Sequencia)
        self.dt_Filtro.setObjectName(u"dt_Filtro")
        self.dt_Filtro.setMinimumSize(QSize(120, 30))
        self.dt_Filtro.setMaximumSize(QSize(120, 30))
        self.dt_Filtro.setCalendarPopup(True)

        self.horizontalLayout_2.addWidget(self.dt_Filtro)

        self.ck_Ocultar = QCheckBox(self.frm_Sequencia)
        self.ck_Ocultar.setObjectName(u"ck_Ocultar")
        self.ck_Ocultar.setMinimumSize(QSize(0, 30))
        self.ck_Ocultar.setMaximumSize(QSize(16777215, 30))

        self.horizontalLayout_2.addWidget(self.ck_Ocultar)

        self.horizontalSpacer = QSpacerItem(781, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_2.addItem(self.horizontalSpacer)

        self.bt_Atualizar = QPushButton(self.frm_Sequencia)
        self.bt_Atualizar.setObjectName(u"bt_Atualizar")
        self.bt_Atualizar.setMinimumSize(QSize(0, 30))
        self.bt_Atualizar.setMaximumSize(QSize(16777215, 30))

        self.horizontalLayout_2.addWidget(self.bt_Atualizar)

        self.bt_Exportar = QPushButton(self.frm_Sequencia)
        self.bt_Exportar.setObjectName(u"bt_Exportar")
        self.bt_Exportar.setMinimumSize(QSize(0, 30))
        self.bt_Exportar.setMaximumSize(QSize(16777215, 30))

        self.horizontalLayout_2.addWidget(self.bt_Exportar)


        self.verticalLayout.addWidget(self.frm_Sequencia)

        self.frm_Lista_Produtos = QFrame(Estoque_Tab)
        self.frm_Lista_Produtos.setObjectName(u"frm_Lista_Produtos")
        self.frm_Lista_Produtos.setFrameShape(QFrame.Shape.StyledPanel)
        self.frm_Lista_Produtos.setFrameShadow(QFrame.Shadow.Raised)
        self.verticalLayout_2 = QVBoxLayout(self.frm_Lista_Produtos)
        self.verticalLayout_2.setSpacing(5)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.verticalLayout_2.setContentsMargins(5, 5, 5, 5)
        self.tb_Estoque = QTableView(self.frm_Lista_Produtos)
        self.tb_Estoque.setObjectName(u"tb_Estoque")

        self.verticalLayout_2.addWidget(self.tb_Estoque)


        self.verticalLayout.addWidget(self.frm_Lista_Produtos)


        self.retranslateUi(Estoque_Tab)

        QMetaObject.connectSlotsByName(Estoque_Tab)
    # setupUi

    def retranslateUi(self, Estoque_Tab):
        Estoque_Tab.setWindowTitle(QCoreApplication.translate("Estoque_Tab", u"Estoque", None))
        self.lb_Saldo_Data.setText(QCoreApplication.translate("Estoque_Tab", u"Ver saldo at\u00e9 a Data:", None))
        self.ck_Ocultar.setText(QCoreApplication.translate("Estoque_Tab", u"Ocultar produtos com saldo zero", None))
        self.bt_Atualizar.setText(QCoreApplication.translate("Estoque_Tab", u"Atualizar", None))
        self.bt_Exportar.setText(QCoreApplication.translate("Estoque_Tab", u"Exportar para Excel", None))
    # retranslateUi

