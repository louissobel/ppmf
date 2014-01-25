
var Page = require('./page')
  , CryptoJS = require('./cryptojs')
  , decrypt = require('./decrypt')
  , b64ToBlob = require('./b64_to_blob')
  ;

var HtmlEncController = module.exports = function () {
  // Setup page
  this.page = new Page();

  this.page.submitCallback = this.submitDecrypt.bind(this);

  this.page.showDecryptForm();

};

HtmlEncController.prototype.submitDecrypt = function (password) {
  var b64ciphertext = this.page.getB64CipherText();
  decrypt(b64ciphertext, password, this.decryptProgressCallback.bind(this));
};

HtmlEncController.prototype.decryptProgressCallback = function (error, percent, done, result) {
  if (error) {
    // for now, assume this means password was bad
    this.badPassword(0);
  } else if (done) {

    var binaryResult
      , decryptedObject
      , blob
      , blobUrl
      ;

    try {
      binaryResult = atob(result);
    } catch (err) {
      return this.badPassword(1);
    }

    try {
      decryptedObj = JSON.parse(binaryResult);
    } catch (err) {
      return this.badPassword(2);
    }

    try {
      blob = b64ToBlob(decryptedObj.b64plaintext, decryptedObj.mimetype);
    } catch (err) {
      return this.badPassword(3);
    }

    blobUrl = URL.createObjectURL(blob);
    this.page.showFileLink(blobUrl);
    this.page.hideDecryptForm();

  } else {
    this.page.setProgressMeter(Math.floor(percent * 10000) / 100);
  }

};

HtmlEncController.prototype.badPassword = function (a) {
  alert('WRONG PASSWORD' + a);
};