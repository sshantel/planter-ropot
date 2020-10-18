Utilizes Python Requests and Beautiful Soup libraries to scrape Craigslist postings by keyword search. Listings are written to database, and posted to a Slack channel with Slack’s API. Deployed on Heroku’s Cloud service.
 
<h4>Technologies</h4>
 
<b>Tech Stack</b>: Python

<b> APIs </b> : Slack  

<b> Installation </b>

<i>You must have the following installed to run Craigslist-Ropot: </i>
 
<br>
Slack 
<br>
Python3 
<br>
Requests Library 
<br>
 
 <h4> External Setup </h4>

You'll need a Slack workspace, a channel for the Slackbot to post,and a Slackbot API key.
 
* Create Slack <a href="https://slack.com/create#email"> workspace </a> 
* Create an <a href= "https://api.slack.com/apps"> App </a> on your workspace  
* Add `chat:write` and `links:write` Bot OAuth Token scopes under Add Features and Functionality --> Permissions
* Install App to workspace
* Create channel for bot to post into
* Add bot to channel
![](static/images/add_app_slack.png "add_app_slack.png")
* Store Slack API in secrets.sh file:
`export SLACK_API_TOKEN='INSERT-TOKEN-HERE'`

<b> Running Ropot-Planter on your computer </b>

1. Clone or fork repository:

```
$ git clone https://github.com/sshantel/craigslist-ropot
```


 