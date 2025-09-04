#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# author        : el3arbi bdabve@gmail.com
# created       :
# desc          :
# ----------------------------------------------------------------------------
from datetime import datetime
from PyQt5 import QtWidgets, QtCore         # , QtGui
from gui.h_confirm_dialog import Ui_Dialog
import qtawesome as qta
import decimal

# ---- Global Var ---- #
NEW_COLOR = "#1dd1a1"
# NEW_COLOR = "#228447"
SAVE_COLOR = '#17c0eb'
BLUE_COLOR = '#4074a3'
TRASH_COLOR = '#f77861'
EDIT_COLOR = '#FF6600'
WHITE_COLOR = "#FFFFFF"
ICON_COLOR = "#ececec"
SKYPE_COLOR = "#00AFF0"

Error_COLOR = "#f77861"
Success_COLOR = "#44e37b"

# Icons
EMPLOYES_HEADERS = ['ID', 'Nom', 'Phone', 'P. Travaille', 'Salaire', 'Date Embauche', 'Observation']
OPERATIONS_HEADERS = ['ID', 'Date', "Operation", 'Employé', 'Montant', 'Motif']
OPERATIONS_SUM_HEADERS = ["Employé", "T. Prime", "T. Retenu", "T. Avance"]

CLIENTS_HEADERS = ["ID", "Nom", "Crédit", "Telephone", "Commune", "Observation"]
CREDITS_HEADERS = ['ID', 'Date', 'Client', 'Motif', 'Montant Total', 'Versement', 'Reste', 'Statut']

CHARGE_HEADERS = ["ID", "Date", "Effectué par", "Montant", "Motif"]


def format_money(value) -> str:
    """
    Format a number as money with comma as thousands separator and two decimals.
    Example: 12000 → '12,000.00'
    """
    try:
        # return "{:,.2f}".format(float(value))     # easy way
        # Frensh style with space
        value = float(value)
        parts = "{:,.2f}".format(value).split('.')
        integer_part = parts[0].replace(',', ' ')  # Replace comma with space
        decimal_part = parts[1]
        return f"{integer_part},{decimal_part}"
    except (ValueError, TypeError):
        return str(value)


def format_to_decimal(value):
    """
    Convert a string value to a Decimal, replacing spaces and commas.
    """
    # print(value)
    try:
        # Replace spaces and commas, then convert to Decimal
        value = value.replace(' ', '').replace(',', '.')
        return {'success': True, 'value': decimal.Decimal(value)}
    except (ValueError, TypeError, decimal.InvalidOperation):
        return {'success': False, 'error': 'Entrez un nombre valide.'}


def is_date(value: str, fmt="%Y-%m-%d") -> bool:
    try:
        datetime.strptime(value, fmt)
        return True
    except ValueError:
        return False


