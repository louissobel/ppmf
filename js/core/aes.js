"use strict";

var CryptoJS = require("./cryptojs")
  , WordArrayChunker = require("./word_array_chunker")
  , stringBuilders = require("./string_builders")
  ;

var aes = module.exports;

// Should be multiple of 4 (cryptojs works in words of 4 bytes).
aes.CHUNK_SIZE = 4096 * 4; // 4KB

aes.decrypt = function (b64ciphertext, password, callback) {
  var cipherParams = CryptoJS.format.OpenSSL.parse(b64ciphertext)
    , derivedParams = _getKeyAndIv(password, cipherParams.salt)
    , decryptor = CryptoJS.algo.AES.createDecryptor(derivedParams.key, {iv: derivedParams.iv})
    ;

  _runCipher({
    cipher: decryptor
  , input: cipherParams.ciphertext
  , builder: new stringBuilders.Latin1Builder()
  }, callback);
};

aes.encrypt = function (plaintext, password, callback) {
  var derivedParams = _getKeyAndIv(password) // Will generate random salt.
    , encryptor = CryptoJS.algo.AES.createEncryptor(derivedParams.key, {iv: derivedParams.iv})
    , plainWords = CryptoJS.enc.Latin1.parse(plaintext)
    ;

  // Need to initialize it with the salt.
  // 0x53616c74, 0x65645f5f are OpenSSL magic salt numbers (Salted__)
  var outputPrefix = CryptoJS.lib.WordArray.create([0x53616c74, 0x65645f5f]).concat(derivedParams.salt)
    , builder = new stringBuilders.Base64Builder()
    ;
  builder.update(outputPrefix);

  _runCipher({
    cipher: encryptor
  , input: plainWords
  , builder: builder
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
  var wordsPerChunk = options.wordsPerChunk || aes.CHUNK_SIZE // Four kilobytes in a chunk.
    , cipher = options.cipher
    , input = options.input
    , builder = options.builder
    , wordChunker = new WordArrayChunker(input, wordsPerChunk)
    ;

  _cipherStep(wordChunker, cipher, builder, callback);
};

var _cipherStep = function (wordChunker, cipher, builder, callback) {
  if (!wordChunker.hasNext()) {

    // base case - finalize and finish
    builder.update(cipher.finalize());

    var result;
    try {
      result = builder.finalize();
    } catch (err) {
      return callback(err);
    }

    return callback(null, 1, true, result, result);
  } else {

    // do a step, tell callback, schedule this again
    // callback can return false to end things
    builder.update(cipher.process(wordChunker.next()));
    var keepGoing = callback(null, wordChunker.percentComplete(), false, null, builder.peek());
    if (keepGoing !== false) {
      setTimeout(function () {
        _cipherStep(wordChunker, cipher, builder, callback);
      }, 0);
    }
  }
};
