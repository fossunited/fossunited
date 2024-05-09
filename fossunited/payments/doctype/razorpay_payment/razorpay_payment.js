// Copyright (c) 2024, Frappe x FOSSUnited and contributors
// For license information, please see license.txt

frappe.ui.form.on("Razorpay Payment", {
	refresh(frm) {
        if (frm.doc.status === "Captured") {
            frm.add_custom_button("Refund", () => {
                frappe.confirm("Are you sure you want to refund in full?", () => {
                    frm.call("refund").then(({message}) => {
                        if (message != "failed") {
                            frappe.show_alert("Refund Processed")
                            frm.refresh()
                        }
                    })
                })
            })
        }

        const btn = frm.add_custom_button("Sync Status", () => {
            frm.call({method: "sync_status", btn, doc: frm.doc}).then(() => {
                frappe.show_alert("Latest status synced")
                frm.refresh()
            })
        })
	},
});
