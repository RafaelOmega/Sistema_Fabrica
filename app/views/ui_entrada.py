# -*- coding: utf-8 -*-

################################################################################
# Form generated from reading UI file 'entradagZTZBq.ui'
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
from PySide6.QtWidgets import (QApplication, QComboBox, QDateEdit, QFrame,
                               QGridLayout, QHBoxLayout, QHeaderView, QLabel,
                               QLineEdit, QPushButton, QSizePolicy, QSpacerItem,
                               QTableView, QVBoxLayout, QWidget)


class Ui_Entrada(object):
    def setupUi(self, Entrada):
        if not Entrada.objectName():
            Entrada.setObjectName(u"Entrada")
        Entrada.resize(799, 538)
        font = QFont()
        font.setFamilies([u"Segoe UI Semibold"])
        font.setPointSize(10)
        font.setBold(True)
        Entrada.setFont(font)
        self.horizontalLayout = QHBoxLayout(Entrada)
        self.horizontalLayout.setSpacing(0)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.frm_Entrada = QFrame(Entrada)
        self.frm_Entrada.setObjectName(u"frm_Entrada")
        self.frm_Entrada.setFrameShape(QFrame.Shape.StyledPanel)
        self.frm_Entrada.setFrameShadow(QFrame.Shadow.Raised)
        self.verticalLayout = QVBoxLayout(self.frm_Entrada)
        self.verticalLayout.setSpacing(5)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(5, 5, 5, 5)
        self.frm_Sequencia = QFrame(self.frm_Entrada)
        self.frm_Sequencia.setObjectName(u"frm_Sequencia")
        self.frm_Sequencia.setFrameShape(QFrame.Shape.StyledPanel)
        self.frm_Sequencia.setFrameShadow(QFrame.Shadow.Raised)
        self.horizontalLayout_2 = QHBoxLayout(self.frm_Sequencia)
        self.horizontalLayout_2.setSpacing(5)
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.horizontalLayout_2.setContentsMargins(5, 5, 5, 5)
        self.lb_Sequencia = QLabel(self.frm_Sequencia)
        self.lb_Sequencia.setObjectName(u"lb_Sequencia")
        self.lb_Sequencia.setMinimumSize(QSize(0, 30))
        self.lb_Sequencia.setMaximumSize(QSize(16777215, 30))

        self.horizontalLayout_2.addWidget(self.lb_Sequencia)

        self.txt_Sequencia = QLineEdit(self.frm_Sequencia)
        self.txt_Sequencia.setObjectName(u"txt_Sequencia")
        self.txt_Sequencia.setMinimumSize(QSize(100, 30))
        self.txt_Sequencia.setMaximumSize(QSize(100, 30))

        self.horizontalLayout_2.addWidget(self.txt_Sequencia)

        self.bt_Pesquisa_Entrada = QPushButton(self.frm_Sequencia)
        self.bt_Pesquisa_Entrada.setObjectName(u"bt_Pesquisa_Entrada")
        self.bt_Pesquisa_Entrada.setMinimumSize(QSize(40, 30))
        self.bt_Pesquisa_Entrada.setMaximumSize(QSize(40, 30))

        self.horizontalLayout_2.addWidget(self.bt_Pesquisa_Entrada)

        self.bt_Novo = QPushButton(self.frm_Sequencia)
        self.bt_Novo.setObjectName(u"bt_Novo")
        self.bt_Novo.setMinimumSize(QSize(40, 30))
        self.bt_Novo.setMaximumSize(QSize(40, 30))

        self.horizontalLayout_2.addWidget(self.bt_Novo)

        self.horizontalSpacer = QSpacerItem(
            40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_2.addItem(self.horizontalSpacer)

        self.verticalLayout.addWidget(self.frm_Sequencia)

        self.frm_Abrir_Itens = QFrame(self.frm_Entrada)
        self.frm_Abrir_Itens.setObjectName(u"frm_Abrir_Itens")
        self.frm_Abrir_Itens.setFrameShape(QFrame.Shape.StyledPanel)
        self.frm_Abrir_Itens.setFrameShadow(QFrame.Shadow.Raised)
        self.horizontalLayout_3 = QHBoxLayout(self.frm_Abrir_Itens)
        self.horizontalLayout_3.setSpacing(5)
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.horizontalLayout_3.setContentsMargins(5, 5, 5, 5)
        self.lb_Data = QLabel(self.frm_Abrir_Itens)
        self.lb_Data.setObjectName(u"lb_Data")
        self.lb_Data.setMinimumSize(QSize(0, 30))
        self.lb_Data.setMaximumSize(QSize(16777215, 30))

        self.horizontalLayout_3.addWidget(self.lb_Data)

        self.dt_Entrada = QDateEdit(self.frm_Abrir_Itens)
        self.dt_Entrada.setObjectName(u"dt_Entrada")
        self.dt_Entrada.setMinimumSize(QSize(0, 30))
        self.dt_Entrada.setMaximumSize(QSize(16777215, 30))
        self.dt_Entrada.setCalendarPopup(True)

        self.horizontalLayout_3.addWidget(self.dt_Entrada)

        self.lb_Motivo = QLabel(self.frm_Abrir_Itens)
        self.lb_Motivo.setObjectName(u"lb_Motivo")
        self.lb_Motivo.setMinimumSize(QSize(0, 30))
        self.lb_Motivo.setMaximumSize(QSize(16777215, 30))

        self.horizontalLayout_3.addWidget(self.lb_Motivo)

        self.cmb_Motivo = QComboBox(self.frm_Abrir_Itens)
        self.cmb_Motivo.setObjectName(u"cmb_Motivo")
        self.cmb_Motivo.setMinimumSize(QSize(150, 30))
        self.cmb_Motivo.setMaximumSize(QSize(150, 30))

        self.horizontalLayout_3.addWidget(self.cmb_Motivo)

        self.bt_Abrir_Itens = QPushButton(self.frm_Abrir_Itens)
        self.bt_Abrir_Itens.setObjectName(u"bt_Abrir_Itens")
        self.bt_Abrir_Itens.setMinimumSize(QSize(0, 30))
        self.bt_Abrir_Itens.setMaximumSize(QSize(16777215, 30))

        self.horizontalLayout_3.addWidget(self.bt_Abrir_Itens)

        self.horizontalSpacer_2 = QSpacerItem(
            40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_3.addItem(self.horizontalSpacer_2)

        self.verticalLayout.addWidget(self.frm_Abrir_Itens)

        self.frm_Prod = QFrame(self.frm_Entrada)
        self.frm_Prod.setObjectName(u"frm_Prod")
        self.frm_Prod.setFrameShape(QFrame.Shape.StyledPanel)
        self.frm_Prod.setFrameShadow(QFrame.Shadow.Raised)
        self.horizontalLayout_7 = QHBoxLayout(self.frm_Prod)
        self.horizontalLayout_7.setSpacing(5)
        self.horizontalLayout_7.setObjectName(u"horizontalLayout_7")
        self.horizontalLayout_7.setContentsMargins(5, 5, 5, 5)
        self.lb_Cod_Prod = QLabel(self.frm_Prod)
        self.lb_Cod_Prod.setObjectName(u"lb_Cod_Prod")
        self.lb_Cod_Prod.setMinimumSize(QSize(0, 30))
        self.lb_Cod_Prod.setMaximumSize(QSize(16777215, 30))

        self.horizontalLayout_7.addWidget(self.lb_Cod_Prod)

        self.txt_Cod_Prod = QLineEdit(self.frm_Prod)
        self.txt_Cod_Prod.setObjectName(u"txt_Cod_Prod")
        self.txt_Cod_Prod.setMinimumSize(QSize(100, 30))
        self.txt_Cod_Prod.setMaximumSize(QSize(100, 30))

        self.horizontalLayout_7.addWidget(self.txt_Cod_Prod)

        self.bt_Pesquisa_Itens = QPushButton(self.frm_Prod)
        self.bt_Pesquisa_Itens.setObjectName(u"bt_Pesquisa_Itens")
        self.bt_Pesquisa_Itens.setMinimumSize(QSize(40, 30))
        self.bt_Pesquisa_Itens.setMaximumSize(QSize(40, 30))

        self.horizontalLayout_7.addWidget(self.bt_Pesquisa_Itens)

        self.txt_Descricao_Prod = QLineEdit(self.frm_Prod)
        self.txt_Descricao_Prod.setObjectName(u"txt_Descricao_Prod")
        self.txt_Descricao_Prod.setMinimumSize(QSize(0, 30))
        self.txt_Descricao_Prod.setMaximumSize(QSize(16777215, 30))

        self.horizontalLayout_7.addWidget(self.txt_Descricao_Prod)

        self.verticalLayout.addWidget(self.frm_Prod)

        self.frm_Qtde = QFrame(self.frm_Entrada)
        self.frm_Qtde.setObjectName(u"frm_Qtde")
        self.frm_Qtde.setFrameShape(QFrame.Shape.StyledPanel)
        self.frm_Qtde.setFrameShadow(QFrame.Shadow.Raised)
        self.horizontalLayout_8 = QHBoxLayout(self.frm_Qtde)
        self.horizontalLayout_8.setSpacing(5)
        self.horizontalLayout_8.setObjectName(u"horizontalLayout_8")
        self.horizontalLayout_8.setContentsMargins(5, 5, 5, 5)
        self.lb_Un = QLabel(self.frm_Qtde)
        self.lb_Un.setObjectName(u"lb_Un")
        self.lb_Un.setMinimumSize(QSize(0, 30))
        self.lb_Un.setMaximumSize(QSize(16777215, 30))

        self.horizontalLayout_8.addWidget(self.lb_Un)

        self.cmb_Un = QComboBox(self.frm_Qtde)
        self.cmb_Un.addItem("")
        self.cmb_Un.addItem("")
        self.cmb_Un.setObjectName(u"cmb_Un")
        self.cmb_Un.setMinimumSize(QSize(60, 30))
        self.cmb_Un.setMaximumSize(QSize(60, 30))

        self.horizontalLayout_8.addWidget(self.cmb_Un)

        self.lb_Qtde = QLabel(self.frm_Qtde)
        self.lb_Qtde.setObjectName(u"lb_Qtde")
        self.lb_Qtde.setMinimumSize(QSize(0, 30))
        self.lb_Qtde.setMaximumSize(QSize(16777215, 30))

        self.horizontalLayout_8.addWidget(self.lb_Qtde)

        self.txt_Qtde = QLineEdit(self.frm_Qtde)
        self.txt_Qtde.setObjectName(u"txt_Qtde")
        self.txt_Qtde.setMinimumSize(QSize(80, 30))
        self.txt_Qtde.setMaximumSize(QSize(80, 30))

        self.horizontalLayout_8.addWidget(self.txt_Qtde)

        self.lb_Custo = QLabel(self.frm_Qtde)
        self.lb_Custo.setObjectName(u"lb_Custo")
        self.lb_Custo.setMinimumSize(QSize(0, 30))
        self.lb_Custo.setMaximumSize(QSize(16777215, 30))

        self.horizontalLayout_8.addWidget(self.lb_Custo)

        self.txt_Custo = QLineEdit(self.frm_Qtde)
        self.txt_Custo.setObjectName(u"txt_Custo")
        self.txt_Custo.setMinimumSize(QSize(80, 30))
        self.txt_Custo.setMaximumSize(QSize(80, 30))

        self.horizontalLayout_8.addWidget(self.txt_Custo)

        self.bt_Salvar_Itens = QPushButton(self.frm_Qtde)
        self.bt_Salvar_Itens.setObjectName(u"bt_Salvar_Itens")
        self.bt_Salvar_Itens.setMinimumSize(QSize(0, 30))
        self.bt_Salvar_Itens.setMaximumSize(QSize(16777215, 30))

        self.horizontalLayout_8.addWidget(self.bt_Salvar_Itens)

        self.bt_Limpar_Itens = QPushButton(self.frm_Qtde)
        self.bt_Limpar_Itens.setObjectName(u"bt_Limpar_Itens")
        self.bt_Limpar_Itens.setMinimumSize(QSize(0, 30))
        self.bt_Limpar_Itens.setMaximumSize(QSize(16777215, 30))

        self.horizontalLayout_8.addWidget(self.bt_Limpar_Itens)

        self.bt_Excluir_Itens = QPushButton(self.frm_Qtde)
        self.bt_Excluir_Itens.setObjectName(u"bt_Excluir_Itens")
        self.bt_Excluir_Itens.setMinimumSize(QSize(0, 30))
        self.bt_Excluir_Itens.setMaximumSize(QSize(16777215, 30))

        self.horizontalLayout_8.addWidget(self.bt_Excluir_Itens)

        self.horizontalSpacer_3 = QSpacerItem(
            40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_8.addItem(self.horizontalSpacer_3)

        self.bt_Sair_Itens = QPushButton(self.frm_Qtde)
        self.bt_Sair_Itens.setObjectName(u"bt_Sair_Itens")
        self.bt_Sair_Itens.setMinimumSize(QSize(0, 30))
        self.bt_Sair_Itens.setMaximumSize(QSize(16777215, 30))

        self.horizontalLayout_8.addWidget(self.bt_Sair_Itens)

        self.verticalLayout.addWidget(self.frm_Qtde)

        self.frm_Itens = QFrame(self.frm_Entrada)
        self.frm_Itens.setObjectName(u"frm_Itens")
        self.frm_Itens.setFrameShape(QFrame.Shape.StyledPanel)
        self.frm_Itens.setFrameShadow(QFrame.Shadow.Raised)
        self.gridLayout = QGridLayout(self.frm_Itens)
        self.gridLayout.setSpacing(5)
        self.gridLayout.setObjectName(u"gridLayout")
        self.gridLayout.setContentsMargins(5, 5, 5, 5)
        self.lb_Total = QLabel(self.frm_Itens)
        self.lb_Total.setObjectName(u"lb_Total")
        self.lb_Total.setMinimumSize(QSize(0, 30))
        self.lb_Total.setMaximumSize(QSize(16777215, 30))

        self.gridLayout.addWidget(self.lb_Total, 1, 1, 1, 1)

        self.txt_Total_Itens = QLineEdit(self.frm_Itens)
        self.txt_Total_Itens.setObjectName(u"txt_Total_Itens")
        self.txt_Total_Itens.setMinimumSize(QSize(150, 30))
        self.txt_Total_Itens.setMaximumSize(QSize(150, 30))

        self.gridLayout.addWidget(self.txt_Total_Itens, 1, 2, 1, 1)

        self.horizontalSpacer_5 = QSpacerItem(
            40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.gridLayout.addItem(self.horizontalSpacer_5, 1, 0, 1, 1)

        self.tb_Itens = QTableView(self.frm_Itens)
        self.tb_Itens.setObjectName(u"tb_Itens")

        self.gridLayout.addWidget(self.tb_Itens, 0, 0, 1, 3)

        self.verticalLayout.addWidget(self.frm_Itens)

        self.frm_Crud = QFrame(self.frm_Entrada)
        self.frm_Crud.setObjectName(u"frm_Crud")
        self.frm_Crud.setFrameShape(QFrame.Shape.StyledPanel)
        self.frm_Crud.setFrameShadow(QFrame.Shadow.Raised)
        self.horizontalLayout_4 = QHBoxLayout(self.frm_Crud)
        self.horizontalLayout_4.setSpacing(5)
        self.horizontalLayout_4.setObjectName(u"horizontalLayout_4")
        self.horizontalLayout_4.setContentsMargins(5, 5, 5, 5)
        self.bt_Salvar = QPushButton(self.frm_Crud)
        self.bt_Salvar.setObjectName(u"bt_Salvar")
        self.bt_Salvar.setMinimumSize(QSize(0, 30))
        self.bt_Salvar.setMaximumSize(QSize(16777215, 30))

        self.horizontalLayout_4.addWidget(self.bt_Salvar)

        self.bt_Editar = QPushButton(self.frm_Crud)
        self.bt_Editar.setObjectName(u"bt_Editar")
        self.bt_Editar.setMinimumSize(QSize(0, 30))
        self.bt_Editar.setMaximumSize(QSize(16777215, 30))

        self.horizontalLayout_4.addWidget(self.bt_Editar)

        self.horizontalSpacer_4 = QSpacerItem(
            40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_4.addItem(self.horizontalSpacer_4)

        self.bt_Limpar = QPushButton(self.frm_Crud)
        self.bt_Limpar.setObjectName(u"bt_Limpar")
        self.bt_Limpar.setMinimumSize(QSize(0, 30))
        self.bt_Limpar.setMaximumSize(QSize(16777215, 30))

        self.horizontalLayout_4.addWidget(self.bt_Limpar)

        self.bt_Excluir = QPushButton(self.frm_Crud)
        self.bt_Excluir.setObjectName(u"bt_Excluir")
        self.bt_Excluir.setMinimumSize(QSize(0, 30))
        self.bt_Excluir.setMaximumSize(QSize(16777215, 30))

        self.horizontalLayout_4.addWidget(self.bt_Excluir)

        self.verticalLayout.addWidget(self.frm_Crud)

        self.horizontalLayout.addWidget(self.frm_Entrada)

        self.retranslateUi(Entrada)

        QMetaObject.connectSlotsByName(Entrada)
    # setupUi

    def retranslateUi(self, Entrada):
        Entrada.setWindowTitle(QCoreApplication.translate(
            "Entrada", u"Entradas", None))
        self.lb_Sequencia.setText(
            QCoreApplication.translate("Entrada", u"Sequencia:", None))
        self.bt_Pesquisa_Entrada.setText(
            QCoreApplication.translate("Entrada", u"...", None))
        self.bt_Novo.setText(QCoreApplication.translate("Entrada", u"+", None))
        self.lb_Data.setText(
            QCoreApplication.translate("Entrada", u"Data:", None))
        self.lb_Motivo.setText(
            QCoreApplication.translate("Entrada", u"Motivo:", None))
        self.bt_Abrir_Itens.setText(
            QCoreApplication.translate("Entrada", u"Abrir Itens", None))
        self.lb_Cod_Prod.setText(
            QCoreApplication.translate("Entrada", u"C\u00f3d:", None))
        self.bt_Pesquisa_Itens.setText(
            QCoreApplication.translate("Entrada", u"...", None))
        self.lb_Un.setText(QCoreApplication.translate("Entrada", u"Un:", None))
        self.cmb_Un.setItemText(
            0, QCoreApplication.translate("Entrada", u"SC", None))
        self.cmb_Un.setItemText(
            1, QCoreApplication.translate("Entrada", u"KG", None))

        self.lb_Qtde.setText(
            QCoreApplication.translate("Entrada", u"Qtde:", None))
        self.lb_Custo.setText(
            QCoreApplication.translate("Entrada", u"Custo:", None))
        self.bt_Salvar_Itens.setText(
            QCoreApplication.translate("Entrada", u"Salvar", None))
        self.bt_Limpar_Itens.setText(
            QCoreApplication.translate("Entrada", u"Limpar", None))
        self.bt_Excluir_Itens.setText(
            QCoreApplication.translate("Entrada", u"Excluir", None))
        self.bt_Sair_Itens.setText(
            QCoreApplication.translate("Entrada", u"Sair Itens", None))
        self.lb_Total.setText(
            QCoreApplication.translate("Entrada", u"Total:", None))
        self.bt_Salvar.setText(
            QCoreApplication.translate("Entrada", u"Salvar", None))
        self.bt_Editar.setText(
            QCoreApplication.translate("Entrada", u"Editar", None))
        self.bt_Limpar.setText(
            QCoreApplication.translate("Entrada", u"Limpar", None))
        self.bt_Excluir.setText(
            QCoreApplication.translate("Entrada", u"Excluir", None))
    # retranslateUi
