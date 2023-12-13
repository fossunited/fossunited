function subscribeHandler(event) {
  let emailInput = document.getElementById("email").value;
  frappe.call({
    method: "frappe.client.insert",
    args: {
      doc: {
        doctype: "Email Group Member",
        email: emailInput,
        email_group: "FOSSU Newsletter",
      },
    },
    callback: (r) => {
      console.log(r);
    },
    error: (e) => {
      console.error(e);
    },
  });
  event.stopPropagation();
  document
    .getElementById("subscribe")
    .removeEventListener("click", subscribeHandler);
}
document
  .getElementById("subscribe")
  .addEventListener("click", subscribeHandler);

function showSuccessMsg() {
  setTimeout( function (){
    document.getElementById("subscribed-page").style.display = 'block';
  }, 500);
  let sections = ["header", "newsletters-list", "footer-cta", "subscribe-section"];
  for (let i=0; i < sections.length; i++) {
    document.getElementById(sections[i]).style.display = 'none';
  }
}

document.getElementById('subscribe').addEventListener('click', function () {
  showSuccessMsg();
});
