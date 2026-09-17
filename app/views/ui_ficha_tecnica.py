# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'ficha_tecnicaWfuvJx.ui'
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
from PySide6.QtWidgets import (QApplication, QFrame, QHBoxLayout, QHeaderView,
    QLabel, QLineEdit, QPushButton, QSizePolicy,
    QSpacerItem, QTableView, QVBoxLayout, QWidget)

class Ui_Ficha_Tecnica(object):
    def setupUi(self, Ficha_Tecnica):
        if not Ficha_Tecnica.objectName():
            Ficha_Tecnica.setObjectName(u"Ficha_Tecnica")
        Ficha_Tecnica.resize(799, 538)
        font = QFont()
        font.setFamilies([u"Segoe UI Semibold"])
        font.setPointSize(10)
        font.setBold(True)
        Ficha_Tecnica.setFont(font)
        self.horizontalLayout = QHBoxLayout(Ficha_Tecnica)
        self.horizontalLayout.setSpacing(0)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.frm_Entrada = QFrame(Ficha_Tecnica)
        self.frm_Entrada.setObjectName(u"frm_Entrada")
        self.frm_Entrada.setFrameShape(QFrame.Shape.StyledPanel)
        self.frm_Entrada.setFrameShadow(QFrame.Shadow.Raised)
        self.verticalLayout = QVBoxLayout(self.frm_Entrada)
        self.verticalLayout.setSpacing(5)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(5, 5, 5, 5)
        self.frm_Cod_Acabado = QFrame(self.frm_Entrada)
        self.frm_Cod_Acabado.setObjectName(u"frm_Cod_Acabado")
        self.frm_Cod_Acabado.setFrameShape(QFrame.Shape.StyledPanel)
        self.frm_Cod_Acabado.setFrameShadow(QFrame.Shadow.Raised)
        self.horizontalLayout_2 = QHBoxLayout(self.frm_Cod_Acabado)
        self.horizontalLayout_2.setSpacing(5)
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.horizontalLayout_2.setContentsMargins(5, 5, 5, 5)
        self.lb_Prod_Acabado = QLabel(self.frm_Cod_Acabado)
        self.lb_Prod_Acabado.setObjectName(u"lb_Prod_Acabado")
        self.lb_Prod_Acabado.setMinimumSize(QSize(0, 30))
        self.lb_Prod_Acabado.setMaximumSize(QSize(16777215, 30))

        self.horizontalLayout_2.addWidget(self.lb_Prod_Acabado)

        self.txt_Prod_Acabado = QLineEdit(self.frm_Cod_Acabado)
        self.txt_Prod_Acabado.setObjectName(u"txt_Prod_Acabado")
        self.txt_Prod_Acabado.setMinimumSize(QSize(80, 30))
        self.txt_Prod_Acabado.setMaximumSize(QSize(80, 30))

        self.horizontalLayout_2.addWidget(self.txt_Prod_Acabado)

        self.bt_Pesquisa_Prod_Acabado = QPushButton(self.frm_Cod_Acabado)
        self.bt_Pesquisa_Prod_Acabado.setObjectName(u"bt_Pesquisa_Prod_Acabado")
        self.bt_Pesquisa_Prod_Acabado.setMinimumSize(QSize(40, 30))
        self.bt_Pesquisa_Prod_Acabado.setMaximumSize(QSize(40, 30))

        self.horizontalLayout_2.addWidget(self.bt_Pesquisa_Prod_Acabado)

        self.bt_Novo = QPushButton(self.frm_Cod_Acabado)
        self.bt_Novo.setObjectName(u"bt_Novo")
        self.bt_Novo.setMinimumSize(QSize(40, 30))
        self.bt_Novo.setMaximumSize(QSize(40, 30))

        self.horizontalLayout_2.addWidget(self.bt_Novo)

        self.txt_Descricao_Prod_Acabado = QLineEdit(self.frm_Cod_Acabado)
        self.txt_Descricao_Prod_Acabado.setObjectName(u"txt_Descricao_Prod_Acabado")
        self.txt_Descricao_Prod_Acabado.setMinimumSize(QSize(0, 30))
        self.txt_Descricao_Prod_Acabado.setMaximumSize(QSize(16777215, 30))
        self.txt_Descricao_Prod_Acabado.setReadOnly(True)

        self.horizontalLayout_2.addWidget(self.txt_Descricao_Prod_Acabado)

        self.lb_Sacos_Batida = QLabel(self.frm_Cod_Acabado)
        self.lb_Sacos_Batida.setObjectName(u"lb_Sacos_Batida")
        self.lb_Sacos_Batida.setMinimumSize(QSize(0, 30))
        self.lb_Sacos_Batida.setMaximumSize(QSize(16777215, 30))

        self.horizontalLayout_2.addWidget(self.lb_Sacos_Batida)

        self.txt_Sacos_Batida = QLineEdit(self.frm_Cod_Acabado)
        self.txt_Sacos_Batida.setObjectName(u"txt_Sacos_Batida")
        self.txt_Sacos_Batida.setMinimumSize(QSize(50, 30))
        self.txt_Sacos_Batida.setMaximumSize(QSize(50, 30))

        self.horizontalLayout_2.addWidget(self.txt_Sacos_Batida)

        self.bt_Abrir_Ficha = QPushButton(self.frm_Cod_Acabado)
        self.bt_Abrir_Ficha.setObjectName(u"bt_Abrir_Ficha")
        self.bt_Abrir_Ficha.setMinimumSize(QSize(0, 30))
        self.bt_Abrir_Ficha.setMaximumSize(QSize(16777215, 30))

        self.horizontalLayout_2.addWidget(self.bt_Abrir_Ficha)


        self.verticalLayout.addWidget(self.frm_Cod_Acabado)

        self.frm_Cod_Materia_Prima = QFrame(self.frm_Entrada)
        self.frm_Cod_Materia_Prima.setObjectName(u"frm_Cod_Materia_Prima")
        self.frm_Cod_Materia_Prima.setFrameShape(QFrame.Shape.StyledPanel)
        self.frm_Cod_Materia_Prima.setFrameShadow(QFrame.Shadow.Raised)
        self.horizontalLayout_7 = QHBoxLayout(self.frm_Cod_Materia_Prima)
        self.horizontalLayout_7.setSpacing(5)
        self.horizontalLayout_7.setObjectName(u"horizontalLayout_7")
        self.horizontalLayout_7.setContentsMargins(5, 5, 5, 5)
        self.lb_Cod_Mat_Prima = QLabel(self.frm_Cod_Materia_Prima)
        self.lb_Cod_Mat_Prima.setObjectName(u"lb_Cod_Mat_Prima")
        self.lb_Cod_Mat_Prima.setMinimumSize(QSize(0, 30))
        self.lb_Cod_Mat_Prima.setMaximumSize(QSize(16777215, 30))

        self.horizontalLayout_7.addWidget(self.lb_Cod_Mat_Prima)

        self.txt_Cod_Mat_Prima = QLineEdit(self.frm_Cod_Materia_Prima)
        self.txt_Cod_Mat_Prima.setObjectName(u"txt_Cod_Mat_Prima")
        self.txt_Cod_Mat_Prima.setMinimumSize(QSize(80, 30))
        self.txt_Cod_Mat_Prima.setMaximumSize(QSize(80, 30))

        self.horizontalLayout_7.addWidget(self.txt_Cod_Mat_Prima)

        self.bt_Pesquisa_Mat_Prima = QPushButton(self.frm_Cod_Materia_Prima)
        self.bt_Pesquisa_Mat_Prima.setObjectName(u"bt_Pesquisa_Mat_Prima")
        self.bt_Pesquisa_Mat_Prima.setMinimumSize(QSize(40, 30))
        self.bt_Pesquisa_Mat_Prima.setMaximumSize(QSize(40, 30))

        self.horizontalLayout_7.addWidget(self.bt_Pesquisa_Mat_Prima)

        self.txt_Descricao_Prod = QLineEdit(self.frm_Cod_Materia_Prima)
        self.txt_Descricao_Prod.setObjectName(u"txt_Descricao_Prod")
        self.txt_Descricao_Prod.setMinimumSize(QSize(0, 30))
        self.txt_Descricao_Prod.setMaximumSize(QSize(16777215, 30))

        self.horizontalLayout_7.addWidget(self.txt_Descricao_Prod)


        self.verticalLayout.addWidget(self.frm_Cod_Materia_Prima)

        self.frm_Qtde = QFrame(self.frm_Entrada)
        self.frm_Qtde.setObjectName(u"frm_Qtde")
        self.frm_Qtde.setFrameShape(QFrame.Shape.StyledPanel)
        self.frm_Qtde.setFrameShadow(QFrame.Shadow.Raised)
        self.horizontalLayout_8 = QHBoxLayout(self.frm_Qtde)
        self.horizontalLayout_8.setSpacing(5)
        self.horizontalLayout_8.setObjectName(u"horizontalLayout_8")
        self.horizontalLayout_8.setContentsMargins(5, 5, 5, 5)
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

        self.horizontalSpacer_3 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_8.addItem(self.horizontalSpacer_3)

        self.bt_Sair_Ficha = QPushButton(self.frm_Qtde)
        self.bt_Sair_Ficha.setObjectName(u"bt_Sair_Ficha")
        self.bt_Sair_Ficha.setMinimumSize(QSize(0, 30))
        self.bt_Sair_Ficha.setMaximumSize(QSize(16777215, 30))

        self.horizontalLayout_8.addWidget(self.bt_Sair_Ficha)


        self.verticalLayout.addWidget(self.frm_Qtde)

        self.frm_Itens = QFrame(self.frm_Entrada)
        self.frm_Itens.setObjectName(u"frm_Itens")
        self.frm_Itens.setFrameShape(QFrame.Shape.StyledPanel)
        self.frm_Itens.setFrameShadow(QFrame.Shadow.Raised)
        self.horizontalLayout_5 = QHBoxLayout(self.frm_Itens)
        self.horizontalLayout_5.setObjectName(u"horizontalLayout_5")
        self.verticalLayout_2 = QVBoxLayout()
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.lb_Batida = QLabel(self.frm_Itens)
        self.lb_Batida.setObjectName(u"lb_Batida")
        self.lb_Batida.setMinimumSize(QSize(0, 30))
        self.lb_Batida.setMaximumSize(QSize(16777215, 30))

        self.verticalLayout_2.addWidget(self.lb_Batida, 0, Qt.AlignmentFlag.AlignHCenter|Qt.AlignmentFlag.AlignVCenter)

        self.tb_Itens_Batida = QTableView(self.frm_Itens)
        self.tb_Itens_Batida.setObjectName(u"tb_Itens_Batida")

        self.verticalLayout_2.addWidget(self.tb_Itens_Batida)


        self.horizontalLayout_5.addLayout(self.verticalLayout_2)

        self.verticalLayout_3 = QVBoxLayout()
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.lb_Saco = QLabel(self.frm_Itens)
        self.lb_Saco.setObjectName(u"lb_Saco")
        self.lb_Saco.setMinimumSize(QSize(0, 30))
        self.lb_Saco.setMaximumSize(QSize(16777215, 30))

        self.verticalLayout_3.addWidget(self.lb_Saco, 0, Qt.AlignmentFlag.AlignHCenter|Qt.AlignmentFlag.AlignVCenter)

        self.tb_Itens_Unitario = QTableView(self.frm_Itens)
        self.tb_Itens_Unitario.setObjectName(u"tb_Itens_Unitario")

        self.verticalLayout_3.addWidget(self.tb_Itens_Unitario)


        self.horizontalLayout_5.addLayout(self.verticalLayout_3)


        self.verticalLayout.addWidget(self.frm_Itens)

        self.frm_Total = QFrame(self.frm_Entrada)
        self.frm_Total.setObjectName(u"frm_Total")
        self.frm_Total.setFrameShape(QFrame.Shape.StyledPanel)
        self.frm_Total.setFrameShadow(QFrame.Shadow.Raised)
        self.horizontalLayout_3 = QHBoxLayout(self.frm_Total)
        self.horizontalLayout_3.setSpacing(5)
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.horizontalLayout_3.setContentsMargins(5, 5, 5, 5)
        self.lb_Total_Batida = QLabel(self.frm_Total)
        self.lb_Total_Batida.setObjectName(u"lb_Total_Batida")
        self.lb_Total_Batida.setMinimumSize(QSize(0, 30))
        self.lb_Total_Batida.setMaximumSize(QSize(16777215, 30))

        self.horizontalLayout_3.addWidget(self.lb_Total_Batida)

        self.txt_Total_Batida = QLineEdit(self.frm_Total)
        self.txt_Total_Batida.setObjectName(u"txt_Total_Batida")
        self.txt_Total_Batida.setMinimumSize(QSize(100, 30))
        self.txt_Total_Batida.setMaximumSize(QSize(100, 30))

        self.horizontalLayout_3.addWidget(self.txt_Total_Batida)

        self.horizontalSpacer_5 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_3.addItem(self.horizontalSpacer_5)

        self.lb_Total_Saco = QLabel(self.frm_Total)
        self.lb_Total_Saco.setObjectName(u"lb_Total_Saco")
        self.lb_Total_Saco.setMinimumSize(QSize(0, 30))
        self.lb_Total_Saco.setMaximumSize(QSize(16777215, 30))

        self.horizontalLayout_3.addWidget(self.lb_Total_Saco)

        self.txt_Total_Saco = QLineEdit(self.frm_Total)
        self.txt_Total_Saco.setObjectName(u"txt_Total_Saco")
        self.txt_Total_Saco.setMinimumSize(QSize(100, 30))
        self.txt_Total_Saco.setMaximumSize(QSize(100, 30))

        self.horizontalLayout_3.addWidget(self.txt_Total_Saco)


        self.verticalLayout.addWidget(self.frm_Total)

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

        self.horizontalSpacer_4 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

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

        QWidget.setTabOrder(self.txt_Prod_Acabado, self.txt_Cod_Mat_Prima)
        QWidget.setTabOrder(self.txt_Cod_Mat_Prima, self.txt_Qtde)
        QWidget.setTabOrder(self.txt_Qtde, self.bt_Salvar_Itens)
        QWidget.setTabOrder(self.bt_Salvar_Itens, self.bt_Pesquisa_Prod_Acabado)
        QWidget.setTabOrder(self.bt_Pesquisa_Prod_Acabado, self.bt_Novo)
        QWidget.setTabOrder(self.bt_Novo, self.bt_Pesquisa_Mat_Prima)
        QWidget.setTabOrder(self.bt_Pesquisa_Mat_Prima, self.txt_Descricao_Prod)
        QWidget.setTabOrder(self.txt_Descricao_Prod, self.bt_Limpar_Itens)
        QWidget.setTabOrder(self.bt_Limpar_Itens, self.bt_Excluir_Itens)
        QWidget.setTabOrder(self.bt_Excluir_Itens, self.bt_Sair_Ficha)
        QWidget.setTabOrder(self.bt_Sair_Ficha, self.tb_Itens_Batida)
        QWidget.setTabOrder(self.tb_Itens_Batida, self.bt_Salvar)
        QWidget.setTabOrder(self.bt_Salvar, self.bt_Editar)
        QWidget.setTabOrder(self.bt_Editar, self.bt_Limpar)
        QWidget.setTabOrder(self.bt_Limpar, self.bt_Excluir)

        self.retranslateUi(Ficha_Tecnica)

        QMetaObject.connectSlotsByName(Ficha_Tecnica)
    # setupUi

    def retranslateUi(self, Ficha_Tecnica):
        Ficha_Tecnica.setWindowTitle(QCoreApplication.translate("Ficha_Tecnica", u"Ficha Tecnica", None))
        self.lb_Prod_Acabado.setText(QCoreApplication.translate("Ficha_Tecnica", u"C\u00f3digo Produto Acabado:", None))
        self.bt_Pesquisa_Prod_Acabado.setText(QCoreApplication.translate("Ficha_Tecnica", u"...", None))
        self.bt_Novo.setText(QCoreApplication.translate("Ficha_Tecnica", u"+", None))
        self.lb_Sacos_Batida.setText(QCoreApplication.translate("Ficha_Tecnica", u"Qtde Sacos por batida:", None))
        self.bt_Abrir_Ficha.setText(QCoreApplication.translate("Ficha_Tecnica", u"Abrir Ficha", None))
        self.lb_Cod_Mat_Prima.setText(QCoreApplication.translate("Ficha_Tecnica", u"C\u00f3digo Mat\u00e9ria Prima:", None))
        self.bt_Pesquisa_Mat_Prima.setText(QCoreApplication.translate("Ficha_Tecnica", u"...", None))
        self.lb_Qtde.setText(QCoreApplication.translate("Ficha_Tecnica", u"Qtde Kg:", None))
        self.bt_Salvar_Itens.setText(QCoreApplication.translate("Ficha_Tecnica", u"Salvar", None))
        self.bt_Limpar_Itens.setText(QCoreApplication.translate("Ficha_Tecnica", u"Limpar", None))
        self.bt_Excluir_Itens.setText(QCoreApplication.translate("Ficha_Tecnica", u"Excluir", None))
        self.bt_Sair_Ficha.setText(QCoreApplication.translate("Ficha_Tecnica", u"Sair Ficha", None))
        self.lb_Batida.setText(QCoreApplication.translate("Ficha_Tecnica", u"Batida", None))
        self.lb_Saco.setText(QCoreApplication.translate("Ficha_Tecnica", u"Saco", None))
        self.lb_Total_Batida.setText(QCoreApplication.translate("Ficha_Tecnica", u"Kg Total:", None))
        self.lb_Total_Saco.setText(QCoreApplication.translate("Ficha_Tecnica", u"Kg Saco:", None))
        self.bt_Salvar.setText(QCoreApplication.translate("Ficha_Tecnica", u"Salvar", None))
        self.bt_Editar.setText(QCoreApplication.translate("Ficha_Tecnica", u"Editar", None))
        self.bt_Limpar.setText(QCoreApplication.translate("Ficha_Tecnica", u"Limpar", None))
        self.bt_Excluir.setText(QCoreApplication.translate("Ficha_Tecnica", u"Excluir", None))
    # retranslateUi

