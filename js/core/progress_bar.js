"use strict";

/* wraps bootstrap progress bar */

var throttle = require("./utils").throttle;

var ProgressBar = module.exports = function (div) {
  // div is the dom element
  this.div = div;
};

ProgressBar.prototype.setPercent = throttle(function (percent) {
  // percent is number 0 - 100
  this.div.style.width = percent + "%";
}, 10, true);

ProgressBar.prototype.show = function () {
  this.div.parentNode.style.display = "block";
};

ProgressBar.prototype.hide = function () {
  this.div.parentNode.style.display = "none";
};
