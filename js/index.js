"use strict";

/* global Buffer */

var mime = require("mime")
  , path = require("path")
  ;

var HtmlWrapper = require("./encrypt/html_wrapper")
  , aes = require("./core/aes")
  ;

var noop = function () {};

// To extract the ciphertext from htmlString
var CIPHERTEXT_REGEX = /<div id="ciphertext"\>([\s\S]*?)<\/div\>/;

module.exports.encrypt = function (options) {
  options = options || {};
  var templateString = options.template
    , plaintextBuffer = options.data
    , filename = options.filename
    , password = options.password
    , progressCallback = options.onprogress || noop
    , callback = options.oncomplete || noop
    ;

  var wrapper = new HtmlWrapper(templateString)
    , obj = {
        b64plaintext: plaintextBuffer.toString("base64")
      , mimetype: mime.lookup(filename)
      , filename: path.basename(filename)
      }
    , objectString = JSON.stringify(obj)
    ;

  aes.encrypt(objectString, password, function (err, percent, done, result) {
    if (err) {
      return callback(err);
    }

    if (done) {
      return callback(null, wrapper.wrap(result));
    } else {
      return progressCallback(percent);
    }
  });

};

module.exports.decrypt = function (options) {
  options = options || {};
  var htmlString = options.htmlString
    , password = options.password
    , ciphertextRegex = options.ciphertextRegex || CIPHERTEXT_REGEX
    , progressCallback = options.onprogress || noop
    , callback = options.oncomplete || noop
    ;

  var regexMatch = ciphertextRegex.exec(htmlString);
  if (!regexMatch) {
    return callback(new Error("Unable to find cipher text in html string"));
  }

  var ciphertext = regexMatch[1].split("\n").join("");

  aes.decrypt(ciphertext, password, function (err, percent, done, result) {
    if (err) {
      return callback(err);
    }

    if (done) {
      // Unpack it
      var obj
        , plaintext
        ;

      try {
        obj = JSON.parse(result);
      } catch (error) {
        return callback(new Error("Invalid Password"));
      }

      try {
        plaintext = new Buffer(obj.b64plaintext, "base64");
      } catch (error) {
        return callback(new Error("Invalid Password"));
      }

      return callback(null, plaintext);
    } else {
      return progressCallback(percent);
    }
  });

};