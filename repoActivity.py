import json, time, datetime, subprocess, os, re

settings = open("settings.txt", "r").read().replace("\n", "").split("|")
username = re.findall("\"[A-z-0-9.]*\"", settings[0])[0][1:-1]
discord = re.findall("\"[A-z-0-9.://]*\"", settings[1])[0][1:-1]
slack = re.findall("\"[A-z-0-9.://]*\"", settings[2])[0][1:-1]
gitter = re.split(" / ", re.findall("[A-z-0-9]* / [A-z-0-9]*", settings[3])[0])
repo = re.findall("\"[A-z-0-9/]*\"", settings[4])[0][1:-1]
userdetails = re.findall("[A-z-0-9]*:[A-z-0-9]*", settings[5])[0]
hooks = settings[6].split(" #")[0]

id = 0
message = []
rss = ""
rssmsg = ""
log = 0
timeGithub = 0
timeFile = 0

os.system('curl -s "https://api.github.com/repos/' + repo + '/events?page=1&per_page=1" -u ' + userdetails + ' > .githubapi')
os.system('touch .githubrss.xml')

rssfile = open(".githubrss.xml", "w")
with rssfile as rss_file:
	rss_file.write("<rss version=\"2.0\"><title>" + repo + "</title></rss>")

while True:
	if os.path.isfile(".githublastid") == True:
		id = open('.githublastid', 'r').read()
	message = []
	timeGithub = subprocess.check_output('curl -I -s --head "https://api.github.com/repos/' + repo + '/events?page=1&per_page=1" -u ' + userdetails + ' | grep -i "Last-Modified"', shell=True)[15:-6]
	timeGithub = int(time.mktime(datetime.datetime.strptime(timeGithub, "%a, %d %b %Y %H:%M:%S").timetuple())) + 3600
	timeFile = int(os.path.getmtime('.githubapi'))

	if timeGithub > timeFile:
		if os.path.isfile(".githubapi") == True:
			os.system('curl -s "https://api.github.com/repos/' + repo + '/events?page=1&per_page=1" -u ' + userdetails + ' > .githubapi')

	apifile = open(".githubapi", 'r')
	with apifile as json_file:
		data = json.load(json_file)
		if "IssuesEvent" in data[-1]['type'] and data[-1]['id'] != id and data[-1]['payload']['issue']['user']['login'] != username:
			id = data[-1]['id']
			event = data[-1]['payload']['issue']
			title = event['title'].replace('\"', "_-doublequote-_").replace("\'", '_-apostrophe-_')
			if data[-1]['payload']['action'] == "reopened":
				message.append("Reopened issue #" + str(event['number']) + " " + title)
			elif data[-1]['payload']['action'] == "closed":
				message.append("Closed issue #" + str(event['number']) + " " + title)
			elif data[-1]['payload']['action'] == "opened":
				message.append("Opened issue #" + str(event['number']) + " " + title)
			message[0] = message[0].replace("_-doublequote-_", '\\"').replace("_-apostrophe-_", "'\\''")

			message.append(str(event['user']['login']))
			message.append(str(event['user']['avatar_url']))
			body = event['body'].replace('\"', "_-doublequote-_").replace("\'", '_-apostrophe-_')
			message.append(repr(body)[2:-1])
			message.append(event['html_url'])
			if data[-1]['payload']['action'] == "reopened":
				message.append("reopened issue ")
			elif data[-1]['payload']['action'] == "closed":
				message.append("closed issue ")
			elif data[-1]['payload']['action'] == "opened":
				message.append(" opened issue ")
			message.append("[" + title + "](https://github.com/minetest/minetest_game/issues/" + str(event['number']) + ")")
			message.append(int(time.mktime(datetime.datetime.strptime(event['created_at'][:-1], "%Y-%m-%dT%H:%M:%S").timetuple())))

			message[3] = message[3].replace("_-doublequote-_", '\\"').replace("_-apostrophe-_", "'\\''")

			message[3] = re.sub("\![A-z0-9]*", " ", message[3])

			if message[3] == "":
				message[3] = "_No description provided._"

			code = re.findall("#[0-9][0-9]*", message[3])
			for i in range(len(code)):
				code[i] = "[" + code[i] + "]" + "(https://github.com/minetest/minetest_game/pull/" + code[i][1:] + ")"
				message[3] = re.sub(re.findall("#[0-9]*", message[3])[i], code[i], message[3])

			if event['labels']:
				message[3] = message[3] + "\\n\\n*Labels: "
				for j in range(len(event['labels'])):
					message[3] = message[3] + event['labels'][j]['name'] + ", "
				message[3] = message[3][:-2] + "*"

			rssmsg = repr(event['body']).replace("\\n", "<br>").replace("\\r", "").replace("\\'", "'")[2:-1]
			log = event['body']

		if "IssueCommentEvent" in data[-1]['type'] and data[-1]['id'] != id and data[-1]['payload']['comment'] and data[-1]['payload']['comment']['user']['login'] != username:
			id = data[-1]['id']
			event = data[-1]['payload']['issue']
			comment = data[-1]['payload']['comment']
			title = event['title'].replace('\"', "_-doublequote-_").replace("\'", '_-apostrophe-_')
			message.append("Commented on #" + str(event['number']) + " " + str(title))
			message[0] = message[0].replace("_-doublequote-_", '\\"').replace("_-apostrophe-_", "'\\''")

			message.append(str(comment['user']['login']))
			message.append(str(comment['user']['avatar_url']))
			body = comment['body'].replace('\"', "_-doublequote-_").replace("\'", '_-apostrophe-_')
			message.append(repr(body)[2:-1])
			message[3] = message[3].replace("_-doublequote-_", '\\"').replace("_-apostrophe-_", "'\\''")
			message.append(comment['html_url'])
			message.append(" commented on ")
			message.append("[" + title + "](" + str(comment['html_url']) + ")" + " [#" + str(event['number']) + "](https://github.com/minetest/minetest_game/pull/" + str(event['number']) + ")")
			message.append(int(time.mktime(datetime.datetime.strptime(comment['created_at'][:-1], "%Y-%m-%dT%H:%M:%S").timetuple())))

			message[3] = re.sub("\![A-z0-9]*", " ", message[3])

			if message[3] == "":
				message[3] = "_No description provided._"

			code = re.findall("#[0-9][0-9]*", message[3])
			for i in range(len(code)):
				code[i] = "[" + code[i] + "]" + "(https://github.com/minetest/minetest_game/pull/" + code[i][1:] + ")"
				message[3] = re.sub(re.findall("#[0-9]*", message[3])[i], code[i], message[3])

			if event['labels']:
				message[3] = message[3] + "\\n\\n*Labels: "
				for j in range(len(event['labels'])):
					message[3] = message[3] + event['labels'][j]['name'] + ", "
				message[3] = message[3][:-2] + "*"

			rssmsg = repr(comment['body']).replace("\\n", "<br>").replace("\\r", "").replace("\\'", "'")[2:-1]
			log = comment['body']

		if "PullRequestEvent" in data[-1]['type'] and data[-1]['id'] != id and data[-1]['payload']['pull_request']['user']['login'] != username:
			id = data[-1]['id']
			event = data[-1]['payload']['pull_request']
			title = event['title'].replace('\"', "_-doublequote-_").replace("\'", '_-apostrophe-_')
			if data[-1]['payload']['action'] == "reopened":
				message.append("Reopened pull request #" + str(event['number']) + " " + title)
			elif data[-1]['payload']['action'] == "closed":
				message.append("Closed pull request #" + str(event['number']) + " " + title)
			elif data[-1]['payload']['action'] == "opened":
				message.append("Opened pull request #" + str(event['number']) + " " + title)
			message[0] = message[0].replace("_-doublequote-_", '\\"').replace("_-apostrophe-_", "'\\''")

			message.append(str(event['user']['login']))
			message.append(str(event['user']['avatar_url']))
			body = event['body'].replace('\"', "_-doublequote-_").replace("\'", '_-apostrophe-_')
			message.append(repr(body)[2:-1])
			message.append(event['html_url'])
			if data[-1]['payload']['action'] == "reopened":
				message.append(" reopened pull request ")
			elif data[-1]['payload']['action'] == "closed":
				message.append(" closed pull request ")
			elif data[-1]['payload']['action'] == "opened":
				message.append(" opened pull request ")
			message.append("[" + title + "](https://github.com/minetest/minetest_game/pull/" + str(event['number']) + ")")
			message.append(int(time.mktime(datetime.datetime.strptime(event['created_at'][:-1], "%Y-%m-%dT%H:%M:%S").timetuple())))

			message[3] = message[3].replace("_-doublequote-_", '\\"').replace("_-apostrophe-_", "'\\''")

			message[3] = re.sub("\![A-z0-9]*", " ", message[3])

			if message[3] == "":
				message[3] = "_No description provided._"

			code = re.findall("#[0-9][0-9]*", message[3])
			for i in range(len(code)):
				code[i] = "[" + code[i] + "]" + "(https://github.com/minetest/minetest_game/issues/" + code[i][1:] + ")"
				message[3] = re.sub(re.findall("#[0-9]*", message[3])[i], code[i], message[3])

			if event['labels']:
				message[3] = message[3] + "\\n\\n*Labels: "
				for j in range(len(event['labels'])):
					message[3] = message[3] + event['labels'][j]['name'] + ", "
				message[3] = message[3][:-2] + "*"

			rssmsg = repr(event['body']).replace("\\n", "<br>").replace("\\r", "").replace("\\'", "'")[2:-1]
			log = event['body']

		if "PullRequestReviewCommentEvent" in data[-1]['type'] and data[-1]['id'] != id and data[-1]['actor']['login'] != username:
			id = data[-1]['id']
			event = data[-1]['payload']['pull_request']
			reviewer = data[-1]['payload']['comment']

			title = event['title'].replace('\"', "_-doublequote-_").replace("\'", '_-apostrophe-_')
			message.append("Reviewed pull request #" + str(event['number']) + " " + str(event['title']))
			message[0] = message[0].replace("_-doublequote-_", '\\"').replace("_-apostrophe-_", "'\\''")

			message.append(str(reviewer['user']['login']))
			message.append(str(reviewer['user']['avatar_url']))
			body = reviewer['body'].replace('\"', "_-doublequote-_").replace("\'", '_-apostrophe-_')
			diff = reviewer['diff_hunk'].replace('\"', "_-doublequote-_").replace("\'", '_-apostrophe-_')
			message.append(repr(body)[2:-1])
			message[3] = message[3] + "```diff" + repr("\\n") + repr(diff)[2:-1] + "```"
			message[3] = message[3].replace("_-doublequote-_", '\\"').replace("_-apostrophe-_", "'\\''")

			print("\n\n DATA:" + message[3])

			message.append(reviewer['html_url'])
			message.append(" reviewed pull request ")
			message.append("[" + title + "](" + str(comment['html_url']) + ")")
			message.append(int(time.mktime(datetime.datetime.strptime(reviewer['created_at'][:-1], "%Y-%m-%dT%H:%M:%S").timetuple())))

			if message[3] == "":
				message[3] = "_No description provided._"

			message[3] = re.sub("\![A-z0-9]*", " ", message[3])

			code = re.findall("#[0-9][0-9]*", message[3])
			for i in range(len(code)):
				code[i] = "[" + code[i] + "]" + "(https://github.com/minetest/minetest_game/issues/" + code[i][1:] + ")"
				message[3] = re.sub(re.findall("#[0-9]*", message[3])[i], code[i], message[3])

			if event['labels']:
				message[3] = message[3] + "\\n\\n*Labels: "
				for j in range(len(event['labels'])):
					message[3] = message[3] + event['labels'][j]['name'] + ", "
				message[3] = message[3][:-2] + "*"

			rssmsg = repr(reviewer['body']).replace("\\n", "<br>").replace("\\r", "").replace("\\'", "'")[2:-1]
			log = reviewer['body'] + "\n" + reviewer['diff_hunk']

		if "PushEvent" in data[-1]['type'] and data[-1]['id'] != id and data[-1]['actor']['login'] != username:
			id = data[-1]['id']
			event = data[-1]
			commit = data[-1]['payload']['commits'][0]
			message.append("Pushed to " + event['repo']['name'])
			message.append(str(event['actor']['login']))
			message.append(str(event['actor']['avatar_url']))
			commitmessage = commit['message'].replace('\"', "_-doublequote-_").replace("\'", '_-apostrophe-_')
			message.append(repr(commitmessage)[2:-1])
			message[3] = "**" + commit['author']['name'] + "**: " + message[3].replace("_-doublequote-_", '\\"').replace("_-apostrophe-_", "'\\''")
			message.append("https://github.com/" + repo + "/commit/" + commit['sha'])
			message.append(" pushed to ")
			message.append(event['repo']['name'])
			message.append(int(time.mktime(datetime.datetime.strptime(data[-1]['payload']['created_at'][:-1], "%Y-%m-%dT%H:%M:%S").timetuple())))

			if message[3] == "":
				message[3] = "_No description provided._"

			code = re.findall("#[0-9][0-9]*", message[3])
			for i in range(len(code)):
				code[i] = "[" + code[i] + "]" + "(https://github.com/minetest/minetest_game/pull/" + code[i][1:] + ")"
				message[3] = re.sub(re.findall("#[0-9]*", message[3])[i], code[i], message[3])

			rssmsg = repr(commit['message']).replace("\\n", "<br>").replace("\\r", "").replace("\\'", "'")[2:-1]
			log = commit['message']

	if len(message) > 0:
		if "IssuesEvent" in data[-1]['type'] and (data[-1]['payload']['action'] == "reopened" or data[-1]['payload']['action'] == "closed"):
			if discord != "":
				if "discord" in hooks:
					os.system("curl -H \"Content-Type: application/json\" -X POST -d \'{ \"embeds\": [ { \"title\": \"" + message[0] + "\", \"url\": \"" + message[4] + "\", \"author\": { \"name\": \"" + message[1] + "\", \"icon_url\": \"" + message[2] + "\" } } ] }\' " + discord)
			if "gitter" in hooks:
				os.system("curl -H \"Content-Type: application/json\" -H \"Authorization: Bearer " + gitter[0] + "\" \"https://api.gitter.im/v1/rooms/" + gitter[1] + "/chatMessages\" -X POST -d '{\"text\":\"[" + message[1] + "](https://github.com/" + message[1] + ")" + message[5] + message[6] + "\"}'")
			if "slack" in hooks:
				jsonSlack = "{ \"attachments\": [ { \"author_name\": \"" + message[1] + "\", \"author_link\": \"https://github.com/" + message[1] + "\", \"author_icon\": \"" + message[2] + "\", \"title\": \"" + message[0] + "\", \"title_link\": \"" + message[4] + "\", \"footer\": \"GitHub\", \"footer_icon\": \"https://github.githubassets.com/images/modules/logos_page/GitHub-Mark.png\", \"ts\": \"" + str(message[7]) + "\" } ] } "
				os.system("curl -X POST -H \"Content-type: application/json\" --data '" + jsonSlack + "' " + slack)
			if "rss" in hooks:
				rss = "<rss version=\"2.0\">\n<channel>\n<title>" + repo + "</title>\n<link>https://github.com/" + repo[0] + "</link><description>" + repo + "</description>\n<item>\n  <title>" + message[0] + "</title>\n   <author>" + message[1] + "</author>\n</item>\n</channel>\n</rss>"
			print("\n\n" + message[0] + "\n" + message[1] + "\n\n")
		else:
			if discord != "":
				if "discord" in hooks:
					os.system("curl -H \"Content-Type: application/json\" -X POST -d \'{ \"embeds\": [ { \"title\": \"" + message[0] + "\", \"url\": \"" + message[4] + "\", \"author\": { \"name\": \"" + message[1] + "\", \"icon_url\": \"" + message[2] + "\" }, \"description\": \"" + message[3] + "\" } ] }\' " + discord)
			if "gitter" in hooks:
				os.system("curl -H \"Content-Type: application/json\" -H \"Authorization: Bearer " + gitter[0] + "\" \"https://api.gitter.im/v1/rooms/" + gitter[1] + "/chatMessages\" -X POST -d '{\"text\":\"[" + message[1] + "](https://github.com/" + message[1] + ")" + message[5] + message[6] + ":\\n" + message[3] + "\"}'")
			if "slack" in hooks:
				jsonSlack = "{ \"attachments\": [ { \"author_name\": \"" + message[1] + "\", \"author_link\": \"https://github.com/" + message[1] + "\", \"author_icon\": \"" + message[2] + "\", \"title\": \"" + message[0] + "\", \"title_link\": \"" + message[4] + "\", \"text\": \"" + message[3][:-1].replace("*Labels", "_Labels") + "_\", \"footer\": \"GitHub\", \"footer_icon\": \"https://github.githubassets.com/images/modules/logos_page/GitHub-Mark.png\", \"ts\": \"" + str(message[7]) + "\" } ] } "
				os.system("curl -X POST -H \"Content-type: application/json\" --data '" + jsonSlack + "' " + slack)
			if "rss" in hooks:
				rss = "<rss version=\"2.0\">\n<channel>\n<title>" + repo + "</title>\n<link>https://github.com/" + repo[0] + "</link><description>" + repo + "</description>\n<item>\n  <title>" + message[0] + "</title>\n  <link>" + message[4] + "</link>\n  <author>" + message[1] + "</author>\n  <description><![CDATA[" + rssmsg + "]]></description>\n</item>\n</channel>\n</rss>"
			print("\n\n" + message[0] + "\n" + message[1] + "\n" + log + "\n\n")

	rssfile = open(".githubrss.xml", "w")
	with rssfile as rss_file:
		rss_file.write(rss)

	if id != None:
		lastid = open(".githublastid", "w")
		with lastid as lastid_file:
			lastid_file.write(id)

	apifile.close()
	time.sleep(2.5)
