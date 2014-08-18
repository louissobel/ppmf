"use strict";
/* String builders so that we don't have to block!
   Algorithms and names taken from cryptojs
*/

// Helper
var WordArrayByteIterator = function (wordArray) {
  wordArray.clamp();
  this._pos = 0;
  this._words = wordArray.words;
  this._sigBytes = wordArray.sigBytes;
};

WordArrayByteIterator.prototype.next = function () {
  if (!this.hasNext()) {
    return null;
  }
  var cp = this._pos;
  this._pos++;
  return (this._words[cp >>> 2] >>> (24 - (cp % 4) * 8)) & 0xff;
};

WordArrayByteIterator.prototype.hasNext = function () {
  return this._pos < this._sigBytes;
};


// Latin1Builder is simple, because 1:1 between sigByte and
// ultimate string representation.
var Latin1Builder = module.exports.Latin1Builder = function () {
  this._string = "";
};

Latin1Builder.prototype.update = function (wordArray) {
  // https://code.google.com/p/crypto-js/source/browse/tags/3.1.2/src/core.js#366
  var chars = []
    , byteIterator = new WordArrayByteIterator(wordArray)
    ;

  while (byteIterator.hasNext()) {
      chars.push(String.fromCharCode(byteIterator.next()));
  }

  this._string += chars.join("");
};

Latin1Builder.prototype.finalize = function () {
  return this._string;
};

Latin1Builder.prototype.peek = function () {
  return this._string;
};

// Base64Builder is harder.
var Base64Builder = module.exports.Base64Builder = function () {
  this._string = "";
  this._bytes = [];
  this._map = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/=";
};

Base64Builder.prototype.update = function (wordArray) {
  // https://code.google.com/p/crypto-js/source/browse/tags/3.1.2/src/enc-base64.js#25

  var blocks = []
    , byteIterator = new WordArrayByteIterator(wordArray)
    , bytes = this._bytes
    ;

  while (byteIterator.hasNext()) {
    // Invariant that bytes will never have 3 items
    // at start of this loop.
    bytes.push(byteIterator.next());
    if (bytes.length === 3) {
      blocks.push(this._doBlock(bytes));
    }
  }

  this._string += blocks.join("");
};

Base64Builder.prototype.finalize = function () {
  var bytes = this._bytes;
  if (bytes.length === 0) {
    return this._string;
  } else {
    var left = bytes.length;
    while (bytes.length < 3) {
      bytes.push(0);
    }
    this._string += this._doBlock(bytes).substr(0, left === 1 ? 2 : 3);
  }
  this._addPadding();
  return this._string;
};

Base64Builder.prototype._doBlock = function (bytes) {
  var triplet = (bytes.shift() << 16) | (bytes.shift() << 8) | bytes.shift()
    , j
    , out = ""
    , v
    ;
  for (j = 0; j < 4; j++) {
      v = (triplet >>> (6 * (3 - j))) & 0x3f;
      out += this._map.charAt(v);
  }
  return out;
};

Base64Builder.prototype._addPadding = function () {
  var paddingChar = this._map.charAt(64);
  while (this._string.length % 4 !== 0) {
    this._string += paddingChar;
  }
};

Base64Builder.prototype.peek = function () {
  return this._string;
};
