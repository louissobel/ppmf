"use strict";

/* global Buffer, console */

var Base64Builder = require("./core/string_builders").Base64Builder
  , CryptoJS = require("./core/cryptojs")
  , WordArrayChunker = require("./core/word_array_chunker")
  ;

var encode = function (string) {
  var words = CryptoJS.enc.Latin1.parse(string)
    , chunker = new WordArrayChunker(words, 4)
    , builder = new Base64Builder()
    ;
  while (chunker.hasNext()) {
    builder.update(chunker.next());
  }
  return builder.finalize();
};

var doTest = function (string) {
  var e = new Buffer(string).toString("base64")
    , a = encode(string)
    ;
  return e === a;
};

var all = true;
for (var i = 1; i<=5000; i+=7) {
  var string = "";
  for (var si=0;si<i;si++) {
    string += String.fromCharCode(Math.floor(Math.random() * 100) + 25);
  }
  all &= doTest(string);
  console.log(i);
}
console.log(all);
