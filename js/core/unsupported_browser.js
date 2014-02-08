"use strict";

/* exports function that if called will display an error message
   separate from Page because that way page can be browser rough
*/

module.exports = function () {
  var errorBox = document.getElementById("error-box");
  errorBox.style.display = "block";
  errorBox.innerHTML = "You are using an unsupported browser.";
};
