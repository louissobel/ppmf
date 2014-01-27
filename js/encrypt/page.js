"use strict";

// Page View for encryption controller

var Page = module.exports = function () {
  this.encryptForm = document.forms.encryptForm;

  this.encryptForm.onsubmit = function (e) {
    if (this.submitCallback) {
      var password = this.encryptForm.children.password.value
        , selectedFile = this.encryptForm.children.file.files[0] || null
        ;
      this.submitCallback(password, selectedFile);
      return false;
    }
  }.bind(this);

};