# ==================
# == UI -- Functions
# ==================
def main_icons_callbacks(root):
    # credit_icon = qta.icon('mdi6.cash', color=NEW_COLOR).themeSearchPaths
    # root.ui.buttonCreditPage.setStyleSheet(f"background-image: {credit_icon}")
    PLUS_ICON = qta.icon('ph.plus', color=NEW_COLOR)
    CASH_PLUS_ICON = qta.icon('mdi6.cash-plus', color=NEW_COLOR)
    SAVE_ICON = qta.icon('mdi.content-save', color=BLUE_COLOR)
    TRASH_ICON = qta.icon('msc.trashcan', color=TRASH_COLOR)
    REFRESH_ICON = qta.icon("mdi6.refresh", color=WHITE_COLOR)
    EDIT_ICON = qta.icon('ph.pencil-line-light', color=EDIT_COLOR)
    LIST_ICON = qta.icon('ph.list', color=WHITE_COLOR)

    # Create the Plus menu
    create_menu(
        root,
        root.ui.plusButtonShurtcut,
        "ph.plus",  # main button icon (QtAwesome)
        [
            ("Client", lambda: root.ui_create_persone('client'), "ph.plus"),
            ("Crédit", root.ui_create_credit, "ph.plus"),
            ("Employée", lambda: root.ui_create_persone('employee'), "ph.plus"),
            ("Charge", root.ui_create_charge, "ph.plus"),
        ],
        with_icons=True
    )

    buttons = [
        # --- MENUS
        # (root.ui.toggleMenuButton, False, lambda: root.toggle_menu(from_btn=True)),
        (root.ui.toggleMenuButton, qta.icon("ri.menu-fold-fill", color=WHITE_COLOR), root.on_toggle_menu),

        # TEST:
        (root.ui.extraCloseColumnBtn, False, lambda: root.toggle_left_box(close=True)),

        # -- Close, Maximize, Minimize
        (root.ui.closeAppBtn, False, root.close),  # Close the application
        (root.ui.minimizeAppBtn, False, root.showMinimized),  # Minimize the application
        (root.ui.maximizeRestoreAppBtn, False, root.toggle_maximize_restore),  # Maximize/Restore the application

        # -- Close Messages Frame
        (root.ui.buttonCloseMsgsFrame, False, lambda: root.close_msgs_frame(close=True)),
        # ===============================================================================

        # == Credit Page ==
        (
            root.ui.buttonCreditPage,
            qta.icon('mdi6.cash', color=NEW_COLOR),
            lambda: root.goto_page('credit')
        ),
        (root.ui.buttonRefreshCreditTable, REFRESH_ICON, root.refresh_credit_table),
        (
            # versement for a specific credit
            root.ui.buttonCreditVersement,
            qta.icon('fa6s.money-check-dollar', color=NEW_COLOR),
            root.credit_list_versement
        ),
        # == New Credit
        (root.ui.buttonNewCredit, CASH_PLUS_ICON, root.ui_create_credit),
        (root.ui.buttonSaveCredit, SAVE_ICON, root.save_new_credit),
        # == Credit Actions Edit/Versement/Delete
        # (root.ui.buttonEditCredit, EDIT_ICON, root.edit_credit),
        (root.ui.buttonDeleteCredit, TRASH_ICON, root.delete_credit),
        # ============================================================================================
        # == Versement Page ==
        # ====================
        (root.ui.buttonCreditAddVersement, qta.icon('fa6s.hand-holding-dollar', color=NEW_COLOR), root.ui_add_versement),
        (root.ui.buttonSaveVersement, SAVE_ICON, root.save_new_versement),
        (root.ui.buttonRegleCredit, qta.icon('mdi6.cash-check', color=NEW_COLOR), root.regle_credit),
        (root.ui.buttonDeleteVersement, TRASH_ICON, root.delete_versement),
        # ==================================================================================================
        # == Clients Page ==
        # ==================
        (root.ui.buttonClientsPage, qta.icon('ph.user', color=NEW_COLOR), lambda: root.goto_page('client')),
        (root.ui.buttonNewClient, PLUS_ICON, lambda: root.ui_create_persone('client')),
        (root.ui.buttonRefreshClientsTable, REFRESH_ICON, lambda: root.display_clients(rows=None)),
        (root.ui.buttonClientNewCredit, CASH_PLUS_ICON, lambda: root.ui_create_credit(client=True)),
        (root.ui.buttonClientCreditList, LIST_ICON, root.client_credit_list),
        (root.ui.buttonDeleteClient, TRASH_ICON, root.delete_client),
        # ================================================================================================
        # == Employes Page ==
        # ==================
        (root.ui.buttonEmployesPage, qta.icon('mdi.account-hard-hat', color=NEW_COLOR), lambda: root.goto_page('employe')),
        (root.ui.buttonNewEmploye, PLUS_ICON, lambda: root.ui_create_persone('employe')),
        (root.ui.buttonRefreshEmpolyeTable, REFRESH_ICON, lambda: root.display_employes(rows=None)),
        # button save new both (EMPLOYE & CLIENTS)
        (root.ui.buttonSaveNewPerson, SAVE_ICON, root.save_new_persone),
        (root.ui.buttonDeleteEmploye, TRASH_ICON, root.delete_employe),

        # == Accompte Employee ==
        (
            root.ui.buttonAccomptePage,
            qta.icon('fa6s.sack-dollar', color=NEW_COLOR),
            lambda: root.goto_page('operations', from_btn=True)
        ),
        (root.ui.buttonEmployeNewAvance, CASH_PLUS_ICON, lambda: root.ui_employe_opration('avance')),
        (root.ui.buttonEmployeNewPrime, CASH_PLUS_ICON, lambda: root.ui_employe_opration('prime')),
        (
            root.ui.buttonEmployeNewRetenu,
            qta.icon('mdi6.cash-minus', color=TRASH_COLOR),
            lambda: root.ui_employe_opration('retenu')
        ),
        (
            root.ui.buttonCalculateSalaire,
            qta.icon('mdi.calculator-variant', color=WHITE_COLOR),
            lambda: root.calculate_salaire(from_btn=True)
        ),

        # Save Operation for Employees
        (root.ui.buttonEmployeSaveOperation, SAVE_ICON, root.save_new_operation),
        # refresh to all
        (
            root.ui.buttonRefreshAccompteTable,
            REFRESH_ICON,
            lambda: root.display_accomptes(rows=None, headers_type="all")
        ),
        (root.ui.buttonDeleteAccompte, TRASH_ICON, root.delete_accompte),
        # ==================================================================================================
        # == Charge Page ==
        # ==================
        (
            root.ui.buttonChargePage, 
            qta.icon('mdi6.cash-minus', color=EDIT_COLOR), 
            lambda: root.goto_page('charge', from_btn=True)
        ),
        (root.ui.buttonRefreshChargeTable, REFRESH_ICON, lambda: root.display_charge(rows=None, month_text=None)),
        (root.ui.buttonNewCharge, PLUS_ICON, root.ui_create_charge),
        (root.ui.buttonSaveCharge, SAVE_ICON, root.insert_new_charge),
        (root.ui.buttonDeleteCharge, TRASH_ICON, root.delete_charge),
    ]
    for button, icon, callback in buttons:
        if icon: button.setIcon(icon)
        if callback: button.clicked.connect(callback)

    # == Just Icons for Buttons ==
    root.ui.buttonIconSumPrime.setIcon(qta.icon('fa5s.comment-dollar', color=WHITE_COLOR))
    root.ui.buttonIconSumAvance.setIcon(qta.icon('fa5s.comment-medical', color=WHITE_COLOR))
    root.ui.buttonIconSumRetenu.setIcon(qta.icon('fa5s.dollar-sign', color=WHITE_COLOR))
    root.ui.extraIconPlus.setIcon(qta.icon('ph.plus', color=SKYPE_COLOR))

    # =============================
    # == QTableWidget Signals
    # ==============================
    # Enable/Disable buttons based on selection
    # Map each table widget to its page key
    tables = [
        (root.ui.clientsTableWidget, "client"),
        (root.ui.employesTableWidget, "employe"),
        (root.ui.creditTableWidget, "credit"),
        (root.ui.versementTableWidget, "payment"),
        (root.ui.accompteTableWidget, "operations"),
        (root.ui.chargeTableWidget, "charge"),
    ]

    # Connect signals dynamically
    for table, page in tables:
        table.itemSelectionChanged.connect(lambda p=page: root.enable_buttons(p))

    # Commit edits when editing is finished
    table_edits = [
        (root.ui.employesTableWidget, root.edit_employe),
        (root.ui.accompteTableWidget, root.edit_accompte),
        (root.ui.clientsTableWidget, root.edit_client),
        (root.ui.creditTableWidget, root.edit_credit),
        (root.ui.chargeTableWidget, root.edit_charge),
    ]
    for table, callback in table_edits:
        table.editingFinished.connect(callback)

    # == Context Menus for Tables ==
    # == Employee Menu
    employe_table_actions = [
        (
            'L. Accompte',
            qta.icon("fa6s.money-check-dollar", color=NEW_COLOR),
            lambda: root.accompte_by_employee()
        ),
        (
            'Calculer Salaire',
            qta.icon('mdi.calculator-variant', color=WHITE_COLOR),
            lambda: root.calculate_salaire(from_btn=False)
        ),
        ('separator', None, None),
        ('Supprimer', qta.icon('msc.trashcan', color=TRASH_COLOR), root.delete_employe),
    ]
    setup_table_context_menu(root.ui.employesTableWidget, employe_table_actions)

    # == Clients Menu
    client_table_actions = [
        ('N. Crédit', CASH_PLUS_ICON, lambda: root.ui_create_credit(client=True)),
        ('L. Crédits', LIST_ICON, root.client_credit_list),
        ('separator', None, None),
        ('Supprimer', TRASH_ICON, root.delete_client),
    ]
    setup_table_context_menu(root.ui.clientsTableWidget, client_table_actions)

    # == Crédits Menu    
    credit_table_actions = [
        ('A. Versement', qta.icon('fa6s.hand-holding-dollar', color=NEW_COLOR), root.ui_add_versement),
        ('L. Versements', qta.icon('fa6s.money-check-dollar', color=NEW_COLOR), root.credit_list_versement),
        ('Régler', qta.icon('mdi6.cash-check', color=NEW_COLOR), root.regle_credit),
        ('separator', None, None),
        ('Supprimer', TRASH_ICON, root.delete_credit),
    ]
    setup_table_context_menu(root.ui.creditTableWidget, credit_table_actions)

    # Charge Menu
    charge_table_actions = [
        ('Modifier', EDIT_ICON, lambda: root.ui_create_charge(edit=True)),
        ('Supprimer', qta.icon('msc.trashcan', color=TRASH_COLOR), root.delete_charge),
    ]
    setup_table_context_menu(root.ui.chargeTableWidget, charge_table_actions)

    # ============================== 
    # == ComboBox Signals
    # ==============================
    # QComboBox for Credit, Salaire, Charge
    cbBoxes = [
        (root.ui.cbBoxCreditByStatus, root.filter_credit_by_status),
        (root.ui.cbBoxSalaireEmpMonth, lambda: root.calculate_salaire(from_btn=False)),
        (root.ui.cbBoxChargeByMonth, lambda: root.filter_charge()),
    ]
    for cbBox, callback in cbBoxes:
        cbBox.currentIndexChanged.connect(callback)
    
    # QComboBox for Accomptes
    for cbBox in (
            root.ui.cbBoxEmployeOperationByName,
            root.ui.cbBoxEmployeOperationByType,
            root.ui.cbBoxEmployeOperationByDate
    ):
        cbBox.currentIndexChanged.connect(root.filter_accomptes)

    # ================================ 
    # == LineEdit Signals
    # ================================
    # QLineEdit for Search
    lineEdits = [
        (root.ui.editSearchCredit, root.filter_credits),
        (root.ui.editSearchClients, root.filter_clients),
        (root.ui.editSearchEmploye, root.filter_employe),
        (root.ui.editSearchCharge, root.filter_charge),
    ]
    for edit, callback in lineEdits:
        edit.textChanged.connect(callback)
        edit.returnPressed.connect(callback)


