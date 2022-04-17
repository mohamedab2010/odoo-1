# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo.addons.account.tests.invoice_test_common import InvoiceTestCommon
from odoo.addons.account_reports.tests.common import _init_options
from odoo.tests import tagged
from odoo.tests.common import Form
from odoo import fields, release
from odoo.tools import date_utils


@tagged('post_install', '-at_install')
class SAFTReportTest(InvoiceTestCommon):

    @classmethod
    def setup_saft_company_data(cls, chart_template, country, **kwargs):
        cls.env.company.write({
            'chart_template_id': chart_template.id
        })
        # below property will be used in various common assertion message
        cls.country_name = country.name
        cls.company_data = cls.setup_company_data(
            '{}Company'.format(country.name),
            country_id=country.id, **kwargs
        )
        cls.company = cls.company_data['company']

        cls.prepare_data()

    @classmethod
    def check_or_create_xsd_attachment(cls, module_name):
        # Check for cached XSD file in attachment
        xsd_file = cls.env['account.general.ledger']._get_xsd_file()
        attachment = cls.env['ir.attachment'].search([
            ('name', '=', 'xsd_cached_{0}'.format(xsd_file.replace('.', '_')))
        ])
        if not attachment:
            # Below might take some time to download XSD file
            cls.env.ref('{}.ir_cron_load_xsd_file'.format(module_name)).method_direct_trigger()
        return True

    @classmethod
    def prepare_data(cls):
        # below will trigger partner onchange that will update partner_id among other fields of account.move.line
        def onchange_partner_b(invoice):
            invoice_form = Form(invoice)
            invoice_form.partner_id = cls.partner_b
            return invoice_form.save()

        # prepare data required to create invoices
        cls.partner_a = cls.env['res.partner'].create({
            'name': 'SAFT Partner A',
            'city': 'Garnich',
            'zip': 'L-8353',
            'country_id': cls.env.ref('base.lu').id,
            'phone': '+352 24 11 11 11'
        })
        cls.partner_b = cls.env['res.partner'].create({
            'name': 'SAFT Partner B',
            'city': 'Garnich',
            'zip': 'L-8353',
            'country_id': cls.env.ref('base.lu').id,
            'phone': '+352 24 11 11 12'
        })
        cls.product_a = cls.env['product.product'].create({
            'name': 'SAFT A',
            'default_code': 'PA',
            'lst_price': 1000.0,
            'standard_price': 800.0,
            'property_account_income_id': cls.company_data['default_account_revenue'].id,
            'property_account_expense_id': cls.company_data['default_account_expense'].id,
        })
        cls.product_b = cls.env['product.product'].create({
            'name': 'SAFT B',
            'default_code': 'PB',
            'uom_id': cls.env.ref('uom.product_uom_dozen').id,
            'lst_price': 200.0,
            'standard_price': 160.0,
            'property_account_income_id': cls.company_data['default_account_revenue'].id,
            'property_account_expense_id': cls.company_data['default_account_expense'].id,
        })

        # Create three invoices, one refund and one bill in current year
        partner_a_invoice1 = cls.init_invoice('out_invoice')
        partner_a_invoice2 = cls.init_invoice('out_invoice')
        partner_a_invoice3 = cls.init_invoice('out_invoice')
        partner_a_refund = cls.init_invoice('out_refund')

        partner_b_bill = onchange_partner_b(cls.init_invoice('in_invoice'))

        date_today = fields.Date.today()

        # Create one invoice for partner B in previous year
        partner_b_invoice1 = onchange_partner_b(cls.init_invoice('out_invoice'))

        # init_invoice has hardcoded 2019 year's date, we are resetting it to current year's one.
        (partner_a_invoice1 + partner_a_invoice2 + partner_a_invoice3 + partner_a_refund + partner_b_bill).write({'invoice_date': date_today, 'date': date_today})
        (partner_a_invoice1 + partner_a_invoice2 + partner_a_invoice3 + partner_b_invoice1 + partner_a_refund + partner_b_bill).post()

        cls.report_options = cls.get_report_options()

    @classmethod
    def get_report_options(cls):
        GeneralLedger = cls.env['account.general.ledger']
        year_df, year_dt = date_utils.get_fiscal_year(fields.Date.today())
        GeneralLedger.filter_date = {'mode': 'range', 'filter': 'this_year'}
        # Generate `options` to feed to SAFT report
        return _init_options(GeneralLedger, year_df, year_dt)

    def generate_saft_report(self):
        return self.env['account.general.ledger'].get_xml(self.report_options)

    def get_report_values(self):
        return self.env['account.general.ledger']._prepare_saft_report_data(self.report_options)

    def assertHeaderData(self, header_values, expected_values):
        expected_values.update({
            'date_created': fields.Date.today(),
            'software_version': release.version,
            'company_currency': self.company.currency_id.name,
            'date_from': self.report_options['date']['date_from'],
            'date_to': self.report_options['date']['date_to'],
        })
        # Test exported accounts' closing balance
        self.assertEqual(header_values, expected_values,
            "Header for {} SAF-T report is not correct.".format(self.country_name))

    def assertAccountBalance(self, values, expected_values):
        # Test exported accounts' closing balance
        for account_vals in values:
            expected = expected_values[account_vals['id']]
            self.assertEqual(account_vals['opening_balance'], expected['opening_balance'],
                "Wrong opening balance for account(s) of {} SAF-T report.".format(self.country_name))
            self.assertEqual(account_vals['closing_balance'], expected['closing_balance'],
                "Wrong closing balance for account(s) of {} SAF-T report.".format(self.country_name))

    def execute_common_tests(self, values):
        self.assertEqual(self.company.country_id.code, values['country_code'],
            "Selected company is not one from {}! SAF-T report can't be generated.".format(self.country_name))

        # Test exported customers/suppliers
        self.assertEqual(len(values['customers']), 1,
            "{} SAF-T report should have 1 customer in master data.".format(self.country_name))
        self.assertEqual(values['customers'][0]['id'], self.partner_a.id,
            "{} SAF-T report should have {} as customer in master data.".format(self.country_name, self.partner_a.name))
        self.assertEqual(len(values['suppliers']), 1,
            "{} SAF-T report should have 1 supplier in master data.".format(self.country_name))
        self.assertEqual(values['suppliers'][0]['id'], self.partner_b.id,
            "{} SAF-T report should have {} as supplier in master data.".format(self.country_name, self.partner_b.name))

        # Test exported taxes
        sales_tax = self.env['account.tax'].search_read([
            ('type_tax_use', '=', 'sale'),
            ('company_id', '=', self.company.id),
        ], ['name', 'amount_type', 'amount'], limit=1) # default sale tax
        purchases_tax = self.env['account.tax'].search_read([
            ('type_tax_use', '=', 'purchase'),
            ('company_id', '=', self.company.id),
        ], ['name', 'amount_type', 'amount'], limit=1) # default purchase tax
        report_taxes = list(values['taxes'].values())
        expected_taxes = sales_tax + purchases_tax
        self.assertEqual(report_taxes, expected_taxes,
            "{} SAF-T report should have default sales and purchase taxes.".format(self.country_name))
