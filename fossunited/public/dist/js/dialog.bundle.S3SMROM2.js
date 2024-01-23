(() => {
  var __defProp = Object.defineProperty;
  var __defProps = Object.defineProperties;
  var __getOwnPropDescs = Object.getOwnPropertyDescriptors;
  var __getOwnPropSymbols = Object.getOwnPropertySymbols;
  var __hasOwnProp = Object.prototype.hasOwnProperty;
  var __propIsEnum = Object.prototype.propertyIsEnumerable;
  var __defNormalProp = (obj, key, value) => key in obj ? __defProp(obj, key, { enumerable: true, configurable: true, writable: true, value }) : obj[key] = value;
  var __spreadValues = (a, b) => {
    for (var prop in b || (b = {}))
      if (__hasOwnProp.call(b, prop))
        __defNormalProp(a, prop, b[prop]);
    if (__getOwnPropSymbols)
      for (var prop of __getOwnPropSymbols(b)) {
        if (__propIsEnum.call(b, prop))
          __defNormalProp(a, prop, b[prop]);
      }
    return a;
  };
  var __spreadProps = (a, b) => __defProps(a, __getOwnPropDescs(b));

  // frappe/public/js/frappe/dom.js
  frappe.provide("frappe.dom");
  frappe.dom = {
    id_count: 0,
    freeze_count: 0,
    by_id: function(id) {
      return document.getElementById(id);
    },
    get_unique_id: function() {
      const id = "unique-" + frappe.dom.id_count;
      frappe.dom.id_count++;
      return id;
    },
    set_unique_id: function(ele) {
      var $ele = $(ele);
      if ($ele.attr("id")) {
        return $ele.attr("id");
      }
      var id = "unique-" + frappe.dom.id_count;
      $ele.attr("id", id);
      frappe.dom.id_count++;
      return id;
    },
    eval: function(txt) {
      if (!txt)
        return;
      var el = document.createElement("script");
      el.appendChild(document.createTextNode(txt));
      document.getElementsByTagName("head")[0].appendChild(el);
    },
    remove_script_and_style: function(txt) {
      const evil_tags = ["script", "style", "noscript", "title", "meta", "base", "head"];
      const parser = new DOMParser();
      const doc = parser.parseFromString(txt, "text/html");
      const body = doc.body;
      let found = !!doc.head.innerHTML;
      for (const tag of evil_tags) {
        for (const element of body.getElementsByTagName(tag)) {
          found = true;
          element.parentNode.removeChild(element);
        }
      }
      for (const element of body.getElementsByTagName("link")) {
        const relation = element.getAttribute("rel");
        if (relation && relation.toLowerCase().trim() === "stylesheet") {
          found = true;
          element.parentNode.removeChild(element);
        }
      }
      if (found) {
        return body.innerHTML;
      } else {
        return txt;
      }
    },
    is_element_in_viewport: function(el, tolerance = 0) {
      if (typeof jQuery === "function" && el instanceof jQuery) {
        el = el[0];
      }
      var rect = el.getBoundingClientRect();
      return rect.top + tolerance >= 0 && rect.left + tolerance >= 0 && rect.bottom - tolerance <= $(window).height() && rect.right - tolerance <= $(window).width();
    },
    is_element_in_modal(element) {
      return Boolean($(element).parents(".modal").length);
    },
    set_style: function(txt, id) {
      if (!txt)
        return;
      var se = document.createElement("style");
      se.type = "text/css";
      if (id) {
        var element = document.getElementById(id);
        if (element) {
          element.parentNode.removeChild(element);
        }
        se.id = id;
      }
      if (se.styleSheet) {
        se.styleSheet.cssText = txt;
      } else {
        se.appendChild(document.createTextNode(txt));
      }
      document.getElementsByTagName("head")[0].appendChild(se);
      return se;
    },
    add: function(parent, newtag, className, cs, innerHTML, onclick) {
      if (parent && parent.substr)
        parent = frappe.dom.by_id(parent);
      var c = document.createElement(newtag);
      if (parent)
        parent.appendChild(c);
      if (className) {
        if (newtag.toLowerCase() == "img")
          c.src = className;
        else
          c.className = className;
      }
      if (cs)
        frappe.dom.css(c, cs);
      if (innerHTML)
        c.innerHTML = innerHTML;
      if (onclick)
        c.onclick = onclick;
      return c;
    },
    css: function(ele, s) {
      if (ele && s) {
        $.extend(ele.style, s);
      }
      return ele;
    },
    activate: function($parent, $child, common_class, active_class = "active") {
      $parent.find(`.${common_class}.${active_class}`).removeClass(active_class);
      $child.addClass(active_class);
    },
    freeze: function(msg, css_class) {
      if (!$("#freeze").length) {
        var freeze = $('<div id="freeze" class="modal-backdrop fade"></div>').on("click", function() {
          if (cur_frm && cur_frm.cur_grid) {
            cur_frm.cur_grid.toggle_view();
            return false;
          }
        }).appendTo("#body");
        freeze.html(
          repl(
            '<div class="freeze-message-container"><div class="freeze-message"><p class="lead">%(msg)s</p></div></div>',
            { msg: msg || "" }
          )
        );
        setTimeout(function() {
          freeze.addClass("in");
        }, 1);
      } else {
        $("#freeze").addClass("in");
      }
      if (css_class) {
        $("#freeze").addClass(css_class);
      }
      frappe.dom.freeze_count++;
    },
    unfreeze: function() {
      if (!frappe.dom.freeze_count)
        return;
      frappe.dom.freeze_count--;
      if (!frappe.dom.freeze_count) {
        var freeze = $("#freeze").removeClass("in").remove();
      }
    },
    save_selection: function() {
      if (window.getSelection) {
        var sel = window.getSelection();
        if (sel.getRangeAt && sel.rangeCount) {
          var ranges = [];
          for (var i = 0, len = sel.rangeCount; i < len; ++i) {
            ranges.push(sel.getRangeAt(i));
          }
          return ranges;
        }
      } else if (document.selection && document.selection.createRange) {
        return document.selection.createRange();
      }
      return null;
    },
    restore_selection: function(savedSel) {
      if (savedSel) {
        if (window.getSelection) {
          var sel = window.getSelection();
          sel.removeAllRanges();
          for (var i = 0, len = savedSel.length; i < len; ++i) {
            sel.addRange(savedSel[i]);
          }
        } else if (document.selection && savedSel.select) {
          savedSel.select();
        }
      }
    },
    is_touchscreen: function() {
      return "ontouchstart" in window;
    },
    handle_broken_images(container) {
      $(container).find("img").on("error", (e) => {
        const $img = $(e.currentTarget);
        $img.addClass("no-image");
      });
    },
    scroll_to_bottom(container) {
      const $container = $(container);
      $container.scrollTop($container[0].scrollHeight);
    },
    file_to_base64(file_obj) {
      return new Promise((resolve) => {
        const reader = new FileReader();
        reader.onload = function() {
          resolve(reader.result);
        };
        reader.readAsDataURL(file_obj);
      });
    },
    scroll_to_section(section_name) {
      setTimeout(() => {
        const section = $(`a:contains("${section_name}")`);
        if (section.length) {
          if (section.parent().hasClass("collapsed")) {
            section.click();
          }
          frappe.ui.scroll(section.parent().parent());
        }
      }, 200);
    },
    pixel_to_inches(pixels) {
      const div = $(
        '<div id="dpi" style="height: 1in; width: 1in; left: 100%; position: fixed; top: 100%;"></div>'
      );
      div.appendTo(document.body);
      const dpi_x = document.getElementById("dpi").offsetWidth;
      const inches = pixels / dpi_x;
      div.remove();
      return inches;
    }
  };
  frappe.ellipsis = function(text, max) {
    if (!max)
      max = 20;
    text = cstr(text);
    if (text.length > max) {
      text = text.substr(0, max) + "...";
    }
    return text;
  };
  frappe.run_serially = function(tasks) {
    var result = Promise.resolve();
    tasks.forEach((task) => {
      if (task) {
        result = result.then ? result.then(task) : Promise.resolve();
      }
    });
    return result;
  };
  frappe.load_image = (src, onload, onerror, preprocess = () => {
  }) => {
    var tester = new Image();
    tester.onload = function() {
      onload(this);
    };
    tester.onerror = onerror;
    preprocess(tester);
    tester.src = src;
  };
  frappe.timeout = (seconds) => {
    return new Promise((resolve) => {
      setTimeout(() => resolve(), seconds * 1e3);
    });
  };
  frappe.scrub = function(text, spacer = "_") {
    return text.replace(/ /g, spacer).toLowerCase();
  };
  frappe.unscrub = function(txt) {
    return frappe.model.unscrub(txt);
  };
  frappe.get_data_pill = (label, target_id = null, remove_action = null, image = null) => {
    let data_pill_wrapper = $(`
		<button class="data-pill btn">
			<div class="flex align-center ellipsis">
				${image ? image : ""}
				<span class="pill-label">${label}</span>
			</div>
		</button>
	`);
    if (remove_action) {
      let remove_btn = $(`
			<span class="remove-btn cursor-pointer">
				${frappe.utils.icon("close", "sm")}
			</span>
		`).click(() => {
        remove_action(target_id || label, data_pill_wrapper);
      });
      data_pill_wrapper.append(remove_btn);
    }
    return data_pill_wrapper;
  };
  frappe.get_modal = function(title, content) {
    return $(`<div class="modal fade" style="overflow: auto;" tabindex="-1">
		<div class="modal-dialog">
			<div class="modal-content">
				<div class="modal-header">
					<div class="fill-width flex title-section">
						<span class="indicator hidden"></span>
						<h4 class="modal-title">${title}</h4>
					</div>
					<div class="modal-actions">
						<button class="btn btn-modal-minimize btn-link hide">
							${frappe.utils.icon("collapse")}
						</button>
						<button class="btn btn-modal-close btn-link" data-dismiss="modal">
							${frappe.utils.icon("close-alt", "sm", "close-alt")}
						</button>
					</div>
				</div>
				<div class="modal-body ui-front">${content}</div>
				<div class="modal-footer hide">
					<div class="custom-actions"></div>
					<div class="standard-actions">
						<button type="button" class="btn btn-secondary btn-sm hide btn-modal-secondary">
						</button>
						<button type="button" class="btn btn-primary btn-sm hide btn-modal-primary">
							${__("Confirm")}
						</button>
					</div>
				</div>
			</div>
		</div>
	</div>`);
  };
  frappe.is_online = function() {
    if (frappe.boot.developer_mode == 1) {
      return true;
    }
    if ("onLine" in navigator) {
      return navigator.onLine;
    }
    return true;
  };
  frappe.create_shadow_element = function(wrapper, html, css, js) {
    let random_id = "custom-block-" + frappe.utils.get_random(5).toLowerCase();
    class CustomBlock extends HTMLElement {
      constructor() {
        var _a, _b, _c, _d;
        super();
        let div = document.createElement("div");
        div.innerHTML = frappe.dom.remove_script_and_style(html);
        let link = document.createElement("link");
        link.rel = "stylesheet";
        link.href = frappe.assets.bundled_asset("desk.bundle.css");
        let style = document.createElement("style");
        style.textContent = css;
        let script = document.createElement("script");
        script.textContent = `
				(function() {
					let cname = ${JSON.stringify(random_id)};
					let root_element = document.querySelector(cname).shadowRoot;
					${js}
				})();
			`;
        this.attachShadow({ mode: "open" });
        (_a = this.shadowRoot) == null ? void 0 : _a.appendChild(link);
        (_b = this.shadowRoot) == null ? void 0 : _b.appendChild(div);
        (_c = this.shadowRoot) == null ? void 0 : _c.appendChild(style);
        (_d = this.shadowRoot) == null ? void 0 : _d.appendChild(script);
      }
    }
    if (!customElements.get(random_id)) {
      customElements.define(random_id, CustomBlock);
    }
    wrapper.innerHTML = `<${random_id}></${random_id}>`;
  };
  $(window).on("online", function() {
    if (document.hidden)
      return;
    frappe.show_alert({
      indicator: "green",
      message: __("You are connected to internet.")
    });
  });
  $(window).on("offline", function() {
    if (document.hidden)
      return;
    frappe.show_alert({
      indicator: "orange",
      message: __("Connection lost. Some features might not work.")
    });
  });

  // frappe/public/js/frappe/form/formatters.js
  frappe.provide("frappe.form.formatters");
  frappe.form.link_formatters = {};
  frappe.form.formatters = {
    _right: function(value, options) {
      if (options && (options.inline || options.only_value)) {
        return value;
      } else {
        return "<div style='text-align: right'>" + value + "</div>";
      }
    },
    _apply_custom_formatter: function(value, df) {
      if (df) {
        const std_df = frappe.meta.docfield_map[df.parent] && frappe.meta.docfield_map[df.parent][df.fieldname];
        if (std_df && std_df.formatter && typeof std_df.formatter === "function") {
          value = std_df.formatter(value, df);
        }
      }
      return value;
    },
    Data: function(value, df) {
      if (df && df.options == "URL") {
        if (!value)
          return;
        return `<a href="${value}" title="Open Link" target="_blank">${value}</a>`;
      }
      value = value == null ? "" : value;
      return frappe.form.formatters._apply_custom_formatter(value, df);
    },
    Autocomplete: function(value, df) {
      return __(frappe.form.formatters["Data"](value, df));
    },
    Select: function(value, df) {
      return __(frappe.form.formatters["Data"](value, df));
    },
    Float: function(value, docfield, options, doc) {
      var precision = docfield.precision || cint(frappe.boot.sysdefaults && frappe.boot.sysdefaults.float_precision) || null;
      if (docfield.options && docfield.options.trim()) {
        docfield.precision = precision;
        return frappe.form.formatters.Currency(value, docfield, options, doc);
      } else {
        if (!(options || {}).always_show_decimals && !is_null(value)) {
          var temp = cstr(value).split(".");
          if (temp[1] == void 0 || cint(temp[1]) === 0) {
            precision = 0;
          }
        }
        value = value == null || value === "" ? "" : value;
        return frappe.form.formatters._right(format_number(value, null, precision), options);
      }
    },
    Int: function(value, docfield, options) {
      if (cstr(docfield.options).trim() === "File Size") {
        return frappe.form.formatters.FileSize(value);
      }
      return frappe.form.formatters._right(value == null ? "" : cint(value), options);
    },
    Percent: function(value, docfield, options) {
      const precision = docfield.precision || cint(frappe.boot.sysdefaults && frappe.boot.sysdefaults.float_precision) || 2;
      return frappe.form.formatters._right(flt(value, precision) + "%", options);
    },
    Rating: function(value, docfield) {
      let rating_html = "";
      let number_of_stars = docfield.options || 5;
      value = value * number_of_stars;
      value = Math.round(value * 2) / 2;
      Array.from({ length: cint(number_of_stars) }, (_, i) => i + 1).forEach((i) => {
        rating_html += `<svg class="icon icon-md" data-rating=${i} viewBox="0 0 24 24" fill="none">
				<path class="right-half ${i <= (value || 0) ? "star-click" : ""}" d="M11.9987 3.00011C12.177 3.00011 12.3554 3.09303 12.4471 3.27888L14.8213 8.09112C14.8941 8.23872 15.0349 8.34102 15.1978 8.3647L20.5069 9.13641C20.917 9.19602 21.0807 9.69992 20.7841 9.9892L16.9421 13.7354C16.8243 13.8503 16.7706 14.0157 16.7984 14.1779L17.7053 19.4674C17.7753 19.8759 17.3466 20.1874 16.9798 19.9945L12.2314 17.4973C12.1586 17.459 12.0786 17.4398 11.9987 17.4398V3.00011Z" fill="var(--star-fill)" stroke="var(--star-fill)"/>
				<path class="left-half ${i <= (value || 0) || i - 0.5 == value ? "star-click" : ""}" d="M11.9987 3.00011C11.8207 3.00011 11.6428 3.09261 11.5509 3.27762L9.15562 8.09836C9.08253 8.24546 8.94185 8.34728 8.77927 8.37075L3.42887 9.14298C3.01771 9.20233 2.85405 9.70811 3.1525 9.99707L7.01978 13.7414C7.13858 13.8564 7.19283 14.0228 7.16469 14.1857L6.25116 19.4762C6.18071 19.8842 6.6083 20.1961 6.97531 20.0045L11.7672 17.5022C11.8397 17.4643 11.9192 17.4454 11.9987 17.4454V3.00011Z" fill="var(--star-fill)" stroke="var(--star-fill)"/>
			</svg>`;
      });
      return `<div class="rating">
			${rating_html}
		</div>`;
    },
    Currency: function(value, docfield, options, doc) {
      var currency = frappe.meta.get_field_currency(docfield, doc);
      let precision;
      if (typeof docfield.precision == "number") {
        precision = docfield.precision;
      } else {
        precision = cint(
          docfield.precision || frappe.boot.sysdefaults.currency_precision || 2
        );
      }
      if (precision > 2) {
        var parts = cstr(value).split(".");
        var decimals = parts.length > 1 ? parts[1] : "";
        if (decimals.length < 3 || decimals.length < precision) {
          const fraction = frappe.model.get_value(":Currency", currency, "fraction_units") || 100;
          if (decimals.length < cstr(fraction).length) {
            precision = cstr(fraction).length - 1;
          }
        }
      }
      value = value == null || value === "" ? "" : value;
      value = format_currency(value, currency, precision);
      if (options && options.only_value) {
        return value;
      } else {
        return frappe.form.formatters._right(value, options);
      }
    },
    Check: function(value) {
      return `<input type="checkbox" disabled
			class="disabled-${value ? "selected" : "deselected"}">`;
    },
    Link: function(value, docfield, options, doc) {
      var doctype = docfield._options || docfield.options;
      var original_value = value;
      let link_title = frappe.utils.get_link_title(doctype, value);
      if (link_title === value) {
        link_title = null;
      }
      if (value && value.match && value.match(/^['"].*['"]$/)) {
        value.replace(/^.(.*).$/, "$1");
      }
      if (options && (options.for_print || options.only_value)) {
        return link_title || value;
      }
      if (frappe.form.link_formatters[doctype]) {
        if (doc && doctype !== doc.doctype) {
          value = frappe.form.link_formatters[doctype](value, doc, docfield);
        }
      }
      if (!value) {
        return "";
      }
      if (value[0] == "'" && value[value.length - 1] == "'") {
        return value.substring(1, value.length - 1);
      }
      if (docfield && docfield.link_onclick) {
        return repl('<a onclick="%(onclick)s" href="#">%(value)s</a>', {
          onclick: docfield.link_onclick.replace(/"/g, "&quot;") + "; return false;",
          value
        });
      } else if (docfield && doctype) {
        if (frappe.model.can_read(doctype)) {
          const a = document.createElement("a");
          a.href = `/app/${encodeURIComponent(
            frappe.router.slug(doctype)
          )}/${encodeURIComponent(original_value)}`;
          a.dataset.doctype = doctype;
          a.dataset.name = original_value;
          a.dataset.value = original_value;
          a.innerText = __(options && options.label || link_title || value);
          return a.outerHTML;
        } else {
          return link_title || value;
        }
      } else {
        return link_title || value;
      }
    },
    Date: function(value) {
      if (!frappe.datetime.str_to_user) {
        return value;
      }
      if (value) {
        value = frappe.datetime.str_to_user(value, false, true);
        if (value === "Invalid date") {
          value = null;
        }
      }
      return value || "";
    },
    DateRange: function(value) {
      if (Array.isArray(value)) {
        return __("{0} to {1}", [
          frappe.datetime.str_to_user(value[0]),
          frappe.datetime.str_to_user(value[1])
        ]);
      } else {
        return value || "";
      }
    },
    Datetime: function(value) {
      if (value) {
        return moment(frappe.datetime.convert_to_user_tz(value)).format(
          frappe.boot.sysdefaults.date_format.toUpperCase() + " " + (frappe.boot.sysdefaults.time_format || "HH:mm:ss")
        );
      } else {
        return "";
      }
    },
    Text: function(value, df) {
      if (value) {
        var tags = ["<p", "<div", "<br", "<table"];
        var match = false;
        for (var i = 0; i < tags.length; i++) {
          if (value.match(tags[i])) {
            match = true;
            break;
          }
        }
        if (!match) {
          value = frappe.utils.replace_newlines(value);
        }
      }
      return frappe.form.formatters.Data(value, df);
    },
    Time: function(value) {
      if (value) {
        value = frappe.datetime.str_to_user(value, true);
      }
      return value || "";
    },
    Duration: function(value, docfield) {
      if (value) {
        let duration_options = frappe.utils.get_duration_options(docfield);
        value = frappe.utils.get_formatted_duration(value, duration_options);
      }
      return value || "0s";
    },
    LikedBy: function(value) {
      var html = "";
      $.each(JSON.parse(value || "[]"), function(i, v) {
        if (v)
          html += frappe.avatar(v);
      });
      return html;
    },
    Tag: function(value) {
      var html = "";
      $.each((value || "").split(","), function(i, v) {
        if (v)
          html += `
				<span
					class="data-pill btn-xs align-center ellipsis"
					style="background-color: var(--control-bg); box-shadow: none; margin-right: 4px;"
					data-field="_user_tags" data-label="${v}'">
					${v}
				</span>`;
      });
      return html;
    },
    Comment: function(value) {
      return value;
    },
    Assign: function(value) {
      var html = "";
      $.each(JSON.parse(value || "[]"), function(i, v) {
        if (v)
          html += '<span class="label label-warning" 				style="margin-right: 7px;"				data-field="_assign">' + v + "</span>";
      });
      return html;
    },
    SmallText: function(value) {
      return frappe.form.formatters.Text(value);
    },
    TextEditor: function(value) {
      let formatted_value = frappe.form.formatters.Text(value);
      try {
        if (!$(formatted_value).find(".ql-editor").length && !$(formatted_value).hasClass("ql-editor")) {
          formatted_value = `<div class="ql-editor read-mode">${formatted_value}</div>`;
        }
      } catch (e) {
        formatted_value = `<div class="ql-editor read-mode">${formatted_value}</div>`;
      }
      return formatted_value;
    },
    Code: function(value) {
      return "<pre>" + (value == null ? "" : $("<div>").text(value).html()) + "</pre>";
    },
    WorkflowState: function(value) {
      var workflow_state = frappe.get_doc("Workflow State", value);
      if (workflow_state) {
        return repl(
          "<span class='label label-%(style)s' 				data-workflow-state='%(value)s'				style='padding-bottom: 4px; cursor: pointer;'>				<i class='fa fa-small fa-white fa-%(icon)s'></i> %(value)s</span>",
          {
            value,
            style: workflow_state.style.toLowerCase(),
            icon: workflow_state.icon
          }
        );
      } else {
        return "<span class='label'>" + value + "</span>";
      }
    },
    Email: function(value) {
      return $("<div></div>").text(value).html();
    },
    FileSize: function(value) {
      value = cint(value);
      if (value > 1048576) {
        return (value / 1048576).toFixed(2) + "M";
      } else if (value > 1024) {
        return (value / 1024).toFixed(2) + "K";
      }
      return value;
    },
    TableMultiSelect: function(rows, df, options) {
      rows = rows || [];
      const meta = frappe.get_meta(df.options);
      const link_field = meta.fields.find((df2) => df2.fieldtype === "Link");
      const formatted_values = rows.map((row) => {
        const value = row[link_field.fieldname];
        return `<span class="text-nowrap">
				${frappe.format(value, link_field, options, row)}
			</span>`;
      });
      return formatted_values.join(", ");
    },
    Color: (value) => {
      return value ? `<div>
			<div class="selected-color" style="background-color: ${value}"></div>
			<span class="color-value">${value}</span>
		</div>` : "";
    },
    Icon: (value) => {
      return value ? `<div>
			<div class="selected-icon">${frappe.utils.icon(value, "md")}</div>
			<span class="icon-value">${value}</span>
		</div>` : "";
    },
    Attach: format_attachment_url,
    AttachImage: format_attachment_url
  };
  function format_attachment_url(url) {
    return url ? `<a href="${url}" target="_blank">${url}</a>` : "";
  }
  frappe.form.get_formatter = function(fieldtype) {
    if (!fieldtype)
      fieldtype = "Data";
    return frappe.form.formatters[fieldtype.replace(/ /g, "")] || frappe.form.formatters.Data;
  };
  frappe.format = function(value, df, options, doc) {
    if (!df)
      df = { fieldtype: "Data" };
    if (df.fieldname == "_user_tags")
      df = __spreadProps(__spreadValues({}, df), { fieldtype: "Tag" });
    var fieldtype = df.fieldtype || "Data";
    if (fieldtype === "Dynamic Link") {
      fieldtype = "Link";
      df._options = doc ? doc[df.options] : null;
    }
    var formatter = df.formatter || frappe.form.get_formatter(fieldtype);
    var formatted = formatter(value, df, options, doc);
    if (typeof formatted == "string")
      formatted = frappe.dom.remove_script_and_style(formatted);
    return formatted;
  };
  frappe.get_format_helper = function(doc) {
    var helper = {
      get_formatted: function(fieldname) {
        var df = frappe.meta.get_docfield(doc.doctype, fieldname);
        if (!df) {
          console.log("fieldname not found: " + fieldname);
        }
        return frappe.format(doc[fieldname], df, { inline: 1 }, doc);
      }
    };
    $.extend(helper, doc);
    return helper;
  };
  frappe.form.link_formatters["User"] = function(value, doc, docfield) {
    let full_name = doc && (doc.full_name || docfield && doc[`${docfield.fieldname}_full_name`]);
    return full_name || value;
  };

  // frappe/public/js/frappe/form/section.js
  var Section = class {
    constructor(parent, df, card_layout, layout) {
      this.layout = layout;
      this.card_layout = card_layout;
      this.parent = parent;
      this.df = df || {};
      this.columns = [];
      this.fields_list = [];
      this.fields_dict = {};
      this.make();
      if (this.df.label && this.df.collapsible && localStorage.getItem(df.css_class + "-closed")) {
        this.collapse();
      }
      this.row = {
        wrapper: this.wrapper
      };
      this.refresh();
    }
    make() {
      let make_card = this.card_layout;
      this.wrapper = $(`<div class="row
				${this.df.is_dashboard_section ? "form-dashboard-section" : "form-section"}
				${make_card ? "card-section" : ""}" data-fieldname="${this.df.fieldname}">
			`).appendTo(this.parent);
      if (this.df) {
        if (this.df.label) {
          this.make_head();
        }
        if (this.df.description) {
          this.description_wrapper = $(
            `<div class="col-sm-12 form-section-description">
						${__(this.df.description)}
					</div>`
          );
          this.wrapper.append(this.description_wrapper);
        }
        if (this.df.css_class) {
          this.wrapper.addClass(this.df.css_class);
        }
        if (this.df.hide_border) {
          this.wrapper.toggleClass("hide-border", true);
        }
      }
      this.body = $('<div class="section-body">').appendTo(this.wrapper);
      if (this.df.body_html) {
        this.body.append(this.df.body_html);
      }
    }
    make_head() {
      this.head = $(`
			<div class="section-head">
				${__(this.df.label)}
				<span class="ml-2 collapse-indicator mb-1"></span>
			</div>
		`);
      this.head.appendTo(this.wrapper);
      this.indicator = this.head.find(".collapse-indicator");
      this.indicator.hide();
      if (this.df.collapsible) {
        this.head.addClass("collapsible");
        this.collapse_link = this.head.on("click", () => {
          this.collapse();
        });
        this.set_icon();
        this.indicator.show();
      }
    }
    replace_field(fieldname, fieldobj) {
      var _a;
      if ((_a = this.fields_dict[fieldname]) == null ? void 0 : _a.df) {
        const olfldobj = this.fields_dict[fieldname];
        const idx = this.fields_list.findIndex((e) => e == olfldobj);
        this.fields_list.splice(idx, 1, fieldobj);
        this.fields_dict[fieldname] = fieldobj;
        fieldobj.section = this;
      }
    }
    add_field(fieldobj) {
      this.fields_list.push(fieldobj);
      this.fields_dict[fieldobj.df.fieldname] = fieldobj;
      fieldobj.section = this;
    }
    refresh(hide) {
      if (!this.df)
        return;
      hide = hide || this.df.hidden || this.df.hidden_due_to_dependency;
      this.wrapper.toggleClass("hide-control", !!hide);
    }
    collapse(hide) {
      if (!(this.head && this.body)) {
        return;
      }
      if (hide === void 0) {
        hide = !this.body.hasClass("hide");
      }
      this.body.toggleClass("hide", hide);
      this.head && this.head.toggleClass("collapsed", hide);
      this.set_icon(hide);
      this.fields_list.forEach((f) => f.on_section_collapse && f.on_section_collapse(hide));
      if (this.df.css_class)
        localStorage.setItem(this.df.css_class + "-closed", hide ? "1" : "");
    }
    set_icon(hide) {
      let indicator_icon = hide ? "es-line-down" : "es-line-up";
      this.indicator && this.indicator.html(frappe.utils.icon(indicator_icon, "sm", "mb-1"));
    }
    is_collapsed() {
      return this.body.hasClass("hide");
    }
    has_missing_mandatory() {
      let missing_mandatory = false;
      for (let j = 0, l = this.fields_list.length; j < l; j++) {
        const section_df = this.fields_list[j].df;
        if (section_df.reqd && this.layout.doc[section_df.fieldname] == null) {
          missing_mandatory = true;
          break;
        }
      }
      return missing_mandatory;
    }
    hide() {
      this.on_section_toggle(false);
    }
    show() {
      this.on_section_toggle(true);
    }
    on_section_toggle(show) {
      this.wrapper.toggleClass("hide-control", !show);
    }
  };

  // frappe/public/js/frappe/form/tab.js
  var Tab = class {
    constructor(layout, df, frm, tab_link_container, tabs_content) {
      this.layout = layout;
      this.df = df || {};
      this.frm = frm;
      this.doctype = this.frm.doctype;
      this.label = this.df && this.df.label;
      this.tab_link_container = tab_link_container;
      this.tabs_content = tabs_content;
      this.make();
      this.setup_listeners();
      this.refresh();
    }
    make() {
      const id = `${frappe.scrub(this.doctype, "-")}-${this.df.fieldname}`;
      this.tab_link = $(`
			<li class="nav-item">
				<a class="nav-link ${this.df.active ? "active" : ""}" id="${id}-tab"
					data-toggle="tab"
					data-fieldname="${this.df.fieldname}"
					href="#${id}"
					role="tab"
					aria-controls="${this.label}">
						${__(this.label)}
				</a>
			</li>
		`).appendTo(this.tab_link_container);
      this.wrapper = $(`<div class="tab-pane fade show ${this.df.active ? "active" : ""}"
			id="${id}" role="tabpanel" aria-labelledby="${id}-tab">`).appendTo(this.tabs_content);
    }
    refresh() {
      if (!this.df)
        return;
      let hide = this.df.hidden || this.df.hidden_due_to_dependency;
      if (!hide && this.frm && !this.frm.get_perm(this.df.permlevel || 0, "read")) {
        hide = true;
      }
      if (!hide) {
        hide = true;
        if (this.wrapper.find(
          ".form-section:not(.hide-control, .empty-section), .form-dashboard-section:not(.hide-control, .empty-section)"
        ).length) {
          hide = false;
        }
      }
      this.toggle(!hide);
    }
    toggle(show) {
      this.tab_link.toggleClass("hide", !show);
      this.wrapper.toggleClass("hide", !show);
      this.tab_link.toggleClass("show", show);
      this.wrapper.toggleClass("show", show);
      this.hidden = !show;
    }
    show() {
      this.tab_link.show();
    }
    hide() {
      this.tab_link.hide();
    }
    add_field(fieldobj) {
      fieldobj.tab = this;
    }
    replace_field(fieldobj) {
      fieldobj.tab = this;
    }
    set_active() {
      var _a, _b;
      this.tab_link.find(".nav-link").tab("show");
      this.wrapper.addClass("show");
      (_b = (_a = this.frm) == null ? void 0 : _a.set_active_tab) == null ? void 0 : _b.call(_a, this);
    }
    is_active() {
      return this.wrapper.hasClass("active");
    }
    is_hidden() {
      return this.wrapper.hasClass("hide") && this.tab_link.hasClass("hide");
    }
    setup_listeners() {
      this.tab_link.find(".nav-link").on("shown.bs.tab", () => {
        var _a, _b;
        (_b = this == null ? void 0 : (_a = this.frm).set_active_tab) == null ? void 0 : _b.call(_a, this);
      });
    }
  };

  // frappe/public/js/frappe/form/column.js
  var Column = class {
    constructor(section, df) {
      if (!df)
        df = {};
      this.df = df;
      this.section = section;
      this.section.columns.push(this);
      this.make();
      this.resize_all_columns();
    }
    make() {
      this.wrapper = $(`
			<div class="form-column" data-fieldname="${this.df.fieldname}">
				<form>
				</form>
			</div>
		`).appendTo(this.section.body);
      this.form = this.wrapper.find("form").on("submit", () => false);
      if (this.df.description) {
        $(`
				<p class="col-sm-12 form-column-description">
					${__(this.df.description)}
				</p>
			`).prependTo(this.wrapper);
      }
      if (this.df.label) {
        $(`
				<label class="column-label">
					${__(this.df.label)}
				</label>
			`).prependTo(this.wrapper);
      }
    }
    resize_all_columns() {
      let columns = this.section.wrapper.find(".form-column").length;
      let colspan = cint(12 / columns);
      if (columns == 5) {
        colspan = 20;
      }
      this.section.wrapper.find(".form-column").removeClass().addClass("form-column").addClass("col-sm-" + colspan);
    }
    add_field() {
    }
    refresh() {
      this.section.refresh();
    }
  };

  // frappe/public/js/frappe/form/layout.js
  frappe.ui.form.Layout = class Layout {
    constructor(opts) {
      this.views = {};
      this.pages = [];
      this.tabs = [];
      this.sections = [];
      this.page_breaks = [];
      this.sections_dict = {};
      this.fields_list = [];
      this.fields_dict = {};
      this.section_count = 0;
      this.column_count = 0;
      $.extend(this, opts);
    }
    make() {
      if (!this.parent && this.body) {
        this.parent = this.body;
      }
      this.wrapper = $('<div class="form-layout">').appendTo(this.parent);
      this.message = $('<div class="form-message hidden"></div>').appendTo(this.wrapper);
      this.page = $('<div class="form-page"></div>').appendTo(this.wrapper);
      if (!this.fields) {
        this.fields = this.get_doctype_fields();
      }
      if (this.is_tabbed_layout()) {
        this.setup_tabbed_layout();
      }
      this.setup_tab_events();
      this.frm && this.setup_tooltip_events();
      this.render();
    }
    setup_tabbed_layout() {
      $(`
			<div class="form-tabs-list">
				<ul class="nav form-tabs" id="form-tabs" role="tablist"></ul>
			</div>
		`).appendTo(this.page);
      this.tab_link_container = this.page.find(".form-tabs");
      this.tabs_content = $(`<div class="form-tab-content tab-content"></div>`).appendTo(
        this.page
      );
      this.setup_events();
    }
    get_doctype_fields() {
      let fields = [this.get_new_name_field()];
      if (this.doctype_layout) {
        fields = fields.concat(this.get_fields_from_layout());
      } else {
        fields = fields.concat(
          frappe.meta.sort_docfields(frappe.meta.docfield_map[this.doctype])
        );
      }
      return fields;
    }
    get_new_name_field() {
      return {
        parent: this.frm.doctype,
        fieldtype: "Data",
        fieldname: "__newname",
        reqd: 1,
        hidden: 1,
        label: __("Name"),
        get_status: function(field) {
          if (field.frm && field.frm.is_new() && field.frm.meta.autoname && ["prompt", "name"].includes(field.frm.meta.autoname.toLowerCase())) {
            return "Write";
          }
          return "None";
        }
      };
    }
    get_fields_from_layout() {
      const fields = [];
      for (let f of this.doctype_layout.fields) {
        const docfield = copy_dict(frappe.meta.docfield_map[this.doctype][f.fieldname]);
        docfield.label = f.label;
        fields.push(docfield);
      }
      return fields;
    }
    show_message(html, color) {
      if (this.message_color) {
        this.message.removeClass(this.message_color);
      }
      let close_message = $(`<div class="close-message">${frappe.utils.icon("close")}</div>`);
      this.message_color = color && ["yellow", "blue", "red", "green", "orange"].includes(color) ? color : "blue";
      if (html) {
        if (html.substr(0, 1) !== "<") {
          html = "<div>" + html + "</div>";
        }
        this.message.removeClass("hidden").addClass(this.message_color);
        $(html).appendTo(this.message);
        close_message.appendTo(this.message);
        close_message.on("click", () => this.message.empty().addClass("hidden"));
      } else {
        this.message.empty().addClass("hidden");
      }
    }
    render(new_fields) {
      let fields = new_fields || this.fields;
      this.section = null;
      this.column = null;
      if (this.no_opening_section() && !this.is_tabbed_layout()) {
        this.fields.unshift({ fieldtype: "Section Break" });
      }
      if (this.is_tabbed_layout()) {
        let default_tab = {
          label: __("Details"),
          fieldtype: "Tab Break",
          fieldname: "__details"
        };
        let first_field_visible = this.fields.find((element) => element.hidden == false);
        let first_tab = (first_field_visible == null ? void 0 : first_field_visible.fieldtype) === "Tab Break" ? first_field_visible : null;
        if (!first_tab) {
          this.fields.splice(0, 0, default_tab);
        } else {
          let newname_field = this.fields.find((df) => df.fieldname === "__newname");
          if (newname_field && newname_field.get_status(this) === "Write") {
            this.fields.splice(0, 1);
            this.fields.splice(1, 0, newname_field);
          }
        }
      }
      fields.forEach((df) => {
        switch (df.fieldtype) {
          case "Fold":
            this.make_page(df);
            break;
          case "Page Break":
            this.make_page_break();
            this.make_section(df);
            break;
          case "Section Break":
            this.make_section(df);
            break;
          case "Column Break":
            this.make_column(df);
            break;
          case "Tab Break":
            this.make_tab(df);
            break;
          default:
            this.make_field(df);
        }
      });
    }
    no_opening_section() {
      return this.fields[0] && this.fields[0].fieldtype != "Section Break" || !this.fields.length;
    }
    no_opening_tab() {
      return this.fields[1] && this.fields[1].fieldtype != "Tab Break" || !this.fields.length;
    }
    is_tabbed_layout() {
      return this.fields.find((f) => f.fieldtype === "Tab Break");
    }
    replace_field(fieldname, df, render) {
      var _a;
      df.fieldname = fieldname;
      if (this.fields_dict[fieldname] && this.fields_dict[fieldname].df) {
        const prev_fieldobj = this.fields_dict[fieldname];
        const fieldobj = this.init_field(df, prev_fieldobj.parent, render);
        prev_fieldobj.$wrapper.replaceWith(fieldobj.$wrapper);
        const idx = this.fields_list.findIndex((e) => e == prev_fieldobj);
        this.fields_list.splice(idx, 1, fieldobj);
        this.fields_dict[fieldname] = fieldobj;
        this.sections.forEach((section) => section.replace_field(fieldname, fieldobj));
        (_a = prev_fieldobj.tab) == null ? void 0 : _a.replace_field(fieldobj);
        this.refresh_fields([df]);
      }
    }
    make_field(df, colspan, render) {
      !this.section && this.make_section();
      !this.column && this.make_column();
      const parent = this.column.form.get(0);
      const fieldobj = this.init_field(df, parent, render);
      this.fields_list.push(fieldobj);
      this.fields_dict[df.fieldname] = fieldobj;
      this.section.add_field(fieldobj);
      this.column.add_field(fieldobj);
      if (this.current_tab) {
        this.current_tab.add_field(fieldobj);
      }
    }
    init_field(df, parent, render = false) {
      const fieldobj = frappe.ui.form.make_control({
        df,
        doctype: this.doctype,
        parent,
        frm: this.frm,
        render_input: render,
        doc: this.doc,
        layout: this
      });
      fieldobj.layout = this;
      return fieldobj;
    }
    make_page_break() {
      this.page = $('<div class="form-page page-break"></div>').appendTo(this.wrapper);
    }
    make_page(df) {
      let me = this;
      let head = $(`
			<div class="form-clickable-section text-center">
				<a class="btn-fold h6 text-muted">
					${__("Show more details")}
				</a>
			</div>
		`).appendTo(this.wrapper);
      this.page = $('<div class="form-page second-page hide"></div>').appendTo(this.wrapper);
      this.fold_btn = head.find(".btn-fold").on("click", function() {
        let page = $(this).parent().next();
        if (page.hasClass("hide")) {
          $(this).removeClass("btn-fold").html(__("Hide details"));
          page.removeClass("hide");
          frappe.utils.scroll_to($(this), true, 30);
          me.folded = false;
        } else {
          $(this).addClass("btn-fold").html(__("Show more details"));
          page.addClass("hide");
          me.folded = true;
        }
      });
      this.section = null;
      this.folded = true;
    }
    unfold() {
      this.fold_btn.trigger("click");
    }
    make_section(df = {}) {
      this.section_count++;
      if (!df.fieldname) {
        df.fieldname = `__section_${this.section_count}`;
        df.fieldtype = "Section Break";
      }
      this.section = new Section(
        this.current_tab ? this.current_tab.wrapper : this.page,
        df,
        this.card_layout,
        this
      );
      this.sections.push(this.section);
      this.sections_dict[df.fieldname] = this.section;
      if (df) {
        this.fields_dict[df.fieldname] = this.section;
        this.fields_list.push(this.section);
      }
      this.column = null;
    }
    make_column(df = {}) {
      this.column_count++;
      if (!df.fieldname) {
        df.fieldname = `__column_${this.section_count}`;
        df.fieldtype = "Column Break";
      }
      this.column = new Column(this.section, df);
      if (df && df.fieldname) {
        this.fields_list.push(this.column);
      }
    }
    make_tab(df) {
      this.section = null;
      let tab = new Tab(this, df, this.frm, this.tab_link_container, this.tabs_content);
      this.current_tab = tab;
      this.make_section({ fieldtype: "Section Break" });
      this.tabs.push(tab);
      return tab;
    }
    refresh(doc) {
      if (doc)
        this.doc = doc;
      if (this.frm) {
        this.wrapper.find(".empty-form-alert").remove();
      }
      this.attach_doc_and_docfields(true);
      if (this.frm && this.frm.wrapper) {
        $(this.frm.wrapper).trigger("refresh-fields");
      }
      this.refresh_dependency();
      this.refresh_sections();
      if (this.frm) {
        this.refresh_section_collapse();
      }
      if (document.activeElement) {
        if (document.activeElement.tagName == "INPUT" && this.is_numeric_field_active()) {
          document.activeElement.select();
        }
      }
    }
    is_numeric_field_active() {
      const control = $(document.activeElement).closest(".frappe-control");
      const fieldtype = (control.data() || {}).fieldtype;
      return frappe.model.numeric_fieldtypes.includes(fieldtype);
    }
    refresh_sections() {
      this.wrapper.find(".form-section:not(.hide-control)").each(function() {
        const section = $(this).removeClass("empty-section visible-section");
        if (section.find(".frappe-control:not(.hide-control)").length) {
          section.addClass("visible-section");
        } else if (section.parent().hasClass("tab-pane") || section.parent().hasClass("form-page")) {
          section.addClass("empty-section");
        }
      });
      this.is_tabbed_layout() && this.refresh_tabs();
    }
    refresh_tabs() {
      for (let tab of this.tabs) {
        tab.refresh();
      }
      const visible_tabs = this.tabs.filter((tab) => !tab.hidden);
      if (visible_tabs && visible_tabs.length == 1) {
        visible_tabs[0].tab_link.toggleClass("hide show");
      }
      this.set_tab_as_active();
    }
    select_tab(label_or_fieldname) {
      var _a;
      for (let tab of this.tabs) {
        if (tab.label.toLowerCase() === label_or_fieldname.toLowerCase() || ((_a = tab.df.fieldname) == null ? void 0 : _a.toLowerCase()) === label_or_fieldname.toLowerCase()) {
          tab.set_active();
          return;
        }
      }
    }
    set_tab_as_active() {
      var _a, _b;
      let frm_active_tab = (_b = this == null ? void 0 : (_a = this.frm).get_active_tab) == null ? void 0 : _b.call(_a);
      if (frm_active_tab) {
        frm_active_tab.set_active();
      } else if (this.tabs.length) {
        let first_visible_tab = this.tabs.find((tab) => !tab.is_hidden());
        first_visible_tab && first_visible_tab.set_active();
      }
    }
    refresh_fields(fields) {
      let fieldnames = fields.map((field) => {
        if (field.fieldname)
          return field.fieldname;
      });
      this.fields_list.map((fieldobj) => {
        if (fieldnames.includes(fieldobj.df.fieldname)) {
          fieldobj.refresh();
          if (fieldobj.df["default"]) {
            fieldobj.set_input(fieldobj.df["default"]);
          }
        }
      });
    }
    add_fields(fields) {
      this.render(fields);
      this.refresh_fields(fields);
    }
    refresh_section_collapse() {
      if (!(this.sections && this.sections.length))
        return;
      for (let i = 0; i < this.sections.length; i++) {
        let section = this.sections[i];
        let df = section.df;
        if (df && df.collapsible) {
          let collapse = true;
          if (df.collapsible_depends_on) {
            collapse = !this.evaluate_depends_on_value(df.collapsible_depends_on);
          }
          if (collapse && section.has_missing_mandatory()) {
            collapse = false;
          }
          section.collapse(collapse);
        }
      }
    }
    attach_doc_and_docfields(refresh) {
      let me = this;
      for (let i = 0, l = this.fields_list.length; i < l; i++) {
        let fieldobj = this.fields_list[i];
        if (me.doc) {
          fieldobj.doc = me.doc;
          fieldobj.doctype = me.doc.doctype;
          fieldobj.docname = me.doc.name;
          fieldobj.df = frappe.meta.get_docfield(me.doc.doctype, fieldobj.df.fieldname, me.doc.name) || fieldobj.df;
        }
        refresh && fieldobj.df && fieldobj.refresh && fieldobj.refresh();
      }
    }
    refresh_section_count() {
      this.wrapper.find(".section-count-label:visible").each(function(i) {
        $(this).html(i + 1);
      });
    }
    setup_events() {
      let last_scroll = 0;
      let tabs_list = $(".form-tabs-list");
      let tabs_content = this.tabs_content[0];
      if (!tabs_list.length)
        return;
      $(window).scroll(
        frappe.utils.throttle(() => {
          let current_scroll = document.documentElement.scrollTop;
          if (current_scroll > 0 && last_scroll <= current_scroll) {
            tabs_list.removeClass("form-tabs-sticky-down");
            tabs_list.addClass("form-tabs-sticky-up");
          } else {
            tabs_list.removeClass("form-tabs-sticky-up");
            tabs_list.addClass("form-tabs-sticky-down");
          }
          last_scroll = current_scroll;
        }, 500)
      );
      this.tab_link_container.off("click").on("click", ".nav-link", (e) => {
        e.preventDefault();
        e.stopImmediatePropagation();
        $(e.currentTarget).tab("show");
        if (tabs_content.getBoundingClientRect().top < 100) {
          tabs_content.scrollIntoView();
          setTimeout(() => {
            $(".page-head").css("top", "-15px");
            $(".form-tabs-list").removeClass("form-tabs-sticky-down");
            $(".form-tabs-list").addClass("form-tabs-sticky-up");
          }, 3);
        }
      });
    }
    setup_tab_events() {
      this.wrapper.on("keydown", (ev) => {
        if (ev.which == 9) {
          let current = $(ev.target);
          let doctype = current.attr("data-doctype");
          let fieldname = current.attr("data-fieldname");
          if (doctype) {
            return this.handle_tab(doctype, fieldname, ev.shiftKey);
          }
        }
      });
    }
    setup_tooltip_events() {
      $(document).on("keydown", (e) => {
        if (e.altKey) {
          this.wrapper.addClass("show-tooltip");
        }
      });
      $(document).on("keyup", (e) => {
        if (!e.altKey) {
          this.wrapper.removeClass("show-tooltip");
        }
      });
      this.frm.page && frappe.ui.keys.add_shortcut({
        shortcut: "alt+hover",
        page: this.frm.page,
        description: __("Show Fieldname (click to copy on clipboard)")
      });
    }
    handle_tab(doctype, fieldname, shift) {
      let grid_row = null, prev = null, fields = this.fields_list, focused = false;
      if (doctype != this.doctype) {
        grid_row = this.get_open_grid_row();
        if (!grid_row || !grid_row.layout) {
          return;
        }
        fields = grid_row.layout.fields_list;
      }
      for (let i = 0, len = fields.length; i < len; i++) {
        if (fields[i].df.fieldname == fieldname) {
          if (shift) {
            if (prev) {
              this.set_focus(prev);
            } else {
              $(this.primary_button).focus();
            }
            break;
          }
          if (i < len - 1) {
            focused = this.focus_on_next_field(i, fields);
          }
          if (focused) {
            break;
          }
        }
        if (this.is_visible(fields[i]))
          prev = fields[i];
      }
      if (!focused) {
        if (grid_row) {
          if (grid_row.doc.idx == grid_row.grid.grid_rows.length) {
            grid_row.toggle_view(false, function() {
              grid_row.grid.frm.layout.handle_tab(
                grid_row.grid.df.parent,
                grid_row.grid.df.fieldname
              );
            });
          } else {
            grid_row.grid.grid_rows[grid_row.doc.idx].toggle_view(true);
          }
        } else if (!shift) {
          $(this.primary_button).focus();
        }
      }
      return false;
    }
    focus_on_next_field(start_idx, fields) {
      for (let i = start_idx + 1, len = fields.length; i < len; i++) {
        let field = fields[i];
        if (this.is_visible(field)) {
          if (field.df.fieldtype === "Table") {
            if (!(field.grid.grid_rows && field.grid.grid_rows.length)) {
              field.grid.add_new_row();
            }
            field.grid.grid_rows[0].show_form();
            return true;
          } else if (!in_list(frappe.model.no_value_type, field.df.fieldtype)) {
            this.set_focus(field);
            return true;
          }
        }
      }
    }
    is_visible(field) {
      return field.disp_status === "Write" && field.df && "hidden" in field.df && !field.df.hidden;
    }
    set_focus(field) {
      if (field.tab) {
        field.tab.set_active();
      }
      if (field.df.fieldtype == "Table") {
        if (!field.grid.grid_rows.length) {
          field.grid.add_new_row(1);
        } else {
          field.grid.grid_rows[0].toggle_view(true);
        }
      } else if (field.editor) {
        field.editor.set_focus();
      } else if (field.$input) {
        field.$input.focus();
      }
    }
    get_open_grid_row() {
      return $(".grid-row-open").data("grid_row");
    }
    refresh_dependency() {
      let has_dep = false;
      const fields = this.fields_list.concat(this.tabs);
      for (let fkey in fields) {
        let f = fields[fkey];
        if (f.df.depends_on || f.df.mandatory_depends_on || f.df.read_only_depends_on) {
          has_dep = true;
          break;
        }
      }
      if (!has_dep)
        return;
      for (let i = fields.length - 1; i >= 0; i--) {
        let f = fields[i];
        f.guardian_has_value = true;
        if (f.df.depends_on) {
          f.guardian_has_value = this.evaluate_depends_on_value(f.df.depends_on);
          if (f.guardian_has_value) {
            if (f.df.hidden_due_to_dependency) {
              f.df.hidden_due_to_dependency = false;
              f.refresh();
            }
          } else {
            if (!f.df.hidden_due_to_dependency) {
              f.df.hidden_due_to_dependency = true;
              f.refresh();
            }
          }
        }
        if (f.df.mandatory_depends_on) {
          this.set_dependant_property(f.df.mandatory_depends_on, f.df.fieldname, "reqd");
        }
        if (f.df.read_only_depends_on) {
          this.set_dependant_property(
            f.df.read_only_depends_on,
            f.df.fieldname,
            "read_only"
          );
        }
      }
      this.refresh_section_count();
    }
    set_dependant_property(condition, fieldname, property) {
      let set_property = this.evaluate_depends_on_value(condition);
      let value = set_property ? 1 : 0;
      let form_obj;
      if (this.frm) {
        form_obj = this.frm;
      } else if (this.is_dialog || this.doctype === "Web Form") {
        form_obj = this;
      }
      if (form_obj) {
        if (this.doc && this.doc.parent && this.doc.parentfield) {
          form_obj.setting_dependency = true;
          form_obj.set_df_property(
            this.doc.parentfield,
            property,
            value,
            this.doc.parent,
            fieldname,
            this.doc.name
          );
          form_obj.setting_dependency = false;
          this.fields_dict[fieldname] && this.fields_dict[fieldname].refresh();
        } else {
          form_obj.set_df_property(fieldname, property, value);
        }
      }
    }
    evaluate_depends_on_value(expression) {
      let out = null;
      let doc = this.doc;
      if (!doc && this.get_values) {
        doc = this.get_values(true);
      }
      if (!doc) {
        return;
      }
      let parent = this.frm ? this.frm.doc : this.doc || null;
      if (typeof expression === "boolean") {
        out = expression;
      } else if (typeof expression === "function") {
        out = expression(doc);
      } else if (expression.substr(0, 5) == "eval:") {
        try {
          out = frappe.utils.eval(expression.substr(5), { doc, parent });
          if (parent && parent.istable && expression.includes("is_submittable")) {
            out = true;
          }
        } catch (e) {
          frappe.throw(__('Invalid "depends_on" expression'));
        }
      } else if (expression.substr(0, 3) == "fn:" && this.frm) {
        out = this.frm.script_manager.trigger(
          expression.substr(3),
          this.doctype,
          this.docname
        );
      } else {
        var value = doc[expression];
        if ($.isArray(value)) {
          out = !!value.length;
        } else {
          out = !!value;
        }
      }
      return out;
    }
  };

  // frappe/public/js/frappe/ui/field_group.js
  frappe.provide("frappe.ui");
  frappe.ui.FieldGroup = class FieldGroup extends frappe.ui.form.Layout {
    constructor(opts) {
      super(opts);
      this.dirty = false;
      $.each(this.fields || [], function(i, f) {
        if (!f.fieldname && f.label) {
          f.fieldname = f.label.replace(/ /g, "_").toLowerCase();
        }
      });
      if (this.values) {
        this.set_values(this.values);
      }
    }
    make() {
      let me = this;
      if (this.fields) {
        super.make();
        this.refresh();
        $.each(this.fields_list, function(i, field) {
          if (field.df["default"]) {
            let def_value = field.df["default"];
            if (def_value == "Today" && field.df["fieldtype"] == "Date") {
              def_value = frappe.datetime.get_today();
            }
            field.set_input(def_value);
            me.refresh_dependency();
          }
        });
        if (!this.no_submit_on_enter) {
          this.catch_enter_as_submit();
        }
        $(this.wrapper).find("input, select").on("change awesomplete-selectcomplete", () => {
          this.dirty = true;
          frappe.run_serially([
            () => frappe.timeout(0.1),
            () => me.refresh_dependency()
          ]);
        });
      }
    }
    focus_on_first_input() {
      if (this.no_focus)
        return;
      $.each(this.fields_list, function(i, f) {
        if (!in_list(["Date", "Datetime", "Time", "Check"], f.df.fieldtype) && f.set_focus) {
          f.set_focus();
          return false;
        }
      });
    }
    catch_enter_as_submit() {
      let me = this;
      $(this.body).find('input[type="text"], input[type="password"], select').keypress(function(e) {
        if (e.which == 13) {
          if (me.has_primary_action) {
            e.preventDefault();
            me.get_primary_btn().trigger("click");
          }
        }
      });
    }
    get_input(fieldname) {
      let field = this.fields_dict[fieldname];
      if (!field)
        return "";
      return $(field.txt ? field.txt : field.input);
    }
    get_field(fieldname) {
      return this.fields_dict[fieldname];
    }
    get_values(ignore_errors, check_invalid) {
      let ret = {};
      let errors = [];
      let invalid = [];
      for (let key in this.fields_dict) {
        let f = this.fields_dict[key];
        if (f.get_value) {
          let v = f.get_value();
          if (f.df.reqd && is_null(typeof v === "string" ? strip_html(v) : v))
            errors.push(__(f.df.label));
          if (f.df.reqd && f.df.fieldtype === "Text Editor" && is_null(strip_html(cstr(v))))
            errors.push(__(f.df.label));
          if (!is_null(v))
            ret[f.df.fieldname] = v;
        }
        if (this.is_dialog && f.df.reqd && !f.value) {
          f.refresh_input();
        }
        if (f.df.invalid) {
          invalid.push(__(f.df.label));
        }
      }
      if (errors.length && !ignore_errors) {
        frappe.msgprint({
          title: __("Missing Values Required"),
          message: __("Following fields have missing values:") + "<br><br><ul><li>" + errors.join("<li>") + "</ul>",
          indicator: "orange"
        });
        return null;
      }
      if (invalid.length && check_invalid) {
        frappe.msgprint({
          title: __("Inavlid Values"),
          message: __("Following fields have invalid values:") + "<br><br><ul><li>" + invalid.join("<li>") + "</ul>",
          indicator: "orange"
        });
        return null;
      }
      return ret;
    }
    get_value(key) {
      let f = this.fields_dict[key];
      return f && (f.get_value ? f.get_value() : null);
    }
    set_value(key, val) {
      return new Promise((resolve) => {
        let f = this.fields_dict[key];
        if (f) {
          f.set_value(val).then(() => {
            var _a;
            (_a = f.set_input) == null ? void 0 : _a.call(f, val);
            this.refresh_dependency();
            resolve();
          });
        } else {
          resolve();
        }
      });
    }
    has_field(fieldname) {
      return !!this.fields_dict[fieldname];
    }
    set_input(key, val) {
      return this.set_value(key, val);
    }
    set_values(dict) {
      let promises = [];
      for (let key in dict) {
        if (this.fields_dict[key]) {
          promises.push(this.set_value(key, dict[key]));
        }
      }
      return Promise.all(promises);
    }
    clear() {
      for (let key in this.fields_dict) {
        let f = this.fields_dict[key];
        if (f && f.set_input) {
          f.set_input(f.df["default"] || "");
        }
      }
    }
    set_df_property(fieldname, prop, value) {
      if (!fieldname) {
        return;
      }
      const field = this.get_field(fieldname);
      field.df[prop] = value;
      field.refresh();
    }
  };

  // frappe/public/js/frappe/form/link_selector.js
  frappe.ui.form.LinkSelector = class LinkSelector {
    constructor(opts) {
      $.extend(this, opts);
      var me = this;
      if (this.doctype != "[Select]") {
        frappe.model.with_doctype(this.doctype, function(r) {
          me.make();
        });
      } else {
        this.make();
      }
    }
    make() {
      var me = this;
      this.start = 0;
      this.page_length = 10;
      this.dialog = new frappe.ui.Dialog({
        title: __("Select {0}", [this.doctype == "[Select]" ? __("value") : __(this.doctype)]),
        fields: [
          {
            fieldtype: "Data",
            fieldname: "txt",
            label: __("Beginning with"),
            description: __("You can use wildcard %")
          },
          {
            fieldtype: "HTML",
            fieldname: "results"
          },
          {
            fieldtype: "Button",
            fieldname: "more",
            label: __("More"),
            click: () => {
              me.start += me.page_length;
              me.search();
            }
          }
        ],
        primary_action_label: __("Search"),
        primary_action: function() {
          me.start = 0;
          me.search();
        }
      });
      if (this.txt)
        this.dialog.fields_dict.txt.set_input(this.txt);
      this.dialog.get_input("txt").on("keypress", function(e) {
        if (e.which === 13) {
          me.start = 0;
          me.search();
        }
      });
      this.dialog.show();
      this.search();
    }
    search() {
      var args = {
        txt: this.dialog.fields_dict.txt.get_value(),
        searchfield: "name",
        start: this.start,
        page_length: this.page_length
      };
      var me = this;
      if (this.target.set_custom_query) {
        this.target.set_custom_query(args);
      }
      if (this.target.is_grid && this.target.fieldinfo[this.fieldname] && this.target.fieldinfo[this.fieldname].get_query) {
        $.extend(args, this.target.fieldinfo[this.fieldname].get_query(cur_frm.doc));
      }
      frappe.link_search(
        this.doctype,
        args,
        function(results) {
          var parent = me.dialog.fields_dict.results.$wrapper;
          if (args.start === 0) {
            parent.empty();
          }
          if (results.length) {
            for (const v of results) {
              var row = $(
                repl(
                  '<div class="row link-select-row">						<div class="col-xs-4">							<b><a href="#">%(name)s</a></b></div>						<div class="col-xs-8">							<span class="text-muted">%(values)s</span></div>						</div>',
                  {
                    name: v[0],
                    values: v.splice(1).join(", ")
                  }
                )
              ).appendTo(parent);
              row.find("a").attr("data-value", v[0]).click(function() {
                var value = $(this).attr("data-value");
                if (me.target.is_grid) {
                  me.set_in_grid(value).then(() => me.search());
                } else {
                  if (me.target.doctype)
                    me.target.parse_validate_and_set_in_model(value);
                  else {
                    me.target.set_input(value);
                    me.target.$input.trigger("change");
                  }
                  me.dialog.hide();
                }
                return false;
              });
            }
          } else {
            $(
              '<p><br><span class="text-muted">' + __("No Results") + "</span>" + (frappe.model.can_create(me.doctype) ? '<br><br><a class="new-doc btn btn-default btn-sm">' + __("Create a new {0}", [__(me.doctype)]) + "</a>" : "") + "</p>"
            ).appendTo(parent).find(".new-doc").click(function() {
              frappe.new_doc(me.doctype);
            });
          }
          var more_btn = me.dialog.fields_dict.more.$wrapper;
          if (results.length < me.page_length) {
            more_btn.hide();
          } else {
            more_btn.show();
          }
        },
        this.dialog.get_primary_btn()
      );
    }
    set_in_grid(value) {
      return new Promise((resolve) => {
        if (this.qty_fieldname) {
          frappe.prompt(
            {
              fieldname: "qty",
              fieldtype: "Float",
              label: "Qty",
              default: 1,
              reqd: 1
            },
            (data) => {
              let updated = (this.target.frm.doc[this.target.df.fieldname] || []).some(
                (d) => {
                  if (d[this.fieldname] === value) {
                    frappe.model.set_value(d.doctype, d.name, this.qty_fieldname, data.qty).then(() => {
                      frappe.show_alert(
                        __("Added {0} ({1})", [
                          value,
                          d[this.qty_fieldname]
                        ])
                      );
                      resolve();
                    });
                    return true;
                  }
                }
              );
              if (!updated) {
                let d = null;
                frappe.run_serially([
                  () => d = this.target.add_new_row(),
                  () => frappe.timeout(0.1),
                  () => {
                    let args = {};
                    args[this.fieldname] = value;
                    args[this.qty_fieldname] = data.qty;
                    return frappe.model.set_value(d.doctype, d.name, args);
                  },
                  () => frappe.show_alert(__("Added {0} ({1})", [value, data.qty])),
                  () => resolve()
                ]);
              }
            },
            __("Set Quantity"),
            __("Set Quantity")
          );
        } else if (this.dynamic_link_field) {
          let d = this.target.add_new_row();
          frappe.model.set_value(
            d.doctype,
            d.name,
            this.dynamic_link_field,
            this.dynamic_link_reference
          );
          frappe.model.set_value(d.doctype, d.name, this.fieldname, value).then(() => {
            frappe.show_alert(__("{0} {1} added", [this.dynamic_link_reference, value]));
            resolve();
          });
        } else {
          let d = this.target.add_new_row();
          frappe.model.set_value(d.doctype, d.name, this.fieldname, value).then(() => {
            frappe.show_alert(__("{0} added", [value]));
            resolve();
          });
        }
      });
    }
  };
  frappe.link_search = function(doctype, args, callback, btn) {
    if (!args) {
      args = {
        txt: ""
      };
    }
    args.doctype = doctype;
    if (!args.searchfield) {
      args.searchfield = "name";
    }
    frappe.call({
      method: "frappe.desk.search.search_widget",
      type: "GET",
      args,
      callback: function(r) {
        callback && callback(r.message);
      },
      btn
    });
  };

  // frappe/public/js/frappe/form/multi_select_dialog.js
  frappe.ui.form.MultiSelectDialog = class MultiSelectDialog {
    constructor(opts) {
      Object.assign(this, opts);
      this.for_select = this.doctype == "[Select]";
      if (!this.for_select) {
        frappe.model.with_doctype(this.doctype, () => this.init());
      } else {
        this.init();
      }
    }
    init() {
      this.page_length = 20;
      this.child_page_length = 20;
      this.fields = this.get_fields();
      this.make();
    }
    get_fields() {
      const primary_fields = this.get_primary_filters();
      const result_fields = this.get_result_fields();
      const data_fields = this.get_data_fields();
      const child_selection_fields = this.get_child_selection_fields();
      return [...primary_fields, ...result_fields, ...data_fields, ...child_selection_fields];
    }
    get_result_fields() {
      const show_next_page = () => {
        this.page_length += 20;
        this.get_results();
      };
      return [
        {
          fieldtype: "HTML",
          fieldname: "results_area"
        },
        {
          fieldtype: "Button",
          fieldname: "more_btn",
          label: __("More"),
          click: show_next_page.bind(this)
        }
      ];
    }
    get_data_fields() {
      if (this.data_fields && this.data_fields.length) {
        return [{ fieldtype: "Section Break" }, ...this.data_fields];
      } else {
        return [];
      }
    }
    get_child_selection_fields() {
      const fields = [];
      if (this.allow_child_item_selection && this.child_fieldname) {
        const show_more_child_results = () => {
          this.child_page_length += 20;
          this.show_child_results();
        };
        fields.push({ fieldtype: "HTML", fieldname: "child_selection_area" });
        fields.push({
          fieldtype: "Button",
          fieldname: "more_child_btn",
          hidden: 1,
          label: __("More"),
          click: show_more_child_results.bind(this)
        });
      }
      return fields;
    }
    make() {
      let doctype_plural = __(this.doctype).plural();
      let title = __("Select {0}", [this.for_select ? __("value") : doctype_plural]);
      this.dialog = new frappe.ui.Dialog({
        title,
        fields: this.fields,
        size: this.size,
        primary_action_label: this.primary_action_label || __("Get Items"),
        secondary_action_label: __("Make {0}", [__(this.doctype)]),
        primary_action: () => {
          let filters_data = this.get_custom_filters();
          const data_values = cur_dialog.get_values();
          const filtered_children = this.get_selected_child_names();
          const selected_documents = [
            ...this.get_checked_values(),
            ...this.get_parent_name_of_selected_children()
          ];
          this.action(selected_documents, __spreadProps(__spreadValues(__spreadValues(__spreadValues({}, this.args), data_values), filters_data), {
            filtered_children
          }));
        },
        secondary_action: this.make_new_document.bind(this)
      });
      if (this.add_filters_group) {
        this.make_filter_area();
      }
      this.args = {};
      this.setup_results();
      this.bind_events();
      this.get_results();
      this.dialog.show();
    }
    make_new_document(e) {
      if (e) {
        this.set_route_options();
        frappe.new_doc(this.doctype, true);
      }
    }
    set_route_options() {
      frappe.route_options = {};
      if (Array.isArray(this.setters)) {
        for (let df of this.setters) {
          frappe.route_options[df.fieldname] = this.dialog.fields_dict[df.fieldname].get_value() || void 0;
        }
      } else {
        Object.keys(this.setters).forEach((setter) => {
          frappe.route_options[setter] = this.dialog.fields_dict[setter].get_value() || void 0;
        });
      }
    }
    setup_results() {
      this.$parent = $(this.dialog.body);
      this.$wrapper = this.dialog.fields_dict.results_area.$wrapper.append(`<div class="results my-3"
			style="border: 1px solid #d1d8dd; border-radius: 3px; height: 300px; overflow: auto;"></div>`);
      this.$results = this.$wrapper.find(".results");
      this.$results.append(this.make_list_row());
    }
    show_child_results() {
      this.get_child_result().then((r) => {
        this.child_results = r.message || [];
        this.render_child_datatable();
        this.$wrapper.addClass("hidden");
        this.$child_wrapper.removeClass("hidden");
        this.dialog.fields_dict.more_btn.$wrapper.hide();
      });
    }
    is_child_selection_enabled() {
      var _a;
      return (_a = this.dialog.fields_dict["allow_child_item_selection"]) == null ? void 0 : _a.get_value();
    }
    toggle_child_selection() {
      if (this.is_child_selection_enabled()) {
        this.show_child_results();
      } else {
        this.child_results = [];
        this.get_results();
        this.$wrapper.removeClass("hidden");
        this.$child_wrapper.addClass("hidden");
      }
    }
    render_child_datatable() {
      if (!this.child_datatable) {
        this.setup_child_datatable();
      } else {
        setTimeout(() => {
          this.child_datatable.rowmanager.checkMap = [];
          this.child_datatable.refresh(this.get_child_datatable_rows());
          this.$child_wrapper.find(".dt-scrollable").css("height", "300px");
          this.$child_wrapper.find(".dt-scrollable").css("overflow-y", "scroll");
        }, 500);
      }
    }
    get_child_datatable_columns() {
      const parent = this.doctype;
      return [parent, ...this.child_columns].map((d) => ({
        name: frappe.unscrub(d),
        editable: false
      }));
    }
    get_child_datatable_rows() {
      if (this.child_results.length > this.child_page_length) {
        this.dialog.fields_dict.more_child_btn.toggle(true);
      } else {
        this.dialog.fields_dict.more_child_btn.toggle(false);
      }
      return this.child_results.slice(0, this.child_page_length).map((d) => Object.values(d).slice(1));
    }
    setup_child_datatable() {
      const header_columns = this.get_child_datatable_columns();
      const rows = this.get_child_datatable_rows();
      this.$child_wrapper = this.dialog.fields_dict.child_selection_area.$wrapper;
      this.$child_wrapper.addClass("my-3");
      this.child_datatable = new frappe.DataTable(this.$child_wrapper.get(0), {
        columns: header_columns,
        data: rows,
        layout: "fluid",
        inlineFilters: true,
        serialNoColumn: false,
        checkboxColumn: true,
        cellHeight: 35,
        noDataMessage: __("No Data"),
        disableReorderColumn: true
      });
      this.$child_wrapper.find(".dt-scrollable").css("height", "300px");
    }
    get_primary_filters() {
      let fields = [];
      let columns = new Array(3);
      columns[0] = [
        {
          fieldtype: "Data",
          label: __("Name"),
          fieldname: "search_term"
        }
      ];
      columns[1] = [];
      columns[2] = [];
      if ($.isArray(this.setters)) {
        this.setters.forEach((setter, index) => {
          columns[(index + 1) % 3].push(setter);
        });
      } else {
        Object.keys(this.setters).forEach((setter, index) => {
          let df_prop = frappe.meta.docfield_map[this.doctype][setter];
          columns[(index + 1) % 3].push({
            fieldtype: df_prop.fieldtype,
            label: df_prop.label,
            fieldname: setter,
            options: df_prop.options,
            default: this.setters[setter]
          });
        });
      }
      if (Object.seal) {
        Object.seal(columns);
      }
      if (this.allow_child_item_selection) {
        this.child_doctype = frappe.meta.get_docfield(
          this.doctype,
          this.child_fieldname
        ).options;
        columns[0].push({
          fieldtype: "Check",
          label: __("Select {0}", [__(this.child_doctype)]),
          fieldname: "allow_child_item_selection",
          onchange: this.toggle_child_selection.bind(this)
        });
      }
      fields = [
        ...columns[0],
        { fieldtype: "Column Break" },
        ...columns[1],
        { fieldtype: "Column Break" },
        ...columns[2],
        { fieldtype: "Section Break", fieldname: "primary_filters_sb" }
      ];
      if (this.add_filters_group) {
        fields.push({
          fieldtype: "HTML",
          fieldname: "filter_area"
        });
      }
      return fields;
    }
    make_filter_area() {
      this.filter_group = new frappe.ui.FilterGroup({
        parent: this.dialog.get_field("filter_area").$wrapper,
        doctype: this.doctype,
        on_change: () => {
          if (this.is_child_selection_enabled()) {
            this.show_child_results();
          } else {
            this.get_results();
          }
        }
      });
      this.filter_group.wrapper.find(".apply-filters").hide();
    }
    get_custom_filters() {
      if (this.add_filters_group && this.filter_group) {
        return this.filter_group.get_filters().reduce((acc, filter) => {
          return Object.assign(acc, {
            [filter[1]]: [filter[2], filter[3]]
          });
        }, {});
      } else {
        return {};
      }
    }
    bind_events() {
      let me = this;
      this.$results.on("click", ".list-item-container", function(e) {
        if (!$(e.target).is(":checkbox") && !$(e.target).is("a")) {
          $(this).find(":checkbox").trigger("click");
        }
      });
      this.$results.on("click", ".list-item--head :checkbox", (e) => {
        this.$results.find(".list-item-container .list-row-check").prop("checked", $(e.target).is(":checked"));
      });
      this.$parent.find(".input-with-feedback").on("change", () => {
        frappe.flags.auto_scroll = false;
        if (this.is_child_selection_enabled()) {
          this.show_child_results();
        } else {
          this.get_results();
        }
      });
      this.$parent.find('[data-fieldtype="Data"]').on("input", () => {
        var $this = $(this);
        clearTimeout($this.data("timeout"));
        $this.data(
          "timeout",
          setTimeout(function() {
            frappe.flags.auto_scroll = false;
            if (me.is_child_selection_enabled()) {
              me.show_child_results();
            } else {
              me.empty_list();
              me.get_results();
            }
          }, 300)
        );
      });
    }
    get_parent_name_of_selected_children() {
      if (!this.child_datatable || !this.child_datatable.datamanager.rows.length)
        return [];
      let parent_names = this.child_datatable.rowmanager.checkMap.reduce(
        (parent_names2, checked, index) => {
          if (checked == 1) {
            const parent_name = this.child_results[index].parent;
            if (!parent_names2.includes(parent_name)) {
              parent_names2.push(parent_name);
            }
          }
          return parent_names2;
        },
        []
      );
      return parent_names;
    }
    get_selected_child_names() {
      if (!this.child_datatable || !this.child_datatable.datamanager.rows.length)
        return [];
      let checked_names = this.child_datatable.rowmanager.checkMap.reduce(
        (checked_names2, checked, index) => {
          if (checked == 1) {
            const child_row_name = this.child_results[index].name;
            checked_names2.push(child_row_name);
          }
          return checked_names2;
        },
        []
      );
      return checked_names;
    }
    get_checked_values() {
      return this.$results.find(".list-item-container").map(function() {
        if ($(this).find(".list-row-check:checkbox:checked").length > 0) {
          return $(this).attr("data-item-name");
        }
      }).get();
    }
    get_checked_items() {
      let checked_values = this.get_checked_values();
      return this.results.filter((res) => checked_values.includes(res.name));
    }
    get_datatable_columns() {
      if (this.get_query && this.get_query().query && this.columns)
        return this.columns;
      if (Array.isArray(this.setters))
        return ["name", ...this.setters.map((df) => df.fieldname)];
      return ["name", ...Object.keys(this.setters)];
    }
    make_list_row(result = {}) {
      var me = this;
      let head = Object.keys(result).length === 0;
      let contents = ``;
      this.get_datatable_columns().forEach(function(column) {
        contents += `<div class="list-item__content ellipsis">
				${head ? `<span class="ellipsis text-muted" title="${__(
          frappe.model.unscrub(column)
        )}">${__(frappe.model.unscrub(column))}</span>` : column !== "name" ? `<span class="ellipsis result-row" title="${__(
          result[column] || ""
        )}">${__(result[column] || "")}</span>` : `<a href="${"/app/" + frappe.router.slug(me.doctype) + "/" + result[column] || ""}" class="list-id ellipsis" title="${__(result[column] || "")}">
							${__(result[column] || "")}</a>`}
			</div>`;
      });
      let $row = $(`<div class="list-item">
			<div class="list-item__content" style="flex: 0 0 10px;">
				<input type="checkbox" class="list-row-check" data-item-name="${result.name}" ${result.checked ? "checked" : ""}>
			</div>
			${contents}
		</div>`);
      head ? $row.addClass("list-item--head") : $row = $(
        `<div class="list-item-container" data-item-name="${result.name}"></div>`
      ).append($row);
      return $row;
    }
    render_result_list(results, more = 0, empty = true) {
      var me = this;
      var more_btn = me.dialog.fields_dict.more_btn.$wrapper;
      if (!frappe.flags.auto_scroll && empty) {
        this.empty_list();
      }
      more_btn.hide();
      $(".modal-dialog .list-item--head").css("z-index", 1);
      if (results.length === 0)
        return;
      if (more)
        more_btn.show();
      let checked = this.get_checked_values();
      results.filter((result) => !checked.includes(result.name)).forEach((result) => {
        me.$results.append(me.make_list_row(result));
      });
      this.$results.find(".list-item--head").css("z-index", 1);
      if (frappe.flags.auto_scroll) {
        this.$results.animate({ scrollTop: me.$results.prop("scrollHeight") }, 500);
      }
    }
    empty_list() {
      let checked = this.get_checked_items().map((item) => {
        return __spreadProps(__spreadValues({}, item), {
          checked: true
        });
      });
      this.$results.find(".list-item-container").remove();
      this.render_result_list(checked, 0, false);
    }
    get_filters_from_setters() {
      let me = this;
      let filters = (this.get_query ? this.get_query().filters : {}) || {};
      let filter_fields = [];
      if ($.isArray(this.setters)) {
        for (let df of this.setters) {
          filters[df.fieldname] = me.dialog.fields_dict[df.fieldname].get_value() || void 0;
          me.args[df.fieldname] = filters[df.fieldname];
          filter_fields.push(df.fieldname);
        }
      } else {
        Object.keys(this.setters).forEach(function(setter) {
          var value = me.dialog.fields_dict[setter].get_value();
          if (me.dialog.fields_dict[setter].df.fieldtype == "Data" && value) {
            filters[setter] = ["like", "%" + value + "%"];
          } else {
            filters[setter] = value || void 0;
            me.args[setter] = filters[setter];
            filter_fields.push(setter);
          }
        });
      }
      return [filters, filter_fields];
    }
    get_args_for_search() {
      let [filters, filter_fields] = this.get_filters_from_setters();
      let custom_filters = this.get_custom_filters();
      Object.assign(filters, custom_filters);
      return {
        doctype: this.doctype,
        txt: this.dialog.fields_dict["search_term"].get_value(),
        filters,
        filter_fields,
        page_length: this.page_length + 5,
        query: this.get_query ? this.get_query().query : "",
        as_dict: 1
      };
    }
    async perform_search(args) {
      const res = await frappe.call({
        type: "GET",
        method: "frappe.desk.search.search_widget",
        no_spinner: true,
        args
      });
      const more = res.message.length && res.message.length > this.page_length ? 1 : 0;
      return [res.message, more];
    }
    async get_results() {
      const args = this.get_args_for_search();
      let [results, more] = await this.perform_search(args);
      if (more) {
        results = results.splice(0, this.page_length);
      }
      this.results = [];
      if (results.length) {
        results.forEach((result) => {
          result.checked = 0;
          this.results.push(result);
        });
      }
      this.render_result_list(this.results, more);
    }
    async get_filtered_parents_for_child_search() {
      const parent_search_args = this.get_args_for_search();
      parent_search_args.filter_fields = ["name"];
      const [results, _] = await this.perform_search(parent_search_args);
      let parent_names = [];
      if (results.length) {
        parent_names = results.map((v) => v.name);
      }
      return parent_names;
    }
    async add_parent_filters(filters) {
      const parent_names = await this.get_filtered_parents_for_child_search();
      if (parent_names.length) {
        filters.push(["parent", "in", parent_names]);
      }
    }
    add_custom_child_filters(filters) {
      if (this.add_filters_group && this.filter_group) {
        this.filter_group.get_filters().forEach((filter) => {
          if (filter[0] == this.child_doctype) {
            filters.push([filter[1], filter[2], filter[3]]);
          }
        });
      }
    }
    async get_child_result() {
      let filters = [["parentfield", "=", this.child_fieldname]];
      await this.add_parent_filters(filters);
      this.add_custom_child_filters(filters);
      return frappe.call({
        method: "frappe.client.get_list",
        args: {
          doctype: this.child_doctype,
          filters,
          fields: ["name", "parent", ...this.child_columns],
          parent: this.doctype,
          limit_page_length: this.child_page_length + 5,
          order_by: "parent"
        }
      });
    }
  };

  // frappe/public/js/frappe/ui/dialog.js
  frappe.provide("frappe.ui");
  window.cur_dialog = null;
  frappe.ui.open_dialogs = [];
  frappe.ui.Dialog = class Dialog extends frappe.ui.FieldGroup {
    constructor(opts) {
      super();
      this.display = false;
      this.is_dialog = true;
      $.extend(this, { animate: true, size: null }, opts);
      this.make();
    }
    make() {
      this.$wrapper = frappe.get_modal("", "");
      if (this.static) {
        this.$wrapper.modal({
          backdrop: "static",
          keyboard: false
        });
        this.get_close_btn().hide();
      }
      if (!this.size)
        this.set_modal_size();
      this.wrapper = this.$wrapper.find(".modal-dialog").get(0);
      if (this.size == "small")
        $(this.wrapper).addClass("modal-sm");
      else if (this.size == "large")
        $(this.wrapper).addClass("modal-lg");
      else if (this.size == "extra-large")
        $(this.wrapper).addClass("modal-xl");
      this.make_head();
      this.modal_body = this.$wrapper.find(".modal-body");
      this.$body = $("<div></div>").appendTo(this.modal_body);
      this.body = this.$body.get(0);
      this.$message = $('<div class="hide modal-message"></div>').appendTo(this.modal_body);
      this.header = this.$wrapper.find(".modal-header");
      this.footer = this.$wrapper.find(".modal-footer");
      this.standard_actions = this.footer.find(".standard-actions");
      this.custom_actions = this.footer.find(".custom-actions");
      this.set_indicator();
      super.make();
      this.refresh_section_collapse();
      this.action = this.action || { primary: {}, secondary: {} };
      if (this.primary_action || this.action.primary && this.action.primary.onsubmit) {
        this.set_primary_action(
          this.primary_action_label || this.action.primary.label || __("Submit", null, "Primary action in dialog"),
          this.primary_action || this.action.primary.onsubmit
        );
      }
      if (this.secondary_action) {
        this.set_secondary_action(this.secondary_action);
      }
      if (this.secondary_action_label || this.action.secondary && this.action.secondary.label) {
        this.set_secondary_action_label(
          this.secondary_action_label || this.action.secondary.label
        );
      }
      if (this.minimizable) {
        this.header.find(".title-section").click(() => this.is_minimized && this.toggle_minimize());
        this.get_minimize_btn().removeClass("hide").on("click", () => this.toggle_minimize());
      }
      var me = this;
      this.$wrapper.on("hide.bs.modal", function() {
        var _a, _b, _c;
        me.display = false;
        me.is_minimized = false;
        me.hide_scrollbar(false);
        (_c = (_b = (_a = frappe.ui.form).get_open_grid_form) == null ? void 0 : _b.call(_a)) == null ? void 0 : _c.hide_form();
        if (frappe.ui.open_dialogs[frappe.ui.open_dialogs.length - 1] === me) {
          frappe.ui.open_dialogs.pop();
          if (frappe.ui.open_dialogs.length) {
            window.cur_dialog = frappe.ui.open_dialogs[frappe.ui.open_dialogs.length - 1];
          } else {
            window.cur_dialog = null;
          }
        }
        me.onhide && me.onhide();
        me.on_hide && me.on_hide();
      }).on("shown.bs.modal", function() {
        me.display = true;
        window.cur_dialog = me;
        frappe.ui.open_dialogs.push(me);
        me.focus_on_first_input();
        me.hide_scrollbar(true);
        me.on_page_show && me.on_page_show();
        $(document).trigger("frappe.ui.Dialog:shown");
        $(document).off("focusin.modal");
      }).on("scroll", function() {
        var $input = $("input:focus");
        if ($input.length && ["Date", "Datetime", "Time"].includes($input.attr("data-fieldtype"))) {
          $input.blur();
        }
      });
    }
    set_modal_size() {
      if (!this.fields) {
        this.size = "";
        return;
      }
      let col_brk = 0;
      let cur_col_brk = 0;
      this.fields.forEach((field) => {
        if (field.fieldtype == "Column Break") {
          cur_col_brk++;
          if (cur_col_brk > col_brk) {
            col_brk = cur_col_brk;
          }
        } else if (field.fieldtype == "Section Break") {
          cur_col_brk = 0;
        }
      });
      this.size = col_brk >= 4 ? "extra-large" : col_brk >= 2 ? "large" : "";
    }
    get_primary_btn() {
      return this.standard_actions.find(".btn-primary");
    }
    get_minimize_btn() {
      return this.$wrapper.find(".modal-header .btn-modal-minimize");
    }
    set_message(text) {
      this.$message.removeClass("hide");
      this.$body.addClass("hide");
      this.$message.text(text);
    }
    clear_message() {
      this.$message.addClass("hide");
      this.$body.removeClass("hide");
    }
    clear() {
      super.clear();
      this.clear_message();
    }
    set_primary_action(label, click) {
      this.footer.removeClass("hide");
      this.has_primary_action = true;
      var me = this;
      const primary_btn = this.get_primary_btn().removeClass("hide").html(label);
      if (typeof click == "function") {
        primary_btn.off("click").on("click", function() {
          me.primary_action_fulfilled = true;
          var values = me.get_values();
          if (!values)
            return;
          click && click.apply(me, [values]);
        });
      }
      return primary_btn;
    }
    set_secondary_action(click) {
      this.footer.removeClass("hide");
      return this.get_secondary_btn().removeClass("hide").off("click").on("click", click);
    }
    set_secondary_action_label(label) {
      this.get_secondary_btn().removeClass("hide").html(label);
    }
    disable_primary_action() {
      this.get_primary_btn().addClass("disabled");
    }
    enable_primary_action() {
      this.get_primary_btn().removeClass("disabled");
    }
    make_head() {
      this.set_title(this.title);
    }
    set_title(t) {
      this.$wrapper.find(".modal-title").html(t);
    }
    set_indicator() {
      if (this.indicator) {
        this.header.find(".indicator").removeClass().addClass("indicator " + this.indicator);
      }
    }
    show() {
      if (this.animate) {
        this.$wrapper.addClass("fade");
      } else {
        this.$wrapper.removeClass("fade");
      }
      this.$wrapper.modal("show");
      this.$wrapper.removeClass("modal-minimize");
      if (this.minimizable && this.is_minimized) {
        $(".modal-backdrop").toggle();
        this.is_minimized = false;
      }
      this.clear_message();
      this.primary_action_fulfilled = false;
      this.is_visible = true;
      return this;
    }
    hide() {
      this.$wrapper.modal("hide");
      this.is_visible = false;
    }
    get_close_btn() {
      return this.$wrapper.find(".btn-modal-close");
    }
    get_secondary_btn() {
      return this.standard_actions.find(".btn-modal-secondary");
    }
    no_cancel() {
      this.get_close_btn().toggle(false);
    }
    cancel() {
      this.get_close_btn().trigger("click");
    }
    toggle_minimize() {
      $(".modal-backdrop").toggle();
      let modal = this.$wrapper.closest(".modal").toggleClass("modal-minimize");
      modal.attr("tabindex") ? modal.removeAttr("tabindex") : modal.attr("tabindex", -1);
      this.is_minimized = !this.is_minimized;
      const icon = this.is_minimized ? "expand" : "collapse";
      this.get_minimize_btn().html(frappe.utils.icon(icon));
      this.on_minimize_toggle && this.on_minimize_toggle(this.is_minimized);
      this.header.find(".modal-title").toggleClass("cursor-pointer");
      this.hide_scrollbar(!this.is_minimized);
    }
    hide_scrollbar(bool) {
      $("body").css("overflow", bool ? "hidden" : "auto");
    }
    add_custom_action(label, action, css_class = null) {
      this.footer.removeClass("hide");
      let action_button = $(`
			<button class="btn btn-secondary btn-sm ${css_class || ""}">
				${label}
			</button>
		`);
      this.custom_actions.append(action_button);
      action && action_button.click(action);
    }
  };
  frappe.ui.hide_open_dialog = () => {
    if (window.cur_dialog) {
      if (!cur_dialog.minimizable) {
        cur_dialog.hide();
      } else if (!cur_dialog.is_minimized) {
        cur_dialog.toggle_minimize();
      }
    }
  };
})();
//# sourceMappingURL=dialog.bundle.S3SMROM2.js.map
