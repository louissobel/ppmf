"use strict";

/* base page. */

var ProgressBar = require("./progress_bar");

var BasePage = module.exports = function () {};

BasePage.prototype.init = function () {
  this.errorBox = document.getElementById("error-box");
  this.readyBox = document.getElementById("ready-box");

  this.progressBar = new ProgressBar(document.getElementById("progress-bar"));

  this.actionForm = document.getElementById("action-form");
  this.passwordInput = document.getElementById("password");
  
  this.actionForm.onsubmit = this.handleFormSubmit.bind(this);
  return this;
};

BasePage.prototype.handleFormSubmit = function () {
  // Abstract
  return false;
};

BasePage.prototype.setProgress = function (percent) {
  this.progressBar.setPercent(Math.floor(percent * 10000) / 100);
};

BasePage.prototype.showReady = function () {
  this.readyBox.style.display = "block";
};

BasePage.prototype.hideReady = function () {
  this.readyBox.style.display = "none";
};

BasePage.prototype.showError = function (errmessage) {
  this.errorBox.style.display = "block";
  this.errorBox.innerHTML = errmessage;
};

BasePage.prototype.hideError = function () {
  this.errorBox.style.display = "none";
};

BasePage.prototype.showProgressBar = function () {
  this.progressBar.show();
};

BasePage.prototype.hideProgressBar = function () {
  this.progressBar.hide();
};