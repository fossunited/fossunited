// Copyright (c) 2024, Frappe x FOSSUnited and contributors
// For license information, please see license.txt

frappe.ui.form.on("Razorpay Payment", {
	refresh(frm) {
        if (frm.doc.status === "Captured") {
            frm.add_custom_button("Refund", () => {
                frm.call("refund").then(({message}) => {
                    if (message != "failed") {
                        frappe.show_alert("Refund Processed")
                        frm.refresh()
                    }
                })
            })
        }
	},
});
