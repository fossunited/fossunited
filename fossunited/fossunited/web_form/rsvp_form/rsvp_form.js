frappe.ready(function() {
	replace_breadcrumb_link()
	handle_rsvp_edit()

	frappe.web_form.after_save = () => {
        redirect_to_event_page()
	}
})

function redirect_to_event_page(){
    frappe.call({
        method: "frappe.client.get",
        args: {
            doctype: "FOSS Chapter Event",
            name: frappe.web_form.doc.event,
        },
        callback: (r)=>{
            setTimeout(() => {
                window.location.href = "/" + r.message.route;
            }, 2000);
        },
    })
}

function replace_breadcrumb_link(){
    /*
        The breadcrumb link is a link to the event page. We want to replace it with just the event name.
    */
    let breadcrumb_link = document.getElementsByClassName("breadcrumb-item")[0].getElementsByTagName("a")[0]
    breadcrumb_link.replaceWith(...breadcrumb_link.childNodes)

    document.getElementsByClassName("breadcrumb-item")[0].style.fontWeight = "600"
}

function handle_rsvp_edit(){
    if(window.location.href.endsWith("/edit")){
        document.getElementsByClassName("web-form-title")[0].getElementsByTagName("h1")[0].innerText = "Edit RSVP"

        // Show Chapter and Event name in place of CFP name
        frappe.call({
            method: "frappe.client.get",
            args: {
                doctype: "FOSS Event RSVP",
                name: frappe.web_form.doc.name,
            },
            callback: (r) => {
                if (r.message) {
                    document.getElementsByClassName("web-form-title")[0].getElementsByTagName("p")[0].innerHTML = "</br><b>Chapter: </b>" + r.message.chapter + "</br><b>" + "Event: " + "</b>" + r.message.event_name
                }
            },
        })

        // change submit-btn text to "Update"
        document.getElementsByClassName("btn-primary")[0].innerText = "Update"

        // change description of the form
        document.getElementsByClassName("web-form-introduction")[0].getElementsByClassName("ql-editor")[0].getElementsByTagName("p")[0].innerText = "Edit the RSVP form for the event"
    }
}
