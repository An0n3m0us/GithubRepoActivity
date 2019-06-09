import json, time, datetime, subprocess, os, re

settings = open("settings.txt", "r").read().replace("\n", "").split("|")
username = re.findall("\"[A-z-0-9.]*\"", settings[0])[0][1:-1]
discord = re.findall("\"[A-z-0-9.://]*\"", settings[1])[0][1:-1]
slack = re.findall("\"[A-z-0-9.://]*\"", settings[2])[0][1:-1]
gitter = re.split(" / ", re.findall("[A-z-0-9]* / [A-z-0-9]*", settings[3])[0])
repo = re.findall("\"[A-z-0-9/]*\"", settings[4])[0][1:-1]
userdetails = re.findall("[A-z-0-9]*:[A-z-0-9]*", settings[5])[0]
hooks = settings[6].split(" #")[0]

slackJson = """{
"attachments": [{
"author_name": "AUTHORNAME",
"author_link": "AUTHORLINK",
"author_icon": "AUTHORICON",
"title": "TITLE",
"title_link": "TITLELINK",
"text": "TEXT",
"footer": "GitHub",
"footer_icon": "https://github.githubassets.com/images/modules/logos_page/GitHub-Mark.png",
"ts": TS,
"color": "COLOR"
},
{
"text": "LABELS",
"color": "COLOR"
}
]}
"""

discordJson = """{"embeds": [{
"author": {
"name": "NAME",
"icon_url": "ICON"
},
"title": "TITLE",
"url": "URL",
"description": "DESC"
}]}
"""

gitterJson = """{
"text":"[TITLE]:\\nTEXT"
}"""

rss = """<rss version="2.0">
<channel>
<title>REPOTITLE</title>
<link>REPOLINK</link>
<item>
<author>AUTHORNAME</author>
<title>TITLE</title>
<link>LINK</link>
<description><![CDATA[DESC]]></description>
</item>
</channel>
</rss>
"""

id = 0
# [0]AuthorName, [1]AuthorLink, [2]AuthorIcon, ([3]Action, [4]ID, [5]Title), [6]TitleLink, ([7]Text, [[8][0]labelsSlack, [8][1]labelsDiscord), [9]TimeCreated, [10]Color
message = ["", "", "", "", "", "", "", "", ["", ""], 0, ""]
log = 0
timeGithub = 0
timeFile = 0

os.system('curl -s "https://api.github.com/repos/' + repo + '/events?page=1&per_page=1" -u ' + userdetails + ' > .githubapi')

if "rss" in hooks:
	os.system('touch .githubrss.xml')