def pagebuttons_stats(root):
    """
    Update page button states based on the current page.
    """
    ui = root.ui
    current_page = ui.stackedWidget.currentIndex()
    ui.buttonClientsPage.setChecked(current_page == 0)
    ui.buttonCreditPage.setChecked(current_page == 1)
    ui.buttonEmployesPage.setChecked(current_page == 2)
    ui.buttonAccomptePage.setChecked(current_page == 3)
    ui.buttonChargePage.setChecked(current_page == 4)


def clear_inputs(inputs: list) -> None:
    """
    This function clear inputs
    """
    for inp in inputs:
        inp.clear()


# -- Table Widget Functions
def populate_table_widget(table: QtWidgets.QTableWidget, rows: list, headers: list) -> None:
    """
    Populate a QTableWidget with rows and headers.

    :param table: The QTableWidget instance.
    :param rows: A list of rows where each row is a list or tuple of values.
    :param headers: A list of column headers.
    """
    table.clear()
    table.setSortingEnabled(False)
    table.setColumnCount(len(headers))
    table.setRowCount(len(rows))
    table.setHorizontalHeaderLabels(headers)

    # These columns will be formatted as money
    money_headers = {'Salaire', 'Crédit', 'Montant Total', 'Versement', 'Reste', 'Montant'}
    for row_idx, row_data in enumerate(rows):
        for col_idx, value in enumerate(row_data):
            header = headers[col_idx].strip()
            if isinstance(value, (int, float)) and header in money_headers:
                text = format_money(value)
            else:
                text = str(value)
            item = QtWidgets.QTableWidgetItem(str(text))
            item.setTextAlignment(QtCore.Qt.AlignCenter)
            table.setItem(row_idx, col_idx, item)

    table.horizontalHeader().setStretchLastSection(True)
    # table.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.ResizeToContents)
    table.setSortingEnabled(True)


