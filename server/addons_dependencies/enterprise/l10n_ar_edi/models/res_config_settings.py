# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo import models, fields, api, _
from odoo.exceptions import UserError


class ResConfigSettings(models.TransientModel):

    _inherit = 'res.config.settings'

    l10n_ar_country_code = fields.Char(related='company_id.country_id.code', string='Country Code')
    l10n_ar_afip_verification_type = fields.Selection(related='company_id.l10n_ar_afip_verification_type', readonly=False)

    l10n_ar_afip_ws_environment = fields.Selection(related='company_id.l10n_ar_afip_ws_environment', readonly=False)
    l10n_ar_afip_ws_key = fields.Binary(related='company_id.l10n_ar_afip_ws_key', readonly=False)
    l10n_ar_afip_ws_crt = fields.Binary(related='company_id.l10n_ar_afip_ws_crt', readonly=False)

    l10n_ar_afip_ws_key_fname = fields.Char('Private Key name', default='private_key.pem')
    l10n_ar_afip_ws_crt_fname = fields.Char(related='company_id.l10n_ar_afip_ws_crt_fname')

    def l10n_ar_action_create_certificate_request(self):
        self.ensure_one()
        if not self.company_id.partner_id.city:
            raise UserError(_('The company city must be defined before this action'))
        if not self.company_id.partner_id.country_id:
            raise UserError(_('The company country must be defined before this action'))
        if not self.company_id.partner_id.l10n_ar_vat:
            raise UserError(_('The company CUIT must be defined before this action'))

        return {'type': 'ir.actions.act_url', 'url': '/l10n_ar_edi/download_csr?', 'target': 'new'}

    @api.onchange('l10n_ar_afip_ws_crt')
    def _l10n_ar_onchange_afip_certificate(self):
        """ Verify if certificate uploaded is well formed before saving """
        if not self.l10n_ar_afip_ws_crt:
            return

        try:
            self.company_id._l10n_ar_get_certificate_object(self.l10n_ar_afip_ws_crt)
        except Exception as error:
            msg = ''
            if 'Expecting: CERTIFICATE' in repr(error):
                msg = _('Wrong Certificate file format.\nBe sure you have BEGIN CERTIFICATE string in your first line.')
            self.l10n_ar_afip_ws_crt = False
            return {'warning': {'title': 'Error uploading certificate', 'message': '\n'.join(['The certificate can be uploaded!', msg, 'This is what we get', repr(error)])}}

    def random_demo_cert(self):
        self.company_id.set_demo_random_cert()
