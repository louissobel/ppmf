// The main view for the page
// Interfaces with DOM

var Page = module.exports = function () {
  this.decryptForm = document.forms.decryptForm;
  this.fileLink = document.getElementById('fileLink');
  this.progressMeter = document.getElementById('progressMeter');

  // Callback for form submit
  this.submitCallback = null;

  this.decryptForm.onsubmit = function () {
    if (this.submitCallback) {
      var password = this.decryptForm.children.password.value;
      this.submitCallback(password);
      return false;
    }
  }.bind(this);

};

Page.prototype.showDecryptForm = function () {
  this.decryptForm.style.visibility = 'visible';
};

Page.prototype.hideDecryptForm = function () {
  this.decryptForm.style.visibility = 'hidden';
};

Page.prototype.getB64CipherText = function () {
  var ciphertextHolder = document.getElementById('ciphertext');
  return ciphertextHolder.textContent.split('\n').join('');
};

Page.prototype.showFileLink = function (url) {
  this.fileLink.href = url;
  this.fileLink.style.visibility = 'visible';
};

Page.prototype.setProgressMeter = function (percentage) {
  this.progressMeter.innerHTML = percentage + "%";
};