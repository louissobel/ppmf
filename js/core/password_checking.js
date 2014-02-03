"use strict";

var PREFIX_STRING = "PPPP"
  , FIRST_WORD = 0x50505050
  ;

module.exports.wrap = function (string) {
  return PREFIX_STRING + string;
};

module.exports.unwrap = function (string) {
  return string.substring(PREFIX_STRING.length);
};

module.exports.checkString = function (string) {
  return string.substring(0, PREFIX_STRING.length) === PREFIX_STRING;
};

module.exports.checkWordArray = function (wordArray) {
  // if word array isnt long enough, return true. because we can't say no.
  if (wordArray.words.length === 0) {
    return true;
  }
  return wordArray.words[0] === FIRST_WORD;
};
