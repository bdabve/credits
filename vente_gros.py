#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# ----------------------------------------------------------------------------
import datetime
from PyQt5 import QtWidgets, QtCore
from gui.h_vente_gros import Ui_Dialog
import utils


class VenteGros(QtWidgets.QDialog):
    def __init__(self, db_handler, logger):
        super().__init__()
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)
        self.db = db_handler
        self.logger = logger

        # date and number
        date = datetime.date.today().strftime("%Y-%m-%d")
        self.ui.dateEditFactDate.setDate(QtCore.QDate.fromString(date, "yyyy-MM-dd"))

        # populate products comboBox
        result = self.db.get_products_sku()
        if result["success"]:
            products = result["data"]
            utils.populate_comboBox(self.ui.comboBoxProduct, products)
        else:
            print("Error fetching products:", result["error"])

        # SIGNALS AND CALLBACKS
        # ---------------------
        # populate price from db
        self.ui.comboBoxProduct.currentIndexChanged.connect(self.get_product_price)
        # Add product
        self.ui.buttonAddProduct.clicked.connect(self.add_product_tableWidget)
        # save invoice
        self.ui.buttonSaveInvoice.clicked.connect(self.save_invoice)
        # get invoice number from database
        result = self.db.get_next_invoice_number()
        if result["success"]:
            next_invoice_number = result["invoice_number"]
            self.ui.lineEditFactNumber.setText(str(next_invoice_number))
        self.get_product_price()

    def get_product_price(self):
        """
        GET PRODUCT PRICE
        This work with 'combooBox.currentIndexChanged' signal
        get the product price to display in QDoubleSpinBox Price
        """
        self.ui.lineEditQte.setText("1")
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
        remise = self.ui.doubleSpinBoxRemise.value()        # %
        remise_calc = total * (remise / 100)
        total_ttc = total - remise_calc
        self.insert_product_tableWidget(sku, qte, price, total, remise, remise_calc, total_ttc)
        self.logger.debug(f"Adding the product to table widget SKU({sku}) - QTE({qte}) - PRICE({price}) - REMISE({remise})")

    def insert_product_tableWidget(self, sku, qte, price, total, remise, remise_calc, total_ttc):
        table = self.ui.tableWidgetProducts
        headers = [
            "SKU", "Qte", "Prix", "Total", "%", "Remise", "Total TTC"
        ]
        table.setColumnCount(len(headers))
        table.setHorizontalHeaderLabels(headers)

        row_position = table.rowCount()
        table.insertRow(row_position)
        table.setItem(row_position, 0, QtWidgets.QTableWidgetItem(sku))
        table.setItem(row_position, 1, QtWidgets.QTableWidgetItem(str(qte)))
        table.setItem(row_position, 2, QtWidgets.QTableWidgetItem(str(price)))
        table.setItem(row_position, 3, QtWidgets.QTableWidgetItem(str(total)))
        table.setItem(row_position, 4, QtWidgets.QTableWidgetItem(str(remise)))
        table.setItem(row_position, 5, QtWidgets.QTableWidgetItem(str(round(remise_calc, 2))))
        table.setItem(row_position, 6, QtWidgets.QTableWidgetItem(str(total_ttc)))

        self.update_totals_labels()

    def update_totals_labels(self):
        table = self.ui.tableWidgetProducts
        total_ht = 0
        total_remise = 0
        total_ttc = 0
        for row in range(table.rowCount()):
            total_ht += float(table.item(row, 3).text())
            total_remise += float(table.item(row, 5).text())
            total_ttc += float(table.item(row, 6).text())
        self.ui.TotalGeneral.setText(f"{round(total_ht, 2)}")
        self.ui.TotalGeneralRemise.setText(f"{round(total_remise, 2)}")
        self.ui.TotalGeneralTTC.setText(f"{round(total_ttc, 2)}")

    def save_invoice(self):
        self.logger.debug("Saving invoice into database")
        self.logger.debug("Invoice details:")

        table = self.ui.tableWidgetProducts
        products = []
        for row in range(table.rowCount()):
            product = {
                "sku": table.item(row, 0).text(),
                "qte": table.item(row, 1).text(),
                "price": table.item(row, 2).text(),
                "total": table.item(row, 3).text(),
                "remise_percent": table.item(row, 4).text(),
                "remise": table.item(row, 5).text(),
                "total_ttc": table.item(row, 6).text()
            }
            products.append(product)
            self.logger.debug(f"Product {row + 1}: {product}")

        fact_date = self.ui.dateEditFactDate.date().toPyDate()
        fact_number = self.ui.lineEditFactNumber.text()
        self.logger.debug(f"Facutre Number({fact_number}), Facture date({fact_date})")
        total_ht = sum(float(product["total"]) for product in products)
        total_remise = sum(float(product["remise"]) for product in products)
        total_ttc = sum(float(product["total_ttc"]) for product in products)
        self.logger.debug(f"Total HT: {total_ht}, Total Remise: {total_remise}, Total TTC: {total_ttc}\n{products}")

        result = self.db.save_invoice(fact_date, fact_number, total_ht, total_remise, total_ttc, products)
        self.logger.info(f"Invoice saved with result: {result}")
        if not result["success"]:
            self.ui.labelErros.setText(result["message"])
        else:
            self.ui.labelErros.setText(f"Facture ({result['invoice_id']}) enregistrée avec succès.")
            self.accept()


if __name__ == '__main__':
    import sys
    import db_handler
    from logger import logger

    app = QtWidgets.QApplication(sys.argv)
    dialog = VenteGros(db_handler, logger)
    dialog.show()
    sys.exit(app.exec_())
