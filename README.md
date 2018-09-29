# GitDump
Use this script when directory traversal is disabled and webpage returns 403 Forbidden error.

### Usage:
1. python3 git-dump.py website.com
2. After running above script type: `git checkout -- .`
   It will recover all source code.

**How does it work?**
GitDump will:
- Fetch all common files (.git/index, .git/HEAD, .git/ORIG_HEAD, etc.).
- Find  as many objects (sha1) as possible by analyzing .git/packed-refs, .git/index, etc.
- Download idx and pack files.
- Now you can run `git checkout -- .` to retrieve source code.

**CREDITS:**
Sean B. Palmer for his index file parser. (https://github.com/sbp/gin)