def table_has_selection(table: QtWidgets.QTableWidget) -> bool:
    """
    Check if table has a selected rows
    :table: table widget name
    :return: True or False
    """
    if len(table.selectionModel().selectedRows()) > 0: return True
    else: return False


def get_column_value(table: QtWidgets.QTableWidget, row: int, column: int) -> str:
    """
    Get the value from a specific column of the selected row in a QTableWidget.

    :param table: The QTableWidget instance.
    :param column: The column index to retrieve the value from.
    :return: The value as a string.
    """
    return table.item(row, column).text()


def table_multi_selection(table: QtWidgets.QTableWidget) -> list:
    """
    This function return column(0) for a selection
    :table: QTableWidget
    :return: a list of ids.
    """
    selected_rows = set(index.row() for index in table.selectedIndexes())   # return index of selected row
    ids = list()
    if len(selected_rows) > 0:
        for row in selected_rows:
            item_id = table.item(row, 0).text()
            ids.append(item_id)
    return ids


def set_table_column_sizes(table_widget, *sizes):
    """
    Set the width of each column in a QTableWidget.

    Args:
        table_widget (QTableWidget): The table widget to modify.
        *sizes (int): Variable number of column widths. Each value sets the width for the corresponding column.
    """
    for col, size in enumerate(sizes):
        table_widget.setColumnWidth(col, size)


