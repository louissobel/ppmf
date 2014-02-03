"use strict";
/* div slider */


var SLIDE_CLASS = "div-slide";
var TRANSITION_DURATION = 1000; // milliseconds.

var Slide = function (options) {
  // Has pos, -100 for all the way to the left, 0 for showing, 100 for all the way to the right
  this.index = options.index;
  this.outOf = options.outOf;

  this.element = options.element;

  this.basePercentPos = 0;
  this.oneSlidePercent = (1 / this.outOf) * 100;

  // move it to the right place, setting pos
  this._moveIntoPlace();
};

Slide.prototype._moveIntoPlace = function () {
  // moves the slide to the right stack if it is not already there.
  if (this.index === 0) {
    // it is already OK, at 0 (showing)
    // To jank it, fake the base pos as a negative value
    this.pos = 0;
    this.basePercentPos = -this.oneSlidePercent;
  } else {
    // We have to move it!, or it's 1 and everything is OK
    var requiredShift = this.index - 1;
    this.basePercentPos = requiredShift * this.oneSlidePercent;
    this._setPercentPos(this.basePercentPos);
    this.pos = 100;
  }
};

Slide.prototype._setPercentPos = function (percent) {
  this.element.style.right = percent + "%";
};

Slide.prototype.setPos = function (pos) {
  // 100 --> basePercent + 0 * UNIT
  // 0 --> basePercent + 1 * UNIT
  // -100 --> basePercent + 2 * UNIT

  // TODO check for out of range?
  var unitMultiplier = (100 - pos) / 100;
  this._setPercentPos(this.basePercentPos + this.oneSlidePercent * unitMultiplier);
  this.pos = pos;
};

Slide.prototype.animateTo = function (pos, duration) {
  var refreshEvery = 50; // milliseconds
  // round duration to nearest multiple of refreshEvery;
  duration = Math.round(duration / refreshEvery) * refreshEvery;
  var frames = duration / refreshEvery
    , distance = pos - this.pos
    , start = this.pos
    ;

  var controlFunc = function (x) {
    // x \in (0, 1]
    // return value in [0, 1]
    // x = 1 ---> y = 1

    // Quartic
    return 1 - Math.pow((x - 1), 4);
  };

  var animationStep = function (stepIndex) {
    var progress = controlFunc(stepIndex / frames) * distance;
    this.setPos(start + progress);
    if (stepIndex !== frames) {
      this.animationTimeout = setTimeout(function () {
        animationStep(stepIndex + 1);
      }, refreshEvery);
    } else {
      // done.
      this.animationTimeout = null;
    }
  }.bind(this);

  // Take control. Shouldn't happen though;
  if (this.animationTimeout) {
    clearTimeout(this.animationTimeout);
  }
  animationStep(1);
};

var SlideView = module.exports = function (wrapper, onrotate) {
  // wrapper is element containing N elements with class SLIDE_CLASS
  // first one is already showing
  // only one rotate at a time!
  var children = wrapper.children
    , slideElements = []
    , numSlides = 0
    , slides = []
    , i
    ;

  for (i=0; i<children.length; i++) {
    if (children[i].className.match(new RegExp("\\b" + SLIDE_CLASS + "\\b"))) {
      numSlides++;
      slideElements.push(children[i]);
    }
  }

  for (i=0; i<numSlides; i++) {
    slides.push(new Slide({
      index: i
    , outOf: numSlides
    , element: slideElements[i]
    }));
  }

  this.leftStack = [];
  this.current = slides.shift();
  this.rightStack = slides.reverse(); // so push and pop work.
  this.index = 0;
  this.numSlides = numSlides;
  this.onrotate = onrotate || function () {};
};

SlideView.prototype.rotateLeft = function () {
  if (this.index === this.numSlides - 1){
    this.index = 0;
  } else {
    this.index++;
  }
  this._rotate(this.rightStack, this.leftStack, -100);
};

SlideView.prototype.rotateRight = function () {
  if (this.index === 0) {
    this.index = this.numSlides - 1;
  } else {
    this.index--;
  }
  this._rotate(this.leftStack, this.rightStack, 100);
};

SlideView.prototype._rotate = function (source, sink, leavePos) {
  if (this.rotating) {
    // NOOP; should throw error?
    return;
  }

  this.rotating = true;
  if (this.numSlides === 1) {
    // NOOP;
    return this.onrotate(this.index);
  } else {
    if (source.length === 0) {
      var temp;
      temp = sink;
      sink = source;
      source = temp;

      this._flip();
    }

    var enter = source.pop()
      , leave = this.current
      ;
    leave.animateTo(leavePos, TRANSITION_DURATION);
    enter.animateTo(0, TRANSITION_DURATION);

    setTimeout(function () {
      this.rotating = false;
      this.onrotate(this.index);
    }.bind(this), TRANSITION_DURATION);

    sink.push(leave);
    this.current = enter;
  }
};

SlideView.prototype._flip = function () {
  // everything in left goes to right side
  // everything in right goes to left side
  this.rightStack.reverse();
  this.leftStack.reverse();

  var i
    , temp
    ;
  for (i=0; i<this.leftStack.length; i++) {
    this.leftStack[i].setPos(100);
  }
  for (i=0; i<this.rightStack.length; i++) {
    this.rightStack[i].setPos(-100);
  }

  // now switch them.
  temp = this.leftStack;
  this.leftStack = this.rightStack;
  this.rightStack = temp;
};
