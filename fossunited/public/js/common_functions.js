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


// from https://github.com/knadh/autocomp.js

function autocomp(el, options = {}) {
	const defaults = {
		onQuery: null, onNavigate: null, onSelect: null, onRender: null, debounce: 100, autoSelect: true
	};

	const opt = { ...defaults, ...options };
	let box, cur = opt.autoSelect ? 0 : -1, items = [], val, req;

	// Disable browser's default autocomplete behaviour on the input.
	el.autocomplete = "off";

	// Attach all the events required for the interactions in one go.
	["input", "keydown", "blur"].forEach(k => el.addEventListener(k, handleEvent));

	function handleEvent(e) {
		if (e.type === "keydown" && !handleKeydown(e)) {
			return;
		};

		if (e.type === "blur") {
			destroy();
			return;
		}

		if (e.target.value === "") {
			destroy();
			val = null;
			return;
		}

		if (e.target.value === val && box) {
			return;
		};

		val = e.target.value;

		// Clear (debounce) any existing pending requests and queue
		// the next search request.
		clearTimeout(req);
		req = setTimeout(query, opt.debounce);
	}

	function handleKeydown(e) {
		if (!box) {
			return (e.keyCode === 38 || e.keyCode === 40) ? true : false;
		}

		switch (e.keyCode) {
			case 38: return navigate(-1, e); // Up arrow.
			case 40: return navigate(1, e); // Down arrow
			case 9: // Tab
				e.preventDefault();
				select(cur);
				destroy();
				return;
			case 13: // Enter
				select(cur);
				destroy();
				return;
			case 27: // Escape.
				destroy();
				return;
		}
	}

	async function query() {
		if (!val) {
			return;
		}

		items = await opt.onQuery(val);
		if (!items.length) {
			destroy();
			return;
		}

		if (!box) {
			createBox();
		}

		renderResults();
	}

	function createBox() {
		box = document.createElement("div");
		Object.assign(box.style, {
			width: window.getComputedStyle(el).width,
			position: "absolute",
			left: `${el.offsetLeft}px`,
			top: `${el.offsetTop + el.offsetHeight}px`
		});

		box.classList.add("autocomp");
		el.parentNode.insertBefore(box, el.nextSibling);
	}

	function renderResults() {
		box.innerHTML = "";

		items.forEach((item, idx) => {
			const div = document.createElement("div");
			div.classList.add("autocomp-item");

			// If there's a custom renderer callback, use it, else, simply insert the value/text as-is.
			opt.onRender ? div.appendChild(opt.onRender(item)) : div.innerText = item;
			if (idx === cur) {
				div.classList.add("autocomp-sel");
			}

			div.addEventListener("mousedown", () => select(idx));
			box.appendChild(div);
		});
	}

	function navigate(direction, e) {
		e.preventDefault();

		// Remove the previous item's highlight;
		const prev = box.querySelector(`:nth-child(${cur + 1})`);
		prev && prev.classList.remove("autocomp-sel");

		// Increment the cursor and highlight the next item, cycled between [0, n].
		cur = (cur + direction + items.length) % items.length;
		box.querySelector(`:nth-child(${cur + 1})`).classList.add("autocomp-sel");
	}

	function select(idx) {
		if (!opt.onSelect) {
			return;
		}

		val = opt.onSelect(items[idx]);
		el.value = val || items[idx];
	}

	function destroy() {
		items = [];
		cur = opt.autoSelect ? 0 : -1;
		if (box) {
			box.remove();
			box = null;
		}
	}
}
