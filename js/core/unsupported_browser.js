"use strict";

/* exports function that if called will display an error message
   separate from Page because that way page can be browser rough
*/

module.exports = function () {
  var errorBox = document.getElementById("error-box");
  errorBox.style.display = "block";
  errorBox.innerHTML = "<p>You are using an unsupported browser.</p>" +
                       "<p>Supported browsers include Chrome, Firefox, Opera, Internet Explorer 10+, and Safari 6.1+</p>";
};
