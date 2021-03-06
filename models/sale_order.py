from openerp import fields, models


class PurchaseOrder(models.Model):
    _inherit = 'sale.order'

    trucks_outlets_ids = fields.One2many('trucks.outlets', 'contract_id')

    def trucks_outlets(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        mod_obj = self.pool.get('ir.model.data')
        dummy, action_id = tuple(mod_obj.get_object_reference(cr, uid, 'trucks_outlets', 'trucks_outlets_list_action'))
        action = self.pool.get('ir.actions.act_window').read(cr, uid, action_id, context=context)
        res = mod_obj.get_object_reference(cr, uid, 'trucks_outlets', 'trucks_outlets_form_view')
        action['views'] = [(res and res[1] or False, 'form')]
        action['context'] = {'default_contract_id': ids[0]}
        return action
