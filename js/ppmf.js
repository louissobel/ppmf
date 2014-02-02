#!/usr/bin/env node
"use strict";

/* global process */

// standalone CLI for node environment
// (not really standalone)
// with API for webby? maybe later

var argv = require("optimist")
           .demand("password")
           .describe("outfile", "Write to a file.")
           .boolean("stdout")
           .describe("stdout", "Send output to STDOUT. Implies --quiet. Can be used with --outfile")
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
           }).check(function (argv) {
             if (!(argv.outfile || argv.stdout)) {
               throw new Error("Must use either --outfile or --stdout");
             }
           })
           .argv
  , request = require("request")
  , fs = require("fs")
  , url = require("url")
  , ProgressBar = require("progress")
  , ppmf = require("./index")
  ;


var TEMPLATE_URL = "http://www.passwordprotectmyfile.com/decrypt_template.html";

var die = function (message) {
  console.error(message);
  process.exit(1);
};

var pickAction = function (argv) {
  // Validated by optimist.
  if (argv.encrypt) {
    return "encrypt";
  } else if (argv.decrypt) {
    return "decrypt";
  } else {
    throw new Error("Something is very wrong. Neither encrypt or decrypt specified");
  }
};

var getTemplate = function (source, callback) {
  var type = url.parse(source).protocol;

  if (type === "file:" || !type) {
    fs.readFile(source, function (err, data) {
      return callback(err, data.toString());
    });
  } else if (type === "http:" || type === "https:") {
    request(source, function (err, response, body) {
      if (!err && response.statusCode === 200) {
        return callback(null, body);
      } else {
        return callback(err);
      }
    });
  }
};

var action = pickAction(argv);

var filename = argv[action]
  , quiet = argv.stdout ? true : argv.quiet
  ;

var noop = function () {};

var progressBar;

if (!quiet) {
  var message = action === "encrypt" ? "Encrypting..." : "Decrypting..."
    , progressBar = new ProgressBar(message + " [:bar] :percent", {
    total: 100
  , incomplete: "-"
  , complete: "#"
  , width: 50
  });
}

var updateBar = function (p) {
  if (Math.ceil(100 * p) > progressBar.curr) {
    progressBar.tick();
  }
};

var doneCallback = function (err, res) {
  if (err) {
    die("Error! " + err.toString());
  }

  if (argv.stdout) {
    process.stdout.write(res);
  }

  if (argv.outfile) {
    fs.writeFile(argv.outfile, res, function (err) {
      if (err) {
        die("Unable to write file: " + err.toString);
      }
    });
  }
  // DONE!

};

// get the file contents
fs.readFile(filename, function (err, data) {
  if (err) {
    die("Unable to open file " + filename + " to " + action + ".");
  }

  var progressCallback = quiet ? noop : updateBar;

  if (action === "encrypt") {
    var templateSource = argv.template || TEMPLATE_URL;

    getTemplate(templateSource, function (err, templateString) {
      if (err) {
        die("Unable to load template: " + err.toString());
      }

      ppmf.encrypt({
        template: templateString
      , data: data
      , password: argv.password
      , filename: filename
      , onprogress: progressCallback
      , oncomplete: doneCallback
      });

    });

  } else if (action === "decrypt") {
    ppmf.decrypt({
      htmlString: data.toString()
    , password: argv.password
    , onprogress: progressCallback
    , oncomplete: doneCallback
    });
  }

});
