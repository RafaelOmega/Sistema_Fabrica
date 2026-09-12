# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'main_windowptHBDG.ui'
##
## Created by: Qt User Interface Compiler version 6.11.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QAction, QBrush, QColor, QConicalGradient,
    QCursor, QFont, QFontDatabase, QGradient,
    QIcon, QImage, QKeySequence, QLinearGradient,
    QPainter, QPalette, QPixmap, QRadialGradient,
    QTransform)
from PySide6.QtWidgets import (QAbstractSpinBox, QApplication, QDateEdit, QFrame,
    QHBoxLayout, QLabel, QMainWindow, QMdiArea,
    QMenu, QMenuBar, QSizePolicy, QSpacerItem,
    QTimeEdit, QVBoxLayout, QWidget)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(800, 600)
        font = QFont()
        font.setFamilies([u"Segoe UI Semibold"])
        font.setPointSize(10)
        font.setBold(True)
        MainWindow.setFont(font)
        self.actionProdutos = QAction(MainWindow)
        self.actionProdutos.setObjectName(u"actionProdutos")
        self.actionMotivo_Entrada = QAction(MainWindow)
        self.actionMotivo_Entrada.setObjectName(u"actionMotivo_Entrada")
        self.actionEntrada = QAction(MainWindow)
        self.actionEntrada.setObjectName(u"actionEntrada")
        self.actionFicha_Tecnica = QAction(MainWindow)
        self.actionFicha_Tecnica.setObjectName(u"actionFicha_Tecnica")
        self.actionSaida = QAction(MainWindow)
        self.actionSaida.setObjectName(u"actionSaida")
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.verticalLayout = QVBoxLayout(self.centralwidget)
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.mdiArea = QMdiArea(self.centralwidget)
        self.mdiArea.setObjectName(u"mdiArea")

        self.verticalLayout.addWidget(self.mdiArea)

        self.frm_StatusBar = QFrame(self.centralwidget)
        self.frm_StatusBar.setObjectName(u"frm_StatusBar")
        self.frm_StatusBar.setFrameShape(QFrame.Shape.StyledPanel)
        self.frm_StatusBar.setFrameShadow(QFrame.Shadow.Raised)
        self.horizontalLayout = QHBoxLayout(self.frm_StatusBar)
        self.horizontalLayout.setSpacing(0)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.lb_Comandos = QLabel(self.frm_StatusBar)
        self.lb_Comandos.setObjectName(u"lb_Comandos")
        self.lb_Comandos.setMinimumSize(QSize(0, 30))
        self.lb_Comandos.setMaximumSize(QSize(16777215, 30))

        self.horizontalLayout.addWidget(self.lb_Comandos)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer)

        self.dt_Data_Atual = QDateEdit(self.frm_StatusBar)
        self.dt_Data_Atual.setObjectName(u"dt_Data_Atual")
        self.dt_Data_Atual.setEnabled(False)
        self.dt_Data_Atual.setMinimumSize(QSize(0, 30))
        self.dt_Data_Atual.setMaximumSize(QSize(16777215, 30))
        self.dt_Data_Atual.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.dt_Data_Atual.setReadOnly(True)
        self.dt_Data_Atual.setButtonSymbols(QAbstractSpinBox.ButtonSymbols.NoButtons)

        self.horizontalLayout.addWidget(self.dt_Data_Atual, 0, Qt.AlignmentFlag.AlignHCenter|Qt.AlignmentFlag.AlignVCenter)

        self.dt_Hora_Atual = QTimeEdit(self.frm_StatusBar)
        self.dt_Hora_Atual.setObjectName(u"dt_Hora_Atual")
        self.dt_Hora_Atual.setEnabled(False)
        self.dt_Hora_Atual.setMinimumSize(QSize(0, 30))
        self.dt_Hora_Atual.setMaximumSize(QSize(16777215, 30))
        self.dt_Hora_Atual.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.dt_Hora_Atual.setReadOnly(True)
        self.dt_Hora_Atual.setButtonSymbols(QAbstractSpinBox.ButtonSymbols.NoButtons)

        self.horizontalLayout.addWidget(self.dt_Hora_Atual, 0, Qt.AlignmentFlag.AlignHCenter|Qt.AlignmentFlag.AlignVCenter)


        self.verticalLayout.addWidget(self.frm_StatusBar)

        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(MainWindow)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 800, 33))
        self.menuCadastros = QMenu(self.menubar)
        self.menuCadastros.setObjectName(u"menuCadastros")
        self.menuLan_amentos = QMenu(self.menubar)
        self.menuLan_amentos.setObjectName(u"menuLan_amentos")
        MainWindow.setMenuBar(self.menubar)

        self.menubar.addAction(self.menuCadastros.menuAction())
        self.menubar.addAction(self.menuLan_amentos.menuAction())
        self.menuCadastros.addAction(self.actionProdutos)
        self.menuCadastros.addAction(self.actionMotivo_Entrada)
        self.menuCadastros.addAction(self.actionFicha_Tecnica)
        self.menuLan_amentos.addAction(self.actionEntrada)
        self.menuLan_amentos.addAction(self.actionSaida)

        self.retranslateUi(MainWindow)

        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"MainWindow", None))
        self.actionProdutos.setText(QCoreApplication.translate("MainWindow", u"Produtos", None))
        self.actionMotivo_Entrada.setText(QCoreApplication.translate("MainWindow", u"Motivo Entrada", None))
        self.actionEntrada.setText(QCoreApplication.translate("MainWindow", u"Entrada", None))
        self.actionFicha_Tecnica.setText(QCoreApplication.translate("MainWindow", u"Ficha T\u00e9cnica", None))
        self.actionSaida.setText(QCoreApplication.translate("MainWindow", u"Saida", None))
        self.lb_Comandos.setText("")
        self.menuCadastros.setTitle(QCoreApplication.translate("MainWindow", u"Cadastros", None))
        self.menuLan_amentos.setTitle(QCoreApplication.translate("MainWindow", u"Lan\u00e7amentos", None))
    # retranslateUi

