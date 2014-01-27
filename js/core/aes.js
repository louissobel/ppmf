"use strict";

var CryptoJS = require("./cryptojs")
  , WordArrayChunker = require("./word_array_chunker")
  ;

var aes = module.exports;

aes.decrypt = function (b64ciphertext, password, callback) {
  var cipherParams = CryptoJS.format.OpenSSL.parse(b64ciphertext)
    , derivedParams = _getKeyAndIv(password, cipherParams.salt)
    , decryptor = CryptoJS.algo.AES.createDecryptor(derivedParams.key, {iv: derivedParams.iv})
    ;

  _runCipher({
    cipher: decryptor
  , input: cipherParams.ciphertext
  }, callback);
};

aes.encrypt = function (b64plaintext, password, callback) {
  var derivedParams = _getKeyAndIv(password) // Will generate random salt.
    , encryptor = CryptoJS.algo.AES.createEncryptor(derivedParams.key, {iv: derivedParams.iv})
    , plainWords = CryptoJS.enc.Base64.parse(b64plaintext)
    ;

  // Need to initialize it with the salt.
  // 0x53616c74, 0x65645f5f are OpenSSL magic salt numbers (SALTED__)
  var output = CryptoJS.lib.WordArray.create([0x53616c74, 0x65645f5f]).concat(derivedParams.salt);

  _runCipher({
    cipher: encryptor
  , input: plainWords
  , output: output
  }, callback);
};

var _getKeyAndIv = function (password, salt) {
  var cipherAlgo = CryptoJS.algo.AES
    , keySize = cipherAlgo.keySize
    , ivSize = cipherAlgo.ivSize
      // TODO: make the KDF configurable?
    , derivedParams = CryptoJS.kdf.OpenSSL.execute(password, keySize, ivSize, salt)
    ;
  return derivedParams;
};

var _runCipher = function (options, callback) {
  options = options || {};
  var output = options.output || CryptoJS.lib.WordArray.create()
    , wordsPerChunk = options.wordsPerChunk || 1024 // Four kilobytes in a chunk.
    , cipher = options.cipher
    , input = options.input
    , wordChunker = new WordArrayChunker(input, wordsPerChunk)
    ;

  _cipherStep(wordChunker, cipher, output, callback);
};

var _cipherStep = function (wordChunker, cipher, output, callback) {
  if (!wordChunker.hasNext()) {

    // base case - finalize and finish
    output.concat(cipher.finalize());

    var result;
    try {
      result = output.toString(CryptoJS.enc.Base64);
    } catch (err) {
      return callback(err);
    }

    return callback(null, 1, true, result);
  } else {

    // do a step, tell callback, schedule this again
    output.concat(cipher.process(wordChunker.next()));
    callback(null, wordChunker.percentComplete(), false);

    setTimeout(function () {
      _cipherStep(wordChunker, cipher, output, callback);
    }, 0);
  }
};
