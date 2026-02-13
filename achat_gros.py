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

        # populate products comboBox
        result = self.db.get_products_sku()
        if result["success"]:
            products = result["data"]
            utils.populate_comboBox(self.ui.comboBoxProduct, products)
        else:
            print("Error fetching products:", result["error"])

        # populate price from db
        self.ui.comboBoxProduct.currentIndexChanged.connect(self.update_price_edit)

    def update_price_edit(self):
        product = self.ui.comboBoxProduct.currentText()
        result = self.db.get_product_price(product)
        if result["success"]:
            print(result)
            self.ui.doubleSpinBoxPrice.setValue(result["data"])
        else:
            return


if __name__ == '__main__':
    import sys
    app = QtWidgets.QApplication(sys.argv)

    dialog = VenteGros()
    dialog.show()
    sys.exit(app.exec_())
