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


function makeQuill(
	id,
	toolbarOptions=[
	[{ 'header': [1, 2, 3, 4, 5, 6, false] }],
	['bold', 'italic', 'underline', 'strike'],
	['blockquote', 'code-block'],
	[{ 'list': 'ordered'}, { 'list': 'bullet' }],
	[{ 'script': 'sub'}, { 'script': 'super' }],
	[{ 'indent': '-1'}, { 'indent': '+1' }],
	[{ 'direction': 'rtl' }],
	[{ 'color': [] }, { 'background': [] }],
	[{ 'align': [] }],
	['clean']])
	{
		let quill = new Quill(`${id}`, {
			modules: {
				toolbar: toolbarOptions
			},
			theme: 'snow'
		});
	return quill;
}
