# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'movimento_estoqueAldzvt.ui'
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
from PySide6.QtWidgets import (QApplication, QDateEdit, QFrame, QHBoxLayout,
    QHeaderView, QLabel, QLineEdit, QPushButton,
    QSizePolicy, QTableView, QVBoxLayout, QWidget)

class Ui_Movimento_Estoque(object):
    def setupUi(self, Movimento_Estoque):
        if not Movimento_Estoque.objectName():
            Movimento_Estoque.setObjectName(u"Movimento_Estoque")
        Movimento_Estoque.resize(1110, 548)
        font = QFont()
        font.setFamilies([u"Segoe UI Semibold"])
        font.setPointSize(10)
        font.setBold(True)
        Movimento_Estoque.setFont(font)
        self.verticalLayout = QVBoxLayout(Movimento_Estoque)
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.frm_Sequencia = QFrame(Movimento_Estoque)
        self.frm_Sequencia.setObjectName(u"frm_Sequencia")
        self.frm_Sequencia.setFrameShape(QFrame.Shape.StyledPanel)
        self.frm_Sequencia.setFrameShadow(QFrame.Shadow.Raised)
        self.horizontalLayout_2 = QHBoxLayout(self.frm_Sequencia)
        self.horizontalLayout_2.setSpacing(5)
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.horizontalLayout_2.setContentsMargins(5, 5, 5, 5)
        self.lb_Data_Inicial = QLabel(self.frm_Sequencia)
        self.lb_Data_Inicial.setObjectName(u"lb_Data_Inicial")
        self.lb_Data_Inicial.setMinimumSize(QSize(0, 30))
        self.lb_Data_Inicial.setMaximumSize(QSize(16777215, 30))

        self.horizontalLayout_2.addWidget(self.lb_Data_Inicial)

        self.dt_Data_Inicial = QDateEdit(self.frm_Sequencia)
        self.dt_Data_Inicial.setObjectName(u"dt_Data_Inicial")
        self.dt_Data_Inicial.setMinimumSize(QSize(120, 30))
        self.dt_Data_Inicial.setMaximumSize(QSize(120, 30))
        self.dt_Data_Inicial.setCalendarPopup(True)

        self.horizontalLayout_2.addWidget(self.dt_Data_Inicial)

        self.lb_Data_Final = QLabel(self.frm_Sequencia)
        self.lb_Data_Final.setObjectName(u"lb_Data_Final")
        self.lb_Data_Final.setMinimumSize(QSize(0, 30))
        self.lb_Data_Final.setMaximumSize(QSize(16777215, 30))

        self.horizontalLayout_2.addWidget(self.lb_Data_Final)

        self.dt_Data_Final = QDateEdit(self.frm_Sequencia)
        self.dt_Data_Final.setObjectName(u"dt_Data_Final")
        self.dt_Data_Final.setMinimumSize(QSize(120, 30))
        self.dt_Data_Final.setMaximumSize(QSize(120, 30))
        self.dt_Data_Final.setCalendarPopup(True)

        self.horizontalLayout_2.addWidget(self.dt_Data_Final)

        self.lb_Cod_Prod = QLabel(self.frm_Sequencia)
        self.lb_Cod_Prod.setObjectName(u"lb_Cod_Prod")
        self.lb_Cod_Prod.setMinimumSize(QSize(0, 30))
        self.lb_Cod_Prod.setMaximumSize(QSize(16777215, 30))

        self.horizontalLayout_2.addWidget(self.lb_Cod_Prod)

        self.txt_Cod_Prod = QLineEdit(self.frm_Sequencia)
        self.txt_Cod_Prod.setObjectName(u"txt_Cod_Prod")
        self.txt_Cod_Prod.setMinimumSize(QSize(80, 30))
        self.txt_Cod_Prod.setMaximumSize(QSize(80, 30))

        self.horizontalLayout_2.addWidget(self.txt_Cod_Prod)

        self.bt_Pesquisar_Produto = QPushButton(self.frm_Sequencia)
        self.bt_Pesquisar_Produto.setObjectName(u"bt_Pesquisar_Produto")
        self.bt_Pesquisar_Produto.setMinimumSize(QSize(40, 30))
        self.bt_Pesquisar_Produto.setMaximumSize(QSize(40, 30))

        self.horizontalLayout_2.addWidget(self.bt_Pesquisar_Produto)

        self.txt_Descricao_Produto = QLineEdit(self.frm_Sequencia)
        self.txt_Descricao_Produto.setObjectName(u"txt_Descricao_Produto")
        self.txt_Descricao_Produto.setMinimumSize(QSize(0, 30))
        self.txt_Descricao_Produto.setMaximumSize(QSize(16777215, 30))
        self.txt_Descricao_Produto.setReadOnly(True)

        self.horizontalLayout_2.addWidget(self.txt_Descricao_Produto)

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

        self.frm_Lista_Produtos = QFrame(Movimento_Estoque)
        self.frm_Lista_Produtos.setObjectName(u"frm_Lista_Produtos")
        self.frm_Lista_Produtos.setFrameShape(QFrame.Shape.StyledPanel)
        self.frm_Lista_Produtos.setFrameShadow(QFrame.Shadow.Raised)
        self.verticalLayout_2 = QVBoxLayout(self.frm_Lista_Produtos)
        self.verticalLayout_2.setSpacing(5)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.verticalLayout_2.setContentsMargins(5, 5, 5, 5)
        self.tb_Kardex = QTableView(self.frm_Lista_Produtos)
        self.tb_Kardex.setObjectName(u"tb_Kardex")

        self.verticalLayout_2.addWidget(self.tb_Kardex)


        self.verticalLayout.addWidget(self.frm_Lista_Produtos)


        self.retranslateUi(Movimento_Estoque)

        QMetaObject.connectSlotsByName(Movimento_Estoque)
    # setupUi

    def retranslateUi(self, Movimento_Estoque):
        Movimento_Estoque.setWindowTitle(QCoreApplication.translate("Movimento_Estoque", u"Ficha Kardex do Produto", None))
        self.lb_Data_Inicial.setText(QCoreApplication.translate("Movimento_Estoque", u"Data Inicial:", None))
        self.lb_Data_Final.setText(QCoreApplication.translate("Movimento_Estoque", u"Data Final:", None))
        self.lb_Cod_Prod.setText(QCoreApplication.translate("Movimento_Estoque", u"Cod. Prod.:", None))
        self.bt_Pesquisar_Produto.setText(QCoreApplication.translate("Movimento_Estoque", u"...", None))
        self.bt_Atualizar.setText(QCoreApplication.translate("Movimento_Estoque", u"Atualizar", None))
        self.bt_Exportar.setText(QCoreApplication.translate("Movimento_Estoque", u"Exportar para Excel", None))
    # retranslateUi

