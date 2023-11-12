$(document).ready(function () {
	window.full_name = frappe.get_cookie("full_name");
	var logged_in = frappe.is_user_logged_in();
	$("#website-login").toggleClass("hide", logged_in ? true : false);
	$("#website-post-login").toggleClass("hide", logged_in ? false : true);
	$(".logged-in").toggleClass("hide", logged_in ? false : true);

	frappe.bind_navbar_search();

	// switch to app link
	if (frappe.get_cookie("system_user") === "yes" && logged_in) {
		frappe.add_switch_to_desk();
	}

	frappe.render_user();

	$(document).trigger("page-change");
});
