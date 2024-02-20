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

	// Onclick event for Event Cards (not needed anymore)
	// $(".event-card").click(function () {
	// 	window.location.pathname = "/" + $(this).data("route");
	// });

	// Horizontal Navbar Controls for Profile & Event Pages
	setNavbarControl();
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

function setNavbarControl(){
	let navItems = document.querySelectorAll('.horizontal-navbar--item');
	let contentDivs = document.querySelectorAll('.content-div');
	let activeNavItem = navItems[0];
	let activeContentDiv = contentDivs[0];

	contentDivs.forEach((contentDiv) => {
		contentDiv.classList.add('hide');
	});
	activeContentDiv.classList.remove('hide');
	activeNavItem.classList.add('active');

	navItems.forEach((navItem) => {
		navItem.addEventListener('click', () => {
			activeNavItem.classList.remove('active');
			activeContentDiv.classList.add('hide');
			navItem.classList.add('active');
			activeNavItem = navItem;
			activeContentDiv = document.querySelector(`#${navItem.id.split('-')[0]}`);
			activeContentDiv.classList.remove('hide');
		});
	});
}

function publish_form(e) {
	let doctype = $(e).data("doctype");
	let docname = $(e).data("docname");
	let parent = $(e).data("parent");
	frappe.call({
		method: "frappe.client.set_value",
		args: {
			doctype: `${doctype}`,
			name: `${docname}`,
			fieldname: "is_published",
			value: 1,
		},
		callback: (r) =>{
			$(`#${parent}`).load(window.location.href + ` #${parent}` );
		},
		error: (e) =>{
			console.log(e)
			frappe.msgprint(e.message)
		},
	});
}

function unpublish_form(e){
	let doctype = $(e).data("doctype");
	let docname = $(e).data("docname");
	let parent = $(e).data("parent");
	frappe.call({
		method: "frappe.client.set_value",
		args: {
			doctype: `${doctype}`,
			name: `${docname}`,
			fieldname: "is_published",
			value: 0,
		},
		callback: (r) =>{
			$(`#${parent}`).load(window.location.href + ` #${parent}` );
		},
		error: (e) =>{
			console.log(e)
			frappe.msgprint(e.message)
		},
	});
}