def setup_table_context_menu(table_widget: QtWidgets.QTableWidget, actions: list):
    """
    Adds a right-click context menu to the provided QTableWidget.
    :param table_widget: The QTableWidget instance.
    """
    table_widget.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
    table_widget.customContextMenuRequested.connect(
        lambda pos: show_table_context_menu(table_widget, actions, pos)
    )


def show_table_context_menu(table_widget: QtWidgets.QTableWidget, actions: list, pos: QtCore.QPoint):
    """
    Display a context menu at the given position.

    :param table_widget: The QTableWidget instance.
    :param pos: The position of the right-click.
    """
    index = table_widget.indexAt(pos)
    if not index.isValid():
        return

    menu = QtWidgets.QMenu(table_widget)
    for label, icon, callback in actions:
        if label == 'separator':
            menu.addSeparator()
            continue
        action = QtWidgets.QAction(icon, label, table_widget) if icon else QtWidgets.QAction(label, table_widget)
        action.triggered.connect(callback)
        menu.addAction(action)

    menu.exec_(table_widget.viewport().mapToGlobal(pos))


# == QComboBox
def populate_comboBox(combobox: QtWidgets.QComboBox, items: list):
    """
    Populate a QComboBox with a list of items.

    :param combobox: The QComboBox instance.
    :param items: A list of strings to populate the combobox.
    """
    combobox.blockSignals(True)
    combobox.clear()
    combobox.addItems(items)
    combobox.blockSignals(False)


def create_menu(root, menu_button, icon_name, actions, with_icons=False):
    """
    Create and attach a menu to a QPushButton.

    :param root: Parent widget.
    :param menu_button: QPushButton to attach the menu to.
    :param icon_name: Name of the icon to set on the button (QtAwesome).
    :param actions: List of tuples:
                    - (label, callback) if with_icons=False
                    - (label, callback, icon_path) if with_icons=True
    :param with_icons: Whether actions include icons.
    """
    # Set main button icon
    menu_button.setIcon(qta.icon(icon_name, color=NEW_COLOR))

    # Create the menu
    menu = QtWidgets.QMenu(root)

    for action in actions:
        if with_icons:
            label, callback, icon_path = action
            act = menu.addAction(qta.icon(icon_name, color=NEW_COLOR), label)
        else:
            label, callback = action
            act = menu.addAction(label)

        act.triggered.connect(callback)

    # Attach menu to button
    menu_button.setMenu(menu)


class ConfirmDialog(QtWidgets.QDialog):
    def __init__(self, title):
        super().__init__()
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)

        # Remove title bar
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_TranslucentBackground)
        self.ui.labelTitle.mouseMoveEvent = self.move_window  # to move window from the upBar

        self.ui.labelMessage.setText(title)
        self.ui.buttonConfirm.clicked.connect(self.accept)
        self.ui.buttonCancel.clicked.connect(self.reject)

    # -- Window UPBAR Controls --
    def mousePressEvent(self, event):
        self.clickPosition = event.globalPos()

    def move_window(self, e):
        """Move the window from upBar"""
        if not self.isMaximized():
            if e.buttons() == QtCore.Qt.LeftButton:
                self.move(self.pos() + e.globalPos() - self.clickPosition)
                self.clickPosition = e.globalPos()
                e.accept()


if __name__ == '__main__':
    import sys
    app = QtWidgets.QApplication(sys.argv)

    dialog = ConfirmDialog("Confirm Action")
    dialog.show()
    sys.exit(app.exec_())
