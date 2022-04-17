# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo.addons.account.tests.invoice_test_common import InvoiceTestCommon
from odoo.addons.account_reports.tests.common import _init_options
from odoo.tests import tagged
from odoo import fields
from odoo.tools import date_utils


@tagged('post_install', '-at_install')
class LuxembourgElectronicReportTest(InvoiceTestCommon):

    @classmethod
    def setUpClass(cls):
        super(LuxembourgElectronicReportTest, cls).setUpClass()

        cls.env.company.write({
            'chart_template_id': cls.env.ref('l10n_lu.lu_2011_chart_1').id
        })
        cls.company_data = cls.setup_company_data('company_LU_data', country_id=cls.env.ref('base.lu').id, ecdf_prefix='1234AB')
        cls.company = cls.company_data['company']

        # ==== Partner ====
        cls.partner_a = cls.env['res.partner'].create({
            'name': 'Partner A'
        })
        # ==== Products ====
        cls.product_a = cls.env['product.product'].create({
            'name': 'product_a',
            'lst_price': 1000.0,
            'standard_price': 800.0,
        })
        cls.product_b = cls.env['product.product'].create({
            'name': 'product_b',
            'lst_price': 200.0,
            'standard_price': 160.0,
        })

    def get_report_options(self, report):
        year_df, year_dt = date_utils.get_fiscal_year(fields.Date.today())
        report.filter_date = {'mode': 'range', 'filter': 'this_year'}
        # Generate `options` to feed to financial report
        options = _init_options(report, year_df, year_dt)
        # Below method generates `filename` in specific format required for XML report
        report.get_report_filename(options)
        return options

    def get_report_values(self, report, options):
        report_values = report._get_lu_electronic_report_values(options)
        values = []
        # Here, we filtered out zero amount values so that `expected_*_report_values` can have lesser items.
        for code, value in report_values['forms'][0]['field_values'].items():
            if value['field_type'] == 'number' and value['value'] != '0,00':
                values.append((code, value['value']))
        return values

    def test_electronic_reports(self):
        # Create one invoice and one bill in current year
        date_today = fields.Date.today()
        lu_invoice = self.init_invoice('out_invoice')
        lu_bill = self.init_invoice('in_invoice')
        # init_invoice() has hardcoded 2019 year's date, we need to reset invoices' dates to current
        # year's date as BS/PL financial reports needs to have previous year's balance in exported file.
        (lu_invoice | lu_bill).write({'invoice_date': date_today, 'date': date_today})
        lu_invoice.post()
        lu_bill.post()

        # Below tuples are having code and it's amount respectively which would go to exported Balance Sheet report
        # if exported with the same invoice and bill as created above
        expected_bs_report_values = [
            ('151', '1567,20'), ('163', '1567,20'), ('165', '1404,00'), ('167', '1404,00'), ('183', '163,20'), ('185', '163,20'),
            ('201', '1567,20'), ('301', '240,00'), ('321', '240,00'), ('435', '1327,20'), ('367', '1123,20'), ('369', '1123,20'),
            ('451', '204,00'), ('393', '204,00'), ('405', '1567,20')
        ]
        bs_report = self.env.ref('l10n_lu_reports.account_financial_report_l10n_lu_bs')
        bs_report_options = self.get_report_options(bs_report)
        bs_report_field_values = self.get_report_values(bs_report, bs_report_options)
        self.assertEqual(expected_bs_report_values, bs_report_field_values, "Wrong values of Luxembourg Balance Sheet report.")
        # test to see if there is any error in XML generation
        bs_report.get_xml(bs_report_options)

        expected_pl_report_values = [('701', '1200,00'), ('671', '-960,00'), ('601', '-960,00'), ('667', '240,00'), ('669', '240,00')]
        pl_report = self.env.ref('l10n_lu_reports.account_financial_report_l10n_lu_pl')
        pl_report_options = self.get_report_options(pl_report)
        pl_report_field_values = self.get_report_values(pl_report, pl_report_options)
        self.assertEqual(expected_pl_report_values, pl_report_field_values, "Wrong values of Luxembourg Profit & Loss report.")
        pl_report.get_xml(pl_report_options)

        expected_tax_report_values = [('037', '1200,00'), ('701', '1200,00'), ('046', '204,00'), ('702', '204,00'), ('093', '163,20'), ('458', '163,20')]
        TaxReport = self.env['account.generic.tax.report']
        tax_report_options = self.get_report_options(TaxReport)
        tax_report_field_values = self.get_report_values(TaxReport, tax_report_options)
        self.assertEqual(expected_tax_report_values, tax_report_field_values, "Wrong values of Luxembourg Tax report.")
        TaxReport.get_xml(tax_report_options)
