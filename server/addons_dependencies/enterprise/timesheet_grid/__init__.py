# -*- coding: utf-8 -*-

from . import models
from . import wizard

from odoo import api, SUPERUSER_ID


def pre_init_hook(cr):
    env = api.Environment(cr, SUPERUSER_ID, {})
    root_menu = env.ref('hr_timesheet.timesheet_menu_root', raise_if_not_found=False)
    if root_menu and not root_menu.active:
        root_menu.write({'active': True})


def uninstall_hook(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})
    root_menu = env.ref('hr_timesheet.timesheet_menu_root', raise_if_not_found=False)
    if root_menu and root_menu.active:
        root_menu.write({'active': False})
