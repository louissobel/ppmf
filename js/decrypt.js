"use strict";

var CryptoJS = require("./cryptojs")
  , WordArrayChunker = require("./word_array_chunker")
  ;

var decrypt = module.exports = function (b64ciphertext, password, callback) {
  // calls back (err, percent done, done, result)

      // get iv, key from password
  var cipher = CryptoJS.algo.AES

      // need to parse the salt out first! (TODO error catching?)
    , cipherParams = CryptoJS.format.OpenSSL.parse(b64ciphertext) // slow and blocking


    , derivedParams = CryptoJS.kdf.OpenSSL.execute(password, cipher.keySize, cipher.ivSize, cipherParams.salt)

      // Four Kilobytes
    , wordsPerChunk = 1024 * 8
    , wordChunker = new WordArrayChunker(cipherParams.ciphertext, wordsPerChunk)

    , decryptor = CryptoJS.algo.AES.createDecryptor(derivedParams.key, {iv: derivedParams.iv})
    , decrypted = CryptoJS.lib.WordArray.create()
    ;

  _decryptStep(wordChunker, decryptor, decrypted, callback);
};

var _decryptStep = function (wordChunker, decryptor, decrypted, callback) {
  if (!wordChunker.hasNext()) {

    // base case - finalize and finish
    decrypted.concat(decryptor.finalize());

    var result;
    try {
      result = decrypted.toString(CryptoJS.enc.Base64);
    } catch (err) {
      return callback(err);
    }

    return callback(null, 1, true, result);
  } else {

    // do a step, tell callback, schedule this again
    decrypted.concat(decryptor.process(wordChunker.next()));
    callback(null, wordChunker.percentComplete(), false);

    setTimeout(function () {
      _decryptStep(wordChunker, decryptor, decrypted, callback);
    }, 0);
  }
};
