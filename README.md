# GitDump
[![Open Source Love](https://badges.frapsoft.com/os/v1/open-source.svg?v=102)](https://github.com/ellerbrock/open-source-badge/)
[![Open Source Love](https://badges.frapsoft.com/os/mit/mit.svg?v=102)](https://github.com/ellerbrock/open-source-badge/)

**GitDump dumps the source code from .git when the directory traversal is disabled**

### Requirements
- Python3

### Tested on
- Windows
- Kali Linux

### What it does
- Dump source code from website/.git directory when directory traversal is disabled. 

### How it works
- Fetch all common files (.git/index, .git/HEAD, .git/ORIG_HEAD, etc.).
- Find as many objects (sha1) as possible by analyzing .git/packed-refs, .git/index, etc.
- Download idx and pack files.
- Now you can run git checkout -- . to retrieve source code.

### How to Use
- python3 git-dump.py https://website.com/.git/
- Create the output directory and dump all the .git files in it.
- After running above script type: `cd output && git checkout -- .`
- It will recover all source code.

### Screenshot
<img src="https://github.com/Ebryx/GitDump/blob/master/poc.png" />

### TODO
- Search through git repository for secrets by digging deep into commit history and branches.

**Credits** Sean B. Palmer for his index file parser. (https://github.com/sbp/gin)