while True:
	if os.path.isfile(".githublastid") == True:
		id = open('.githublastid', 'r').read()
	timeGithub = subprocess.check_output('curl -I -s --head "https://api.github.com/repos/' + repo + '/events?page=1&per_page=1" -u ' + userdetails + ' | grep -i "Last-Modified"', shell=True)[15:-6]
	timeGithub = int(time.mktime(datetime.datetime.strptime(timeGithub, "%a, %d %b %Y %H:%M:%S").timetuple())) + 3600
	timeFile = int(os.path.getmtime('.githubapi'))

	if timeGithub > timeFile:
		if os.path.isfile(".githubapi") == True:
			os.system('curl -s "https://api.github.com/repos/' + repo + '/events?page=1&per_page=1" -u ' + userdetails + ' > .githubapi')

	apifile = open(".githubapi", 'r')
	with apifile as json_file:
		data = json.load(json_file)

		if "IssuesEvent" in data[0]['type'] and data[0]['id'] != id:
			id = data[0]['id']
			payload = data[0]['payload']
			issue = data[0]['payload']['issue']

			message[0] = str(issue['user']['login'])
			message[1] = str(issue['user']['html_url'])
			message[2] = str(issue['user']['avatar_url'])

			if payload['action'] == "opened":
				message[3] = "Opened issue"
				message[10] = "#2cbe4e"
			elif payload['action'] == "closed":
				message[3] = "Closed issue"
				message[10] = "#cb2431"
			elif payload['action'] == "reopened":
				message[3] = "Reopened issue"

			message[4] = " #" + str(issue['number']) + " "
			message[5] = str(issue['title'].replace("'", "\u0027"))
			message[6] = str(issue['html_url'])

			images = re.findall("![A-z(0-9.://)-]*", issue['body'])
			for i in range(len(images)):
				images[i] = images[i].split("(")
				images[i][0] = images[i][0][2:-1]
				images[i][1] = images[i][1][:-1]
				code = "<" + images[i][1] + "|" + images[i][0] + "-img>"
				issue['body'] = re.sub("![A-z(0-9.://)-]*", code, issue['body'], 1)

			ids = re.findall("#[0-9][0-9]*", issue['body'])
			for i in range(len(ids)):
				code = "<https://github.com/" + repo + "/issues/" + ids[i][1:] + "|" + ids[i] + ">"
				issue['body'] = re.sub("#[0-9][0-9]*", code, issue['body'], 1)

			message[7] = repr(str(issue['body']))
			if str(issue['body']) == "":
				message[7] = "_No description provided._"

			if issue['labels']:
				message[8][0] = "_Labels: "
				message[8][1] = "*Labels: "
				for i in range(len(issue['labels'])):
					message[8][0] = message[8][0] + issue['labels'][i]['name'] + ", "
					message[8][1] = message[8][1] + issue['labels'][i]['name'] + ", "
				message[8][0] = repr("\\n\\n")[1:-1] + message[8][0][:-2] + "_"
				message[8][1] = repr("\\n\\n")[1:-1] + message[8][1][:-2] + "*"

			message[9] = int(time.mktime(datetime.datetime.strptime(issue['created_at'][:-1], "%Y-%m-%dT%H:%M:%S").timetuple()))

		if "IssueCommentEvent" in data[0]['type'] and data[0]['id'] != id and data[0]['payload']['comment']:
			id = data[0]['id']
			issue = data[0]['payload']['issue']
			comment = data[0]['payload']['comment']

			message[0] = str(comment['user']['login'])
			message[1] = str(comment['user']['html_url'])
			message[2] = str(comment['user']['avatar_url'])
			message[3] = "Commented on"
			message[4] = " #" + str(issue['number']) + " "
			message[5] = str(issue['title'].replace("'", "\u0027"))
			message[6] = str(comment['html_url'])

			images = re.findall("![A-z(0-9.://)-]*", comment['body'])
			for i in range(len(images)):
				images[i] = images[i].split("(")
				images[i][0] = images[i][0][2:-1]
				images[i][1] = images[i][1][:-1]
				code = "<" + images[i][1] + "|" + images[i][0] + "-img>"
				comment['body'] = re.sub("![A-z(0-9.://)-]*", code, comment['body'], 1)

			ids = re.findall("#[0-9][0-9]*", comment['body'])
			for i in range(len(ids)):
				code = "<https://github.com/" + repo + "/pull/" + ids[i][1:] + "|" + ids[i] + ">"
				comment['body'] = re.sub("#[0-9][0-9]*", code, comment['body'], 1)

			message[7] = repr(str(comment['body']))
			if str(issue['body']) == "":
				message[7] = "_No description provided._"

			if issue['labels']:
				message[8][0] = "_Labels: "
				message[8][1] = "*Labels: "
				for i in range(len(issue['labels'])):
					message[8][0] = message[8][0] + issue['labels'][i]['name'] + ", "
					message[8][1] = message[8][1] + issue['labels'][i]['name'] + ", "
				message[8][0] = repr("\\n\\n")[1:-1] + message[8][0][:-2] + "_"
				message[8][1] = repr("\\n\\n")[1:-1] + message[8][1][:-2] + "*"

			message[9] = int(time.mktime(datetime.datetime.strptime(comment['created_at'][:-1], "%Y-%m-%dT%H:%M:%S").timetuple()))

		if "PullRequestEvent" in data[0]['type'] and data[0]['id'] != id:
			id = data[0]['id']
			payload = data[0]['payload']
			pull = data[0]['payload']['pull_request']

			message[0] = str(pull['user']['login'])
			message[1] = str(pull['user']['html_url'])
			message[2] = str(pull['user']['avatar_url'])

			if payload['action'] == "opened":
				message[3] = "Opened pull request"
				message[10] = "#2cbe4e"
			elif payload['action'] == "closed":
				if pull['merged_at'] == None:
					message[3] = "Closed pull request"
					message[10] = "#cb2431"
				else:
					message[3] = "Merged pull request"
					message[10] = "#6f42c1"
			elif payload['action'] == "reopened":
				message[3] = "Reopened pull request"

			message[4] = " #" + str(pull['number']) + " "
			message[5] = str(pull['title'].replace("'", "\u0027"))
			message[6] = str(pull['html_url'])

			images = re.findall("![A-z(0-9.://)-]*", pull['body'])
			for i in range(len(images)):
				images[i] = images[i].split("(")
				images[i][0] = images[i][0][2:-1]
				images[i][1] = images[i][1][:-1]
				code = "<" + images[i][1] + "|" + images[i][0] + "-img>"
				pull['body'] = re.sub("![A-z(0-9.://)-]*", code, pull['body'], 1)

			ids = re.findall("#[0-9][0-9]*", pull['body'])
			for i in range(len(ids)):
				code = "<https://github.com/" + repo + "/pull/" + ids[i][1:] + "|" + ids[i] + ">"
				pull['body'] = re.sub("#[0-9][0-9]*", code, pull['body'], 1)

			message[7] = repr(str(pull['body']))
			if str(pull['body']) == "":
				message[7] = "_No description provided._"

			if pull['labels']:
				message[8][0] = "_Labels: "
				message[8][1] = "*Labels: "
				for i in range(len(pull['labels'])):
					message[8][0] = message[8][0] + pull['labels'][i]['name'] + ", "
					message[8][1] = message[8][1] + pull['labels'][i]['name'] + ", "
				message[8][0] = repr("\\n\\n")[1:-1] + message[8][0][:-2] + "_"
				message[8][1] = repr("\\n\\n")[1:-1] + message[8][1][:-2] + "*"

			message[9] = int(time.mktime(datetime.datetime.strptime(pull['created_at'][:-1], "%Y-%m-%dT%H:%M:%S").timetuple()))

		if "PullRequestReviewCommentEvent" in data[0]['type'] and data[0]['id'] != id and data[0]['payload']['comment']:
			id = data[0]['id']
			payload = data[0]['payload']
			pull = data[0]['payload']['pull_request']
			review = data[0]['payload']['comment']

			message[0] = str(review['user']['login'])
			message[1] = str(review['user']['html_url'])
			message[2] = str(review['user']['avatar_url'])
			message[3] = "Reviewed pull request"
			message[4] = " #" + str(pull['number']) + " "
			message[5] = str(pull['title'].replace("'", "\u0027"))
			message[6] = str(review['html_url'])

			images = re.findall("![A-z(0-9.://)-]*", review['body'])
			for i in range(len(images)):
				images[i] = images[i].split("(")
				images[i][0] = images[i][0][2:-1]
				images[i][1] = images[i][1][:-1]
				code = "<" + images[i][1] + "|" + images[i][0] + "-img>"
				review['body'] = re.sub("![A-z(0-9.://)-]*", code, review['body'], 1)

			ids = re.findall("#[0-9][0-9]*", review['body'])
			for i in range(len(ids)):
				code = "<https://github.com/" + repo + "/pull/" + ids[i][1:] + "|" + ids[i] + ">"
				review['body'] = re.sub("#[0-9][0-9]*", code, review['body'], 1)

			message[7] = repr(str(review['body']))
			if str(review['body']) == "":
				message[7] = "_No description provided._"

			if pull['labels']:
				message[8][0] = "_Labels: "
				message[8][1] = "*Labels: "
				for i in range(len(pull['labels'])):
					message[8][0] = message[8][0] + pull['labels'][i]['name'] + ", "
					message[8][1] = message[8][1] + pull['labels'][i]['name'] + ", "
				message[8][0] = repr("\\n\\n")[1:-1] + message[8][0][:-2] + "_"
				message[8][1] = repr("\\n\\n")[1:-1] + message[8][1][:-2] + "*"

			message[9] = int(time.mktime(datetime.datetime.strptime(pull['created_at'][:-1], "%Y-%m-%dT%H:%M:%S").timetuple()))

		if "PushEvent" in data[0]['type'] and data[0]['id'] != id:
			id = data[0]['id']
			event = data[0]
			commit = data[0]['payload']['commits'][0]

			message[0] = str(event['actor']['login'])
			message[1] = str(event['actor']['html_url'])
			message[2] = str(event['actor']['avatar_url'])
			message[3] = "Pushed"
			message[4] = " to "
			message[5] = repo
			message[6] = str("https://github.com/" + repo + "/commit/" + commit['sha'])

			ids = re.findall("#[0-9][0-9]*", commit['message'])
			for i in range(len(ids)):
				code = "<https://github.com/" + repo + "/pull/" + ids[i][1:] + "|" + ids[i] + ">"
				commit['message'] = re.sub("#[0-9][0-9]*", code, commit['message'], 1)

			message[7] = repr(str(commit['message']))
			message[9] = int(time.mktime(datetime.datetime.strptime(event['created_at'][:-1], "%Y-%m-%dT%H:%M:%S").timetuple()))

	slackJson = re.sub("\"author_name\": \"AUTHORNAME\"", "\"author_name\": \"" + message[0] + "\"", slackJson)
	slackJson = re.sub("\"author_link\": \"AUTHORLINK\"", "\"author_link\": \"" + message[1] + "\"", slackJson)
	slackJson = re.sub("\"author_icon\": \"AUTHORICON\"", "\"author_icon\": \"" + message[2] + "\"", slackJson)
	slackJson = re.sub("\"title\": \"TITLE\"", "\"title\": \"" + message[3] + message[4] + message[5] + "\"", slackJson)
	slackJson = re.sub("\"title_link\": \"TITLELINK\"", "\"title_link\": \"" + message[6] + "\"", slackJson)
	if ("IssuesEvent" in data[0]['type'] or "PullRequestEvent" in data[0]['type']) and (data[0]['payload']['action'] == "reopened" or data[0]['payload']['action'] == "closed"):
		slackJson = re.sub("\"text\": \"TEXT\"", "\"text\": \"" + " " + "\"", slackJson)
		slackJson = re.sub("\"text\": \"LABELS\"", "\"text\": \"" + str(message[8][0]) + "\"", slackJson)
	else:
		slackJson = re.sub("\"text\": \"TEXT\"", "\"text\": \"" + repr(message[7])[2:-2].replace("'", "\u0027").replace("No description provided.", "_No description provided._") + "\"", slackJson)
		slackJson = re.sub("\"text\": \"LABELS\"", "\"text\": \"" + str(message[8][0]) + "\"", slackJson)
	slackJson = re.sub("\"ts\": TS", "\"ts\": " + str(message[9]), slackJson)
	slackJson = re.sub("\"color\": \"COLOR\"", "\"color\": \"" + str(message[10]) + "\"", slackJson)
	slackJson = slackJson.replace("\n", "")

	discordJson = re.sub("\"name\": \"NAME\"", "\"name\": \"" + message[0] + "\"", discordJson)
	discordJson = re.sub("\"icon_url\": \"ICON\"", "\"icon_url\": \"" + message[2] + "\"", discordJson)
	discordJson = re.sub("\"title\": \"TITLE\"", "\"title\": \"" + message[3] + message[4] + message[5] + "\"", discordJson)
	discordJson = re.sub("\"url\": \"URL\"", "\"url\": \"" + message[6] + "\"", discordJson)
	if ("IssuesEvent" in data[0]['type'] or "PullRequestEvent" in data[0]['type']) and (data[0]['payload']['action'] == "reopened" or data[0]['payload']['action'] == "closed"):
		discordJson = re.sub("\"description\": \"DESC\"", "\"description\": \"" + str(message[8][1]) + "\"", discordJson)
	else:
		discordJson = re.sub("\"description\": \"DESC\"", "\"description\": \"" + repr(message[7])[2:-2].replace("'", "\u0027").replace("No description provided.", "*No description provided.*") + str(message[8][1]) + "\"", discordJson)
	discordJson = discordJson.replace("\n", "")

	gitterJson = re.sub("\"text\":\"\[TITLE\]", "\"text\":\"[" + message[0] + "](" + message[1] + ") " + message[3].lower() + " [" + message[4][1:-1] + "](" + re.findall("https://github.com/minetest/minetest_game/[A-z]*/[0-9][0-9]*", message[6])[0] + ") [" + message[5] + "](" + message[6] + ")", gitterJson)
	gitterJson = re.sub("TEXT", repr(message[7])[2:-2].replace("'", "\u0027").replace("No description provided.", "_No description provided._") + str(message[8][1]), gitterJson)
	gitterJson = gitterJson.replace("\n", "")

	rss = re.sub("<title>REPOTITLE</title>", "<title>" + repo + "</title>", rss)
	rss = re.sub("<author>AUTHORNAME</author>", "<author>" + message[0] + "</author>", rss)
	rss = re.sub("<link>REPOLINK</link>", "<link>https://github.com/" + repo + "</link>", rss)
	rss = re.sub("<title>TITLE</title>", "<title>" + message[3] + message[4] + message[5] + "</title>", rss)
	rss = re.sub("<link>LINK</link>", "<link>" + message[6] + "</link>", rss)
	rss = re.sub("\<description\>\<\!\[CDATA\[DESC", "<description><![CDATA[" + message[7].replace("\\n", "<br>").replace("\\r", "")[2:-2].replace("No description provided.", "*No description provided.*") + str(message[8][1].replace("\\\\n", "<br>").replace("*", "")) + "</description>", rss)

	if message[9] != 0:
		if "slack" in hooks:
			subprocess.check_output("curl -X POST -H \"Content-type: application/json\" --data '" + slackJson + "' " + slack, shell=True)[:-1]
		if "discord" in hooks:
			subprocess.check_output("curl -H \"Content-Type: application/json\" -X POST -d '" + discordJson + "' " + discord, shell=True)[:-1]
		if "gitter" in hooks:
			subprocess.check_output("curl -H \"Content-Type: application/json\" -H \"Accept: application/json\" -H \"Authorization: Bearer " + gitter[0] + "\" \"https://api.gitter.im/v1/rooms/" + gitter[1] + "/chatMessages\" -X POST -d '" + gitterJson + "'", shell=True)[:-1]
		if "rss" in hooks:
			rssfile = open(".githubrss.xml", "w")
			with rssfile as rss_file:
				rss_file.write(rss)
		print("\n\n" + message[0] + "\n" + message[3] + message[4] + message[5] + "\n\n")

	if id != None:
		lastid = open(".githublastid", "w")
		with lastid as lastid_file:
			lastid_file.write(id)

	message = ["", "", "", "", "", "", "", "", ["", ""], 0, ""]
	time.sleep(2.5)
