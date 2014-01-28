"use strict";

var Page = require("./page")
  , base64 = require("../core/base64")
  , aes = require("../core/aes")
  , HtmlWrapper = require("./html_wrapper")
  ;

var EncryptController = module.exports = function () {
  this.page = new Page();
  this.page.submitCallback = this.submitEncrypt.bind(this);
};

EncryptController.prototype.submitEncrypt = function (password, file) {
  // file is a file Object?

  // handle no file
  // handle no password

  // turn the file into a base64 string
  base64.blobToB64(file, function (err, result) {
    var decryptedObj = {
          b64plaintext: result
        , mimetype: file.type
        }
      , jsonifiedString = JSON.stringify(decryptedObj)
      , b64jsonifiedString = btoa(jsonifiedString)
      ;
    aes.encrypt(b64jsonifiedString, password, this.encryptProgressCallback.bind(this));
  }.bind(this));

};

EncryptController.prototype.encryptProgressCallback = function (err, percent, done, result) {
  if (done) {
    var htmlWrapper = new HtmlWrapper(this.page.getDecryptTemplate())
      , htmlBlob = htmlWrapper.wrap(result)
      , blobUrl = URL.createObjectURL(htmlBlob)
      ;

    this.page.setResultUrl(blobUrl);

  } else {
    this.page.setProgress(percent);
  }
};
