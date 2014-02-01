"use strict";

/* global process, Buffer */

// standalone CLI for node environment
// (not really standalone)
// with API for webby? maybe later

var argv = require("optimist")
           .demand("password")
           .demand("outfile")
           .describe("encrypt", "File to encrypt")
           .describe("decrypt", "File to decrypt")
           .boolean("quiet")
           .default("quiet", false)
           .describe("quiet", "make it quiet")
           .describe("template", "File to use as a template. Defaults to one from website.")
           .check(function (argv) {
             if (!(argv.encrypt || argv.decrypt)) {
               throw new Error("Must use either --encrypt or --decrypt");
             } if (argv.encrypt && argv.decrypt) {
               throw new Error("Cannot both encrypt and decrypt.");
             }
           })
           .argv
  , request = require("request")
  , mime = require("mime")
  , path = require("path")
  , fs = require("fs")
  , url = require("url")
  , aes = require("./core/aes")
  , HtmlWrapper = require("./encrypt/html_wrapper")
  ;

var CIPHERTEXT_REGEX = /<div id="ciphertext"\>([\s\S]*?)<\/div\>/
  , TEMPLATE_URL = "http://www.passwordprotectmyfile.com/decrypt_template.html"
  ;

var die = function (message) {
  console.error(message);
  process.exit(1);
};

var pickAction = function (argv) {
  if (argv.encrypt && argv.decrypt) {
    return null;
  }

  if (argv.encrypt) {
    return "encrypt";
  } else if (argv.decrypt) {
    return "decrypt";
  } else {
    return null;
  }
};

var encrypt = function (templateString, plaintextBuffer, password, progressCallback, callback) {
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

var decrypt = function (htmlString, password, progressCallback, callback) {
  var regexMatch = CIPHERTEXT_REGEX.exec(htmlString);
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

var getTemplate = function (source, callback) {
  var type = url.parse(source).protocol;

  if (type === "file:" || !type) {
    fs.readFile(source, function (err, data) {
      return callback(err, data.toString());
    });
  } else if (type === "http:" || type === "https:") {
    request(source, function (err, response, body) {
      if (err && response.statusCode == 200) {
        return callback(null, body);
      } else {
        return callback(err);
      }
    });
  }
};

var action = pickAction(argv);
if (action === null) {
  die("Use either --encrypt or --decrypt");
}

var filename = argv[action];

var noop = function () {};

var printProgress = function (p) {
  console.log(p);
};

var doneCallback = function (err, res) {
  if (err) {
    die("Error! " + err.toString());
  }

  fs.writeFile(argv.outfile, res, function (err) {
    if (err) {
      die("Unable to write file: " + err.toString);
    }
    // DONE!
  });
};

// get the file contents
fs.readFile(filename, function (err, data) {
  if (err) {
    die("Unable to open file " + filename + " to " + action + ".");
  }

  var progressCallback = argv.quiet ? noop : printProgress;

  if (action === "encrypt") {
    var templateSource = argv.template || TEMPLATE_URL;

    getTemplate(templateSource, function (err, templateString) {
      if (err) {
        die("Unable to load template: " + err.toString());
      }
      encrypt(templateString, data, argv.password, progressCallback, doneCallback);
    });

  } else if (action === "decrypt") {
    decrypt(data.toString(), argv.password, progressCallback, doneCallback);
  }

});
