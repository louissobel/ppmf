var CryptoJS = require('./cryptojs');

var WordArrayChunker = module.exports = function (wordArray, wordsPerChunk) {
  this.wordArray = wordArray;
  this.wordArray.clamp();

  this.wordsPerChunk = wordsPerChunk;

  this.totalWords = wordArray.words.length;
  this.wordsRemaining = wordArray.words.length;

  this.lastChunkEnd = 0; // exclusive

};

WordArrayChunker.prototype.next = function () {
  if (!this.hasNext()) {
    return null;
  }

  var thisChunkEnd
    , thisChunk
    , sigBytes
    ;

  thisChunkEnd = this.lastChunkEnd + this.wordsPerChunk;
  thisChunk = this.wordArray.words.slice(this.lastChunkEnd, thisChunkEnd);
  this.lastChunkEnd = thisChunkEnd;

  if (thisChunkEnd >= this.totalWords) {
    // this is the last chunk!
    // if wordArray sigbytes is multiple of 4, then 
    // our sigbytes is the number of words we got times 4
    //
    // but otherwise, its one minus th number of wrods we got times 4
    // plus wordArray sigbytes % 4
    if (this.wordArray.sigBytes % 4 === 0) {
      sigBytes = thisChunk.length * 4;
    } else {
      sigBytes = (thisChunk.length - 1) * 4 + (this.wordArray.sigBytes % 4);
    }
  } else {
    // otherwise, we know for sure that sigBytes is length of the chunk times 4
    sigBytes = thisChunk.length * 4;
  }

  this.wordsRemaining -= thisChunk.length;
  return CryptoJS.lib.WordArray.create(thisChunk, sigBytes);

};

WordArrayChunker.prototype.hasNext = function () {
  return (this.wordsRemaining > 0);
};

WordArrayChunker.prototype.percentComplete = function () {
  return (this.totalWords - this.wordsRemaining) / this.totalWords;
};
