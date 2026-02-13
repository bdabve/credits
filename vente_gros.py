#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# ----------------------------------------------------------------------------
from PyQt5 import QtWidgets     # , QtCore
from gui.h_vente_gros import Ui_Dialog
import db_handler
import utils


class VenteGros(QtWidgets.QDialog):
    def __init__(self):
        super().__init__()
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)
        self.db = db_handler.Database()

        # populate price from db
        self.ui.comboBoxProduct.currentIndexChanged.connect(self.get_product_price)

        # populate products comboBox
        result = self.db.get_products_sku()
        if result["success"]:
            products = result["data"]
            utils.populate_comboBox(self.ui.comboBoxProduct, products)
        else:
            print("Error fetching products:", result["error"])

        self.ui.buttonAddProduct.clicked.connect(self.add_product_tableWidget)

    def get_product_price(self):
        """
        GET PRODUCT PRICE
        get the product price to display in QDoubleSpinBox Price
        """
        product = self.ui.comboBoxProduct.currentText()
        result = self.db.get_product_price(product)
        if result["success"]:
            # print(result)
            self.ui.doubleSpinBoxPrice.setValue(result["data"])
        else:
            return

    def add_product_tableWidget(self):
        """
        Add Product details to the TableWidget
        """
        sku = self.ui.comboBoxProduct.currentText()

        qte = self.ui.lineEditQte.text()
        try:
            qte = eval(qte)
        except Exception:
            self.ui.labelErros.setText("Verifier la quentité SVP.")
            return
        else:
            self.ui.lineEditQte.setText(str(qte))

        price = self.ui.doubleSpinBoxPrice.value()
        if price == 0:
            self.ui.labelErros.setText("Verifie le PRIX SVP.")
            return

        total = price * qte
        remise = self.ui.doubleSpinBoxRemise.value()
        remise_calc = total * (remise / 100)
        total_ttc = total - remise_calc
        self.insert_product_tableWidget(sku, qte, price, total, remise_calc, total_ttc)
        print(f"Adding the product to table widget SKU({sku}) - QTE({qte}) - PRICE({price}) - REMISE({remise})")

    def insert_product_tableWidget(self, sku, qte, price, total, remise_calc, total_ttc):
        table = self.ui.tableWidgetProducts
        row_position = table.rowCount()
        table.insertRow(row_position)
        table.setItem(row_position, 0, QtWidgets.QTableWidgetItem(sku))
        table.setItem(row_position, 1, QtWidgets.QTableWidgetItem(str(qte)))
        table.setItem(row_position, 3, QtWidgets.QTableWidgetItem(str(price)))
        table.setItem(row_position, 4, QtWidgets.QTableWidgetItem(str(total)))
        table.setItem(row_position, 5, QtWidgets.QTableWidgetItem(str(round(remise_calc, 2))))
        table.setItem(row_position, 6, QtWidgets.QTableWidgetItem(str(total_ttc)))

        self.update_totals_labels()

    def update_totals_labels(self):
        table = self.ui.tableWidgetProducts
        total_ht = 0
        total_remise = 0
        total_ttc = 0
        for row in range(table.rowCount()):
            total_ht += float(table.item(row, 4).text())
            total_remise += float(table.item(row, 5).text())
            total_ttc += float(table.item(row, 6).text())
        self.ui.TotalGeneral.setText(f"{round(total_ht, 2)}")
        self.ui.TotalGeneralRemise.setText(f"{round(total_remise, 2)}")
        self.ui.TotalGeneralTTC.setText(f"{round(total_ttc, 2)}")


if __name__ == '__main__':
    import sys
    app = QtWidgets.QApplication(sys.argv)

    dialog = VenteGros()
    dialog.show()
    sys.exit(app.exec_())
