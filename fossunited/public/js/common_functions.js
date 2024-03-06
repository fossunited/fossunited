$(document).ready(function () {
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

	if (navItems.length === 0 || contentDivs.length === 0 ) return;

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

function validate_mandatory_fields(){
	// get all the input tags which have an attribute of required, and see if they are filled or not
	let inputs = document.querySelectorAll('input[required]');
	let selects = document.querySelectorAll('select[required]');
	let textareas = document.querySelectorAll('textarea[required]');

	// for all input, selects and textareas, check if they are filled or not. If they are not filled or selected then return false with message to fill that field
	let messages = [];

	for (let input of inputs){
		if (input.value === ""){
			let label = document.querySelector(`label[for="${input.id}"]`);
			let labelText = label ? label.innerText : input.name;
			messages.push(`<strong>${labelText}</strong> is a required field.<br>`);
		}
	}

	for (let select of selects){
		if (select.value === ""){
			let label = document.querySelector(`label[for="${select.id}"]`);
			let labelText = label ? label.innerText : select.name;
			messages.push(`<strong>${labelText}</strong> is a required field.<br>`);
		}
	}

	for (let textarea of textareas){
		if (textarea.value === ""){
			let label = document.querySelector(`label[for="${textarea.id}"]`);
			let labelText = label ? label.innerText : textarea.name;
			messages.push(`<strong>${labelText}</strong> is a required field.<br>`);
		}
	}

	if (messages.length > 0) {
		frappe.msgprint(messages.join('\n'));
		return false;
	}

	return true;
}

function check_if_logged_in(){
	if (frappe.session.user == 'Guest') {
		frappe.msgprint({
			message:__('You need to be logged in to edit this form.'),
			indicator:'red'
		}, 2);
		setTimeout(() => {
			window.location.href = `/login?redirect-to=${window.location.pathname}`;
		}, 2000);
		return false;
	}
	return true;
}

function check_if_profile_complete(){
	frappe.call({
		method: "fossunited.fossunited.utils.validate_profile_completion",
	}).then(r => {
		if (!r.message){
			frappe.msgprint({
				message:__('You need to complete your profile to edit this form.'),
				indicator:'red'
			}, 2);
			setTimeout(() => {
				window.location.href = `/create-foss-profile?redirect-to=${window.location.pathname}`;
			}, 2000);
			return false;
		}
		return true;
	})
}


function set_mandatory_asterisk(){
	// for every required input, textarea and select, add a red asterisk after their label. Wrap the label in a span to do this
	$('input[required], textarea[required], select[required], .ql-editor-custom[required]').each((idx, element) => {
		let label = $(element).prev('label');
		if($(element).hasClass('ql-editor-custom')){
			label = $(element).prev('div').prev('div');
		}

		label.html(`<span>${label.html()}</span>`);
		label.find('span').append('<span class="text-danger">*</span>');
	});
}
