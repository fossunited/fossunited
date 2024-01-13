(() => {
  // ../fossunited/fossunited/public/js/common_functions.js
  $(document).ready(function() {
    window.full_name = frappe.get_cookie("full_name");
    var logged_in = frappe.is_user_logged_in();
    $("#website-login").toggleClass("hide", logged_in ? true : false);
    $("#website-post-login").toggleClass("hide", logged_in ? false : true);
    $(".logged-in").toggleClass("hide", logged_in ? false : true);
    frappe.bind_navbar_search();
    if (frappe.get_cookie("system_user") === "yes" && logged_in) {
      frappe.add_switch_to_desk();
    }
    frappe.render_user();
    $(document).trigger("page-change");
  });

  // node_modules/frappe-charts/dist/frappe-charts.esm.js
  function t(e2) {
    return (t = "function" == typeof Symbol && "symbol" == typeof Symbol.iterator ? function(t3) {
      return typeof t3;
    } : function(t3) {
      return t3 && "function" == typeof Symbol && t3.constructor === Symbol && t3 !== Symbol.prototype ? "symbol" : typeof t3;
    })(e2);
  }
  function e(t3, e2) {
    if (!(t3 instanceof e2))
      throw new TypeError("Cannot call a class as a function");
  }
  function n(t3, e2) {
    for (var n2 = 0; n2 < e2.length; n2++) {
      var i2 = e2[n2];
      i2.enumerable = i2.enumerable || false, i2.configurable = true, "value" in i2 && (i2.writable = true), Object.defineProperty(t3, i2.key, i2);
    }
  }
  function i(t3, e2, i2) {
    return e2 && n(t3.prototype, e2), i2 && n(t3, i2), t3;
  }
  function a(t3, e2) {
    if ("function" != typeof e2 && null !== e2)
      throw new TypeError("Super expression must either be null or a function");
    t3.prototype = Object.create(e2 && e2.prototype, { constructor: { value: t3, writable: true, configurable: true } }), e2 && r(t3, e2);
  }
  function s(t3) {
    return (s = Object.setPrototypeOf ? Object.getPrototypeOf : function(t4) {
      return t4.__proto__ || Object.getPrototypeOf(t4);
    })(t3);
  }
  function r(t3, e2) {
    return (r = Object.setPrototypeOf || function(t4, e3) {
      return t4.__proto__ = e3, t4;
    })(t3, e2);
  }
  function o(t3, e2) {
    return !e2 || "object" != typeof e2 && "function" != typeof e2 ? function(t4) {
      if (void 0 === t4)
        throw new ReferenceError("this hasn't been initialised - super() hasn't been called");
      return t4;
    }(t3) : e2;
  }
  function l(t3) {
    var e2 = function() {
      if ("undefined" == typeof Reflect || !Reflect.construct)
        return false;
      if (Reflect.construct.sham)
        return false;
      if ("function" == typeof Proxy)
        return true;
      try {
        return Date.prototype.toString.call(Reflect.construct(Date, [], function() {
        })), true;
      } catch (t4) {
        return false;
      }
    }();
    return function() {
      var n2, i2 = s(t3);
      if (e2) {
        var a2 = s(this).constructor;
        n2 = Reflect.construct(i2, arguments, a2);
      } else
        n2 = i2.apply(this, arguments);
      return o(this, n2);
    };
  }
  function c(t3, e2, n2) {
    return (c = "undefined" != typeof Reflect && Reflect.get ? Reflect.get : function(t4, e3, n3) {
      var i2 = function(t5, e4) {
        for (; !Object.prototype.hasOwnProperty.call(t5, e4) && null !== (t5 = s(t5)); )
          ;
        return t5;
      }(t4, e3);
      if (i2) {
        var a2 = Object.getOwnPropertyDescriptor(i2, e3);
        return a2.get ? a2.get.call(n3) : a2.value;
      }
    })(t3, e2, n2 || t3);
  }
  function h(t3, e2) {
    return function(t4) {
      if (Array.isArray(t4))
        return t4;
    }(t3) || function(t4, e3) {
      if ("undefined" == typeof Symbol || !(Symbol.iterator in Object(t4)))
        return;
      var n2 = [], i2 = true, a2 = false, s2 = void 0;
      try {
        for (var r2, o2 = t4[Symbol.iterator](); !(i2 = (r2 = o2.next()).done) && (n2.push(r2.value), !e3 || n2.length !== e3); i2 = true)
          ;
      } catch (t5) {
        a2 = true, s2 = t5;
      } finally {
        try {
          i2 || null == o2.return || o2.return();
        } finally {
          if (a2)
            throw s2;
        }
      }
      return n2;
    }(t3, e2) || d(t3, e2) || function() {
      throw new TypeError("Invalid attempt to destructure non-iterable instance.\nIn order to be iterable, non-array objects must have a [Symbol.iterator]() method.");
    }();
  }
  function u(t3) {
    return function(t4) {
      if (Array.isArray(t4))
        return p(t4);
    }(t3) || function(t4) {
      if ("undefined" != typeof Symbol && Symbol.iterator in Object(t4))
        return Array.from(t4);
    }(t3) || d(t3) || function() {
      throw new TypeError("Invalid attempt to spread non-iterable instance.\nIn order to be iterable, non-array objects must have a [Symbol.iterator]() method.");
    }();
  }
  function d(t3, e2) {
    if (t3) {
      if ("string" == typeof t3)
        return p(t3, e2);
      var n2 = Object.prototype.toString.call(t3).slice(8, -1);
      return "Object" === n2 && t3.constructor && (n2 = t3.constructor.name), "Map" === n2 || "Set" === n2 ? Array.from(t3) : "Arguments" === n2 || /^(?:Ui|I)nt(?:8|16|32)(?:Clamped)?Array$/.test(n2) ? p(t3, e2) : void 0;
    }
  }
  function p(t3, e2) {
    (null == e2 || e2 > t3.length) && (e2 = t3.length);
    for (var n2 = 0, i2 = new Array(e2); n2 < e2; n2++)
      i2[n2] = t3[n2];
    return i2;
  }
  function f(t3, e2) {
    return "string" == typeof t3 ? (e2 || document).querySelector(t3) : t3 || null;
  }
  function v(t3) {
    var e2 = t3.getBoundingClientRect();
    return { top: e2.top + (document.documentElement.scrollTop || document.body.scrollTop), left: e2.left + (document.documentElement.scrollLeft || document.body.scrollLeft) };
  }
  function g(t3) {
    return null === t3.offsetParent;
  }
  function m(t3) {
    var e2 = t3.getBoundingClientRect();
    return e2.top >= 0 && e2.left >= 0 && e2.bottom <= (window.innerHeight || document.documentElement.clientHeight) && e2.right <= (window.innerWidth || document.documentElement.clientWidth);
  }
  !function(t3, e2) {
    void 0 === e2 && (e2 = {});
    var n2 = e2.insertAt;
    if (t3 && "undefined" != typeof document) {
      var i2 = document.head || document.getElementsByTagName("head")[0], a2 = document.createElement("style");
      a2.type = "text/css", "top" === n2 && i2.firstChild ? i2.insertBefore(a2, i2.firstChild) : i2.appendChild(a2), a2.styleSheet ? a2.styleSheet.cssText = t3 : a2.appendChild(document.createTextNode(t3));
    }
  }(':root {\n  --charts-label-color: #313b44;\n  --charts-axis-line-color: #f4f5f6;\n  --charts-tooltip-title: var(--charts-label-color);\n  --charts-tooltip-label: var(--charts-label-color);\n  --charts-tooltip-value: #192734;\n  --charts-tooltip-bg: #ffffff;\n  --charts-stroke-width: 2px;\n  --charts-dataset-circle-stroke: #ffffff;\n  --charts-dataset-circle-stroke-width: var(--charts-stroke-width);\n  --charts-legend-label: var(--charts-label-color);\n  --charts-legend-value: var(--charts-label-color); }\n\n.chart-container {\n  position: relative;\n  /* for absolutely positioned tooltip */\n  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "Roboto", "Oxygen", "Ubuntu", "Cantarell", "Fira Sans", "Droid Sans", "Helvetica Neue", sans-serif; }\n  .chart-container .axis,\n  .chart-container .chart-label {\n    fill: var(--charts-label-color); }\n    .chart-container .axis line,\n    .chart-container .chart-label line {\n      stroke: var(--charts-axis-line-color); }\n  .chart-container .dataset-units circle {\n    stroke: var(--charts-dataset-circle-stroke);\n    stroke-width: var(--charts-dataset-circle-stroke-width); }\n  .chart-container .dataset-units path {\n    fill: none;\n    stroke-opacity: 1;\n    stroke-width: var(--charts-stroke-width); }\n  .chart-container .dataset-path {\n    stroke-width: var(--charts-stroke-width); }\n  .chart-container .path-group path {\n    fill: none;\n    stroke-opacity: 1;\n    stroke-width: var(--charts-stroke-width); }\n  .chart-container line.dashed {\n    stroke-dasharray: 5, 3; }\n  .chart-container .axis-line .specific-value {\n    text-anchor: start; }\n  .chart-container .axis-line .y-line {\n    text-anchor: end; }\n  .chart-container .axis-line .x-line {\n    text-anchor: middle; }\n  .chart-container .legend-dataset-label {\n    fill: var(--charts-legend-label);\n    font-weight: 600; }\n  .chart-container .legend-dataset-value {\n    fill: var(--charts-legend-value); }\n\n.graph-svg-tip {\n  position: absolute;\n  z-index: 99999;\n  padding: 10px;\n  font-size: 12px;\n  text-align: center;\n  background: var(--charts-tooltip-bg);\n  box-shadow: 0px 1px 4px rgba(17, 43, 66, 0.1), 0px 2px 6px rgba(17, 43, 66, 0.08), 0px 40px 30px -30px rgba(17, 43, 66, 0.1);\n  border-radius: 6px; }\n  .graph-svg-tip ul {\n    padding-left: 0;\n    display: flex; }\n  .graph-svg-tip ol {\n    padding-left: 0;\n    display: flex; }\n  .graph-svg-tip ul.data-point-list li {\n    min-width: 90px;\n    font-weight: 600; }\n  .graph-svg-tip .svg-pointer {\n    position: absolute;\n    height: 12px;\n    width: 12px;\n    border-radius: 2px;\n    background: var(--charts-tooltip-bg);\n    transform: rotate(45deg);\n    margin-top: -7px;\n    margin-left: -6px; }\n  .graph-svg-tip.comparison {\n    text-align: left;\n    padding: 0px;\n    pointer-events: none; }\n    .graph-svg-tip.comparison .title {\n      display: block;\n      padding: 16px;\n      margin: 0;\n      color: var(--charts-tooltip-title);\n      font-weight: 600;\n      line-height: 1;\n      pointer-events: none;\n      text-transform: uppercase; }\n      .graph-svg-tip.comparison .title strong {\n        color: var(--charts-tooltip-value); }\n    .graph-svg-tip.comparison ul {\n      margin: 0;\n      white-space: nowrap;\n      list-style: none; }\n      .graph-svg-tip.comparison ul.tooltip-grid {\n        display: grid;\n        grid-template-columns: repeat(4, minmax(0, 1fr));\n        gap: 5px; }\n    .graph-svg-tip.comparison li {\n      display: inline-block;\n      display: flex;\n      flex-direction: row;\n      font-weight: 600;\n      line-height: 1;\n      padding: 5px 15px 15px 15px; }\n      .graph-svg-tip.comparison li .tooltip-legend {\n        height: 12px;\n        width: 12px;\n        margin-right: 8px;\n        border-radius: 2px; }\n      .graph-svg-tip.comparison li .tooltip-label {\n        margin-top: 4px;\n        font-size: 11px;\n        line-height: 1.25;\n        max-width: 150px;\n        white-space: normal;\n        color: var(--charts-tooltip-label); }\n      .graph-svg-tip.comparison li .tooltip-value {\n        color: var(--charts-tooltip-value); }\n'), f.create = function(e2, n2) {
    var i2 = document.createElement(e2);
    for (var a2 in n2) {
      var s2 = n2[a2];
      if ("inside" === a2)
        f(s2).appendChild(i2);
      else if ("around" === a2) {
        var r2 = f(s2);
        r2.parentNode.insertBefore(i2, r2), i2.appendChild(r2);
      } else
        "styles" === a2 ? "object" === t(s2) && Object.keys(s2).map(function(t3) {
          i2.style[t3] = s2[t3];
        }) : a2 in i2 ? i2[a2] = s2 : i2.setAttribute(a2, s2);
    }
    return i2;
  };
  var y = { margins: { top: 10, bottom: 10, left: 20, right: 20 }, paddings: { top: 20, bottom: 40, left: 30, right: 10 }, baseHeight: 240, titleHeight: 20, legendHeight: 30, titleFontSize: 12 };
  function b(t3) {
    return t3.titleHeight + t3.margins.top + t3.paddings.top;
  }
  function x(t3) {
    return t3.margins.left + t3.paddings.left;
  }
  function k(t3) {
    return t3.margins.top + t3.margins.bottom + t3.paddings.top + t3.paddings.bottom + t3.titleHeight + t3.legendHeight;
  }
  function w(t3) {
    return t3.margins.left + t3.margins.right + t3.paddings.left + t3.paddings.right;
  }
  var A = ["pink", "blue", "green", "grey", "red", "yellow", "purple", "teal", "cyan", "orange"];
  var D = { bar: A, line: A, pie: A, percentage: A, heatmap: ["#ebedf0", "#c6e48b", "#7bc96f", "#239a3b", "#196127"], donut: A };
  var L = Math.PI / 180;
  var M = function() {
    function t3(n2) {
      var i2 = n2.parent, a2 = void 0 === i2 ? null : i2, s2 = n2.colors, r2 = void 0 === s2 ? [] : s2;
      e(this, t3), this.parent = a2, this.colors = r2, this.titleName = "", this.titleValue = "", this.listValues = [], this.titleValueFirst = 0, this.x = 0, this.y = 0, this.top = 0, this.left = 0, this.setup();
    }
    return i(t3, [{ key: "setup", value: function() {
      this.makeTooltip();
    } }, { key: "refresh", value: function() {
      this.fill(), this.calcPosition();
    } }, { key: "makeTooltip", value: function() {
      var t4 = this;
      this.container = f.create("div", { inside: this.parent, className: "graph-svg-tip comparison", innerHTML: '<span class="title"></span>\n				<ul class="data-point-list"></ul>\n				<div class="svg-pointer"></div>' }), this.hideTip(), this.title = this.container.querySelector(".title"), this.list = this.container.querySelector(".data-point-list"), this.dataPointList = this.container.querySelector(".data-point-list"), this.parent.addEventListener("mouseleave", function() {
        t4.hideTip();
      });
    } }, { key: "fill", value: function() {
      var t4, e2 = this;
      this.index && this.container.setAttribute("data-point-index", this.index), t4 = this.titleValueFirst ? "<strong>".concat(this.titleValue, "</strong>").concat(this.titleName) : "".concat(this.titleName, "<strong>").concat(this.titleValue, "</strong>"), this.listValues.length > 4 ? this.list.classList.add("tooltip-grid") : this.list.classList.remove("tooltip-grid"), this.title.innerHTML = t4, this.dataPointList.innerHTML = "", this.listValues.map(function(t5, n2) {
        var i2 = e2.colors[n2] || "black", a2 = 0 === t5.formatted || t5.formatted ? t5.formatted : t5.value, s2 = f.create("li", { innerHTML: '<div class="tooltip-legend" style="background: '.concat(i2, ';"></div>\n					<div>\n						<div class="tooltip-value">').concat(0 === a2 || a2 ? a2 : "", '</div>\n						<div class="tooltip-label">').concat(t5.title ? t5.title : "", "</div>\n					</div>") });
        e2.dataPointList.appendChild(s2);
      });
    } }, { key: "calcPosition", value: function() {
      var t4 = this.container.offsetWidth;
      this.top = this.y - this.container.offsetHeight - 7.48, this.left = this.x - t4 / 2;
      var e2 = this.parent.offsetWidth - t4, n2 = this.container.querySelector(".svg-pointer");
      if (this.left < 0)
        n2.style.left = "calc(50% - ".concat(-1 * this.left, "px)"), this.left = 0;
      else if (this.left > e2) {
        var i2 = this.left - e2, a2 = "calc(50% + ".concat(i2, "px)");
        n2.style.left = a2, this.left = e2;
      } else
        n2.style.left = "50%";
    } }, { key: "setValues", value: function(t4, e2) {
      var n2 = arguments.length > 2 && void 0 !== arguments[2] ? arguments[2] : {}, i2 = arguments.length > 3 && void 0 !== arguments[3] ? arguments[3] : [], a2 = arguments.length > 4 && void 0 !== arguments[4] ? arguments[4] : -1;
      this.titleName = n2.name, this.titleValue = n2.value, this.listValues = i2, this.x = t4, this.y = e2, this.titleValueFirst = n2.valueFirst || 0, this.index = a2, this.refresh();
    } }, { key: "hideTip", value: function() {
      this.container.style.top = "0px", this.container.style.left = "0px", this.container.style.opacity = "0";
    } }, { key: "showTip", value: function() {
      this.container.style.top = this.top + "px", this.container.style.left = this.left + "px", this.container.style.opacity = "1";
    } }]), t3;
  }();
  function T(t3) {
    return parseFloat(t3.toFixed(2));
  }
  function P(t3, e2, n2) {
    var i2 = arguments.length > 3 && void 0 !== arguments[3] && arguments[3];
    n2 || (n2 = i2 ? t3[0] : t3[t3.length - 1]);
    var a2 = new Array(Math.abs(e2)).fill(n2);
    return t3 = i2 ? a2.concat(t3) : t3.concat(a2);
  }
  function C(t3, e2) {
    return (t3 + "").length * e2;
  }
  function N(t3, e2) {
    return { x: Math.sin(t3 * L) * e2, y: Math.cos(t3 * L) * e2 };
  }
  function O(t3) {
    var e2 = arguments.length > 1 && void 0 !== arguments[1] && arguments[1];
    return !Number.isNaN(t3) && (void 0 !== t3 && (!!Number.isFinite(t3) && !(e2 && t3 < 0)));
  }
  function E(t3) {
    return Number(Math.round(t3 + "e4") + "e-4");
  }
  function S(e2) {
    var n2, i2, a2;
    if (e2 instanceof Date)
      return new Date(e2.getTime());
    if ("object" !== t(e2) || null === e2)
      return e2;
    for (a2 in n2 = Array.isArray(e2) ? [] : {}, e2)
      i2 = e2[a2], n2[a2] = S(i2);
    return n2;
  }
  function F(t3, e2) {
    var n2, i2;
    return t3 <= e2 ? (n2 = e2 - t3, i2 = t3) : (n2 = t3 - e2, i2 = e2), [n2, i2];
  }
  function z(t3, e2) {
    var n2 = arguments.length > 2 && void 0 !== arguments[2] ? arguments[2] : e2.length - t3.length;
    return n2 > 0 ? t3 = P(t3, n2) : e2 = P(e2, n2), [t3, e2];
  }
  function H(t3, e2) {
    if (t3)
      return t3.length > e2 ? t3.slice(0, e2 - 3) + "..." : t3;
  }
  function R(t3) {
    var e2;
    if ("number" == typeof t3)
      e2 = t3;
    else if ("string" == typeof t3 && (e2 = Number(t3), Number.isNaN(e2)))
      return t3;
    var n2 = Math.floor(Math.log10(Math.abs(e2)));
    if (n2 <= 2)
      return e2;
    var i2 = Math.floor(n2 / 3), a2 = Math.pow(10, n2 - 3 * i2) * +(e2 / Math.pow(10, n2)).toFixed(1);
    return Math.round(100 * a2) / 100 + ["", "K", "M", "B", "T"][i2];
  }
  function W(t3, e2) {
    for (var n2 = [], i2 = (Math.min(t3.length, e2.length), 0); i2 < t3.length; i2++)
      n2.push([t3[i2], e2[i2]]);
    var a2 = function(t4, e3, n3, i3) {
      var a3, s2, r2, o2, l2 = (a3 = e3 || t4, r2 = (s2 = n3 || t4)[0] - a3[0], o2 = s2[1] - a3[1], { length: Math.sqrt(Math.pow(r2, 2) + Math.pow(o2, 2)), angle: Math.atan2(o2, r2) }), c2 = l2.angle + (i3 ? Math.PI : 0), h2 = 0.2 * l2.length;
      return [t4[0] + Math.cos(c2) * h2, t4[1] + Math.sin(c2) * h2];
    };
    return function(t4, e3) {
      return t4.reduce(function(t5, n3, i3, a3) {
        return 0 === i3 ? "".concat(n3[0], ",").concat(n3[1]) : "".concat(t5, " ").concat(e3(n3, i3, a3));
      }, "");
    }(n2, function(t4, e3, n3) {
      var i3 = a2(n3[e3 - 1], n3[e3 - 2], t4), s2 = a2(t4, n3[e3 - 1], n3[e3 + 1], true);
      return "C ".concat(i3[0], ",").concat(i3[1], " ").concat(s2[0], ",").concat(s2[1], " ").concat(t4[0], ",").concat(t4[1]);
    });
  }
  function B(t3, e2) {
    return "string" == typeof t3 ? (e2 || document).querySelector(t3) : t3 || null;
  }
  function j(e2, n2) {
    var i2 = document.createElementNS("http://www.w3.org/2000/svg", e2);
    for (var a2 in n2) {
      var s2 = n2[a2];
      if ("inside" === a2)
        B(s2).appendChild(i2);
      else if ("around" === a2) {
        var r2 = B(s2);
        r2.parentNode.insertBefore(i2, r2), i2.appendChild(r2);
      } else
        "styles" === a2 ? "object" === t(s2) && Object.keys(s2).map(function(t3) {
          i2.style[t3] = s2[t3];
        }) : ("className" === a2 && (a2 = "class"), "innerHTML" === a2 ? i2.textContent = s2 : i2.setAttribute(a2, s2));
    }
    return i2;
  }
  function I(t3, e2) {
    return j("linearGradient", { inside: t3, id: e2, x1: 0, x2: 0, y1: 0, y2: 1 });
  }
  function Y(t3, e2, n2, i2) {
    return j("stop", { inside: t3, style: "stop-color: ".concat(n2), offset: e2, "stop-opacity": i2 });
  }
  function V(t3) {
    var e2 = arguments.length > 1 && void 0 !== arguments[1] ? arguments[1] : "", n2 = arguments.length > 2 && void 0 !== arguments[2] ? arguments[2] : void 0, i2 = { className: t3, transform: e2 };
    return n2 && (i2.inside = n2), j("g", i2);
  }
  function U(t3) {
    var e2 = arguments.length > 1 && void 0 !== arguments[1] ? arguments[1] : "", n2 = arguments.length > 2 && void 0 !== arguments[2] ? arguments[2] : "none", i2 = arguments.length > 3 && void 0 !== arguments[3] ? arguments[3] : "none", a2 = arguments.length > 4 && void 0 !== arguments[4] ? arguments[4] : 2;
    return j("path", { className: e2, d: t3, styles: { stroke: n2, fill: i2, "stroke-width": a2 } });
  }
  function q(t3, e2, n2, i2) {
    var a2 = arguments.length > 4 && void 0 !== arguments[4] ? arguments[4] : 1, s2 = arguments.length > 5 && void 0 !== arguments[5] ? arguments[5] : 0, r2 = n2.x + t3.x, o2 = n2.y + t3.y, l2 = n2.x + e2.x, c2 = n2.y + e2.y;
    return "M".concat(n2.x, " ").concat(n2.y, "\n		L").concat(r2, " ").concat(o2, "\n		A ").concat(i2, " ").concat(i2, " 0 ").concat(s2, " ").concat(a2 ? 1 : 0, "\n		").concat(l2, " ").concat(c2, " z");
  }
  function G(t3, e2, n2, i2) {
    var a2 = arguments.length > 4 && void 0 !== arguments[4] ? arguments[4] : 1, s2 = arguments.length > 5 && void 0 !== arguments[5] ? arguments[5] : 0, r2 = n2.x + t3.x, o2 = n2.y + t3.y, l2 = n2.x + e2.x, c2 = 2 * n2.y, h2 = n2.y + e2.y;
    return "M".concat(n2.x, " ").concat(n2.y, "\n		L").concat(r2, " ").concat(o2, "\n		A ").concat(i2, " ").concat(i2, " 0 ").concat(s2, " ").concat(a2 ? 1 : 0, "\n		").concat(l2, " ").concat(c2, " z\n		L").concat(r2, " ").concat(c2, "\n		A ").concat(i2, " ").concat(i2, " 0 ").concat(s2, " ").concat(a2 ? 1 : 0, "\n		").concat(l2, " ").concat(h2, " z");
  }
  function _(t3, e2, n2, i2) {
    var a2 = arguments.length > 4 && void 0 !== arguments[4] ? arguments[4] : 1, s2 = arguments.length > 5 && void 0 !== arguments[5] ? arguments[5] : 0, r2 = n2.x + t3.x, o2 = n2.y + t3.y, l2 = n2.x + e2.x, c2 = n2.y + e2.y;
    return "M".concat(r2, " ").concat(o2, "\n		A ").concat(i2, " ").concat(i2, " 0 ").concat(s2, " ").concat(a2 ? 1 : 0, "\n		").concat(l2, " ").concat(c2);
  }
  function X(t3, e2, n2, i2) {
    var a2 = arguments.length > 4 && void 0 !== arguments[4] ? arguments[4] : 1, s2 = arguments.length > 5 && void 0 !== arguments[5] ? arguments[5] : 0, r2 = n2.x + t3.x, o2 = n2.y + t3.y, l2 = n2.x + e2.x, c2 = 2 * i2 + o2, h2 = n2.y + t3.y;
    return "M".concat(r2, " ").concat(o2, "\n		A ").concat(i2, " ").concat(i2, " 0 ").concat(s2, " ").concat(a2 ? 1 : 0, "\n		").concat(l2, " ").concat(c2, "\n		M").concat(r2, " ").concat(c2, "\n		A ").concat(i2, " ").concat(i2, " 0 ").concat(s2, " ").concat(a2 ? 1 : 0, "\n		").concat(l2, " ").concat(h2);
  }
  function J(t3, e2) {
    var n2 = arguments.length > 2 && void 0 !== arguments[2] && arguments[2], i2 = "path-fill-gradient-" + e2 + "-" + (n2 ? "lighter" : "default"), a2 = I(t3, i2), s2 = [1, 0.6, 0.2];
    return n2 && (s2 = [0.15, 0.05, 0]), Y(a2, "0%", e2, s2[0]), Y(a2, "50%", e2, s2[1]), Y(a2, "100%", e2, s2[2]), i2;
  }
  function K(t3, e2, n2) {
    var i2 = n2 / 2, a2 = e2 - i2;
    return "M".concat(t3, ",0 h").concat(a2, " q").concat(i2, ",0 ").concat(i2, ",").concat(i2, " q0,").concat(i2, " -").concat(i2, ",").concat(i2, " h-").concat(a2, " v").concat(n2, "z");
  }
  function $2(t3, e2, n2) {
    var i2 = n2 / 2, a2 = e2 - i2;
    return "M".concat(t3 + i2, ",0 h").concat(a2, " v").concat(n2, " h-").concat(a2, " q-").concat(i2, ", 0 -").concat(i2, ",-").concat(i2, " q0,-").concat(i2, " ").concat(i2, ",-").concat(i2, "z");
  }
  function Q(t3, e2, n2, i2, a2) {
    var s2 = arguments.length > 5 && void 0 !== arguments[5] ? arguments[5] : "none", r2 = arguments.length > 6 && void 0 !== arguments[6] ? arguments[6] : {}, o2 = { className: t3, x: e2, y: n2, width: i2, height: i2, rx: a2, fill: s2 };
    return Object.keys(r2).map(function(t4) {
      o2[t4] = r2[t4];
    }), j("rect", o2);
  }
  function Z(t3, e2, n2, i2) {
    var a2 = arguments.length > 4 && void 0 !== arguments[4] ? arguments[4] : "none", s2 = arguments.length > 5 ? arguments[5] : void 0, r2 = arguments.length > 6 ? arguments[6] : void 0, o2 = arguments.length > 7 && void 0 !== arguments[7] ? arguments[7] : null, l2 = arguments.length > 8 && void 0 !== arguments[8] && arguments[8];
    o2 || (o2 = 10);
    var c2 = { className: "legend-dot", x: 0, y: 4 - n2, height: n2, width: n2, rx: i2, fill: a2 }, h2 = j("text", { className: "legend-dataset-label", x: n2, y: 0, dx: o2 + "px", dy: o2 / 3 + "px", "font-size": 1.6 * o2 + "px", "text-anchor": "start", innerHTML: s2 = l2 ? H(s2, 18) : s2 }), u2 = null;
    r2 && (u2 = j("text", { className: "legend-dataset-value", x: n2, y: 20, dx: "10px", dy: 10 / 3 + "px", "font-size": "12px", "text-anchor": "start", innerHTML: r2 }));
    var d2 = j("g", { transform: "translate(".concat(t3, ", ").concat(e2, ")") });
    return d2.appendChild(j("rect", c2)), d2.appendChild(h2), r2 && u2 && d2.appendChild(u2), d2;
  }
  function tt(t3, e2, n2, i2) {
    var a2 = arguments.length > 4 && void 0 !== arguments[4] ? arguments[4] : {}, s2 = a2.fontSize || 10, r2 = void 0 !== a2.dy ? a2.dy : s2 / 2, o2 = a2.fill || "var(--charts-label-color)", l2 = a2.textAnchor || "start";
    return j("text", { className: t3, x: e2, y: n2, dy: r2 + "px", "font-size": s2 + "px", fill: o2, "text-anchor": l2, innerHTML: i2 });
  }
  function et(t3, e2, n2, i2) {
    var a2 = arguments.length > 4 && void 0 !== arguments[4] ? arguments[4] : {}, s2 = j("line", { className: "line-vertical " + a2.className, x1: 0, x2: 0, y1: n2, y2: i2, styles: { stroke: a2.stroke } }), r2 = j("text", { x: 0, y: n2 > i2 ? n2 + 4 : n2 - 4 - 10, dy: "10px", "font-size": "10px", "text-anchor": "middle", innerHTML: e2 + "" }), o2 = j("g", { transform: "translate(".concat(t3, ", 0)") });
    return o2.appendChild(s2), o2.appendChild(r2), o2;
  }
  function nt(t3, e2, n2, i2) {
    var a2 = arguments.length > 4 && void 0 !== arguments[4] ? arguments[4] : {};
    a2.lineType || (a2.lineType = ""), a2.shortenNumbers && (e2 = a2.numberFormatter ? a2.numberFormatter(e2) : R(e2));
    var s2 = "line-horizontal " + a2.className + ("dashed" === a2.lineType ? "dashed" : ""), r2 = j("line", { className: s2, x1: n2, x2: i2, y1: 0, y2: 0, styles: { stroke: a2.stroke } }), o2 = j("text", { x: n2 < i2 ? n2 - 4 : n2 + 4, y: 0, dy: "3px", "font-size": "10px", "text-anchor": n2 < i2 ? "end" : "start", innerHTML: e2 + "" }), l2 = j("g", { transform: "translate(0, ".concat(t3, ")"), "stroke-opacity": 1 });
    return 0 !== o2 && "0" !== o2 || (l2.style.stroke = "rgba(27, 31, 35, 0.6)"), l2.appendChild(r2), l2.appendChild(o2), l2;
  }
  function it(t3, e2, n2, i2) {
    var a2 = arguments.length > 4 && void 0 !== arguments[4] ? arguments[4] : "", s2 = arguments.length > 5 && void 0 !== arguments[5] ? arguments[5] : 0, r2 = arguments.length > 6 && void 0 !== arguments[6] && arguments[6], o2 = j("circle", { style: "fill: ".concat(i2, "; ").concat(r2 ? "stroke: ".concat(i2) : ""), "data-point-index": s2, cx: t3, cy: e2, r: n2 });
    if ((a2 += "") || a2.length) {
      o2.setAttribute("cy", 0), o2.setAttribute("cx", 0);
      var l2 = j("text", { className: "data-point-value", x: 0, y: 0, dy: -5 - n2 + "px", "font-size": "10px", "text-anchor": "middle", innerHTML: a2 }), c2 = j("g", { "data-point-index": s2, transform: "translate(".concat(t3, ", ").concat(e2, ")") });
      return c2.appendChild(o2), c2.appendChild(l2), c2;
    }
    return o2;
  }
  var at = { bar: function(t3) {
    var e2;
    "rect" !== t3.nodeName && (e2 = t3.getAttribute("transform"), t3 = t3.childNodes[0]);
    var n2 = t3.cloneNode();
    return n2.style.fill = "#000000", n2.style.opacity = "0.4", e2 && n2.setAttribute("transform", e2), n2;
  }, dot: function(t3) {
    var e2;
    "circle" !== t3.nodeName && (e2 = t3.getAttribute("transform"), t3 = t3.childNodes[0]);
    var n2 = t3.cloneNode(), i2 = t3.getAttribute("r"), a2 = t3.getAttribute("fill");
    return n2.setAttribute("r", parseInt(i2) + 4), n2.setAttribute("fill", a2), n2.style.opacity = "0.6", e2 && n2.setAttribute("transform", e2), n2;
  }, heat_square: function(t3) {
    var e2;
    "circle" !== t3.nodeName && (e2 = t3.getAttribute("transform"), t3 = t3.childNodes[0]);
    var n2 = t3.cloneNode(), i2 = t3.getAttribute("r"), a2 = t3.getAttribute("fill");
    return n2.setAttribute("r", parseInt(i2) + 4), n2.setAttribute("fill", a2), n2.style.opacity = "0.6", e2 && n2.setAttribute("transform", e2), n2;
  } };
  var st = { bar: function(t3, e2) {
    var n2;
    "rect" !== t3.nodeName && (n2 = t3.getAttribute("transform"), t3 = t3.childNodes[0]);
    var i2 = ["x", "y", "width", "height"];
    Object.values(t3.attributes).filter(function(t4) {
      return i2.includes(t4.name) && t4.specified;
    }).map(function(t4) {
      e2.setAttribute(t4.name, t4.nodeValue);
    }), n2 && e2.setAttribute("transform", n2);
  }, dot: function(t3, e2) {
    var n2;
    "circle" !== t3.nodeName && (n2 = t3.getAttribute("transform"), t3 = t3.childNodes[0]);
    var i2 = ["cx", "cy"];
    Object.values(t3.attributes).filter(function(t4) {
      return i2.includes(t4.name) && t4.specified;
    }).map(function(t4) {
      e2.setAttribute(t4.name, t4.nodeValue);
    }), n2 && e2.setAttribute("transform", n2);
  }, heat_square: function(t3, e2) {
    var n2;
    "circle" !== t3.nodeName && (n2 = t3.getAttribute("transform"), t3 = t3.childNodes[0]);
    var i2 = ["cx", "cy"];
    Object.values(t3.attributes).filter(function(t4) {
      return i2.includes(t4.name) && t4.specified;
    }).map(function(t4) {
      e2.setAttribute(t4.name, t4.nodeValue);
    }), n2 && e2.setAttribute("transform", n2);
  } };
  var rt = { pink: "#F683AE", blue: "#318AD8", green: "#48BB74", grey: "#A6B1B9", red: "#F56B6B", yellow: "#FACF7A", purple: "#44427B", teal: "#5FD8C4", cyan: "#15CCEF", orange: "#F8814F", "light-pink": "#FED7E5", "light-blue": "#BFDDF7", "light-green": "#48BB74", "light-grey": "#F4F5F6", "light-red": "#F6DFDF", "light-yellow": "#FEE9BF", "light-purple": "#E8E8F7", "light-teal": "#D3FDF6", "light-cyan": "#DDF8FD", "light-orange": "#FECDB8" };
  function ot(t3, e2, n2, i2) {
    var a2 = "string" == typeof e2 ? e2 : e2.join(", ");
    return [t3, { transform: n2.join(", ") }, i2, "easein", "translate", { transform: a2 }];
  }
  function lt(t3, e2, n2) {
    return ot(t3, [0, n2], [0, e2], 350);
  }
  function ct(t3, e2) {
    return [t3, { d: e2 }, 350, "easein"];
  }
  var ht = { ease: "0.25 0.1 0.25 1", linear: "0 0 1 1", easein: "0.1 0.8 0.2 1", easeout: "0 0 0.58 1", easeinout: "0.42 0 0.58 1" };
  function ut(t3, e2, n2) {
    var i2 = arguments.length > 3 && void 0 !== arguments[3] ? arguments[3] : "linear", a2 = arguments.length > 4 && void 0 !== arguments[4] ? arguments[4] : void 0, s2 = arguments.length > 5 && void 0 !== arguments[5] ? arguments[5] : {}, r2 = t3.cloneNode(true), o2 = t3.cloneNode(true);
    for (var l2 in e2) {
      var c2 = void 0;
      c2 = "transform" === l2 ? document.createElementNS("http://www.w3.org/2000/svg", "animateTransform") : document.createElementNS("http://www.w3.org/2000/svg", "animate");
      var h2 = s2[l2] || t3.getAttribute(l2), u2 = e2[l2], d2 = { attributeName: l2, from: h2, to: u2, begin: "0s", dur: n2 / 1e3 + "s", values: h2 + ";" + u2, keySplines: ht[i2], keyTimes: "0;1", calcMode: "spline", fill: "freeze" };
      for (var p2 in a2 && (d2.type = a2), d2)
        c2.setAttribute(p2, d2[p2]);
      r2.appendChild(c2), a2 ? o2.setAttribute(l2, "translate(".concat(u2, ")")) : o2.setAttribute(l2, u2);
    }
    return [r2, o2];
  }
  function dt(t3, e2) {
    t3.style.transform = e2, t3.style.webkitTransform = e2, t3.style.msTransform = e2, t3.style.mozTransform = e2, t3.style.oTransform = e2;
  }
  function pt(t3, e2) {
    var n2 = [], i2 = [];
    e2.map(function(t4) {
      var e3, a3, s2 = t4[0], r2 = s2.parentNode;
      t4[0] = s2;
      var o2 = h(ut.apply(void 0, u(t4)), 2);
      e3 = o2[0], a3 = o2[1], n2.push(a3), i2.push([e3, r2]), r2.replaceChild(e3, s2);
    });
    var a2 = t3.cloneNode(true);
    return i2.map(function(t4, i3) {
      t4[1].replaceChild(n2[i3], t4[0]), e2[i3][0] = n2[i3];
    }), a2;
  }
  function ft(t3, e2, n2) {
    if (0 !== n2.length) {
      var i2 = pt(e2, n2);
      e2.parentNode == t3 && (t3.removeChild(e2), t3.appendChild(i2)), setTimeout(function() {
        i2.parentNode == t3 && (t3.removeChild(i2), t3.appendChild(e2));
      }, 250);
    }
  }
  var vt = function() {
    function t3(n2, i2) {
      if (e(this, t3), i2 = S(i2), this.parent = "string" == typeof n2 ? document.querySelector(n2) : n2, !(this.parent instanceof HTMLElement))
        throw new Error("No `parent` element to render on was provided.");
      this.rawChartArgs = i2, this.title = i2.title || "", this.type = i2.type || "", this.realData = this.prepareData(i2.data), this.data = this.prepareFirstData(this.realData), this.colors = this.validateColors(i2.colors, this.type), this.config = { showTooltip: 1, showLegend: void 0 !== i2.showLegend ? i2.showLegend : 1, isNavigable: i2.isNavigable || 0, animate: void 0 !== i2.animate ? i2.animate : 1, disableEntryAnimation: i2.disableEntryAnimation || 0, truncateLegends: i2.truncateLegends || 1 }, this.measures = JSON.parse(JSON.stringify(y));
      var a2 = this.measures;
      this.setMeasures(i2), this.title.length || (a2.titleHeight = 0), this.config.showLegend || (a2.legendHeight = 0), this.argHeight = i2.height || a2.baseHeight, this.state = {}, this.options = {}, this.initTimeout = 700, this.config.isNavigable && (this.overlays = []), this.configure(i2);
    }
    return i(t3, [{ key: "prepareData", value: function(t4) {
      return t4;
    } }, { key: "prepareFirstData", value: function(t4) {
      return t4;
    } }, { key: "validateColors", value: function(t4, e2) {
      var n2 = [];
      return (t4 = (t4 || []).concat(D[e2])).forEach(function(t5) {
        var e3 = function(t6) {
          return /rgb[a]{0,1}\([\d, ]+\)/gim.test(t6) ? /\D+(\d*)\D+(\d*)\D+(\d*)/gim.exec(t6).map(function(t7, e4) {
            return 0 !== e4 ? Number(t7).toString(16) : "#";
          }).reduce(function(t7, e4) {
            return "".concat(t7).concat(e4);
          }) : rt[t6] || t6;
        }(t5);
        !function(t6) {
          return /(^\s*)(#)((?:[A-Fa-f0-9]{3}){1,2})$/i.test(t6) || /(^\s*)(rgb|hsl)(a?)[(]\s*([\d.]+\s*%?)\s*,\s*([\d.]+\s*%?)\s*,\s*([\d.]+\s*%?)\s*(?:,\s*([\d.]+)\s*)?[)]$/i.test(t6);
        }(e3) ? console.warn('"' + t5 + '" is not a valid color.') : n2.push(e3);
      }), n2;
    } }, { key: "setMeasures", value: function() {
    } }, { key: "configure", value: function() {
      var t4 = this, e2 = this.argHeight;
      this.baseHeight = e2, this.height = e2 - k(this.measures), this.boundDrawFn = function() {
        return t4.draw(true);
      }, ResizeObserver && (this.resizeObserver = new ResizeObserver(this.boundDrawFn), this.resizeObserver.observe(this.parent)), window.addEventListener("resize", this.boundDrawFn), window.addEventListener("orientationchange", this.boundDrawFn);
    } }, { key: "destroy", value: function() {
      this.resizeObserver && this.resizeObserver.disconnect(), window.removeEventListener("resize", this.boundDrawFn), window.removeEventListener("orientationchange", this.boundDrawFn);
    } }, { key: "setup", value: function() {
      this.makeContainer(), this.updateWidth(), this.makeTooltip(), this.draw(false, true);
    } }, { key: "makeContainer", value: function() {
      this.parent.innerHTML = "";
      var t4 = { inside: this.parent, className: "chart-container" };
      this.independentWidth && (t4.styles = { width: this.independentWidth + "px" }), this.container = f.create("div", t4);
    } }, { key: "makeTooltip", value: function() {
      this.tip = new M({ parent: this.container, colors: this.colors }), this.bindTooltip();
    } }, { key: "bindTooltip", value: function() {
    } }, { key: "draw", value: function() {
      var t4 = this, e2 = arguments.length > 0 && void 0 !== arguments[0] && arguments[0], n2 = arguments.length > 1 && void 0 !== arguments[1] && arguments[1];
      e2 && g(this.parent) || (this.updateWidth(), this.calc(e2), this.makeChartArea(), this.setupComponents(), this.components.forEach(function(e3) {
        return e3.setup(t4.drawArea);
      }), this.render(this.components, false), n2 && (this.data = this.realData, setTimeout(function() {
        t4.update(t4.data, true);
      }, this.initTimeout)), this.config.showLegend && this.renderLegend(), this.setupNavigation(n2));
    } }, { key: "calc", value: function() {
    } }, { key: "updateWidth", value: function() {
      var t4, e2, n2;
      this.baseWidth = (t4 = this.parent, e2 = window.getComputedStyle(t4), n2 = parseFloat(e2.paddingLeft) + parseFloat(e2.paddingRight), t4.clientWidth - n2), this.width = this.baseWidth - w(this.measures);
    } }, { key: "makeChartArea", value: function() {
      this.svg && this.container.removeChild(this.svg);
      var t4, e2, n2, i2, a2 = this.measures;
      this.svg = (t4 = this.container, e2 = "frappe-chart chart", n2 = this.baseWidth, i2 = this.baseHeight, j("svg", { className: e2, inside: t4, width: n2, height: i2 })), this.svgDefs = j("defs", { inside: this.svg }), this.title.length && (this.titleEL = tt("title", a2.margins.left, a2.margins.top, this.title, { fontSize: a2.titleFontSize, fill: "#666666", dy: a2.titleFontSize }));
      var s2 = b(a2);
      this.drawArea = V(this.type + "-chart chart-draw-area", "translate(".concat(x(a2), ", ").concat(s2, ")")), this.config.showLegend && (s2 += this.height + a2.paddings.bottom, this.legendArea = V("chart-legend", "translate(".concat(x(a2), ", ").concat(s2, ")"))), this.title.length && this.svg.appendChild(this.titleEL), this.svg.appendChild(this.drawArea), this.config.showLegend && this.svg.appendChild(this.legendArea), this.updateTipOffset(x(a2), b(a2));
    } }, { key: "updateTipOffset", value: function(t4, e2) {
      this.tip.offset = { x: t4, y: e2 };
    } }, { key: "setupComponents", value: function() {
      this.components = /* @__PURE__ */ new Map();
    } }, { key: "update", value: function(t4) {
      var e2 = arguments.length > 1 && void 0 !== arguments[1] && arguments[1];
      t4 || console.error("No data to update."), e2 || (t4 = S(t4));
      var n2 = e2 ? !this.config.disableEntryAnimation : this.config.animate;
      this.data = this.prepareData(t4), this.calc(), this.render(this.components, n2);
    } }, { key: "render", value: function() {
      var t4 = this, e2 = arguments.length > 0 && void 0 !== arguments[0] ? arguments[0] : this.components, n2 = !(arguments.length > 1 && void 0 !== arguments[1]) || arguments[1];
      this.config.isNavigable && this.overlays.map(function(t5) {
        return t5.parentNode.removeChild(t5);
      });
      var i2 = [];
      e2.forEach(function(t5) {
        i2 = i2.concat(t5.update(n2));
      }), i2.length > 0 ? (ft(this.container, this.svg, i2), setTimeout(function() {
        e2.forEach(function(t5) {
          return t5.make();
        }), t4.updateNav();
      }, 400)) : (e2.forEach(function(t5) {
        return t5.make();
      }), this.updateNav());
    } }, { key: "updateNav", value: function() {
      this.config.isNavigable && (this.makeOverlay(), this.bindUnits());
    } }, { key: "renderLegend", value: function(t4) {
      var e2 = this;
      this.legendArea.textContent = "";
      var n2 = 0, i2 = 0;
      t4.map(function(t5, a2) {
        var s2 = Math.floor(e2.width / 150);
        n2 > s2 && (n2 = 0, i2 += e2.config.legendRowHeight);
        var r2 = 150 * n2, o2 = e2.makeLegend(t5, a2, r2, i2);
        e2.legendArea.appendChild(o2), n2++;
      });
    } }, { key: "makeLegend", value: function() {
    } }, { key: "setupNavigation", value: function() {
      var t4 = this, e2 = arguments.length > 0 && void 0 !== arguments[0] && arguments[0];
      this.config.isNavigable && e2 && (this.bindOverlay(), this.keyActions = { 13: this.onEnterKey.bind(this), 37: this.onLeftArrow.bind(this), 38: this.onUpArrow.bind(this), 39: this.onRightArrow.bind(this), 40: this.onDownArrow.bind(this) }, document.addEventListener("keydown", function(e3) {
        m(t4.container) && (e3 = e3 || window.event, t4.keyActions[e3.keyCode] && t4.keyActions[e3.keyCode]());
      }));
    } }, { key: "makeOverlay", value: function() {
    } }, { key: "updateOverlay", value: function() {
    } }, { key: "bindOverlay", value: function() {
    } }, { key: "bindUnits", value: function() {
    } }, { key: "onLeftArrow", value: function() {
    } }, { key: "onRightArrow", value: function() {
    } }, { key: "onUpArrow", value: function() {
    } }, { key: "onDownArrow", value: function() {
    } }, { key: "onEnterKey", value: function() {
    } }, { key: "addDataPoint", value: function() {
    } }, { key: "removeDataPoint", value: function() {
    } }, { key: "getDataPoint", value: function() {
    } }, { key: "setCurrentDataPoint", value: function() {
    } }, { key: "updateDataset", value: function() {
    } }, { key: "export", value: function() {
      var t4 = function(t5) {
        var e2 = t5.cloneNode(true);
        e2.classList.add("chart-container"), e2.setAttribute("xmlns", "http://www.w3.org/2000/svg"), e2.setAttribute("xmlns:xlink", "http://www.w3.org/1999/xlink");
        var n2 = f.create("style", { innerHTML: ".chart-container{position:relative;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI','Roboto','Oxygen','Ubuntu','Cantarell','Fira Sans','Droid Sans','Helvetica Neue',sans-serif}.chart-container .axis,.chart-container .chart-label{fill:#555b51}.chart-container .axis line,.chart-container .chart-label line{stroke:#dadada}.chart-container .dataset-units circle{stroke:#fff;stroke-width:2}.chart-container .dataset-units path{fill:none;stroke-opacity:1;stroke-width:2px}.chart-container .dataset-path{stroke-width:2px}.chart-container .path-group path{fill:none;stroke-opacity:1;stroke-width:2px}.chart-container line.dashed{stroke-dasharray:5,3}.chart-container .axis-line .specific-value{text-anchor:start}.chart-container .axis-line .y-line{text-anchor:end}.chart-container .axis-line .x-line{text-anchor:middle}.chart-container .legend-dataset-text{fill:#6c7680;font-weight:600}.graph-svg-tip{position:absolute;z-index:99999;padding:10px;font-size:12px;color:#959da5;text-align:center;background:rgba(0,0,0,.8);border-radius:3px}.graph-svg-tip ul{padding-left:0;display:flex}.graph-svg-tip ol{padding-left:0;display:flex}.graph-svg-tip ul.data-point-list li{min-width:90px;flex:1;font-weight:600}.graph-svg-tip strong{color:#dfe2e5;font-weight:600}.graph-svg-tip .svg-pointer{position:absolute;height:5px;margin:0 0 0 -5px;content:' ';border:5px solid transparent;}.graph-svg-tip.comparison{padding:0;text-align:left;pointer-events:none}.graph-svg-tip.comparison .title{display:block;padding:10px;margin:0;font-weight:600;line-height:1;pointer-events:none}.graph-svg-tip.comparison ul{margin:0;white-space:nowrap;list-style:none}.graph-svg-tip.comparison li{display:inline-block;padding:5px 10px}" });
        e2.insertBefore(n2, e2.firstChild);
        var i2 = f.create("div");
        return i2.appendChild(e2), i2.innerHTML;
      }(this.svg);
      !function(t5, e2) {
        var n2 = document.createElement("a");
        n2.style = "display: none";
        var i2 = new Blob(e2, { type: "image/svg+xml; charset=utf-8" }), a2 = window.URL.createObjectURL(i2);
        n2.href = a2, n2.download = t5, document.body.appendChild(n2), n2.click(), setTimeout(function() {
          document.body.removeChild(n2), window.URL.revokeObjectURL(a2);
        }, 300);
      }(this.title || "Chart", [t4]);
    } }]), t3;
  }();
  var gt = function(t3) {
    a(r2, vt);
    var n2 = l(r2);
    function r2(t4, i2) {
      return e(this, r2), n2.call(this, t4, i2);
    }
    return i(r2, [{ key: "configure", value: function(t4) {
      c(s(r2.prototype), "configure", this).call(this, t4), this.config.formatTooltipY = (t4.tooltipOptions || {}).formatTooltipY, this.config.maxSlices = t4.maxSlices || 20, this.config.maxLegendPoints = t4.maxLegendPoints || 20, this.config.legendRowHeight = 60;
    } }, { key: "calc", value: function() {
      var t4 = this, e2 = this.state, n3 = this.config.maxSlices;
      e2.sliceTotals = [];
      var i2 = this.data.labels.map(function(e3, n4) {
        var i3 = 0;
        return t4.data.datasets.map(function(t5) {
          i3 += t5.values[n4];
        }), [i3, e3];
      }).filter(function(t5) {
        return t5[0] >= 0;
      }), a2 = i2;
      if (i2.length > n3) {
        i2.sort(function(t5, e3) {
          return e3[0] - t5[0];
        }), a2 = i2.slice(0, n3 - 1);
        var s2 = i2.slice(n3 - 1), r3 = 0;
        s2.map(function(t5) {
          r3 += t5[0];
        }), a2.push([r3, "Rest"]), this.colors[n3 - 1] = "grey";
      }
      e2.labels = [], a2.map(function(t5) {
        e2.sliceTotals.push(E(t5[0])), e2.labels.push(t5[1]);
      }), e2.grandTotal = e2.sliceTotals.reduce(function(t5, e3) {
        return t5 + e3;
      }, 0), this.center = { x: this.width / 2, y: this.height / 2 };
    } }, { key: "renderLegend", value: function() {
      var t4 = this.state;
      this.legendArea.textContent = "", this.legendTotals = t4.sliceTotals.slice(0, this.config.maxLegendPoints), c(s(r2.prototype), "renderLegend", this).call(this, this.legendTotals);
    } }, { key: "makeLegend", value: function(t4, e2, n3, i2) {
      var a2 = this.config.formatTooltipY ? this.config.formatTooltipY(t4) : t4;
      return Z(n3, i2, 12, 3, this.colors[e2], this.state.labels[e2], a2, null, this.config.truncateLegends);
    } }]), r2;
  }();
  var mt = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"];
  var yt = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"];
  function bt(t3) {
    var e2 = new Date(t3);
    return e2.setMinutes(e2.getMinutes() - e2.getTimezoneOffset()), e2;
  }
  function xt(t3) {
    var e2 = t3.getDate(), n2 = t3.getMonth() + 1;
    return [t3.getFullYear(), (n2 > 9 ? "" : "0") + n2, (e2 > 9 ? "" : "0") + e2].join("-");
  }
  function kt(t3) {
    return new Date(t3.getTime());
  }
  function wt(t3, e2) {
    var n2 = Mt(t3);
    return Math.ceil(function(t4, e3) {
      return (bt(e3) - bt(t4)) / 864e5;
    }(n2, e2) / 7);
  }
  function At(t3, e2) {
    return t3.getMonth() === e2.getMonth() && t3.getFullYear() === e2.getFullYear();
  }
  function Dt(t3) {
    var e2 = arguments.length > 1 && void 0 !== arguments[1] && arguments[1], n2 = mt[t3];
    return e2 ? n2.slice(0, 3) : n2;
  }
  function Lt(t3, e2) {
    return new Date(e2, t3 + 1, 0);
  }
  function Mt(t3) {
    var e2 = kt(t3), n2 = e2.getDay();
    return 0 !== n2 && Tt(e2, -1 * n2), e2;
  }
  function Tt(t3, e2) {
    t3.setDate(t3.getDate() + e2);
  }
  var Pt = function() {
    function t3(n2) {
      var i2 = n2.layerClass, a2 = void 0 === i2 ? "" : i2, s2 = n2.layerTransform, r2 = void 0 === s2 ? "" : s2, o2 = n2.constants, l2 = n2.getData, c2 = n2.makeElements, h2 = n2.animateElements;
      e(this, t3), this.layerTransform = r2, this.constants = o2, this.makeElements = c2, this.getData = l2, this.animateElements = h2, this.store = [], this.labels = [], this.layerClass = a2, this.layerClass = "function" == typeof this.layerClass ? this.layerClass() : this.layerClass, this.refresh();
    }
    return i(t3, [{ key: "refresh", value: function(t4) {
      this.data = t4 || this.getData();
    } }, { key: "setup", value: function(t4) {
      this.layer = V(this.layerClass, this.layerTransform, t4);
    } }, { key: "make", value: function() {
      this.render(this.data), this.oldData = this.data;
    } }, { key: "render", value: function(t4) {
      var e2 = this;
      this.store = this.makeElements(t4), this.layer.textContent = "", this.store.forEach(function(t5) {
        e2.layer.appendChild(t5);
      }), this.labels.forEach(function(t5) {
        e2.layer.appendChild(t5);
      });
    } }, { key: "update", value: function() {
      var t4 = !(arguments.length > 0 && void 0 !== arguments[0]) || arguments[0];
      this.refresh();
      var e2 = [];
      return t4 && (e2 = this.animateElements(this.data) || []), e2;
    } }]), t3;
  }();
  var Ct = { donutSlices: { layerClass: "donut-slices", makeElements: function(t3) {
    return t3.sliceStrings.map(function(e2, n2) {
      var i2 = U(e2, "donut-path", t3.colors[n2], "none", t3.strokeWidth);
      return i2.style.transition = "transform .3s;", i2;
    });
  }, animateElements: function(t3) {
    return this.store.map(function(e2, n2) {
      return ct(e2, t3.sliceStrings[n2]);
    });
  } }, pieSlices: { layerClass: "pie-slices", makeElements: function(t3) {
    return t3.sliceStrings.map(function(e2, n2) {
      var i2 = U(e2, "pie-path", "none", t3.colors[n2]);
      return i2.style.transition = "transform .3s;", i2;
    });
  }, animateElements: function(t3) {
    return this.store.map(function(e2, n2) {
      return ct(e2, t3.sliceStrings[n2]);
    });
  } }, percentageBars: { layerClass: "percentage-bars", makeElements: function(t3) {
    var e2 = this, n2 = t3.xPositions.length;
    return t3.xPositions.map(function(i2, a2) {
      var s2 = a2 == n2 - 1, r2 = 0 == a2;
      return function(t4, e3, n3, i3, a3, s3) {
        var r3 = arguments.length > 6 && void 0 !== arguments[6] ? arguments[6] : "none";
        if (s3) {
          var o2 = K(t4, n3, i3);
          return U(o2, "percentage-bar", null, r3);
        }
        if (a3) {
          var l2 = $2(t4, n3, i3);
          return U(l2, "percentage-bar", null, r3);
        }
        var c2 = { className: "percentage-bar", x: t4, y: e3, width: n3, height: i3, fill: r3 };
        return j("rect", c2);
      }(i2, 0, t3.widths[a2], e2.constants.barHeight, r2, s2, t3.colors[a2]);
    });
  }, animateElements: function(t3) {
    if (t3)
      return [];
  } }, yAxis: { layerClass: "y axis", makeElements: function(t3) {
    var e2 = this;
    return t3.positions.map(function(n2, i2) {
      return function(t4, e3, n3) {
        var i3 = arguments.length > 3 && void 0 !== arguments[3] ? arguments[3] : {};
        O(t4) || (t4 = 0), i3.pos || (i3.pos = "left"), i3.offset || (i3.offset = 0), i3.mode || (i3.mode = "span"), i3.stroke || (i3.stroke = "#E2E6E9"), i3.className || (i3.className = "");
        var a2 = -6, s2 = "span" === i3.mode ? n3 + 6 : 0;
        return "tick" === i3.mode && "right" === i3.pos && (a2 = n3 + 6, s2 = n3), a2 += i3.offset, s2 += i3.offset, "number" == typeof e3 && (e3 = E(e3)), nt(t4, e3, a2, s2, { className: i3.className, lineType: i3.lineType, shortenNumbers: i3.shortenNumbers, numberFormatter: i3.numberFormatter });
      }(n2, t3.labels[i2], e2.constants.width, { mode: e2.constants.mode, pos: e2.constants.pos, shortenNumbers: e2.constants.shortenNumbers, numberFormatter: e2.constants.numberFormatter });
    });
  }, animateElements: function(t3) {
    var e2 = t3.positions, n2 = t3.labels, i2 = this.oldData.positions, a2 = this.oldData.labels, s2 = h(z(i2, e2), 2);
    i2 = s2[0], e2 = s2[1];
    var r2 = h(z(a2, n2), 2);
    return a2 = r2[0], n2 = r2[1], this.render({ positions: i2, labels: n2 }), this.store.map(function(t4, n3) {
      return lt(t4, e2[n3], i2[n3]);
    });
  } }, xAxis: { layerClass: "x axis", makeElements: function(t3) {
    var e2 = this;
    return t3.positions.map(function(n2, i2) {
      return function(t4, e3, n3) {
        var i3 = arguments.length > 3 && void 0 !== arguments[3] ? arguments[3] : {};
        O(t4) || (t4 = 0), i3.pos || (i3.pos = "bottom"), i3.offset || (i3.offset = 0), i3.mode || (i3.mode = "span"), i3.className || (i3.className = "");
        var a2 = n3 + 6, s2 = "span" === i3.mode ? -6 : n3;
        return "tick" === i3.mode && "top" === i3.pos && (a2 = -6, s2 = 0), et(t4, e3, a2, s2, { className: i3.className, lineType: i3.lineType });
      }(n2, t3.calcLabels[i2], e2.constants.height, { mode: e2.constants.mode, pos: e2.constants.pos });
    });
  }, animateElements: function(t3) {
    var e2 = t3.positions, n2 = t3.calcLabels, i2 = this.oldData.positions, a2 = this.oldData.calcLabels, s2 = h(z(i2, e2), 2);
    i2 = s2[0], e2 = s2[1];
    var r2 = h(z(a2, n2), 2);
    return a2 = r2[0], n2 = r2[1], this.render({ positions: i2, calcLabels: n2 }), this.store.map(function(t4, n3) {
      return function(t5, e3, n4) {
        return ot(t5, [n4, 0], [e3, 0], 350);
      }(t4, e2[n3], i2[n3]);
    });
  } }, yMarkers: { layerClass: "y-markers", makeElements: function(t3) {
    var e2 = this;
    return t3.map(function(t4) {
      return function(t5, e3, n2) {
        var i2 = arguments.length > 3 && void 0 !== arguments[3] ? arguments[3] : {};
        O(t5) || (t5 = 0), i2.labelPos || (i2.labelPos = "right"), i2.lineType || (i2.lineType = "dashed");
        var a2 = "left" === i2.labelPos ? 4 : n2 - C(e3, 5) - 4, s2 = j("text", { className: "chart-label", x: a2, y: 0, dy: "-5px", "font-size": "10px", "text-anchor": "start", innerHTML: e3 + "" }), r2 = nt(t5, "", 0, n2, { stroke: i2.stroke || "#E2E6E9", className: i2.className || "", lineType: i2.lineType });
        return r2.appendChild(s2), r2;
      }(t4.position, t4.label, e2.constants.width, { labelPos: t4.options.labelPos, stroke: t4.options.stroke, mode: "span", lineType: t4.options.lineType });
    });
  }, animateElements: function(t3) {
    var e2 = h(z(this.oldData, t3), 2);
    this.oldData = e2[0];
    var n2 = (t3 = e2[1]).map(function(t4) {
      return t4.position;
    }), i2 = t3.map(function(t4) {
      return t4.label;
    }), a2 = t3.map(function(t4) {
      return t4.options;
    }), s2 = this.oldData.map(function(t4) {
      return t4.position;
    });
    return this.render(s2.map(function(t4, e3) {
      return { position: s2[e3], label: i2[e3], options: a2[e3] };
    })), this.store.map(function(t4, e3) {
      return lt(t4, n2[e3], s2[e3]);
    });
  } }, yRegions: { layerClass: "y-regions", makeElements: function(t3) {
    var e2 = this;
    return t3.map(function(t4) {
      return function(t5, e3, n2, i2) {
        var a2 = arguments.length > 4 && void 0 !== arguments[4] ? arguments[4] : {}, s2 = t5 - e3, r2 = j("rect", { className: "bar mini", styles: { fill: a2.fill || "rgba(228, 234, 239, 0.49)", stroke: a2.stroke || "#E2E6E9", "stroke-dasharray": "".concat(n2, ", ").concat(s2) }, x: 0, y: 0, width: n2, height: s2 });
        a2.labelPos || (a2.labelPos = "right");
        var o2 = "left" === a2.labelPos ? 4 : n2 - C(i2 + "", 4.5) - 4, l2 = j("text", { className: "chart-label", x: o2, y: 0, dy: "-5px", "font-size": "10px", "text-anchor": "start", innerHTML: i2 + "" }), c2 = j("g", { transform: "translate(0, ".concat(e3, ")") });
        return c2.appendChild(r2), c2.appendChild(l2), c2;
      }(t4.startPos, t4.endPos, e2.constants.width, t4.label, { labelPos: t4.options.labelPos, stroke: t4.options.stroke, fill: t4.options.fill });
    });
  }, animateElements: function(t3) {
    var e2 = h(z(this.oldData, t3), 2);
    this.oldData = e2[0];
    var n2 = (t3 = e2[1]).map(function(t4) {
      return t4.endPos;
    }), i2 = t3.map(function(t4) {
      return t4.label;
    }), a2 = t3.map(function(t4) {
      return t4.startPos;
    }), s2 = t3.map(function(t4) {
      return t4.options;
    }), r2 = this.oldData.map(function(t4) {
      return t4.endPos;
    }), o2 = this.oldData.map(function(t4) {
      return t4.startPos;
    });
    this.render(r2.map(function(t4, e3) {
      return { startPos: o2[e3], endPos: r2[e3], label: i2[e3], options: s2[e3] };
    }));
    var l2 = [];
    return this.store.map(function(t4, e3) {
      l2 = l2.concat(function(t5, e4, n3, i3) {
        var a3 = e4 - n3, s3 = t5.childNodes[0], r3 = s3.getAttribute("width");
        return [[s3, { height: a3, "stroke-dasharray": "".concat(r3, ", ").concat(a3) }, 350, "easein"], ot(t5, [0, i3], [0, n3], 350)];
      }(t4, a2[e3], n2[e3], r2[e3]));
    }), l2;
  } }, heatDomain: { layerClass: function() {
    return "heat-domain domain-" + this.constants.index;
  }, makeElements: function(t3) {
    var e2 = this, n2 = this.constants, i2 = n2.index, a2 = n2.colWidth, s2 = n2.rowHeight, r2 = n2.squareSize, o2 = n2.radius, l2 = n2.xTranslate, c2 = l2, h2 = 0;
    return this.serializedSubDomains = [], t3.cols.map(function(t4, n3) {
      1 === n3 && e2.labels.push(tt("domain-name", c2, -12, Dt(i2, true).toUpperCase(), { fontSize: 9 })), t4.map(function(t5, n4) {
        if (t5.fill) {
          var i3 = { "data-date": t5.yyyyMmDd, "data-value": t5.dataValue, "data-day": n4 }, a3 = Q("day", c2, h2, r2, o2, t5.fill, i3);
          e2.serializedSubDomains.push(a3);
        }
        h2 += s2;
      }), h2 = 0, c2 += a2;
    }), this.serializedSubDomains;
  }, animateElements: function(t3) {
    if (t3)
      return [];
  } }, barGraph: { layerClass: function() {
    return "dataset-units dataset-bars dataset-" + this.constants.index;
  }, makeElements: function(t3) {
    var e2 = this.constants;
    return this.unitType = "bar", this.units = t3.yPositions.map(function(n2, i2) {
      return function(t4, e3, n3, i3) {
        var a2 = arguments.length > 4 && void 0 !== arguments[4] ? arguments[4] : "", s2 = arguments.length > 5 && void 0 !== arguments[5] ? arguments[5] : 0, r2 = arguments.length > 6 && void 0 !== arguments[6] ? arguments[6] : 0, o2 = arguments.length > 7 && void 0 !== arguments[7] ? arguments[7] : {}, l2 = F(e3, o2.zeroLine), c2 = h(l2, 2), u2 = c2[0], d2 = c2[1];
        d2 -= r2, 0 === u2 && (u2 = o2.minHeight, d2 -= o2.minHeight), O(t4) || (t4 = 0), O(d2) || (d2 = 0), O(u2, true) || (u2 = 0), O(n3, true) || (n3 = 0);
        var p2 = j("rect", { className: "bar mini", style: "fill: ".concat(i3), "data-point-index": s2, x: t4, y: d2, width: n3, height: u2 });
        if ((a2 += "") || a2.length) {
          p2.setAttribute("y", 0), p2.setAttribute("x", 0);
          var f2 = j("text", { className: "data-point-value", x: n3 / 2, y: 0, dy: "-5px", "font-size": "10px", "text-anchor": "middle", innerHTML: a2 }), v2 = j("g", { "data-point-index": s2, transform: "translate(".concat(t4, ", ").concat(d2, ")") });
          return v2.appendChild(p2), v2.appendChild(f2), v2;
        }
        return p2;
      }(t3.xPositions[i2], n2, t3.barWidth, e2.color, t3.labels[i2], i2, t3.offsets[i2], { zeroLine: t3.zeroLine, barsWidth: t3.barsWidth, minHeight: e2.minHeight });
    }), this.units;
  }, animateElements: function(t3) {
    var e2 = t3.xPositions, n2 = t3.yPositions, i2 = t3.offsets, a2 = t3.labels, s2 = this.oldData.xPositions, r2 = this.oldData.yPositions, o2 = this.oldData.offsets, l2 = this.oldData.labels, c2 = h(z(s2, e2), 2);
    s2 = c2[0], e2 = c2[1];
    var u2 = h(z(r2, n2), 2);
    r2 = u2[0], n2 = u2[1];
    var d2 = h(z(o2, i2), 2);
    o2 = d2[0], i2 = d2[1];
    var p2 = h(z(l2, a2), 2);
    l2 = p2[0], a2 = p2[1], this.render({ xPositions: s2, yPositions: r2, offsets: o2, labels: a2, zeroLine: this.oldData.zeroLine, barsWidth: this.oldData.barsWidth, barWidth: this.oldData.barWidth });
    var f2 = [];
    return this.store.map(function(a3, s3) {
      f2 = f2.concat(function(t4, e3, n3, i3) {
        var a4 = arguments.length > 4 && void 0 !== arguments[4] ? arguments[4] : 0, s4 = arguments.length > 5 && void 0 !== arguments[5] ? arguments[5] : {}, r3 = F(n3, s4.zeroLine), o3 = h(r3, 2), l3 = o3[0], c3 = o3[1];
        if (c3 -= a4, "rect" !== t4.nodeName) {
          var u3 = t4.childNodes[0], d3 = [u3, { width: i3, height: l3 }, 350, "easein"], p3 = t4.getAttribute("transform").split("(")[1].slice(0, -1), f3 = ot(t4, p3, [e3, c3], 350);
          return [d3, f3];
        }
        return [[t4, { width: i3, height: l3, x: e3, y: c3 }, 350, "easein"]];
      }(a3, e2[s3], n2[s3], t3.barWidth, i2[s3], { zeroLine: t3.zeroLine }));
    }), f2;
  } }, lineGraph: { layerClass: function() {
    return "dataset-units dataset-line dataset-" + this.constants.index;
  }, makeElements: function(t3) {
    var e2 = this.constants;
    if (this.unitType = "dot", this.paths = {}, e2.hideLine || (this.paths = function(t4, e3, n3) {
      var i3 = arguments.length > 3 && void 0 !== arguments[3] ? arguments[3] : {}, a2 = arguments.length > 4 && void 0 !== arguments[4] ? arguments[4] : {}, s2 = e3.map(function(e4, n4) {
        return t4[n4] + "," + e4;
      }), r2 = s2.join("L");
      i3.spline && (r2 = W(t4, e3));
      var o2 = U("M" + r2, "line-graph-path", n3);
      if (i3.heatline) {
        var l2 = J(a2.svgDefs, n3);
        o2.style.stroke = "url(#".concat(l2, ")");
      }
      var c2 = { path: o2 };
      if (i3.regionFill) {
        var h2 = J(a2.svgDefs, n3, true), u2 = "M" + "".concat(t4[0], ",").concat(a2.zeroLine, "L") + r2 + "L".concat(t4.slice(-1)[0], ",").concat(a2.zeroLine);
        c2.region = U(u2, "region-fill", "none", "url(#".concat(h2, ")"));
      }
      return c2;
    }(t3.xPositions, t3.yPositions, e2.color, { heatline: e2.heatline, regionFill: e2.regionFill, spline: e2.spline }, { svgDefs: e2.svgDefs, zeroLine: t3.zeroLine })), this.units = [], e2.showDots && (this.units = t3.yPositions.map(function(n3, i3) {
      return it(t3.xPositions[i3], n3, t3.radius, e2.color, e2.valuesOverPoints ? t3.values[i3] : "", i3, e2.hideDotBorder);
    })), e2.trailingDot && !e2.showDots) {
      var n2 = t3.yPositions.length - 1, i2 = it(t3.xPositions[n2], t3.yPositions[n2], t3.radius, e2.color, e2.valuesOverPoints ? t3.values[n2] : "", n2, e2.hideDotBorder);
      this.units.push(i2);
    }
    return Object.values(this.paths).concat(this.units);
  }, animateElements: function(t3) {
    var e2 = t3.xPositions, n2 = t3.yPositions, i2 = t3.values, a2 = this.oldData.xPositions, s2 = this.oldData.yPositions, r2 = this.oldData.values, o2 = h(z(a2, e2), 2);
    a2 = o2[0], e2 = o2[1];
    var l2 = h(z(s2, n2), 2);
    s2 = l2[0], n2 = l2[1];
    var c2 = h(z(r2, i2), 2);
    r2 = c2[0], i2 = c2[1], this.render({ xPositions: a2, yPositions: s2, values: i2, zeroLine: this.oldData.zeroLine, radius: this.oldData.radius });
    var u2 = [];
    return Object.keys(this.paths).length && (u2 = u2.concat(function(t4, e3, n3, i3, a3) {
      var s3 = [], r3 = n3.map(function(t5, n4) {
        return e3[n4] + "," + t5;
      }).join("L");
      a3 && (r3 = W(e3, n3));
      var o3 = [t4.path, { d: "M" + r3 }, 350, "easein"];
      if (s3.push(o3), t4.region) {
        var l3 = "".concat(e3[0], ",").concat(i3, "L"), c3 = "L".concat(e3.slice(-1)[0], ", ").concat(i3), h2 = [t4.region, { d: "M" + l3 + r3 + c3 }, 350, "easein"];
        s3.push(h2);
      }
      return s3;
    }(this.paths, e2, n2, t3.zeroLine, this.constants.spline))), this.units.length && this.units.map(function(t4, i3) {
      u2 = u2.concat(function(t5, e3, n3) {
        if ("circle" !== t5.nodeName) {
          var i4 = t5.getAttribute("transform").split("(")[1].slice(0, -1);
          return [ot(t5, i4, [e3, n3], 350)];
        }
        return [[t5, { cx: e3, cy: n3 }, 350, "easein"]];
      }(t4, e2[i3], n2[i3]));
    }), u2;
  } } };
  function Nt(t3, e2, n2) {
    var i2 = Object.keys(Ct).filter(function(e3) {
      return t3.includes(e3);
    }), a2 = Ct[i2[0]];
    return Object.assign(a2, { constants: e2, getData: n2 }), new Pt(a2);
  }
  var Ot = function(t3) {
    a(r2, gt);
    var n2 = l(r2);
    function r2(t4, i2) {
      var a2;
      return e(this, r2), (a2 = n2.call(this, t4, i2)).type = "percentage", a2.setup(), a2;
    }
    return i(r2, [{ key: "setMeasures", value: function(t4) {
      var e2 = this.measures;
      this.barOptions = t4.barOptions || {};
      var n3 = this.barOptions;
      n3.height = n3.height || 16, e2.paddings.right = 30, e2.paddings.top = 60, e2.paddings.bottom = 0, e2.legendHeight = 80, e2.baseHeight = 8 * n3.height + k(e2);
    } }, { key: "setupComponents", value: function() {
      var t4 = this.state, e2 = [["percentageBars", { barHeight: this.barOptions.height }, function() {
        return { xPositions: t4.xPositions, widths: t4.widths, colors: this.colors };
      }.bind(this)]];
      this.components = new Map(e2.map(function(t5) {
        var e3 = Nt.apply(void 0, u(t5));
        return [t5[0], e3];
      }));
    } }, { key: "calc", value: function() {
      var t4 = this;
      c(s(r2.prototype), "calc", this).call(this);
      var e2 = this.state;
      e2.xPositions = [], e2.widths = [];
      var n3 = 0;
      e2.sliceTotals.map(function(i2) {
        var a2 = t4.width * i2 / e2.grandTotal;
        e2.widths.push(a2), e2.xPositions.push(n3), n3 += a2;
      });
    } }, { key: "makeDataByIndex", value: function() {
    } }, { key: "bindTooltip", value: function() {
      var t4 = this, e2 = this.state;
      this.container.addEventListener("mousemove", function(n3) {
        var i2 = t4.components.get("percentageBars").store, a2 = n3.target;
        if (i2.includes(a2)) {
          var s2 = i2.indexOf(a2), r3 = v(t4.container), o2 = v(a2), l2 = a2.getAttribute("width") || a2.getBoundingClientRect().width, c2 = o2.left - r3.left + parseInt(l2) / 2, h2 = o2.top - r3.top, u2 = (t4.formattedLabels && t4.formattedLabels.length > 0 ? t4.formattedLabels[s2] : t4.state.labels[s2]) + ": ", d2 = e2.sliceTotals[s2] / e2.grandTotal;
          t4.tip.setValues(c2, h2, { name: u2, value: (100 * d2).toFixed(1) + "%" }), t4.tip.showTip();
        }
      });
    } }]), r2;
  }();
  var Et = function(t3) {
    a(r2, gt);
    var n2 = l(r2);
    function r2(t4, i2) {
      var a2;
      return e(this, r2), (a2 = n2.call(this, t4, i2)).initTimeout = 0, a2.init = 1, a2.setup(), a2;
    }
    return i(r2, [{ key: "configure", value: function(t4) {
      c(s(r2.prototype), "configure", this).call(this, t4), this.mouseMove = this.mouseMove.bind(this), this.mouseLeave = this.mouseLeave.bind(this), this.hoverRadio = t4.hoverRadio || 0.1, this.config.startAngle = t4.startAngle || 0, this.type = "pie", this.sliceName = "pieSlices", this.arcFunc = q, this.shapeFunc = G, this.clockWise = t4.clockWise || false;
    } }, { key: "getRadius", value: function() {
      return this.height > this.width ? this.center.x : this.center.y;
    } }, { key: "calc", value: function() {
      var t4 = this;
      c(s(r2.prototype), "calc", this).call(this);
      var e2 = this.state;
      this.radius = this.getRadius();
      var n3 = this.radius, i2 = this.clockWise, a2 = e2.slicesProperties || [];
      e2.sliceStrings = [], e2.slicesProperties = [];
      var o2 = 180 - this.config.startAngle;
      e2.sliceTotals.map(function(s2, r3) {
        var l2, c2, h2 = o2, u2 = s2 / e2.grandTotal * 360, d2 = u2 > 180 ? 1 : 0, p2 = i2 ? -u2 : u2, f2 = o2 += p2, v2 = N(h2, n3), g2 = N(f2, n3), m2 = t4.init && a2[r3];
        t4.init ? (l2 = m2 ? m2.startPosition : v2, c2 = m2 ? m2.endPosition : v2) : (l2 = v2, c2 = g2);
        var y2 = 360 === u2 ? t4.shapeFunc(l2, c2, t4.center, t4.radius, i2, d2) : t4.arcFunc(l2, c2, t4.center, t4.radius, i2, d2);
        e2.sliceStrings.push(y2), e2.slicesProperties.push({ startPosition: v2, endPosition: g2, value: s2, total: e2.grandTotal, startAngle: h2, endAngle: f2, angle: p2 });
      }), this.init = 0;
    } }, { key: "setupComponents", value: function() {
      var t4 = this.state, e2 = [["pieSlices", {}, function() {
        return { sliceStrings: t4.sliceStrings, colors: this.colors };
      }.bind(this)]];
      this.components = new Map(e2.map(function(t5) {
        var e3 = Nt.apply(void 0, u(t5));
        return [t5[0], e3];
      }));
    } }, { key: "calTranslateByAngle", value: function(t4) {
      var e2 = this.radius, n3 = this.hoverRadio, i2 = N(t4.startAngle + t4.angle / 2, e2);
      return "translate3d(".concat(i2.x * n3, "px,").concat(i2.y * n3, "px,0)");
    } }, { key: "hoverSlice", value: function(t4, e2, n3, i2) {
      if (t4) {
        var a2 = this.colors[e2];
        if (n3) {
          dt(t4, this.calTranslateByAngle(this.state.slicesProperties[e2]));
          var s2 = v(this.svg), r3 = i2.pageX - s2.left + 10, o2 = i2.pageY - s2.top - 10, l2 = (this.formatted_labels && this.formatted_labels.length > 0 ? this.formatted_labels[e2] : this.state.labels[e2]) + ": ", c2 = (100 * this.state.sliceTotals[e2] / this.state.grandTotal).toFixed(1);
          this.tip.setValues(r3, o2, { name: l2, value: c2 + "%" }), this.tip.showTip();
        } else
          this.resetHover(t4, a2);
      }
    } }, { key: "resetHover", value: function(t4, e2) {
      dt(t4, "translate3d(0,0,0)"), this.tip.hideTip(), t4.style.fill = e2;
    } }, { key: "bindTooltip", value: function() {
      this.container.addEventListener("mousemove", this.mouseMove), this.container.addEventListener("mouseleave", this.mouseLeave);
    } }, { key: "mouseMove", value: function(t4) {
      var e2 = t4.target, n3 = this.components.get(this.sliceName).store, i2 = this.curActiveSliceIndex, a2 = this.curActiveSlice;
      if (n3.includes(e2)) {
        var s2 = n3.indexOf(e2);
        this.hoverSlice(a2, i2, false), this.curActiveSlice = e2, this.curActiveSliceIndex = s2, this.hoverSlice(e2, s2, true, t4);
      } else
        this.mouseLeave();
    } }, { key: "mouseLeave", value: function() {
      this.hoverSlice(this.curActiveSlice, this.curActiveSliceIndex, false);
    } }]), r2;
  }();
  function St(t3) {
    if (0 === t3)
      return [0, 0];
    if (isNaN(t3))
      return { mantissa: -6755399441055744, exponent: 972 };
    var e2 = t3 > 0 ? 1 : -1;
    if (!isFinite(t3))
      return { mantissa: 4503599627370496 * e2, exponent: 972 };
    t3 = Math.abs(t3);
    var n2 = Math.floor(Math.log10(t3));
    return [e2 * (t3 / Math.pow(10, n2)), n2];
  }
  function Ft(t3) {
    var e2 = arguments.length > 1 && void 0 !== arguments[1] ? arguments[1] : 0, n2 = Math.ceil(t3), i2 = Math.floor(e2), a2 = n2 - i2, s2 = a2, r2 = 1;
    a2 > 5 && (a2 % 2 != 0 && (a2 = ++n2 - i2), s2 = a2 / 2, r2 = 2), a2 <= 2 && (r2 = a2 / (s2 = 4)), 0 === a2 && (s2 = 5, r2 = 1);
    for (var o2 = [], l2 = 0; l2 <= s2; l2++)
      o2.push(i2 + r2 * l2);
    return o2;
  }
  function zt(t3) {
    var e2 = arguments.length > 1 && void 0 !== arguments[1] ? arguments[1] : 0, n2 = St(t3), i2 = h(n2, 2), a2 = i2[0], s2 = i2[1], r2 = e2 ? e2 / Math.pow(10, s2) : 0, o2 = Ft(a2 = a2.toFixed(6), r2);
    return o2 = o2.map(function(t4) {
      return t4 * Math.pow(10, s2);
    });
  }
  function Ht(t3) {
    var e2 = arguments.length > 1 && void 0 !== arguments[1] && arguments[1], n2 = arguments.length > 2 && void 0 !== arguments[2] ? arguments[2] : {}, i2 = Math.max.apply(Math, u(t3)), a2 = Math.min.apply(Math, u(t3));
    void 0 !== n2.max && (i2 = i2 > n2.max ? i2 : n2.max), void 0 !== n2.min && (a2 = a2 < n2.min ? a2 : n2.min);
    var s2 = [];
    function r2(t4, e3) {
      for (var n3 = zt(t4), i3 = n3[1] - n3[0], a3 = 0, s3 = 1; a3 < e3; s3++)
        a3 += i3, n3.unshift(-1 * a3);
      return n3;
    }
    if (i2 >= 0 && a2 >= 0)
      St(i2)[1], s2 = e2 ? zt(i2, a2) : zt(i2);
    else if (i2 > 0 && a2 < 0) {
      var o2 = Math.abs(a2);
      if (i2 >= o2)
        St(i2)[1], s2 = r2(i2, o2);
      else {
        St(o2)[1];
        var l2 = r2(o2, i2);
        s2 = l2.reverse().map(function(t4) {
          return -1 * t4;
        });
      }
    } else if (i2 <= 0 && a2 <= 0) {
      var c2 = Math.abs(a2), h2 = Math.abs(i2);
      St(c2)[1], s2 = (s2 = e2 ? zt(c2, h2) : zt(c2)).reverse().map(function(t4) {
        return -1 * t4;
      });
    }
    return s2;
  }
  function Rt(t3) {
    var e2, n2 = Wt(t3);
    if (t3.indexOf(0) >= 0)
      e2 = t3.indexOf(0);
    else if (t3[0] > 0) {
      e2 = -1 * t3[0] / n2;
    } else {
      e2 = -1 * t3[t3.length - 1] / n2 + (t3.length - 1);
    }
    return e2;
  }
  function Wt(t3) {
    return t3[1] - t3[0];
  }
  function Bt(t3) {
    return t3[t3.length - 1] - t3[0];
  }
  function jt(t3, e2) {
    return T(e2.zeroLine - t3 * e2.scaleMultiplier);
  }
  var It = function(t3) {
    a(s2, vt);
    var n2 = l(s2);
    function s2(t4, i2) {
      var a2;
      e(this, s2), (a2 = n2.call(this, t4, i2)).type = "heatmap", a2.countLabel = i2.countLabel || "";
      var r2 = ["Sunday", "Monday"], o2 = r2.includes(i2.startSubDomain) ? i2.startSubDomain : "Sunday";
      return a2.startSubDomainIndex = r2.indexOf(o2), a2.setup(), a2;
    }
    return i(s2, [{ key: "setMeasures", value: function(t4) {
      var e2 = this.measures;
      this.discreteDomains = 0 === t4.discreteDomains ? 0 : 1, e2.paddings.top = 36, e2.paddings.bottom = 0, e2.legendHeight = 24, e2.baseHeight = 84 + k(e2);
      var n3 = this.data, i2 = this.discreteDomains ? 12 : 0;
      this.independentWidth = 12 * (wt(n3.start, n3.end) + i2) + w(e2);
    } }, { key: "updateWidth", value: function() {
      var t4 = this.discreteDomains ? 12 : 0, e2 = this.state.noOfWeeks ? this.state.noOfWeeks : 52;
      this.baseWidth = 12 * (e2 + t4) + w(this.measures);
    } }, { key: "prepareData", value: function() {
      var t4 = arguments.length > 0 && void 0 !== arguments[0] ? arguments[0] : this.data;
      if (t4.start && t4.end && t4.start > t4.end)
        throw new Error("Start date cannot be greater than end date.");
      if (t4.start || (t4.start = new Date(), t4.start.setFullYear(t4.start.getFullYear() - 1)), t4.end || (t4.end = new Date()), t4.dataPoints = t4.dataPoints || {}, parseInt(Object.keys(t4.dataPoints)[0]) > 1e5) {
        var e2 = {};
        Object.keys(t4.dataPoints).forEach(function(n3) {
          var i2 = new Date(1e3 * n3);
          e2[xt(i2)] = t4.dataPoints[n3];
        }), t4.dataPoints = e2;
      }
      return t4;
    } }, { key: "calc", value: function() {
      var t4 = this.state;
      t4.start = kt(this.data.start), t4.end = kt(this.data.end), t4.firstWeekStart = kt(t4.start), t4.noOfWeeks = wt(t4.start, t4.end), t4.distribution = function(t5, e2) {
        for (var n3 = Math.max.apply(Math, u(t5)), i2 = 1 / (e2 - 1), a2 = [], s3 = 0; s3 < e2; s3++) {
          var r2 = n3 * (i2 * s3);
          a2.push(r2);
        }
        return a2;
      }(Object.values(this.data.dataPoints), 5), t4.domainConfigs = this.getDomains();
    } }, { key: "setupComponents", value: function() {
      var t4 = this, e2 = this.state, n3 = this.discreteDomains ? 0 : 1, i2 = e2.domainConfigs.map(function(i3, a3) {
        return ["heatDomain", { index: i3.index, colWidth: 12, rowHeight: 12, squareSize: 10, radius: t4.rawChartArgs.radius || 0, xTranslate: 12 * e2.domainConfigs.filter(function(t5, e3) {
          return e3 < a3;
        }).map(function(t5) {
          return t5.cols.length - n3;
        }).reduce(function(t5, e3) {
          return t5 + e3;
        }, 0) }, function() {
          return e2.domainConfigs[a3];
        }.bind(t4)];
      });
      this.components = new Map(i2.map(function(t5, e3) {
        var n4 = Nt.apply(void 0, u(t5));
        return [t5[0] + "-" + e3, n4];
      }));
      var a2 = 0;
      yt.forEach(function(e3, n4) {
        if ([1, 3, 5].includes(n4)) {
          var i3 = tt("subdomain-name", -6, a2, e3, { fontSize: 10, dy: 8, textAnchor: "end" });
          t4.drawArea.appendChild(i3);
        }
        a2 += 12;
      });
    } }, { key: "update", value: function(t4) {
      t4 || console.error("No data to update."), this.data = this.prepareData(t4), this.draw(), this.bindTooltip();
    } }, { key: "bindTooltip", value: function() {
      var t4 = this;
      this.container.addEventListener("mousemove", function(e2) {
        t4.components.forEach(function(n3) {
          var i2 = n3.store, a2 = e2.target;
          if (i2.includes(a2)) {
            var s3 = a2.getAttribute("data-value"), r2 = a2.getAttribute("data-date").split("-"), o2 = Dt(parseInt(r2[1]) - 1, true), l2 = t4.container.getBoundingClientRect(), c2 = a2.getBoundingClientRect(), h2 = parseInt(e2.target.getAttribute("width")), u2 = c2.left - l2.left + h2 / 2, d2 = c2.top - l2.top, p2 = s3 + " " + t4.countLabel, f2 = " on " + o2 + " " + r2[0] + ", " + r2[2];
            t4.tip.setValues(u2, d2, { name: f2, value: p2, valueFirst: 1 }, []), t4.tip.showTip();
          }
        });
      });
    } }, { key: "renderLegend", value: function() {
      var t4 = this;
      this.legendArea.textContent = "";
      var e2 = 0, n3 = this.rawChartArgs.radius || 0, i2 = tt("subdomain-name", e2, 12, "Less", { fontSize: 11, dy: 9 });
      e2 = 30, this.legendArea.appendChild(i2), this.colors.slice(0, 5).map(function(i3, a3) {
        var s3 = Q("heatmap-legend-unit", e2 + 15 * a3, 12, 10, n3, i3);
        t4.legendArea.appendChild(s3);
      });
      var a2 = tt("subdomain-name", e2 + 75 + 3, 12, "More", { fontSize: 11, dy: 9 });
      this.legendArea.appendChild(a2);
    } }, { key: "getDomains", value: function() {
      for (var t4 = this.state, e2 = [t4.start.getMonth(), t4.start.getFullYear()], n3 = e2[0], i2 = e2[1], a2 = [t4.end.getMonth(), t4.end.getFullYear()], s3 = a2[0] - n3 + 1 + 12 * (a2[1] - i2), r2 = [], o2 = kt(t4.start), l2 = 0; l2 < s3; l2++) {
        var c2 = t4.end;
        if (!At(o2, t4.end)) {
          var h2 = [o2.getMonth(), o2.getFullYear()];
          c2 = Lt(h2[0], h2[1]);
        }
        r2.push(this.getDomainConfig(o2, c2)), Tt(c2, 1), o2 = c2;
      }
      return r2;
    } }, { key: "getDomainConfig", value: function(t4) {
      var e2 = arguments.length > 1 && void 0 !== arguments[1] ? arguments[1] : "", n3 = [t4.getMonth(), t4.getFullYear()], i2 = n3[0], a2 = n3[1], s3 = Mt(t4), r2 = { index: i2, cols: [] };
      Tt(e2 = kt(e2) || Lt(i2, a2), 1);
      for (var o2, l2 = wt(s3, e2), c2 = [], h2 = 0; h2 < l2; h2++)
        o2 = this.getCol(s3, i2), c2.push(o2), Tt(s3 = new Date(o2[6].yyyyMmDd), 1);
      return void 0 !== o2[6].dataValue && (Tt(s3, 1), c2.push(this.getCol(s3, i2, true))), r2.cols = c2, r2;
    } }, { key: "getCol", value: function(t4, e2) {
      for (var n3 = arguments.length > 2 && void 0 !== arguments[2] && arguments[2], i2 = this.state, a2 = kt(t4), s3 = [], r2 = 0; r2 < 7; r2++, Tt(a2, 1)) {
        var o2 = {}, l2 = a2 >= i2.start && a2 <= i2.end;
        n3 || a2.getMonth() !== e2 || !l2 ? o2.yyyyMmDd = xt(a2) : o2 = this.getSubDomainConfig(a2), s3.push(o2);
      }
      return s3;
    } }, { key: "getSubDomainConfig", value: function(t4) {
      var e2, n3, i2 = xt(t4), a2 = this.data.dataPoints[i2];
      return { yyyyMmDd: i2, dataValue: a2 || 0, fill: this.colors[e2 = a2, n3 = this.state.distribution, n3.filter(function(t5) {
        return t5 < e2;
      }).length] };
    } }]), s2;
  }();
  function Yt(t3, e2) {
    t3.labels = t3.labels || [];
    var n2 = t3.labels.length, i2 = t3.datasets, a2 = new Array(n2).fill(0);
    return i2 || (i2 = [{ values: a2 }]), i2.map(function(t4) {
      if (t4.values) {
        var i3 = t4.values;
        i3 = (i3 = i3.map(function(t5) {
          return isNaN(t5) ? 0 : t5;
        })).length > n2 ? i3.slice(0, n2) : P(i3, n2 - i3.length, 0), t4.values = i3;
      } else
        t4.values = a2;
      t4.chartType || (t4.chartType = e2);
    }), t3.yRegions && t3.yRegions.map(function(t4) {
      if (t4.end < t4.start) {
        var e3 = [t4.end, t4.start];
        t4.start = e3[0], t4.end = e3[1];
      }
    }), t3;
  }
  function Vt(t3) {
    var e2 = t3.labels.length, n2 = new Array(e2).fill(0), i2 = { labels: t3.labels.slice(0, -1), datasets: t3.datasets.map(function(t4) {
      return { name: "", values: n2.slice(0, -1), chartType: t4.chartType };
    }) };
    return t3.yMarkers && (i2.yMarkers = [{ value: 0, label: "" }]), t3.yRegions && (i2.yRegions = [{ start: 0, end: 0, label: "" }]), i2;
  }
  var Ut = function(t3) {
    a(r2, vt);
    var n2 = l(r2);
    function r2(t4, i2) {
      var a2;
      return e(this, r2), (a2 = n2.call(this, t4, i2)).barOptions = i2.barOptions || {}, a2.lineOptions = i2.lineOptions || {}, a2.type = i2.type || "line", a2.init = 1, a2.setup(), a2;
    }
    return i(r2, [{ key: "setMeasures", value: function() {
      this.data.datasets.length <= 1 && (this.config.showLegend = 0, this.measures.paddings.bottom = 30);
    } }, { key: "configure", value: function(t4) {
      c(s(r2.prototype), "configure", this).call(this, t4), t4.axisOptions = t4.axisOptions || {}, t4.tooltipOptions = t4.tooltipOptions || {}, this.config.xAxisMode = t4.axisOptions.xAxisMode || "span", this.config.yAxisMode = t4.axisOptions.yAxisMode || "span", this.config.xIsSeries = t4.axisOptions.xIsSeries || 0, this.config.shortenYAxisNumbers = t4.axisOptions.shortenYAxisNumbers || 0, this.config.numberFormatter = t4.axisOptions.numberFormatter, this.config.yAxisRange = t4.axisOptions.yAxisRange || {}, this.config.formatTooltipX = t4.tooltipOptions.formatTooltipX, this.config.formatTooltipY = t4.tooltipOptions.formatTooltipY, this.config.valuesOverPoints = t4.valuesOverPoints, this.config.legendRowHeight = 30;
    } }, { key: "prepareData", value: function() {
      var t4 = arguments.length > 0 && void 0 !== arguments[0] ? arguments[0] : this.data;
      return Yt(t4, this.type);
    } }, { key: "prepareFirstData", value: function() {
      var t4 = arguments.length > 0 && void 0 !== arguments[0] ? arguments[0] : this.data;
      return Vt(t4);
    } }, { key: "calc", value: function() {
      var t4 = arguments.length > 0 && void 0 !== arguments[0] && arguments[0];
      this.calcXPositions(), t4 || this.calcYAxisParameters(this.getAllYValues(), "line" === this.type), this.makeDataByIndex();
    } }, { key: "calcXPositions", value: function() {
      var t4 = this.state, e2 = this.data.labels;
      t4.datasetLength = e2.length, t4.unitWidth = this.width / t4.datasetLength, t4.xOffset = t4.unitWidth / 2, t4.xAxis = { labels: e2, positions: e2.map(function(e3, n3) {
        return T(t4.xOffset + n3 * t4.unitWidth);
      }) };
    } }, { key: "calcYAxisParameters", value: function(t4) {
      var e2 = arguments.length > 1 && void 0 !== arguments[1] ? arguments[1] : "false", n3 = Ht(t4, e2, this.config.yAxisRange), i2 = this.height / Bt(n3), a2 = Wt(n3) * i2, s2 = this.height - Rt(n3) * a2;
      this.state.yAxis = { labels: n3, positions: n3.map(function(t5) {
        return s2 - t5 * i2;
      }), scaleMultiplier: i2, zeroLine: s2 }, this.calcDatasetPoints(), this.calcYExtremes(), this.calcYRegions();
    } }, { key: "calcDatasetPoints", value: function() {
      var t4 = this.state, e2 = function(e3) {
        return e3.map(function(e4) {
          return jt(e4, t4.yAxis);
        });
      };
      t4.datasets = this.data.datasets.map(function(t5, n3) {
        var i2 = t5.values, a2 = t5.cumulativeYs || [];
        return { name: t5.name && t5.name.replace(/<|>|&/g, function(t6) {
          return "&" == t6 ? "&amp;" : "<" == t6 ? "&lt;" : "&gt;";
        }), index: n3, chartType: t5.chartType, values: i2, yPositions: e2(i2), cumulativeYs: a2, cumulativeYPos: e2(a2) };
      });
    } }, { key: "calcYExtremes", value: function() {
      var t4 = this.state;
      this.barOptions.stacked ? t4.yExtremes = t4.datasets[t4.datasets.length - 1].cumulativeYPos : (t4.yExtremes = new Array(t4.datasetLength).fill(9999), t4.datasets.map(function(e2) {
        e2.yPositions.map(function(e3, n3) {
          e3 < t4.yExtremes[n3] && (t4.yExtremes[n3] = e3);
        });
      }));
    } }, { key: "calcYRegions", value: function() {
      var t4 = this.state;
      this.data.yMarkers && (this.state.yMarkers = this.data.yMarkers.map(function(e2) {
        return e2.position = jt(e2.value, t4.yAxis), e2.options || (e2.options = {}), e2;
      })), this.data.yRegions && (this.state.yRegions = this.data.yRegions.map(function(e2) {
        return e2.startPos = jt(e2.start, t4.yAxis), e2.endPos = jt(e2.end, t4.yAxis), e2.options || (e2.options = {}), e2;
      }));
    } }, { key: "getAllYValues", value: function() {
      var t4, e2 = this, n3 = "values";
      if (this.barOptions.stacked) {
        n3 = "cumulativeYs";
        var i2 = new Array(this.state.datasetLength).fill(0);
        this.data.datasets.map(function(t5, a3) {
          var s2 = e2.data.datasets[a3].values;
          t5[n3] = i2 = i2.map(function(t6, e3) {
            return t6 + s2[e3];
          });
        });
      }
      var a2 = this.data.datasets.map(function(t5) {
        return t5[n3];
      });
      return this.data.yMarkers && a2.push(this.data.yMarkers.map(function(t5) {
        return t5.value;
      })), this.data.yRegions && this.data.yRegions.map(function(t5) {
        a2.push([t5.end, t5.start]);
      }), (t4 = []).concat.apply(t4, u(a2));
    } }, { key: "setupComponents", value: function() {
      var t4 = this, e2 = [["yAxis", { mode: this.config.yAxisMode, width: this.width, shortenNumbers: this.config.shortenYAxisNumbers, numberFormatter: this.config.numberFormatter }, function() {
        return this.state.yAxis;
      }.bind(this)], ["xAxis", { mode: this.config.xAxisMode, height: this.height }, function() {
        var t5 = this.state;
        return t5.xAxis.calcLabels = function(t6) {
          var e3 = arguments.length > 1 && void 0 !== arguments[1] ? arguments[1] : [], n4 = !(arguments.length > 2 && void 0 !== arguments[2]) || arguments[2], i3 = t6 / e3.length * 0.6;
          i3 <= 0 && (i3 = 1);
          var a3, s3 = i3 / 7;
          if (n4) {
            var r4 = Math.max.apply(Math, u(e3.map(function(t7) {
              return t7.length;
            })));
            a3 = Math.ceil(r4 / s3);
          }
          var o3 = e3.map(function(t7, i4) {
            return (t7 += "").length > s3 && (n4 ? i4 % a3 != 0 ? i4 !== e3.length - 1 && (t7 = "") : i4 > e3.length - a3 / 2 && (t7 = "") : t7 = s3 - 3 > 0 ? t7.slice(0, s3 - 3) + " ..." : t7.slice(0, s3) + ".."), t7;
          });
          return o3;
        }(this.width, t5.xAxis.labels, this.config.xIsSeries), t5.xAxis;
      }.bind(this)], ["yRegions", { width: this.width, pos: "right" }, function() {
        return this.state.yRegions;
      }.bind(this)]], n3 = this.state.datasets.filter(function(t5) {
        return "bar" === t5.chartType;
      }), i2 = this.state.datasets.filter(function(t5) {
        return "line" === t5.chartType;
      }), a2 = n3.map(function(e3) {
        var i3 = e3.index;
        return ["barGraph-" + e3.index, { index: i3, color: t4.colors[i3], stacked: t4.barOptions.stacked, valuesOverPoints: t4.config.valuesOverPoints, minHeight: 0 * t4.height }, function() {
          var t5 = this.state, e4 = t5.datasets[i3], a3 = this.barOptions.stacked, s3 = this.barOptions.spaceRatio || 0.5, r4 = t5.unitWidth * (1 - s3), o3 = r4 / (a3 ? 1 : n3.length), l2 = t5.xAxis.positions.map(function(t6) {
            return t6 - r4 / 2;
          });
          a3 || (l2 = l2.map(function(t6) {
            return t6 + o3 * i3;
          }));
          var c2 = new Array(t5.datasetLength).fill("");
          this.config.valuesOverPoints && (c2 = a3 && e4.index === t5.datasets.length - 1 ? e4.cumulativeYs : e4.values);
          var h2 = new Array(t5.datasetLength).fill(0);
          return a3 && (h2 = e4.yPositions.map(function(t6, n4) {
            return t6 - e4.cumulativeYPos[n4];
          })), { xPositions: l2, yPositions: e4.yPositions, offsets: h2, labels: c2, zeroLine: t5.yAxis.zeroLine, barsWidth: r4, barWidth: o3 };
        }.bind(t4)];
      }), s2 = i2.map(function(e3) {
        var n4 = e3.index;
        return ["lineGraph-" + e3.index, { index: n4, color: t4.colors[n4], svgDefs: t4.svgDefs, heatline: t4.lineOptions.heatline, regionFill: t4.lineOptions.regionFill, spline: t4.lineOptions.spline, showDots: t4.lineOptions.showDots, trailingDot: t4.lineOptions.trailingDot, hideDotBorder: t4.lineOptions.hideDotBorder, hideLine: t4.lineOptions.hideLine, valuesOverPoints: t4.config.valuesOverPoints }, function() {
          var t5 = this.state, e4 = t5.datasets[n4], i3 = t5.yAxis.positions[0] < t5.yAxis.zeroLine ? t5.yAxis.positions[0] : t5.yAxis.zeroLine;
          return { xPositions: t5.xAxis.positions, yPositions: e4.yPositions, values: e4.values, zeroLine: i3, radius: this.lineOptions.dotSize || 4 };
        }.bind(t4)];
      }), r3 = [["yMarkers", { width: this.width, pos: "right" }, function() {
        return this.state.yMarkers;
      }.bind(this)]];
      e2 = e2.concat(a2, s2, r3);
      var o2 = ["yMarkers", "yRegions"];
      this.dataUnitComponents = [], this.components = new Map(e2.filter(function(e3) {
        return !o2.includes(e3[0]) || t4.state[e3[0]];
      }).map(function(e3) {
        var n4 = Nt.apply(void 0, u(e3));
        return (e3[0].includes("lineGraph") || e3[0].includes("barGraph")) && t4.dataUnitComponents.push(n4), [e3[0], n4];
      }));
    } }, { key: "makeDataByIndex", value: function() {
      var t4 = this;
      this.dataByIndex = {};
      var e2 = this.state, n3 = this.config.formatTooltipX, i2 = this.config.formatTooltipY;
      e2.xAxis.labels.map(function(a2, s2) {
        var r3 = t4.state.datasets.map(function(e3, n4) {
          var a3 = e3.values[s2];
          return { title: e3.name, value: a3, yPos: e3.yPositions[s2], color: t4.colors[n4], formatted: i2 ? i2(a3) : a3 };
        });
        t4.dataByIndex[s2] = { label: a2, formattedLabel: n3 ? n3(a2) : a2, xPos: e2.xAxis.positions[s2], values: r3, yExtreme: e2.yExtremes[s2] };
      });
    } }, { key: "bindTooltip", value: function() {
      var t4 = this;
      this.container.addEventListener("mousemove", function(e2) {
        var n3 = t4.measures, i2 = v(t4.container), a2 = e2.pageX - i2.left - x(n3), s2 = e2.pageY - i2.top;
        s2 < t4.height + b(n3) && s2 > b(n3) ? t4.mapTooltipXPosition(a2) : t4.tip.hideTip();
      });
    } }, { key: "mapTooltipXPosition", value: function(t4) {
      var e2 = this.state;
      if (e2.yExtremes) {
        var n3 = function(t5, e3) {
          var n4 = arguments.length > 2 && void 0 !== arguments[2] && arguments[2], i3 = e3.reduce(function(e4, n5) {
            return Math.abs(n5 - t5) < Math.abs(e4 - t5) ? n5 : e4;
          }, []);
          return n4 ? e3.indexOf(i3) : i3;
        }(t4, e2.xAxis.positions, true);
        if (n3 >= 0) {
          var i2 = this.dataByIndex[n3];
          this.tip.setValues(i2.xPos + this.tip.offset.x, i2.yExtreme + this.tip.offset.y, { name: i2.formattedLabel, value: "" }, i2.values, n3), this.tip.showTip();
        }
      }
    } }, { key: "renderLegend", value: function() {
      var t4 = this.data;
      t4.datasets.length > 1 && c(s(r2.prototype), "renderLegend", this).call(this, t4.datasets);
    } }, { key: "makeLegend", value: function(t4, e2, n3, i2) {
      return Z(n3, i2 + 5, 12, 3, this.colors[e2], t4.name, null, 8.75, this.config.truncateLegends);
    } }, { key: "makeOverlay", value: function() {
      var t4 = this;
      this.init ? this.init = 0 : (this.overlayGuides && this.overlayGuides.forEach(function(t5) {
        var e2 = t5.overlay;
        e2.parentNode.removeChild(e2);
      }), this.overlayGuides = this.dataUnitComponents.map(function(t5) {
        return { type: t5.unitType, overlay: void 0, units: t5.units };
      }), void 0 === this.state.currentIndex && (this.state.currentIndex = this.state.datasetLength - 1), this.overlayGuides.map(function(e2) {
        var n3 = e2.units[t4.state.currentIndex];
        e2.overlay = at[e2.type](n3), t4.drawArea.appendChild(e2.overlay);
      }));
    } }, { key: "updateOverlayGuides", value: function() {
      this.overlayGuides && this.overlayGuides.forEach(function(t4) {
        var e2 = t4.overlay;
        e2.parentNode.removeChild(e2);
      });
    } }, { key: "bindOverlay", value: function() {
      var t4 = this;
      this.parent.addEventListener("data-select", function() {
        t4.updateOverlay();
      });
    } }, { key: "bindUnits", value: function() {
      var t4 = this;
      this.dataUnitComponents.map(function(e2) {
        e2.units.map(function(e3) {
          e3.addEventListener("click", function() {
            var n3 = e3.getAttribute("data-point-index");
            t4.setCurrentDataPoint(n3);
          });
        });
      }), this.tip.container.addEventListener("click", function() {
        var e2 = t4.tip.container.getAttribute("data-point-index");
        t4.setCurrentDataPoint(e2);
      });
    } }, { key: "updateOverlay", value: function() {
      var t4 = this;
      this.overlayGuides.map(function(e2) {
        var n3 = e2.units[t4.state.currentIndex];
        st[e2.type](n3, e2.overlay);
      });
    } }, { key: "onLeftArrow", value: function() {
      this.setCurrentDataPoint(this.state.currentIndex - 1);
    } }, { key: "onRightArrow", value: function() {
      this.setCurrentDataPoint(this.state.currentIndex + 1);
    } }, { key: "getDataPoint", value: function() {
      var t4 = arguments.length > 0 && void 0 !== arguments[0] ? arguments[0] : this.state.currentIndex, e2 = this.state, n3 = { index: t4, label: e2.xAxis.labels[t4], values: e2.datasets.map(function(e3) {
        return e3.values[t4];
      }) };
      return n3;
    } }, { key: "setCurrentDataPoint", value: function(t4) {
      var e2 = this.state;
      (t4 = parseInt(t4)) < 0 && (t4 = 0), t4 >= e2.xAxis.labels.length && (t4 = e2.xAxis.labels.length - 1), t4 !== e2.currentIndex && (e2.currentIndex = t4, function(t5, e3, n3) {
        var i2 = document.createEvent("HTMLEvents");
        for (var a2 in i2.initEvent(e3, true, true), n3)
          i2[a2] = n3[a2];
        t5.dispatchEvent(i2);
      }(this.parent, "data-select", this.getDataPoint()));
    } }, { key: "addDataPoint", value: function(t4, e2) {
      var n3 = arguments.length > 2 && void 0 !== arguments[2] ? arguments[2] : this.state.datasetLength;
      c(s(r2.prototype), "addDataPoint", this).call(this, t4, e2, n3), this.data.labels.splice(n3, 0, t4), this.data.datasets.map(function(t5, i2) {
        t5.values.splice(n3, 0, e2[i2]);
      }), this.update(this.data);
    } }, { key: "removeDataPoint", value: function() {
      var t4 = arguments.length > 0 && void 0 !== arguments[0] ? arguments[0] : this.state.datasetLength - 1;
      this.data.labels.length <= 1 || (c(s(r2.prototype), "removeDataPoint", this).call(this, t4), this.data.labels.splice(t4, 1), this.data.datasets.map(function(e2) {
        e2.values.splice(t4, 1);
      }), this.update(this.data));
    } }, { key: "updateDataset", value: function(t4) {
      var e2 = arguments.length > 1 && void 0 !== arguments[1] ? arguments[1] : 0;
      this.data.datasets[e2].values = t4, this.update(this.data);
    } }, { key: "updateDatasets", value: function(t4) {
      this.data.datasets.map(function(e2, n3) {
        t4[n3] && (e2.values = t4[n3]);
      }), this.update(this.data);
    } }]), r2;
  }();
  var qt = { bar: Ut, line: Ut, percentage: Ot, heatmap: It, pie: Et, donut: function(t3) {
    a(r2, Et);
    var n2 = l(r2);
    function r2(t4, i2) {
      return e(this, r2), n2.call(this, t4, i2);
    }
    return i(r2, [{ key: "configure", value: function(t4) {
      c(s(r2.prototype), "configure", this).call(this, t4), this.type = "donut", this.sliceName = "donutSlices", this.arcFunc = _, this.shapeFunc = X, this.strokeWidth = t4.strokeWidth || 30;
    } }, { key: "getRadius", value: function() {
      return this.height > this.width ? this.center.x - this.strokeWidth / 2 : this.center.y - this.strokeWidth / 2;
    } }, { key: "resetHover", value: function(t4, e2) {
      dt(t4, "translate3d(0,0,0)"), this.tip.hideTip(), t4.style.stroke = e2;
    } }, { key: "setupComponents", value: function() {
      var t4 = this.state, e2 = [[this.sliceName, {}, function() {
        return { sliceStrings: t4.sliceStrings, colors: this.colors, strokeWidth: this.strokeWidth };
      }.bind(this)]];
      this.components = new Map(e2.map(function(t5) {
        var e3 = Nt.apply(void 0, u(t5));
        return [t5[0], e3];
      }));
    } }]), r2;
  }() };
  var Gt = function t2(n2, i2) {
    return e(this, t2), function() {
      var t3 = arguments.length > 0 && void 0 !== arguments[0] ? arguments[0] : "line", e2 = arguments.length > 1 ? arguments[1] : void 0, n3 = arguments.length > 2 ? arguments[2] : void 0;
      return "axis-mixed" === t3 ? (n3.type = "line", new Ut(e2, n3)) : qt[t3] ? new qt[t3](e2, n3) : void console.error("Undefined chart type: " + t3);
    }(i2.type, n2, i2);
  };

  // frappe/public/js/frappe/ui/chart.js
  frappe.provide("frappe.ui");
  frappe.Chart = Gt;
  frappe.ui.RealtimeChart = class RealtimeChart extends frappe.Chart {
    constructor(element, socketEvent, maxLabelPoints = 8, data) {
      super(element, data);
      if (data.data.datasets[0].values.length > maxLabelPoints) {
        frappe.throw(
          __(
            "Length of passed data array is greater than value of maximum allowed label points!"
          )
        );
      }
      this.currentSize = data.data.datasets[0].values.length;
      this.socketEvent = socketEvent;
      this.maxLabelPoints = maxLabelPoints;
      this.start_updating = function() {
        frappe.realtime.on(this.socketEvent, (data2) => {
          this.update_chart(data2.label, data2.points);
        });
      };
      this.stop_updating = function() {
        frappe.realtime.off(this.socketEvent);
      };
      this.update_chart = function(label, data2) {
        if (this.currentSize >= this.maxLabelPoints) {
          this.removeDataPoint(0);
        } else {
          this.currentSize++;
        }
        this.addDataPoint(label, data2);
      };
    }
  };

  // frappe/public/js/frappe/ui/alt_keyboard_shortcuts.js
  frappe.provide("frappe.ui.keys");
  var shortcut_groups = /* @__PURE__ */ new WeakMap();
  var shortcut_group_list = [];
  frappe.ui.keys.shortcut_groups = shortcut_groups;
  frappe.ui.keys.get_shortcut_group = (parent) => {
    if (!shortcut_groups.has(parent)) {
      shortcut_groups.set(parent, new frappe.ui.keys.AltShortcutGroup());
    }
    return shortcut_groups.get(parent);
  };
  var listener_added = false;
  var $current_dropdown = null;
  var $body = $(document.body);
  frappe.ui.keys.bind_shortcut_group_event = () => {
    if (listener_added)
      return;
    listener_added = true;
    function highlight_alt_shortcuts() {
      if ($current_dropdown) {
        $current_dropdown.addClass("alt-pressed");
        $body.removeClass("alt-pressed");
      } else {
        $body.addClass("alt-pressed");
        $current_dropdown && $current_dropdown.removeClass("alt-pressed");
      }
    }
    function unhighlight_alt_shortcuts() {
      $current_dropdown && $current_dropdown.removeClass("alt-pressed");
      $body.removeClass("alt-pressed");
    }
    $(document).on("keydown", (e2) => {
      let key = (frappe.ui.keys.key_map[e2.which] || "").toLowerCase();
      if (key === "alt") {
        highlight_alt_shortcuts();
      }
      if (e2.shiftKey || e2.ctrlKey || e2.metaKey) {
        return;
      }
      if (key && e2.altKey) {
        let shortcut = get_shortcut_for_key(key);
        if (shortcut) {
          e2.preventDefault();
          shortcut.$target[0].click();
        }
        highlight_alt_shortcuts();
      }
    });
    $(document).on("keyup", (e2) => {
      if (e2.key === "Alt") {
        unhighlight_alt_shortcuts();
      }
    });
    $(document).on("mousemove", () => {
      unhighlight_alt_shortcuts();
    });
  };
  function get_shortcut_for_key(key) {
    let shortcuts = shortcut_group_list.filter((shortcut_group) => key in shortcut_group.shortcuts_dict).map((shortcut_group) => shortcut_group.shortcuts_dict[key]).filter((shortcut2) => shortcut2.$target.is(":visible"));
    let shortcut = null;
    if ($current_dropdown && $current_dropdown.is(".open")) {
      shortcut = shortcuts.find(
        (shortcut2) => $.contains($current_dropdown[0], shortcut2.$target[0])
      );
    }
    if (shortcut)
      return shortcut;
    shortcut = shortcuts.find(
      (shortcut2) => $.contains(window.cur_page.page.page.wrapper[0], shortcut2.$target[0])
    );
    return shortcut;
  }
  frappe.ui.keys.AltShortcutGroup = class AltShortcutGroup {
    constructor() {
      this.shortcuts_dict = {};
      $current_dropdown = null;
      this.bind_events();
      frappe.ui.keys.bind_shortcut_group_event();
      shortcut_group_list.push(this);
    }
    bind_events() {
      $(document).on("show.bs.dropdown", (e2) => {
        $current_dropdown && $current_dropdown.removeClass("alt-pressed");
        let $target = $(e2.target);
        if ($target.is(".dropdown, .btn-group")) {
          $current_dropdown = $target;
        }
      });
      $(document).on("hide.bs.dropdown", () => {
        $current_dropdown && $current_dropdown.removeClass("alt-pressed");
        $current_dropdown = null;
      });
    }
    add($target, $text_el) {
      if (!$text_el) {
        $text_el = $target;
      }
      let text_content = $text_el.text().trim();
      let letters = text_content.split("");
      let shortcut_letter = letters.find((letter) => {
        letter = letter.toLowerCase();
        let is_valid_char = letter >= "a" && letter <= "z";
        return !this.is_taken(letter) && is_valid_char;
      });
      if (!shortcut_letter) {
        $text_el.attr("data-label", encodeURIComponent(text_content));
        return;
      }
      for (let key in this.shortcuts_dict) {
        let shortcut2 = this.shortcuts_dict[key];
        if (shortcut2.text === text_content) {
          shortcut2.$target = $target;
          shortcut2.$text_el = $text_el;
          this.underline_text(shortcut2);
          return;
        }
      }
      let shortcut = {
        $target,
        $text_el,
        letter: shortcut_letter,
        text: text_content
      };
      this.shortcuts_dict[shortcut_letter.toLowerCase()] = shortcut;
      this.underline_text(shortcut);
    }
    underline_text(shortcut) {
      shortcut.$text_el.attr("data-label", encodeURIComponent(shortcut.text));
      let underline_el_found = false;
      let text_html = shortcut.text.split("").map((letter) => {
        if (letter === shortcut.letter && !underline_el_found) {
          letter = `<span class="alt-underline">${letter}</span>`;
          underline_el_found = true;
        }
        return letter;
      }).join("");
      text_html = `<span>${text_html}</span>`;
      let original_text_html = shortcut.$text_el.html();
      text_html = original_text_html.replace(shortcut.text.trim(), text_html.trim());
      shortcut.$text_el.html(text_html);
    }
    is_taken(letter) {
      let is_in_global_shortcut = frappe.ui.keys.standard_shortcuts.filter((s2) => !s2.page).some((s2) => s2.shortcut === `alt+${letter}`);
      return letter in this.shortcuts_dict || is_in_global_shortcut;
    }
  };

  // frappe/public/js/frappe/ui/keyboard.js
  frappe.provide("frappe.ui.keys.handlers");
  frappe.ui.keys.setup = function() {
    $(window).on("keydown", function(e2) {
      var key = frappe.ui.keys.get_key(e2);
      if (frappe.ui.keys.handlers[key]) {
        var out = null;
        for (var i2 = 0, l2 = frappe.ui.keys.handlers[key].length; i2 < l2; i2++) {
          var handler = frappe.ui.keys.handlers[key][i2];
          var _out = handler.apply(this, [e2]);
          if (_out === false) {
            out = _out;
          }
        }
        return out;
      }
    });
  };
  var standard_shortcuts = [];
  frappe.ui.keys.standard_shortcuts = standard_shortcuts;
  frappe.ui.keys.add_shortcut = ({
    shortcut,
    action,
    description,
    page,
    target,
    condition,
    ignore_inputs = false
  } = {}) => {
    if (target instanceof jQuery) {
      let $target = target;
      action = () => {
        $target[0].click();
      };
    }
    if (!condition) {
      condition = () => true;
    }
    let handler = (e2) => {
      let $focused_element = $(document.activeElement);
      let is_input_focused = $focused_element.is(
        "input, select, textarea, [contenteditable=true]"
      );
      if (is_input_focused && !ignore_inputs)
        return;
      if (!condition())
        return;
      if (action && (!page || page.wrapper.is(":visible"))) {
        let prevent_default = action(e2);
        if (prevent_default || prevent_default === void 0) {
          e2.preventDefault();
        }
      }
    };
    handler.page = page;
    frappe.ui.keys.off(shortcut, page);
    frappe.ui.keys.on(shortcut, handler);
    let existing_shortcut_index = standard_shortcuts.findIndex((s2) => s2.shortcut === shortcut);
    let new_shortcut = { shortcut, action, description, page, condition };
    if (existing_shortcut_index === -1) {
      standard_shortcuts.push(new_shortcut);
    } else {
      standard_shortcuts[existing_shortcut_index] = new_shortcut;
    }
  };
  frappe.ui.keys.show_keyboard_shortcut_dialog = () => {
    if (frappe.ui.keys.is_dialog_shown)
      return;
    let global_shortcuts = standard_shortcuts.filter((shortcut) => !shortcut.page);
    let current_page_shortcuts = standard_shortcuts.filter(
      (shortcut) => shortcut.page && shortcut.page === window.cur_page.page.page
    );
    let grid_shortcuts = standard_shortcuts.filter(
      (shortcut) => shortcut.page && shortcut.page === window.cur_page.page.frm
    );
    function generate_shortcuts_html(shortcuts, heading) {
      if (!shortcuts.length) {
        return "";
      }
      let html = shortcuts.filter((s2) => s2.condition ? s2.condition() : true).filter((s2) => !!s2.description).map((shortcut) => {
        let shortcut_label = shortcut.shortcut.split("+").map(frappe.utils.to_title_case).join("+");
        if (frappe.utils.is_mac()) {
          shortcut_label = shortcut_label.replace("Ctrl", "\u2318");
        }
        return `<tr>
					<td width="40%"><kbd>${shortcut_label}</kbd></td>
					<td width="60%">${shortcut.description || ""}</td>
				</tr>`;
      }).join("");
      if (!html)
        return "";
      html = `<h5 style="margin: 0;">${heading}</h5>
			<table style="margin-top: 10px;" class="table table-bordered">
				${html}
			</table>`;
      return html;
    }
    let global_shortcuts_html = generate_shortcuts_html(global_shortcuts, __("Global Shortcuts"));
    let current_page_shortcuts_html = generate_shortcuts_html(
      current_page_shortcuts,
      __("Page Shortcuts")
    );
    let grid_shortcuts_html = generate_shortcuts_html(grid_shortcuts, __("Grid Shortcuts"));
    let dialog = new frappe.ui.Dialog({
      title: __("Keyboard Shortcuts"),
      on_hide() {
        frappe.ui.keys.is_dialog_shown = false;
      }
    });
    dialog.$body.append(global_shortcuts_html);
    dialog.$body.append(current_page_shortcuts_html);
    dialog.$body.append(grid_shortcuts_html);
    dialog.$body.append(`
		<div class="text-muted">
			${__("Press Alt Key to trigger additional shortcuts in Menu and Sidebar")}
		</div>
	`);
    dialog.show();
    frappe.ui.keys.is_dialog_shown = true;
  };
  frappe.ui.keys.get_key = function(e2) {
    var keycode = e2.keyCode || e2.which;
    var key = frappe.ui.keys.key_map[keycode] || String.fromCharCode(keycode);
    if (e2.ctrlKey || e2.metaKey) {
      key = "ctrl+" + key;
    }
    if (e2.shiftKey) {
      key = "shift+" + key;
    }
    if (e2.altKey) {
      key = "alt+" + key;
    }
    if (e2.altKey && e2.ctrlKey) {
      return key.toLowerCase();
    }
    return key.toLowerCase();
  };
  frappe.ui.keys.on = function(key, handler) {
    if (!frappe.ui.keys.handlers[key]) {
      frappe.ui.keys.handlers[key] = [];
    }
    frappe.ui.keys.handlers[key].push(handler);
  };
  frappe.ui.keys.off = function(key, page) {
    let handlers = frappe.ui.keys.handlers[key];
    if (!handlers || handlers.length === 0)
      return;
    frappe.ui.keys.handlers[key] = handlers.filter((h2) => {
      if (!page)
        return false;
      return h2.page !== page;
    });
  };
  frappe.ui.keys.add_shortcut({
    shortcut: "ctrl+s",
    action: function(e2) {
      frappe.app.trigger_primary_action();
      e2.preventDefault();
      return false;
    },
    description: __("Trigger Primary Action"),
    ignore_inputs: true
  });
  frappe.ui.keys.add_shortcut({
    shortcut: "ctrl+g",
    action: function(e2) {
      $("#navbar-search").focus();
      e2.preventDefault();
      return false;
    },
    description: __("Open Awesomebar")
  });
  frappe.ui.keys.add_shortcut({
    shortcut: "ctrl+h",
    action: function(e2) {
      e2.preventDefault();
      $(".navbar-home img").click();
    },
    description: __("Navigate Home")
  });
  frappe.ui.keys.add_shortcut({
    shortcut: "alt+s",
    action: function(e2) {
      e2.preventDefault();
      $(".dropdown-navbar-user a").eq(0).click();
    },
    description: __("Open Settings")
  });
  frappe.ui.keys.add_shortcut({
    shortcut: "shift+/",
    action: function() {
      frappe.ui.keys.show_keyboard_shortcut_dialog();
    },
    description: __("Show Keyboard Shortcuts")
  });
  frappe.ui.keys.add_shortcut({
    shortcut: "alt+h",
    action: function(e2) {
      e2.preventDefault();
      $(".dropdown-help a").eq(0).click();
    },
    description: __("Open Help")
  });
  frappe.ui.keys.on("escape", function(e2) {
    handle_escape_key();
  });
  frappe.ui.keys.on("esc", function(e2) {
    handle_escape_key();
  });
  frappe.ui.keys.on("enter", function(e2) {
    if (window.cur_dialog && cur_dialog.confirm_dialog) {
      cur_dialog.get_primary_btn().trigger("click");
    }
  });
  frappe.ui.keys.on("ctrl+down", function(e2) {
    var grid_row = frappe.ui.form.get_open_grid_form();
    grid_row && grid_row.toggle_view(false, function() {
      grid_row.open_next();
    });
  });
  frappe.ui.keys.on("ctrl+up", function(e2) {
    var grid_row = frappe.ui.form.get_open_grid_form();
    grid_row && grid_row.toggle_view(false, function() {
      grid_row.open_prev();
    });
  });
  frappe.ui.keys.add_shortcut({
    shortcut: "shift+ctrl+r",
    action: function() {
      frappe.ui.toolbar.clear_cache();
    },
    description: __("Clear Cache and Reload")
  });
  frappe.ui.keys.key_map = {
    8: "backspace",
    9: "tab",
    13: "enter",
    16: "shift",
    17: "ctrl",
    91: "meta",
    18: "alt",
    27: "escape",
    37: "left",
    39: "right",
    38: "up",
    40: "down",
    32: "space",
    112: "f1",
    113: "f2",
    114: "f3",
    115: "f4",
    116: "f5",
    191: "/",
    188: "<",
    190: ">"
  };
  "abcdefghijklmnopqrstuvwxyz".split("").forEach((letter, i2) => {
    frappe.ui.keys.key_map[65 + i2] = letter;
  });
  frappe.ui.keyCode = {
    ESCAPE: 27,
    LEFT: 37,
    RIGHT: 39,
    UP: 38,
    DOWN: 40,
    ENTER: 13,
    TAB: 9,
    SPACE: 32,
    BACKSPACE: 8
  };
  function handle_escape_key() {
    var _a;
    close_grid_and_dialog();
    (_a = document.activeElement) == null ? void 0 : _a.blur();
  }
  function close_grid_and_dialog() {
    var open_row = $(".grid-row-open");
    if (open_row.length) {
      var grid_row = open_row.data("grid_row");
      grid_row.toggle_view(false);
      return false;
    }
    if (cur_dialog && !cur_dialog.no_cancel_flag && !cur_dialog.static) {
      cur_dialog.cancel();
      return false;
    }
  }

  // frappe/public/js/frappe/event_emitter.js
  frappe.provide("frappe.utils");
  var EventEmitterMixin = {
    init() {
      this.jq = jQuery({});
    },
    trigger(evt, data) {
      !this.jq && this.init();
      this.jq.trigger(evt, data);
    },
    once(evt, handler) {
      !this.jq && this.init();
      this.jq.one(evt, (e2, data) => handler(data));
    },
    on(evt, handler) {
      !this.jq && this.init();
      this.jq.bind(evt, (e2, data) => handler(data));
    },
    off(evt, handler) {
      !this.jq && this.init();
      this.jq.unbind(evt, (e2, data) => handler(data));
    }
  };
  frappe.utils.make_event_emitter = function(object) {
    Object.assign(object, EventEmitterMixin);
    return object;
  };
})();
//# sourceMappingURL=website.bundle.X5T3KKLJ.js.map
