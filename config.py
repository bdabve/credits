#!/usr/bin/env python3
# -*- coding: utf-8 -*-

PAGES = {
    'client': {
        'title': 'Clients',
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
        'title': 'Employée',
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
        'title': 'Employée Operation',
        'widget': lambda self: self.ui.EmployeOperationsPage,
        'action': lambda self: (
            self.ui.labelEmployesOperationByEmpID.setText(''),
            self.display_operations()
        ),
        'buttons': lambda self: (
            self.ui.employesOperationTableWidget,
            (self.ui.buttonDeleteEmployeOperation,)
        )
    },
    'credit': {
        'title': 'Crédits',
        'widget': lambda self: self.ui.CreditPage,
        'action': lambda self: self.display_credits(),
        'buttons': lambda self: (
            self.ui.creditTableWidget,
            (self.ui.buttonEditCredit,
             self.ui.buttonDeleteCredit,
             self.ui.buttonCreditVersement,
             self.ui.buttonCreditAddVersement,
             self.ui.buttonRegleCredit)
        )
    },
    'payment': {
        'title': 'Paiements',
        'widget': lambda self: self.ui.versementTableWidget,
        'action': None,  # No display action
        'buttons': lambda self: (
            self.ui.versementTableWidget,
            (self.ui.buttonDeleteVersement,)
        )
    }
}
