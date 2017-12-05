
from __future__ import unicode_literals

import json
import urllib
import frappe
from frappe import _, throw

@frappe.whitelist()
def octopart_lookup(sq_number):

	# Get the api key from settings

	sq = frappe.get_doc('Supplier Quotation', sq_number)
	supplier = frappe.get_value('Supplier',sq.supplier,'octopart_seller_name') or sq.supplier
	for item in sq.items:
		mfg, mfg_pn, sku = frappe.get_value('Item', item.item_code, ['manufacturer','manufacturer_part_no', 'item_code'])
		api_key = frappe.db.get_single_value('OctoERP Settings', "api_key")
		#frappe.msgprint(_("{0}     {1}      {2}").format(mfg, mfg_pn, sku))

		mpn_or_sku = ""
		# Give precedence to the mfg_pn if existing
		if mfg_pn:
			mpn_or_sku = mfg_pn
		else:
			mpn_or_sku = sku

		url = 'http://octopart.com/api/v3/parts/match?'
		url += '&queries=[{{"mpn_or_sku":"{0}"}}]'.format(mpn_or_sku)
		url += '&apikey={0}'.format(api_key)
		
		#frappe.msgprint(_("{0}").format(url))
		
		data = urllib.urlopen(url).read()
		response = json.loads(data)
		
		#frappe.msgprint(_("{0}").format(response))
		
		found = 0

		item.rate = 0
		found_seller = False
		if 'results' in response:
			for result in response['results']:
				for item_result in result['items']:
					# If we have a manufacturer (not mfg is false) only match the same manufacturer, otherwise all
					if item_result['manufacturer']['name'] == mfg or not mfg:
						for offer in item_result['offers']:
							if offer['seller']['name'] == supplier:
								found_seller = True
								if sq.currency in offer['prices']:
									for qty_rate in offer['prices'][sq.currency]:
										if qty_rate[0] <= item.qty:
											if item.rate == 0:
												item.rate = qty_rate[1]
											elif qty_rate[1] < item.rate:
												item.rate = qty_rate[1]

		if not found_seller:
			frappe.msgprint(_("{0} does not supply {1}. Please check that the supplier name matches the Octopart name list exactly").format(supplier, item.item_name))
		elif item.rate > 0:
			frappe.msgprint(_("Best rate that {0} supplies item {1} at is {2}").format(sq.supplier, item.item_code,item.rate))
		else:
			frappe.msgprint(_("Could not find currency {0} for {1}.").format(sq.currency,item.item_name))

	sq.save()

@frappe.whitelist()
def octopart_seller(seller):
	api_key = frappe.db.get_single_value('OctoERP Settings', "api_key")
	url = 'http://octopart.com/api/v3/sellers/search?'
	url += 'q=*{0}*'.format(seller)
	url += '&sortby=name%20asc'.format(seller)
	url += '&apikey={0}'.format(api_key)

	seller_list = []
	data = urllib.urlopen(url).read()
	response = json.loads(data)
	if 'results' in response:
		for result in response['results']:
			item_result = result.get('item')
			seller_list.append(item_result.get('name'))
			frappe.msgprint(item_result.get('name'))
	if not seller_list:
		frappe.msgprint(_("Could not find any supplier with this name: {0}".format(str(response))))
	return seller_list
