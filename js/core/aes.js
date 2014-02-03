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
  , format: CryptoJS.enc.Latin1
  }, callback);
};

aes.encrypt = function (plaintext, password, callback) {
  var derivedParams = _getKeyAndIv(password) // Will generate random salt.
    , encryptor = CryptoJS.algo.AES.createEncryptor(derivedParams.key, {iv: derivedParams.iv})
    , plainWords = CryptoJS.enc.Latin1.parse(plaintext)
    ;

  // Need to initialize it with the salt.
  // 0x53616c74, 0x65645f5f are OpenSSL magic salt numbers (Salted__)
  var output = CryptoJS.lib.WordArray.create([0x53616c74, 0x65645f5f]).concat(derivedParams.salt);

  _runCipher({
    cipher: encryptor
  , input: plainWords
  , output: output
  , format: CryptoJS.enc.Base64
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
    , format = options.format
    , wordChunker = new WordArrayChunker(input, wordsPerChunk)
    ;

  _cipherStep(wordChunker, cipher, output, format, callback);
};

var _cipherStep = function (wordChunker, cipher, output, format, callback) {
  if (!wordChunker.hasNext()) {

    // base case - finalize and finish
    output.concat(cipher.finalize());

    var result;
    try {
      result = output.toString(format);
    } catch (err) {
      return callback(err);
    }

    return callback(null, 1, true, result, output);
  } else {

    // do a step, tell callback, schedule this again
    // callback can return false to end things
    output.concat(cipher.process(wordChunker.next()));
    var keepGoing = callback(null, wordChunker.percentComplete(), false, null, output);
    if (keepGoing !== false) {
      setTimeout(function () {
        _cipherStep(wordChunker, cipher, output, format, callback);
      }, 0);
    }
  }
};
