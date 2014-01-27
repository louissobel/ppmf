"use strict";

var Page = require("./page")
  , base64 = require("../core/base64")
  , aes = require("../core/aes")
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
    aes.encrypt(b64jsonifiedString, document.getElementById("password").value, this.encryptProgressCallback.bind(this));
  }.bind(this));

};

EncryptController.prototype.encryptProgressCallback = function (err, percent, done, result) {
  if (done) {
    // create an html blob.
    // TODO this need be refactored
    // TODO so much b64!!
    // TODO SO MUCH JANK
    var htmlString = document.getElementById("decrypt-template").innerText
      , wrapped = htmlString.replace("{{ ciphertext }}", result.match(/.{1,128}/g).join("\n"))
      , blob = base64.b64ToBlob(btoa(wrapped), "text/html")
      , blobUrl = URL.createObjectURL(blob)
      ;

    var e = document.getElementById("done-link");
    e.href = blobUrl;

  } else {
    console.log(percent);
  }
};
