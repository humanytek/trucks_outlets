from openerp import _, api, exceptions, fields, models


class TrucksOutlets(models.Model):
    _name = 'trucks.outlets'
    _inherit = ['mail.thread']

    name = fields.Char()

    state = fields.Selection([
        ('analysis', 'Analysis'),
        ('weight_input', 'Weight Input'),
        ('loading', 'Loading'),
        ('weight_output', 'Weight Output'),
        ('done', 'Done'),
    ], default='analysis')

    contract_id = fields.Many2one('sale.order')
    contract_type = fields.Selection(readonly=True, related="contract_id.contract_type")
    partner_id = fields.Many2one('res.partner', related="contract_id.partner_id", readonly=True)
    street = fields.Char(readonly=True, related='partner_id.street')

    driver = fields.Char()
    car_plates = fields.Char()

    hired = fields.Float(readonly=True, compute="_compute_hired", store=False)
    delivered = fields.Float(readonly=True, compute="_compute_delivered", store=False)
    pending = fields.Float(readonly=True, compute="_compute_pending", store=False)

    product_id = fields.Many2one('product.product', compute="_compute_product_id", store=False, readonly=True)
    warehouse_id = fields.Many2one('stock.warehouse', related="contract_id.warehouse_id", readonly=True)

    humidity = fields.Float(min_value=0)
    density = fields.Float(min_value=0)
    temperature = fields.Float(min_value=0)

    damaged = fields.Float(min_value=0, max_value=10)
    broken = fields.Float(min_value=0)
    impurities = fields.Float(min_value=0)

    transgenic = fields.Float(min_value=0)

    ticket = fields.Char()

    weight_input = fields.Float(min_value=0)
    weight_output = fields.Float(min_value=0)
    weight_neto = fields.Float(compute="_compute_weight_neto", store=False)

    kilos_damaged = fields.Float(compute="_compute_kilos_damaged", store=False)
    kilos_broken = fields.Float(compute="_compute_kilos_broken", store=False)
    kilos_impurities = fields.Float(compute="_compute_kilos_impurities", store=False)
    kilos_humidity = fields.Float(compute="_compute_kilos_humidity", store=False)
    weight_neto_analized = fields.Float(compute="_compute_weight_neto_analized", store=False)

    stock_picking = fields.Many2one('stock.picking', readonly=True)

    _defaults = {'name': lambda obj, cr, uid, context: obj.pool.get('ir.sequence').get(cr, uid, 'reg_code'), }

    @api.one
    @api.depends('weight_input', 'weight_output')
    def _compute_weight_neto(self):
        self.weight_neto = self.weight_input - self.weight_output

    @api.one
    @api.depends('weight_neto', 'damaged')
    def _compute_kilos_damaged(self):
        if self.damaged > 5:
            self.kilos_damaged = ((self.damaged - 5) / 100) * self.weight_neto
        else:
            self.kilos_damaged = 0

    @api.one
    @api.depends('weight_neto', 'broken')
    def _compute_kilos_broken(self):
        if self.broken > 2:
            self.kilos_broken = ((self.broken - 2) / 100) * self.weight_neto
        else:
            self.kilos_broken = 0

    @api.one
    @api.depends('weight_neto', 'impurities')
    def _compute_kilos_impurities(self):
        if self.impurities > 2:
            self.kilos_impurities = ((self.impurities - 2) / 100) * self.weight_neto
        else:
            self.kilos_impurities = 0

    @api.one
    @api.depends('weight_neto', 'humidity')
    def _compute_kilos_humidity(self):
        if self.humidity > 14:
            self.kilos_humidity = ((self.humidity - 14) * .0116) * self.weight_neto
        else:
            self.kilos_humidity = 0

    @api.one
    @api.depends('weight_neto', 'kilos_damaged', 'kilos_broken', 'kilos_impurities', 'kilos_humidity')
    def _compute_weight_neto_analized(self):
        self.weight_neto_analized = self.weight_neto - self.kilos_damaged - self.kilos_broken - self.kilos_impurities - self.kilos_humidity

    @api.one
    @api.depends('contract_id')
    def _compute_hired(self):
        self.hired = sum(line.product_uom_qty for line in self.contract_id.order_line)

    @api.one
    @api.depends('contract_id', 'weight_neto')
    def _compute_delivered(self):
        self.delivered = sum(record.weight_neto for record in self.contract_id.trucks_outlets_ids) / 1000

    @api.one
    @api.depends('contract_id')
    def _compute_pending(self):
        self.pending = self.hired - self.delivered

    @api.one
    @api.depends('contract_id')
    def _compute_product_id(self):
        product_id = False
        for line in self.contract_id.order_line:
            product_id = line.product_id
            break
        self.product_id = product_id

    @api.one
    def fun_load(self):
        self.state = 'weight_output'

    @api.multi
    def write(self, values, context=None):
        res = super(TrucksOutlets, self).write(values)
        if self.state == 'done':
            zxc = 'zxc' # TODO
        return res

    @api.multi
    def write(self, vals, recursive=None):
        if not recursive:
            if self.state == 'analysis':
                self.write({'state': 'weight_input'}, 'r')
            elif self.state == 'weight_input':
                self.write({'state': 'unloading'}, 'r')
            elif self.state == 'loading':
                self.write({'state': 'weight_output'}, 'r')
            elif self.state == 'weight_output':
                self.write({'state': 'done'}, 'r')

        res = super(TrucksOutlets, self).write(vals)
        return res

    @api.model
    def create(self, vals):
        vals['state'] = 'weight_input'
        res = super(TrucksOutlets, self).create(vals)
        return res
