# GithubRepoActivity

Python script that uses the Github API to follow the activity of a repository then converts it into a WebHook format (for Discord, RocketChat and so on) and an RSS feed file.

Tested on Linux (it should work on Mac and Windows)

Example using the `minetest/minetest_game` repo:

(Only some events are shown)

![img](https://raw.githubusercontent.com/An0n3m0us/GithubRepoActivity/master/.img.png)

# Apps supported

Discord

Slack

RSS

## Events

### Supported

IssuesEvent (opened, closed, reopened)

IssueCommentEvent (comments in issues and pull requests) (edits not supported)

PullRequestEvent (opened, closed, reopened)

PullRequestReviewCommentEvent (diffs)

PushEvent (commits pushed to repo)

### Not supported

Multiple commits in a push (TODO)

Receiving multiple messages (TODO)

Edited issues & comments, pull request & comments (no global API event)

WatchEvent (not adding)

StarEvent (not adding)

## Setup

1. Clone this repository

2. Create a webhook from an application (optional) then modify the settings in `settings.txt`.

3. Run `repoActivity.py`

For an RSS feed, add the feed URL `file:///PATH/.githubrss.xml` where `PATH` is the path to the cloned repository directory e.g (file:///tmp/githubrepoactivity/.githubrss.xml) (tested with QuiteRSS)
