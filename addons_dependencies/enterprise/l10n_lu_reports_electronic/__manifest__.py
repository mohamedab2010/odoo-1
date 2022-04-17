# -*- encoding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': 'Luxembourg - Electronic Accounting Reports',
    'version': '1.0',
    'description': """
Electronic Accounting reports for Luxembourg
============================================
    """,
    'category': 'Accounting',
    'depends': ['l10n_lu_reports'],
    'data': [
        'data/ir_cron_data.xml',
        'data/account.tax.report.line.csv',
        'views/res_company_views.xml',
        'views/electronic_report_template.xml',
    ],
    'license': 'OEEL-1',
    'auto_install': True,
}
