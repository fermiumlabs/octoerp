## Octo-ERP

App for using Octo-part to look up part pricing and availability

### Install

Run the following commands to install:

	bench get-app octoerp https://github.com/bcornwellmott/octoerp.git
	bench --site myErpWebsite.com install-app octoerp
	
Go to Setup > Custom Script. Add a new custom script for Doctype "Supplier Quotation" with the following content:

	frappe.ui.form.on("Supplier Quotation",{
		refresh: function(frm) {
			frm.add_custom_button(__("Octopart Lookup"), function(foo) {

					frappe.call({
						method:"octoerp.octo_erp.octo_erp.octopart_lookup",
						args: {
							sq_number: cur_frm.doc.name
						}, 
						callback: function(r) { 
							frm.reload_doc();

						}
					});
			});
		}
	});
	
(It's also a good idea to add a comment with a link to this repository)

Go to [Octopart API](https://octopart.com/api/dashboard) and register a new api key. It's a short, alphanumerical string.

Go to the newly-installed Octo-ERP module > Setup. Insert your API key and save.
You can use the supplier lookup to check the exact name of a supplier. For example, if you search "Tme" and look it up, it will return "TME", if you look up "mouser" it will return "Mouser".

You can also check them [here](https://octopart.com/distributors).

### Usage
	
The system will only look up items in a supplier quotation where the manufacturer's part number has been set.
		
There is a custom field in each supplier (under Additional Information) where you should plug in the supplier's Octopart Name (this may be different from the supplier name you have entered). 

=
#### License

MIT
