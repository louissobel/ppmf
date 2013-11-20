cryptbox
=========

858 Project for encryption in dropbox

Getting set up
-------------

requires FUSE:

 - [MacFUSE](https://code.google.com/p/macfuse/)
 - [Linux](http://fuse.sourceforge.net/)

Then:

```
virtualenv env
source env/bin/activate
pip install -r requirements.txt
```

Then? Code!

Workflow
---------
Do your shit on a git branch.
When at good point, open pull request on github, assign to someone
if you want someone to look at it, or yourself.

If yourself, take a 15 or more minute break, then give yourself code review and
merge into master. If someone else, tell them to review it.

Hurray!

Tests
------
run tests using `nosetests`

Right now, super basic sanity checks. Please! Add more test cases.
Including unit tests as you write.
It will really help us evolve and iterate on the project.