#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#

import sys
from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtPrintSupport import QPrinter, QPrintDialog
import qtawesome as qta

import utils
from db_handler import Database
from gui.h_credit import Ui_MainWindow
from logger import logger
from datetime import datetime

TODAY = datetime.now()


class Credit(QtWidgets.QMainWindow):
    # #######################################
    # TODO
    # ====
    # - Add PDF Export for Salary Slip
    # - work with the charge page
    # - handle all the search functions
    # - handle edit for other function that need it
    # - Add more validations
    # ####################################################
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.setWindowIcon(QtGui.QIcon('./images/images/app_icon.png'))

        self.db = Database()
        self.CURRENT_MONTH = TODAY.strftime("%Y-%m")

        # Track menu state
        self.menu_expanded = True

        if sys.platform.startswith('win'):
            self.menu_expanded_width = 350
            self.left_box_width = 600
        else:
            self.menu_expanded_width = 220
            self.left_box_width = 400

        # Remove title bar
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_TranslucentBackground)
        self.ui.contentTopBg.mouseMoveEvent = self.move_window  # to move window from the upBar

        # Callback Functions
        utils.main_icons_callbacks(self)

        self.PAGES = {
            'client': {
                'title': 'List des Clients',
                'widget': lambda self: self.ui.ClientsPage,
                'action': lambda self: self.display_clients(),
                'buttons': lambda self: (
                    self.ui.clientsTableWidget,
                    (self.ui.buttonClientCreditList,
                     self.ui.buttonDeleteClient,
                     self.ui.buttonClientNewCredit)
                )
            },
            'employe': {
                'title': 'List des Employées',
                'widget': lambda self: self.ui.EmployesPage,
                'action': lambda self: self.display_employes(),
                'buttons': lambda self: (
                    self.ui.employesTableWidget,
                    (self.ui.buttonDeleteEmploye,
                     self.ui.buttonEmployeNewAvance,
                     self.ui.buttonEmployeNewPrime,
                     self.ui.buttonEmployeNewRetenu,
                     self.ui.buttonCalculateSalaire)
                )
            },
            'operations': {
                'title': 'Liste des Accomptes',
                'widget': lambda self: self.ui.EmployeOperationsPage,
                'action': lambda self: (
                    self.display_accomptes()
                ),
                'buttons': lambda self: (
                    self.ui.accompteTableWidget,
                    (self.ui.buttonDeleteAccompte,)
                )
            },
            'credit': {
                'title': 'List des Crédits',
                'widget': lambda self: self.ui.CreditPage,
                'action': lambda self: self.display_credits(),
                'buttons': lambda self: (
                    self.ui.creditTableWidget,
                    (self.ui.buttonDeleteCredit,
                     self.ui.buttonCreditVersement,
                     self.ui.buttonCreditAddVersement,
                     self.ui.buttonRegleCredit)
                )
            },
            'payment': {
                'title': 'List des Versements',
                'widget': lambda self: self.ui.versementTableWidget,
                'action': None,  # No display action
                'buttons': lambda self: (
                    self.ui.versementTableWidget,
                    (self.ui.buttonDeleteVersement,)
                )
            },
            'charge': {
                'title': 'List des Charges',
                'widget': lambda self: self.ui.ChargePage,
                'action': lambda self: self.display_charge(),
                'buttons': lambda self: (
                    self.ui.chargeTableWidget,
                    (self.ui.buttonDeleteCharge,)
                )

            }
        }

        self.init_ui()

    def init_ui(self):
        """
        Sets up the initial state of the user interface by toggling the menu,
        navigating to the default 'credit' page, displaying the current date,
        populating the employee account combo box, and maximizing the window.
        """
        self.on_toggle_menu()
        self.goto_page('credit')  # Default page
        self.ui.labelDate.setText(f"{TODAY.date()}")
        #
        self.showMaximized()

    # -- Window UPBAR Controls --
    def mousePressEvent(self, event):
        """
        Handles the mouse press event by storing the global position of the mouse click.

        Args:
            event (QMouseEvent): The mouse event containing information about the click.
        """
        self.clickPosition = event.globalPos()

    def move_window(self, e):
        """Move the window from upBar"""
        if not self.isMaximized():
            if e.buttons() == QtCore.Qt.LeftButton:
                self.move(self.pos() + e.globalPos() - self.clickPosition)
                self.clickPosition = e.globalPos()
                e.accept()

    def toggle_maximize_restore(self):
        icon = QtGui.QIcon()
        if self.isMaximized():
            icon.addPixmap(QtGui.QPixmap(":/icons/images/icons/icon_maximize.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
            self.ui.maximizeRestoreAppBtn.setIcon(icon)
            self.ui.maximizeRestoreAppBtn.setIconSize(QtCore.QSize(20, 20))
            self.showNormal()
        else:
            icon.addPixmap(QtGui.QPixmap(":/icons/images/icons/icon_restore.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
            self.ui.maximizeRestoreAppBtn.setIcon(icon)
            self.ui.maximizeRestoreAppBtn.setIconSize(QtCore.QSize(20, 20))
            self.showMaximized()

    # ===================================
    # -- Toggle Left Menu and Left Box ==
    # ===================================
    def on_toggle_menu(self):
        """
        Toggles the menu's expanded or collapsed state.
        Calls the `toggle_menu` method with the current state of `menu_expanded` to
        either collapse or expand the menu, then updates `menu_expanded` to reflect
        the new state.
        """

        self.toggle_menu(collapse=self.menu_expanded)
        self.menu_expanded = not self.menu_expanded

    def auto_close_menu(self):
        # Only close if currently expanded
        if self.menu_expanded:
            self.toggle_menu(collapse=True)
            self.menu_expanded = False

    def toggle_menu(self, collapse=False, from_btn=False):
        """
        This will animate the Client/Product badge up/down
        :frame: the frame to animate (product_badge | client_badge)
        :button: the button to change his icon
        """
        frame = self.ui.leftMenuBg
        width = frame.width()

        # If left frame is toggled then return
        if self.ui.extraLeftBox.width() > 0:
            return

        # expanded_width = 280  # Width when expanded
        collapsed_width = 70

        page_buttons = {
            self.ui.toggleMenuButton: 'Menu',
            self.ui.buttonClientsPage: '  Clients',
            self.ui.buttonEmployesPage: '  Employés',
            self.ui.buttonCreditPage: '  Crédits',
            self.ui.buttonAccomptePage: '  Les Accomptes',
            self.ui.buttonChargePage: '  Les Charges'

        }
        if collapse:
            # Close Menu
            new_width = collapsed_width
            # Remove text from button but keep icons
            self.ui.toggleMenuButton.setIcon(qta.icon('ri.menu-unfold-fill', color="#ffffff"))
            for button in page_buttons.keys():
                button.setText('')
        else:
            new_width = self.menu_expanded_width
            # Restore text to button
            self.ui.toggleMenuButton.setIcon(qta.icon('ri.menu-fold-fill', color="#ffffff"))
            for button, text in page_buttons.items():
                button.setText(text)

        self.anim_left_menu = QtCore.QPropertyAnimation(frame, b'minimumWidth')  # wont work without self
        self.anim_left_menu.setDuration(250)
        self.anim_left_menu.setStartValue(width)
        self.anim_left_menu.setEndValue(new_width)
        self.anim_left_menu.setEasingCurve(QtCore.QEasingCurve.InOutQuart)
        self.anim_left_menu.start()

    def toggle_left_box(self, close=False):
        """
        This will animate the Client/Product badge up/down
        :frame: the frame to animate (product_badge | client_badge)
        :button: the button to change his icon
        """
        frame = self.ui.extraLeftBox
        width = frame.width()
        new_width = 0 if close else self.left_box_width

        self.anim_extra_box = QtCore.QPropertyAnimation(frame, b'minimumWidth')  # wont work without self
        self.anim_extra_box.setDuration(250)
        self.anim_extra_box.setStartValue(width)
        self.anim_extra_box.setEndValue(new_width)
        self.anim_extra_box.setEasingCurve(QtCore.QEasingCurve.InOutQuart)
        self.anim_extra_box.start()

    def show_error_message(self, message, success=False):
        """
        Show an animated error or success message inside the frame.
        Auto-hide if success.

        Args:
            message (str): The message to display.
            success (bool): If True, color is green and auto-close after timeout.
        """
        label = self.ui.labelMsgs
        label.setText(message)
        close_button = self.ui.buttonCloseMsgsFrame

        btn_ssheet = 'background: transparent; border-radius: 0; border-top-right-radius: 5px; border-bottom-right-radius: 5px'
        label_ssheet = 'background: transparent; padding: 5px 7px; border-top-left-radius: 5px; border-bottom-left-radius: 5px; '
        frame_ssheet = 'border-radius: 5px 7px; '
        if success:
            # Green for success
            frame_ssheet += 'background-color: rgba(60, 184, 127, 47);'
            label_ssheet += 'color: #44e37b'
            close_button.setIcon(qta.icon('ph.x-light', color=utils.Success_COLOR))
        else:
            frame_ssheet += 'background: #3b3230;'
            label_ssheet += 'color: #f77861'
            close_button.setIcon(qta.icon('ph.x-light', color=utils.Error_COLOR))

        # Apply StyleSheets
        self.ui.frameMsgs.setStyleSheet(frame_ssheet)
        label.setStyleSheet(label_ssheet)
        close_button.setStyleSheet(btn_ssheet)

        # Start timer to auto-close after 3 seconds
        self.auto_close_timer = QtCore.QTimer()
        self.auto_close_timer.setSingleShot(True)
        self.auto_close_timer.timeout.connect(lambda: self.close_msgs_frame(close=True))
        self.auto_close_timer.start(3000)  # 3000 milliseconds = 3 seconds

        # Open the frame
        self.close_msgs_frame(close=False)

    def close_msgs_frame(self, close=True):
        """
        Animate the height of the QTextBrowser.
        :close: bool True to close; False to open
        """
        msgs_frame = self.ui.widgetMessages
        width = msgs_frame.maximumWidth()
        new_width = 0 if close else 900
        # Create the animation object
        self.close_msgs_animation = QtCore.QPropertyAnimation(msgs_frame, b"maximumWidth")
        self.close_msgs_animation.setDuration(250)  # Duration in milliseconds
        self.close_msgs_animation.setEasingCurve(QtCore.QEasingCurve.InOutQuart)
        self.close_msgs_animation.setStartValue(width)
        self.close_msgs_animation.setEndValue(new_width)

        # Start the animation
        self.close_msgs_animation.start()

    # ===============================
    # == Switch between Pages ==
    # == Enable or disable Buttons ==
    # ===============================
    def goto_page(self, page='client', title='', from_btn=True) -> None:
        """
        Navigates to a specified page within the application's UI.

        Args:
            page (str): The key identifying the page to navigate to. Defaults to 'client'.
            title (str): The title to display on the UI. If not provided, uses the page's default title.
            from_btn (bool): Indicates if the navigation was triggered by a button. If True, executes the page's associated action.

        Behavior:
            - Retrieves the page configuration from self.PAGES.
            - Updates the UI title with the provided or default page title.
            - Instantiates and displays the corresponding page widget.
            - Executes the page's action if triggered from a button.
            - Enables/disables navigation buttons based on the current page.
            - Updates page button statistics via utils.pagebuttons_stats.

        Returns:
            None

        """
        config = self.PAGES.get(page)
        if not config:
            return  # Invalid page name

        self.ui.titleRightInfo.setText(title or config['title'])
        st_page = config['widget'](self)

        if from_btn and callable(config.get('action')):
            config['action'](self)

        self.enable_buttons(page)
        self.ui.stackedWidget.setCurrentWidget(st_page)
        utils.pagebuttons_stats(self)

    def enable_buttons(self, page: str) -> None:
        """
        Enable or disable buttons for the current page based on the selection state of a table widget.
        Args:
            page (str): The name of the current page whose buttons should be enabled or disabled.
        Returns:
            None
        """
        config = self.PAGES.get(page)
        if not config or 'buttons' not in config:
            return

        table_widget, buttons = config['buttons'](self)
        has_selection = utils.table_has_selection(table_widget)
        for btn in buttons:
            btn.setEnabled(has_selection)

    def set_total_credits(self) -> None:
        """
        Updates the UI labels to display the total credits for all clients.

        Retrieves the total credit amount from the database, formats it as currency,
        and sets the text of the corresponding UI labels to show the total credits in DA.

        Returns:
            None
        """
        # Get the total credits by client type
        total_credit = self.db.get_total_credit()
        self.ui.labelTotalCredits.setText(f"Total Crédits: {utils.format_money(total_credit)} DA")
        self.ui.labelTotalCreditClients.setText(f"Total Crédits: {utils.format_money(total_credit)} DA")

    def setup_extraCenter_ui(self, title, page):
        """
        Set up the extra center stackedWidget UI.
        """
        self.ui.extraLabelTitle.setText(title)
        # self.ui.extraLabelTitle.setStyleSheet(f"color: {utils.SKYPE_COLOR};")
        self.toggle_left_box(close=False)
        self.auto_close_menu()
        self.ui.extraCenter.setCurrentWidget(page)

    def get_item_id(self, tableWidget):
        """
        This return the current selected row and column 0, item ID from tableWidget
        :tableWidget: the table widget to get item
        """
        if utils.table_has_selection(tableWidget):
            row = tableWidget.currentRow()
            item_id = utils.get_column_value(tableWidget, row, 0)
            return item_id

    # =======================
    # == Employe & Clients ==
    # =======================
    def display_employes(self, rows=None):
        """
        Display all personnes in the table widget.
        """
        if rows is None: rows = self.db.dump_employes()
        utils.populate_table_widget(self.ui.employesTableWidget, rows, utils.EMPLOYES_HEADERS)
        utils.set_table_column_sizes(self.ui.employesTableWidget, 80, 300, 120, 250, 190, 200)
        self.ui.labelEmployesCount.setText(f"Total: {len(rows)}")

    # == Create Employee | Clients ==
    def ui_create_persone(self, persone_type):
        """
        Sets up the user interface for creating a new person, either a client or an employee.

        Depending on the persone_type ('client' or 'employe'), this function:
            - Updates UI labels and placeholders to reflect the type of person being created.
            - Shows or hides relevant input fields for employee-specific information.
            - Clears and focuses the name input field.
            - Sets the default date for the date of employment field.
            - Updates the title label to indicate the creation of a new person.
            - Opens the left box and auto-closes the menu.
            - Switches the central widget to the Add Person page.

        Args:
            persone_type (str): The type of person to create ('client' or 'employe').
        """
        logger.info(f"Creating a new {persone_type}...")
        self.ui.labelNewPersonType.setText(persone_type)
        self.ui.labelNewPersonType.hide()

        # Remove and show lineEdits based on type( client | employe )
        employe_edits = [
            # self.ui.labelNewPersonJobText, # self.ui.editNewPersonJob,
            self.ui.labelNewPersonSalaire, self.ui.editNewPersonSalaire,
            self.ui.labelNewPersonDateEmbauche, self.ui.editNewPersonDateEmbauche
        ]
        # client_edits = [self.ui.labelNewPersonObs, self.ui.editNewPersonObs]

        # Clear the inputs and setFucus to name edit
        self.ui.editNewPersonName.setFocus()
        self.ui.editNewPersonDateEmbauche.setDate(TODAY)

        # Hide inused inputs
        if persone_type == 'client':
            # for edit in client_edits: edit.show()     # Clients
            for edit in employe_edits: edit.hide()      # Employe
            self.ui.labelNewPersonJobText.setText('Commune')
            self.ui.editNewPersonJob.setPlaceholderText('Commune')

        elif persone_type == 'employe':
            # for edit in client_edits: edit.hide()     # Clients
            for edit in employe_edits: edit.show()      # Employe
            self.ui.labelNewPersonJobText.setText('Poste')
            self.ui.editNewPersonJob.setPlaceholderText('Poste de Travaille')

        self.setup_extraCenter_ui(f"Nouveau {persone_type.title()}", self.ui.AddPersonePage)

    def save_new_persone(self):
        """
        Save the new persone to the database.
        """
        person_type = self.ui.labelNewPersonType.text()
        logger.info(f"Saving the new {person_type}...")

        # Get values from UI
        name = self.ui.editNewPersonName.text()
        phone = self.ui.editNewPersonPhone.text()
        job = self.ui.editNewPersonJob.text()
        salaire = self.ui.editNewPersonSalaire.value()
        date_embauche = self.ui.editNewPersonDateEmbauche.date().toPyDate()
        commune = self.ui.editNewPersonJob.text()        # FIXME This work with lineEditJob
        obs = self.ui.editNewPersonObs.toPlainText()

        logger.info(f"Saving new {person_type} with Values: ")
        if person_type == 'client':
            logger.debug(f"Name: {name}, Phone: {phone}, Observations: {obs}")
            result = self.db.insert_new_client(name, phone, commune, obs)
        else:
            logger.info(
                f"Name: {name}, Phone: {phone}, P. Travaille: {job}, Salaire: {salaire}, "
                f"Date Embauche: {date_embauche}"
            )
            result = self.db.insert_new_employe(name, job, phone, salaire, date_embauche, obs)

        logger.debug(result)
        if result['success']:
            self.show_error_message(f"{person_type.title()} ajouté avec succès.", success=True)
            self.toggle_left_box(close=True)
            self.goto_page(f"{person_type}", title='Clients')
            # Clear all edits
            edits_to_clear = [
                self.ui.editNewPersonName, self.ui.editNewPersonJob, self.ui.editNewPersonSalaire,
                self.ui.editNewPersonPhone, self.ui.editNewPersonObs
            ]
            for edit in edits_to_clear:
                edit.clear()
        else:
            self.show_error_message(f"Erreur: {result['error']}", success=False)

    def filter_employe(self):
        """
        Search Persones
        """
        search_word = self.ui.editSearchEmploye.text()
        if not search_word: return  # or show a message to the user that the search input is empty
        else: search_word = f"%{search_word}%"
        rows = self.db.search_employe(search_word)
        self.display_employes(rows)

    def edit_employe(self, row, col, text):
        """
        Edits an employee's information in the table and updates the database.

        Args:
            row (int): The row index of the employee in the table.
            col (int): The column index being edited.
            text (str): The new text value to set.

        Validates the date format if the edited column is the date column (col == 5).
        Displays an error message if the date format is invalid.
        Updates the employee information in the database and displays a success or error message based on the result.
        Refreshes the employee table display after editing.
        """
        emp_id = self.get_item_id(self.ui.employesTableWidget)
        logger.info(f"Edit Employe({emp_id}) at Row({row}), Column({col}), New Text({text})")
        if col == 5:    # verify date format
            if not utils.is_date(text):
                self.show_error_message("Date invalide. Utiliser le format YYYY-MM-DD.", success=False)
                self.display_employes()
                return
        # Database update
        result = self.db.update_employe(emp_id, col, text)
        if result['success']:
            self.show_error_message(result['message'], success=True)
            self.display_employes()
        else:
            self.show_error_message(f"Erreur: {result['error']}", success=False)

    def delete_employe(self):
        """
        Deletes one or multiple selected employees from the database after user confirmation.

        - Retrieves selected employee IDs from the employesTableWidget.
        - Shows an error message if no employee is selected.
        - Prompts the user for confirmation, displaying the employee name(s) in the dialog.
        - If confirmed, deletes the selected employee(s) from the 'employes' table.
        - Displays a success or error message based on the result.
        - Refreshes the employee list upon successful deletion.

        Returns:
            None
        """
        ids = utils.table_multi_selection(self.ui.employesTableWidget)
        if not ids:
            self.show_error_message("Aucun employé sélectionné.", success=False)
            return
        if len(ids) > 1:
            logger.debug(f'Delete Multitple IDS({ids})')
            title = f"Etes-vous sûr de vouloir supprimer la selection [{ids}] ?"
        else:
            logger.debug(f'Delete One ID({ids[0]})')
            employe = utils.get_column_value(
                self.ui.employesTableWidget,
                self.ui.employesTableWidget.currentRow(),
                1
            )
            logger.info(f"Deleting the selected employe: ID({ids[0]}), Name({employe})...")
            title = f"Etes-vous sûr de vouloir supprimer '{employe.upper()}' ?"

        dialog = utils.ConfirmDialog(title)
        if dialog.exec_() == QtWidgets.QDialog.Accepted:
            result = self.db.delete_item('employes', ids)
            logger.debug(f"Delete Employe: {result}")
            if result['success']:
                self.show_error_message("Employée supprimé avec succès.", success=True)
                self.display_employes()
            else:
                self.show_error_message(f"{result['error']}", success=False)

    # =================================================
    # == Employee Accompte ( Prime, Retenu, Avance) ==
    # ================================================
    def display_totals(self, month='Tous'):
        """
        Display the total sums of Prime, Retenu, and Avance for all employees.
        """
        sums = self.db.get_sums_operations(month)
        logger.info(f"Total Sums of accompte for month({month}): {sums}")
        self.ui.labelSumAvance.setText(f"{utils.format_money(sums.total_avance)} DA")
        self.ui.labelSumRetenu.setText(f"{utils.format_money(sums.total_retenu)} DA")
        self.ui.labelSumPrime.setText(f"{utils.format_money(sums.total_prime)} DA")

    def display_accomptes(self, rows=None, headers_type="all", **kwargs):
        """
        This function display the SUM of (Prime, Retenu, Avance) for all employees.
        :param rows: List of rows to display, if None it will fetch from the database.
        :param headers_type: Type of headers to display, "all" for all operations or "one" for one employe.
        """
        if rows is None:
            month = self.CURRENT_MONTH
            rows = self.db.dump_operations(month)
            self.display_totals(month)  # Display total sums of operations

        headers = utils.OPERATIONS_SUM_HEADERS if headers_type == "all" else utils.OPERATIONS_HEADERS
        # FIXME: fix this

        cbboxes = [
            self.ui.cbBoxEmployeOperationByName,
            self.ui.cbBoxEmployeOperationByType,
            self.ui.cbBoxEmployeOperationByDate
        ]
        # Block CBBoxes Signals
        for cbbox in cbboxes: cbbox.blockSignals(True)

        if headers_type == 'all':
            # setup the comboBoxes
            self.populate_cbBoxEmployeAccompte()
            self.ui.cbBoxEmployeOperationByName.setCurrentText('Tous')
            self.ui.cbBoxEmployeOperationByDate.setCurrentText('Tous')
            self.ui.cbBoxEmployeOperationByType.setCurrentText('Tous')
            self.ui.labelAccompteEdit.setText('False')  # Disable Edit or Delete
        elif headers_type == 'one':
            self.ui.cbBoxEmployeOperationByName.setCurrentText(kwargs.get("employee"))
            self.ui.cbBoxEmployeOperationByDate.setCurrentText(kwargs.get("month"))
            self.ui.labelAccompteEdit.setText('True')   # Enable Edit or Delete
        self.ui.labelAccompteEdit.hide()
        for cbbox in cbboxes: cbbox.blockSignals(False)     # Unblock signals

        # Display Result in QTableWidget
        utils.populate_table_widget(self.ui.accompteTableWidget, rows, headers)
        utils.set_table_column_sizes(self.ui.accompteTableWidget, 220, 170, 170, 170, 200)
        self.ui.labelAccompteCount.setText(f"Total: {len(rows)}")

    def filter_accomptes(self):
        """
        This Global function works with comboBoxes for date, and operationtype
        """

        employe = self.ui.cbBoxEmployeOperationByName.currentText()
        emp_id = self.db.get_item_id('employes', 'nom', employe)
        self.ui.labelAccompteEmpID.setText(str(emp_id)) if emp_id else self.ui.labelAccompteEmpID.setText('')
        self.ui.labelAccompteEmpID.hide()

        operation = self.ui.cbBoxEmployeOperationByType.currentText().lower()
        month_text = self.ui.cbBoxEmployeOperationByDate.currentText()
        month = f"{TODAY.year}-{month_text}" if month_text != 'Tous' else 'Tous'

        logger.info(f"Filter Operation: Operation({operation}), Month({month}), Employee({employe})")

        rows = self.db.filter_accomptes(employe, operation, month)

        # Display Result in QTableWidget
        self.display_totals(month_text)                     # Display total sums of operations
        self.display_accomptes(rows, headers_type="one")
        self.goto_page(page='operations', from_btn=False)

    def accompte_by_employee(self, emp_id=None, **kwargs):
        """
        This function will display operations by the selected employe.
        """
        if not emp_id:
            emp_id = self.get_item_id(self.ui.employesTableWidget)

            emp_name = utils.get_column_value(
                self.ui.employesTableWidget,
                self.ui.employesTableWidget.currentRow(),
                1
            )
            month = TODAY.strftime("%m")
        else:
            emp_name = self.db.get_item('employes', 'nom', emp_id)
            month = kwargs.get("month")

        logger.debug(f"Getting accompte for employe({emp_name} - {emp_id}), month({month})")

        # Here the date for displaying result
        # the month to display in ComboBox
        date = f"{self.CURRENT_MONTH}" if not month else f"{TODAY.strftime(f"%Y")}-{month}"
        rows = self.db.employee_accompts(emp_id, date)
        self.display_accomptes(rows, headers_type="one", employee=emp_name, month=month)
        self.goto_page(page='operations', from_btn=False)

    def populate_cbBoxEmployeAccompte(self):
        # Populate EmployeOperationByName ComboBox
        employes = self.db.get_names('employes')
        employes.insert(0, 'Tous')  # Add 'Tous' option for all employes
        utils.populate_comboBox(self.ui.cbBoxEmployeOperationByName, employes)

    def ui_employe_opration(self, operation):
        """"""
        employe_id = self.get_item_id(self.ui.employesTableWidget)
        employe_name = utils.get_column_value(self.ui.employesTableWidget, self.ui.employesTableWidget.currentRow(), 1)
        # operation_dict = {  # For Title
            # 'prime': f"Nouveau Prime pour {employe_name}",
            # 'retenu': "Nouveau Retenu pour {employe_name}",
            # 'avance': "Nouveau Avance pour {employe_name}"
        # }

        self.ui.labelEmployeOperationEmpID.setText(employe_id)
        self.ui.labelEmployeOperationEmpID.hide()

        self.ui.labelEmployeOperationType.setText(operation)    # Label Operation Type
        self.ui.labelEmployeOperationType.hide()

        self.ui.dateEditEmployeOperationDate.setDate(TODAY)

        title = f"{operation.title()} {employe_name}"
        self.setup_extraCenter_ui(title, self.ui.AddEmpOperationPage)

    def save_new_operation(self):
        """"""
        emp_opeartions = ['prime', 'retenu', 'avance']
        emp_id = self.ui.labelEmployeOperationEmpID.text()
        operation = self.ui.labelEmployeOperationType.text()
        date = self.ui.dateEditEmployeOperationDate.date().toPyDate()
        montant = self.ui.editEmployeOperationMontant.value()
        motif = self.ui.editEmployeOperationMotif.toPlainText()
        observation = ''    # FIXME: Not implemented yet

        # Some Chacking
        if montant <= 0:
            self.show_error_message('Entré un chiffre pour le Montant.', success=False)
            return
        if operation not in emp_opeartions:
            self.show_error_message(f"Operation {operation} n'existe pas.", success=False)
            return
        if not date:
            self.show_error_message('Entré une date.', success=False)
            return
        if not motif:
            self.show_error_message('Entré un Motif.', success=False)
            return

        logger.debug(
            f"Insert New({operation}) for ({emp_id}):"
            f"Date({date}), Montant({montant}), Motif({motif})"
        )
        result = self.db.insert_new_operation(emp_id, operation, montant, motif, date, observation)
        if result['success']:
            self.show_error_message(f"{operation.title()} ajouté avec succès.", success=True)
            self.toggle_left_box(close=True)
            self.goto_page("employe", title='Employée')
            # Clear all edits
            edits_to_clear = [
                self.ui.labelEmployeOperationEmpID, self.ui.labelEmployeOperationType,
                self.ui.dateEditEmployeOperationDate,
                self.ui.editEmployeOperationMontant, self.ui.editEmployeOperationMotif
            ]
            utils.clear_inputs(edits_to_clear)
        else:
            self.show_error_message(f"Erreur: {result['error']}", success=False)
            # close

    def calculate_salaire(self, from_btn=False):
        employe_id = self.get_item_id(self.ui.employesTableWidget)
        employe = utils.get_column_value(self.ui.employesTableWidget, self.ui.employesTableWidget.currentRow(), 1)
        logger.info(f"Calculating salary for Employe({employe_id})...")

        # setup Date
        if from_btn:
            month = TODAY.strftime('%m')
            # Set current month in the comboBox
            self.ui.cbBoxSalaireEmpMonth.blockSignals(True)
            self.ui.cbBoxSalaireEmpMonth.setCurrentText(month)
            self.ui.cbBoxSalaireEmpMonth.blockSignals(False)
        else:
            month = self.ui.cbBoxSalaireEmpMonth.currentText()

        date = f"{TODAY.strftime('%Y')}-{month}"  # Get month from comboBox
        # Get db result
        result = self.db.calculate_salaire_mensuel(date, employe_id)

        if result:
            # Display result
            self.ui.labelSalaireEmpName.setText(employe.upper())
            self.ui.labelSalaireEmpSalaire.setText(utils.format_money(result['salaire_base']))
            self.ui.labelSalaireEmpPrime.setText(utils.format_money(result['total_prime']))
            self.ui.labelSalaireEmpAvance.setText(utils.format_money(result['total_avance']))
            self.ui.labelSalaireEmpRetenu.setText(utils.format_money(result['total_retenue']))
            self.ui.labelSalaireEmpTotal.setText(utils.format_money(result['salaire_final']))
            self.setup_extraCenter_ui('Salaire', self.ui.salairePage)
            # html = self.generate_payslip_html(employe.upper(), date,
            #                                 # result['salaire_base'], result['total_prime'],
            #                                 # result['total_retenue'], result['total_avance'],
            #                                 # result['salaire_final'])
            # self.ui.textBrowserSalary.setHtml(html)
        else:
            self.show_error_message(f"Aucun salaire trouvé pour l'employé {employe} en {month}.", success=False)

    def edit_accompte(self, row, col, text):
        """
        Edits an accompte entry in the table widget and updates the database.

        Parameters:
            row (int): The row index of the edited item.
            col (int): The column index of the edited item.
            text (str): The new text value to be set.

        Workflow:
            - Checks if editing is enabled via the UI label.
            - Validates the input based on the column:
                - For date column (col == 1), verifies date format (YYYY-MM-DD).
                - For amount column (col == 4), converts and validates decimal format.
            - Updates the accompte entry in the database.
            - Displays success or error messages based on the operation result.
            - Refreshes the accompte display for the employee and selected month.

        Returns:
            None
        """
        edit = self.ui.labelAccompteEdit.text()
        date_str = utils.get_column_value(self.ui.accompteTableWidget, row, 1)
        # date_str is in 'dd-mm-yyyy' format, extract month
        try:
            month = date_str.split('-')[1]
        except Exception:
            month = ''

        if edit != 'True':
            logger.debug('Edit or Delete is disabled.')
            self.show_error_message("Modification non autorisée.", success=False)
            self.display_accomptes()
            return

        emp_id = self.ui.labelAccompteEmpID.text()
        accompte_id = self.get_item_id(self.ui.accompteTableWidget)
        logger.info(f"Edit Accompte({accompte_id}) at Row({row}), Column({col}), New Text({text})")
        # Validating
        if col == 1:    # verify date format
            if not utils.is_date(text):
                self.show_error_message("Date invalide. Utiliser le format YYYY-MM-DD.", success=False)
                self.accompte_by_employee(emp_id)
                return
        elif col == 4:
            # handle montant converstion to decimal
            text = utils.format_to_decimal(text)
            if not text['success']:
                self.show_error_message(f"Erreur: {text['error']}", success=False)
                self.display_credits()      # refresh tablhu
                return
            else:
                text = text['value']

        # Database Handling
        result = self.db.update_accompte(accompte_id, col, text)
        if result['success']:
            self.show_error_message(result['message'], success=True)
        else:
            self.show_error_message(f"Erreur: {result['error']}", success=False)

        # refresh table
        self.accompte_by_employee(emp_id, month=month)

    # =========================================
    # NOTE:  Not implemented yet
    def generate_payslip_html(self, nom, mois, base, prime, retenue, avance, net):
        return f"""
        <html>
        <head>
            <style>
                body {{ font-family: 'Arial'; font-size: 12pt; }}
                h2 {{ text-align: center; }}
                table {{ width: 100%; border-collapse: collapse; margin-top: 20px; }}
                td, th {{ padding: 8px; border: 1px solid black; }}
            </style>
        </head>
        <body>
            <h2>Fiche de Paie - {mois}</h2>
            <p><strong>Employé :</strong> {nom}</p>
            <table>
                <tr><th>Base</th><td>{base:.2f}</td></tr>
                <tr><th>Prime</th><td>{prime:.2f}</td></tr>
                <tr><th>Retenue</th><td>{retenue:.2f}</td></tr>
                <tr><th>Avance</th><td>{avance:.2f}</td></tr>
                <tr><th><strong>Net à Payer</strong></th><td><strong>{net:.2f}</strong></td></tr>
            </table>
        </body>
        </html>
        """

    def print_payslip(self, nom, mois, base, prime, retenue, avance, net):
        html = self.generate_payslip_html(nom, mois, base, prime, retenue, avance, net)

        doc = QtGui.QTextDocument()
        doc.setDefaultFont(QtGui.QFont("Arial", 12))
        doc.setHtml(html)

        printer = QPrinter()
        print_dialog = QPrintDialog(printer)
        if print_dialog.exec_() == QPrintDialog.Accepted:
            doc.print_(printer)
        else:
            QtWidgets.QMessageBox.information(None, "Annulé", "L'impression a été annulée.")
    # =========================================

    def delete_accompte(self):
        delete = self.ui.labelAccompteEdit.text()
        if delete != 'True':
            logger.debug('Edit or Delete is disabled.')
            return
        ids = utils.table_multi_selection(self.ui.accompteTableWidget)
        if len(ids) > 1:
            logger.debug(f'Delete Multitple IDS({ids})')
            title = f"Etes-vous sûr de vouloir supprimer la selection [{ids}] ?"
        else:
            logger.debug(f"Deleting the selected accomte: ID({ids[0]})...")
            title = f"Etes-vous sûr de vouloir supprimer accompte avec ID '{ids[0]}' ?"

        dialog = utils.ConfirmDialog(title)
        if dialog.exec_() == QtWidgets.QDialog.Accepted:
            result = self.db.delete_item('operations', ids)
            logger.debug(f"Delete Accompte: {result}")
            if result['success']:
                self.show_error_message("Accompte supprimé avec succès.", success=True)
            else:
                self.show_error_message(f"{result['error']}", success=False)
        # display result
        employe_id = self.ui.labelAccompteEmpID.text()
        self.accompte_by_employee(employe_id)

    # ===============================================
    # == Clients ==
    # =============
    def display_clients(self, rows=None):
        """
        Display all personnes in the table widget.
        """
        if rows is None:
            rows = self.db.dump_clients()
        utils.populate_table_widget(self.ui.clientsTableWidget, rows, utils.CLIENTS_HEADERS)
        utils.set_table_column_sizes(self.ui.clientsTableWidget, 80, 320, 270, 200, 300)
        self.ui.labelClientsCount.setText(f"Total: {len(rows)}")
        self.set_total_credits()

    def client_credit_list(self):
        """
        Display all credits for the selected persone.
        """
        client_id = self.get_item_id(self.ui.clientsTableWidget)
        logger.info(f"Displaying credits for the selected client: {client_id}...")
        rows = self.db.get_client_credits(client_id)
        if not rows:
            self.show_error_message("Aucun crédit trouvé pour ce client.", success=False)
            return
        self.display_credits(rows)

        client = utils.get_column_value(self.ui.clientsTableWidget, self.ui.clientsTableWidget.currentRow(), 1)
        self.goto_page('credit', title=f"Crédits ({client})", from_btn=False)

    def refresh_clients_table(self):
        """
        Refresh the persone table widget.
        """
        logger.info('Refreshing persone table...')

    def filter_clients(self):
        """
        Search Persones
        """
        search_word = self.ui.editSearchClients.text()
        if not search_word: return  # or show a message to the user that the search input is empty
        else: search_word = f"%{search_word}%"
        rows = self.db.search_clients(search_word)
        self.display_clients(rows)

    def edit_client(self, row, col, text):
        client_id = self.get_item_id(self.ui.clientsTableWidget)
        logger.info(f"Edit Client({client_id}) at Row({row}), Column({col}), New Text({text})")
        result = self.db.update_client(client_id, col, text)
        if result['success']:
            self.show_error_message(result['message'], success=True)
            self.display_clients()
        else:
            self.show_error_message(f"Erreur: {result['error']}", success=False)
            if col == 2:
                self.display_clients()

    def delete_client(self):
        ids = utils.table_multi_selection(self.ui.clientsTableWidget)
        if len(ids) > 1:
            logger.debug(f'Delete Multitple IDS({ids})')
            title = f"Etes-vous sûr de vouloir supprimer la selection [{ids}] ?"
        else:
            client = utils.get_column_value(
                self.ui.clientsTableWidget,
                self.ui.clientsTableWidget.currentRow(),
                1
            )
            title = f"Etes-vous sûr de vouloir supprimer '{client.upper()}' ?"
            logger.debug(f"Deleting the selected client: Name({client})...")

        dialog = utils.ConfirmDialog(title)
        if dialog.exec_() == QtWidgets.QDialog.Accepted:
            result = self.db.delete_item('clients', ids)
            logger.debug(f"Delete Clients: {result}")
            if result['success']:
                self.show_error_message("Client supprimé avec succès.", success=True)
                self.display_clients()
            else:
                self.show_error_message(f"{result['error']}", success=False)

    # ========================================
    # == Credits Functions ==
    # =======================
    def display_credits(self, rows=None):
        """
        Display all credits in the table widget.
        """
        if rows is None:
            rows = self.db.dump_credits()
        utils.populate_table_widget(self.ui.creditTableWidget, rows, utils.CREDITS_HEADERS)
        utils.set_table_column_sizes(self.ui.creditTableWidget, 80, 220, 300, 200, 270, 270)
        self.ui.labelCreditCount.setText(f"Total: {len(rows)}")
        self.set_total_credits()

    def refresh_credit_table(self):
        logger.info('Refreshing credit table...')
        self.ui.cbBoxCreditByStatus.setCurrentText("Tous")  # Reset filter
        self.display_credits()

    def filter_credits(self):
        """
        Search Credits
        """
        search_word = self.ui.editSearchCredit.text()
        if not search_word: return  # or show a message to the user that the search input is empty
        else: search_word = f"%{search_word}%"
        rows = self.db.search_credits(search_word)
        self.display_credits(rows)

    def filter_credit_by_status(self):
        """
        Filter credits by status selected in the comboBox.
        """
        status = self.ui.cbBoxCreditByStatus.currentText().strip().lower()
        if status == 'tous':
            self.display_credits()
            return
        else:
            rows = self.db.credit_by_status(status)
            if not rows:
                self.show_error_message(f"Aucun crédit trouvé pour le statut '{status}'.", success=False)
                return
            logger.debug(f'Filter Credit By Status: {rows}')
            self.display_credits(rows)

    def ui_create_credit(self, client=False):
        """
        This function set up the UI for creating a new credit.
        """
        logger.info("Creating a new credit...")
        clients = self.db.get_names('clients')
        utils.populate_comboBox(self.ui.cbBoxAddCreditClients, clients)
        if client:
            # If a specific client is provided, set it as the current text
            client = utils.get_column_value(
                self.ui.clientsTableWidget,
                self.ui.clientsTableWidget.currentRow(),
                1
            )
            self.ui.cbBoxAddCreditClients.setCurrentText(client)
            self.ui.cbBoxAddCreditClients.setEnabled(False)
        else:
            self.ui.cbBoxAddCreditClients.setEnabled(True)

        self.ui.dateEditCreditDate.setDate(TODAY)  # Set current date as default
        self.setup_extraCenter_ui("Créer un nouveau crédit", self.ui.AddCreditPage)

    def save_new_credit(self):
        """
        Save the new credit to the database.
        """
        logger.info("Saving the new credit...")
        # Get values from UI
        client = self.ui.cbBoxAddCreditClients.currentText()
        date_credit = self.ui.dateEditCreditDate.date().toPyDate()
        montant = self.ui.editCreditMontant.value()
        motif = self.ui.editCreditDescription.toPlainText()         # FIXME: this work for motif

        # Validate the montant must be greater the 0
        if montant <= 0:
            self.show_error_message("Entré un chiffre pour le Montant.")
            return

        logger.debug(f"Date: {date_credit}, Client ID: {client}, "
                     f"Description: {motif}, Montant: {montant}")

        result = self.db.insert_new_credit(client, date_credit, montant, motif)
        logger.debug(result)
        if result['success']:
            self.show_error_message("Crédit ajouté avec succès.", success=True)
            self.toggle_left_box(close=True)
            self.goto_page('credit', title='Crédits')
            # clear inputs
            inputs_to_clear = [
                self.ui.cbBoxAddCreditClients,
                self.ui.dateEditCreditDate,
                self.ui.editCreditMontant,
                self.ui.editCreditDescription
            ]
            utils.clear_inputs(inputs_to_clear)
        else:
            self.show_error_message(f"Erreur: {result['error']}", success=False)

    def edit_credit(self, row, col, text):
        logger.info("Editing an existing credit...")
        credit_id = self.get_item_id(self.ui.creditTableWidget)
        versement = utils.get_column_value(self.ui.creditTableWidget, self.ui.creditTableWidget.currentRow(), 5)
        logger.info(f"Edit Client({credit_id}) at Row({row}), Column({col}), New Text({text})")
        versment = utils.format_to_decimal(versement)
        if not versment['success']:
            self.show_error_message(f"Erreur: {versment['error']}", success=False)
            return

        if col in (2, 5, 6, 7):
            self.display_credits()
        elif col == 1:
            # Validate the date
            if not utils.is_date(text):
                self.show_error_message("La date n'est pas valide. Utilisez le format Année-Mois-Jour.", success=False)
                self.display_credits()
                return
        elif col == 4:
            # handle montant converstion to decimal
            text = utils.format_to_decimal(text)
            if not text['success']:
                self.show_error_message(f"Erreur: {text['error']}", success=False)
                self.display_credits()      # refresh tablhu
                return
            else:
                text = text['value']

        result = self.db.update_credit(credit_id, col, text, versment['value'])
        if result['success']:
            self.show_error_message(result['message'], success=True)
            self.display_credits()
        else:
            self.show_error_message(f"Erreur: {result['error']}", success=False)

    def delete_credit(self):
        """ Delete the selected credit. """
        ids = utils.table_multi_selection(self.ui.creditTableWidget)
        if len(ids) > 1:
            logger.debug(f'Delete Multitple IDS({ids})')
            title = f"Etes-vous sûr de vouloir supprimer la selection [{ids}] ?"
        else:
            client = utils.get_column_value(
                self.ui.creditTableWidget,
                self.ui.creditTableWidget.currentRow(),
                2
            )
            logger.debug(f"Deleting the selected credit for client Name({client})...")
            title = f"Etes-vous sûr de vouloir supprimer crédit N° {ids[0]} \ndu client '{client.upper()}'?"

        dialog = utils.ConfirmDialog(title)
        if dialog.exec_() == QtWidgets.QDialog.Accepted:
            result = self.db.delete_item('credit', ids)
            if result['success']:
                self.show_error_message("Crédit supprimé avec succès.", success=True)
                self.display_credits()
                # self.goto_page('credit', title='Crédits')
            else:
                self.show_error_message(f"{result['error']}", success=False)

    # =================================================================================
    # == Payments(Versement) Functions ==
    # ===================================
    def display_versement(self, rows):
        """
        Displays a list of versements in the table widget and updates the versement count label.

        Args:
            rows (list): A list of versement records, where each record contains
                information such as ID, date, montant, and observation.

        Side Effects:
            - Populates the versementTableWidget with the provided rows and headers.
            - Updates the labelVersementCount to show the total number of versements.

        Display all versements in the table widget.
        """
        headers = ['ID', 'Date', 'Montant', 'Observation']
        utils.populate_table_widget(self.ui.versementTableWidget, rows, headers)
        utils.set_table_column_sizes(self.ui.versementTableWidget, 80, 150, 150)
        self.ui.labelVersementCount.setText(f"Total: {len(rows)}")

    def ui_add_versement(self):
        """
        This function set up the UI for creating a new credit.
        """
        # Check if credit has Reste
        reste = utils.get_column_value(
            self.ui.creditTableWidget,
            self.ui.creditTableWidget.currentRow(),
            6
        )
        if reste == '0,00':
            self.show_error_message("Ce crédit est déjà terminé. Aucun versement n'est nécessaire.", success=False)
            return

        # Setup Usefull Information
        credit_id = self.get_item_id(self.ui.creditTableWidget)
        client = utils.get_column_value(
            self.ui.creditTableWidget,
            self.ui.creditTableWidget.currentRow(),
            2
        )
        # add client_id
        client_id = self.db.get_item_id('clients', 'nom', client)
        self.ui.labelVersementCreditID.setText(f"{credit_id}")
        self.ui.labelVersementCreditID.hide()
        self.ui.labelVersementClientID.setText(f"{client_id}")
        self.ui.labelVersementClientID.hide()

        # remove DA
        # self.ui.labelAddVersementMontant.setText(f"{reste} DA")
        self.ui.labelAddVersementMontant.setText(f"{reste}")
        self.ui.dateEditVersementDate.setDate(TODAY)

        # maximum value for reste restrict user
        # conver to Decimal in place
        logger.info(f"Add payment for Credit({credit_id}), ClientID({client_id}), reste({reste})")
        reste_decimal = utils.format_to_decimal(reste)
        if not reste_decimal['success']:
            self.show_error_message(f"Erreur: {reste_decimal['error']}", success=False)
            return
        self.ui.editVersementMontant.setMaximum(reste_decimal['value'])

        # hide the ID Labels
        for label in [self.ui.labelVersementCreditID, self.ui.labelVersementClientID]:
            label.hide()

        self.setup_extraCenter_ui('Ajouter un versement', self.ui.AddCreditVersementPage)

    def save_new_versement(self):
        """
        Save the new versement to the database.
        """
        # collecting info
        reste = self.ui.labelAddVersementMontant.text()
        logger.debug(f'Reste: {reste}')
        reste = utils.format_to_decimal(self.ui.labelAddVersementMontant.text())
        if not reste['success']:
            self.show_error_message(f"Erreur: {reste['error']}", success=False)
            return
        reste = reste['value']
        credit_id = self.ui.labelVersementCreditID.text()
        client_id = self.ui.labelVersementClientID.text()
        date_vers = self.ui.dateEditVersementDate.date().toPyDate()
        montant = self.ui.editVersementMontant.value()
        description = self.ui.editVersementDescription.toPlainText()

        self.insert_versement_db(credit_id, client_id, date_vers, montant, reste, description)

    def insert_versement_db(self, credit_id, client_id, date_vers, montant, reste, description):
        """
        :rest: is just to check if the montant is less than or equal to reste.
        """
        # Chack Qte
        if montant <= 0:
            self.show_error_message("Entré un chiffre pour le Montant.")
            return
        elif montant > reste:
            self.show_error_message("Le Montant depasse le reste.")
            return

        logger.debug(f"CreditID({credit_id}), ClientID({client_id}) Date({date_vers}), "
                     f"Description({description}), Montant({montant})")

        # Insert into DATABASE
        result = self.db.insert_new_versement(credit_id, client_id, date_vers, montant, description)
        logger.debug(result)
        if result['success']:
            self.show_error_message("Versement ajouté avec succès.", success=True)
            self.toggle_left_box(close=True)
            self.goto_page('credit', title='Crédits')
        else:
            self.show_error_message(f"Erreur: {result['error']}", success=False)

    def credit_list_versement(self):
        """ Display all versements for a selected credit."""
        credit_id = self.get_item_id(self.ui.creditTableWidget)
        client = utils.get_column_value(
            self.ui.creditTableWidget,
            self.ui.creditTableWidget.currentRow(),
            2
        )
        logger.info(f"Displaying versements for the selected credit {credit_id} - client({client})...")
        rows = self.db.get_credit_versements(credit_id)
        if not rows:
            self.show_error_message("Aucun versement trouvé pour ce crédit.", success=False)
            self.toggle_left_box(close=True)
            return
        self.display_versement(rows)
        self.setup_extraCenter_ui("List des Versements", self.ui.VersementPage)

    def regle_credit(self):
        """
        Mark the selected credit as 'terminé' if all versements are done.
        """
        credit_id = self.get_item_id(self.ui.creditTableWidget)
        client = utils.get_column_value(
            self.ui.creditTableWidget,
            self.ui.creditTableWidget.currentRow(),
            2
        )
        client_id = self.db.get_item_id('clients', 'nom', client)

        logger.info(f"Marking credit({credit_id}) for client({client}) as 'terminé'...")
        result = self.db.regle_credit(credit_id, client_id)

        if result['success']:
            self.show_error_message(result["message"], success=True)
            self.goto_page('credit', title='Crédits')
        else:
            self.show_error_message(f"{result['error']}", success=False)

        logger.info("Updating the selected versement...")

    def delete_versement(self):
        """
        Delete the selected versement.
        """
        title = "Etes-vous sûr de vouloir supprimer ce versement ?"
        dialog = utils.ConfirmDialog(title)
        if dialog.exec_() == QtWidgets.QDialog.Accepted:
            paiement_id = self.get_item_id(self.ui.versementTableWidget)
            logger.info(f"Deleting versement {paiement_id}...")
            # Implement deletion logic here
            result = self.db.delete_paiement(paiement_id)
            if result['success']:
                self.show_error_message("Versement supprimé avec succès.", success=True)
                self.goto_page('credit', title='Crédits')
                self.toggle_left_box(close=True)
            else:
                self.show_error_message(f"{result['error']}", success=False)

    # =================================================================================
    # == Charge Page ==
    # =================
    def display_charge(self, rows=None):
        """
        Display all versements in the table widget.
        """
        MONTHS_FR = {
            "01": "janvier",
            "02": "février",
            "03": "mars",
            "04": "avril",
            "05": "mai",
            "06": "juin",
            "07": "juillet",
            "08": "août",
            "09": "septembre",
            "10": "octobre",
            "11": "novembre",
            "12": "décembre"
        }

        month_text = self.ui.cbBoxChargeByMonth.currentText()
        month_name = MONTHS_FR.get(month_text) if month_text != 'Mois' else MONTHS_FR.get(TODAY.strftime("%m"))
        month = self.CURRENT_MONTH if month_text == 'Mois' else f"{TODAY.strftime('%Y')}-{month_text}"
        # Get result from database
        rows = self.db.dump_charges(month) if rows is None else rows
        total_charges = self.db.sum_charges(month)

        logger.debug(f'Display Charge Records for {month}')
        message = f"Total Charges {month_name.title()}: {utils.format_money(total_charges.total_charges)}"
        self.ui.labelTotalCharge.setText(message)
        # Display records in QTable
        utils.populate_table_widget(self.ui.chargeTableWidget, rows, utils.CHARGE_HEADERS)
        utils.set_table_column_sizes(self.ui.chargeTableWidget, 80, 170, 250, 200)
        self.ui.labelChargeCount.setText(f"Total: {len(rows)}")

    def filter_charge(self):
        logger.info('Filter Charges')

    def ui_create_charge(self, edit=False):
        """
        Initializes the UI for creating or editing a charge entry.
        If `edit` is True, populates the UI fields with the data of the selected charge for editing.
        Otherwise, clears the input fields and sets default values for creating a new charge.
        Args:
            edit (bool): If True, the UI is set up for editing an existing charge. If False, for creating a new charge.
        Side Effects:
            - Populates the charge-by combo box with employee names.
            - Sets up the UI fields with either existing charge data or default values.
            - Updates the page title to reflect the current operation (add or edit).
            - Displays an error message if the charge to edit is not found.
        """

        employees = self.db.get_names('employes')
        utils.populate_comboBox(self.ui.cbBoxChargeBy, employees)
        if edit:
            logger.info("Editing an existing charge...")
            charge_id = self.get_item_id(self.ui.chargeTableWidget)
            self.ui.labelChargeID.setText(charge_id)
            self.ui.labelChargeID.hide()
            self.ui.labelChargeEditEnabled.setText('True')
            self.ui.labelChargeEditEnabled.hide()

            charge = self.db.get_charge_by_id(charge_id)
            if not charge:
                self.show_error_message("Erreur: Charge introuvable.", success=False)
                return

            # Populate fields with existing data
            date_obj = QtCore.QDate.fromString(charge.date_charge, 'yyyy-MM-dd')
            self.ui.dateEditChargeDate.setDate(date_obj)
            self.ui.cbBoxChargeBy.setCurrentText(charge.effectue_par)
            self.ui.editChargeMontant.setValue(charge.montant)
            self.ui.editChargeMotif.setPlainText(charge.motif)
            title = "Modifier Charge"
            self.ui.extraIconPlus.setIcon(qta.icon('ph.pencil-line-light', color="#FF6600"))
            self.ui.extraLabelTitle.setStyleSheet("color: #FF6600;")
        else:
            logger.info("Creating a new charge...")
            # Clear previous inputs
            inputs_to_clear = [
                self.ui.dateEditChargeDate,
                self.ui.editChargeMontant,
                self.ui.editChargeMotif
            ]
            utils.clear_inputs(inputs_to_clear)
            self.ui.dateEditChargeDate.setDate(TODAY)  # Set current date as default
            title = "Ajouter Une Charge"
            self.ui.extraIconPlus.setIcon(qta.icon('ph.plus', color=utils.SKYPE_COLOR))
            self.ui.extraLabelTitle.setStyleSheet(f"color: {utils.SKYPE_COLOR};")
            self.ui.labelChargeEditEnabled.setText('False')
            self.ui.labelChargeID.clear()

        self.setup_extraCenter_ui(title, self.ui.addChargePage)

    def insert_new_charge(self):
        """
        Inserts a new charge record into the database using values from the UI.
        Retrieves the charge date, the person responsible, the amount, and the reason from the UI elements.
        Attempts to insert the new charge into the database. If successful, displays a success message,
        closes the left box, and navigates to the charges page. If unsuccessful, displays an error message.
        Note:
            This function currently only handles insertion. Update functionality is to be added.
        Returns:
            None
        """

        # Get values from UI
        date = self.ui.dateEditChargeDate.date().toPyDate()
        par = self.ui.cbBoxChargeBy.currentText()
        montant = self.ui.editChargeMontant.value()
        motif = self.ui.editChargeMotif.toPlainText()

        # Procedure to database
        editable = self.ui.labelChargeEditEnabled.text()
        if editable == 'True':
            charge_id = self.ui.labelChargeID.text()
            logger.debug(f"Editing charge({charge_id}): "
                         f"Date({date}), Par({par}), Montant({montant}), Motif({motif})")
            result = self.db.update_charge_values(charge_id, date, par, montant, motif)
        else:
            logger.debug("Inserting new charge with values: "
                         f"Date({date}), Par({par}), Montant({montant}), Motif({motif})")
            result = self.db.insert_new_charge(date, par, montant, motif)

        if result['success']:
            logger.info(f"{result['message']}")
            self.show_error_message(f"{result['message']}", success=True)

            self.show_error_message("Charge ajoutée avec succès.", success=True)
            self.toggle_left_box(close=True)
            self.goto_page('charge', title='Charges')
        else:
            logger.error(f"Error inserting charge: {result['error']}")
            self.show_error_message(f"Erreur: {result['error']}", success=False)

    def edit_charge(self, row, col, text):
        charge_id = self.get_item_id(self.ui.chargeTableWidget)
        logger.info(f"Edit Charge({charge_id}) at Row({row}), Column({col}), New Text({text})")

        # check the date
        if col == 1:
            if not utils.is_date(text):
                self.show_error_message("Vérifier la date.")
                self.display_charge()
                return
        result = self.db.update_charge(charge_id, col, text)
        if result['success']:
            self.show_error_message(result['message'], success=True)
            self.display_employes()
        else:
            self.show_error_message(f"Erreur: {result['error']}", success=False)

    def delete_charge(self):
        logger.debug('Delete Charge')
        title = "Etes-vous sûr de vouloir supprimer cette charge ?"
        dialog = utils.ConfirmDialog(title)
        if dialog.exec_() == QtWidgets.QDialog.Accepted:
            charge_id = self.get_item_id(self.ui.chargeTableWidget)
            logger.info(f"Deleting charge {charge_id}...")
            # Implement deletion logic here
            result = self.db.delete_item('charges', charge_id)
            if result['success']:
                self.show_error_message("Charge supprimé avec succès.", success=True)
                self.goto_page('charge', title='Charges')
            else:
                self.show_error_message(f"{result['error']}", success=False)


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)

    dialog = Credit()
    dialog.show()
    sys.exit(app.exec_())
