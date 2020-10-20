## Table of contents
* <a href="https://github.com/sshantel/planter-ropot#-about-"> About
* <a href="https://github.com/sshantel/planter-ropot#-external-setup-"> External Setup
* <a href="https://github.com/sshantel/planter-ropot#-deployment-"> Deployment

<h4> About </h4>

Utilizes Python Requests and Beautiful Soup libraries to scrape Craigslist postings by keyword search. Listings are written to CSV, and posted to a Slack channel with Slack’s API. Deployed on Heroku’s Cloud service.

![](static/images//planter_ropot.gif)
 
 <h4> External Setup </h4>

* <a href="https://slack.com/create#email"> Slack workspace </a> 
* An <a href= "https://api.slack.com/apps"> App </a> on workspace  
* Add `chat:write`  `links:write` OAuth Token scopes under Add Features and Functionality --> Permissions:
    * ![](static/images/slackbot_oath_scopes.png "slackbot_oath_scopes")
* Install App to workspace
* Channel for bot to post into
* Add bot to channel:
    * ![](static/images/add_app_slack.png "add_app_slack.png")
* Store Slack API in secrets.sh file: 
    * ```export SLACK_API_TOKEN='INSERT-TOKEN-HERE'```

<b> Running Planter-Ropot locally on your computer </b>

1. Clone repository

```
$ git clone https://github.com/sshantel/planter-ropot
```

2. Install dependencies:
$ pip install -r requirements.txt

3. If you don't want to search for planters for sale in the SF Bay Area, you'll need to update the ```region``` and ```term```  in line 149 of ```scraper.py``` to fit your desired needs. The URL in line 37 can be adjusted according to what you want to scrape on Craigslist as well.

4. Source the Slackbot API by running the following command:
```
$ source secrets.sh 
```
5. Final command to run Planter-Ropot locally:
```
$ python3 scraper.py
```
Listings should now be posting on the desired Slack channel, if such listings in your Craigslist region with keywords exist.

<h4> Deployment </h4>

1. Download and Install <a href="https://devcenter.heroku.com/articles/heroku-cli#download-and-install"> Heroku </a>

2. Store the Slack API using the following command:
```
heroku config:set SLACK_API_TOKEN='INSERT-TOKEN-BETWEEN-THESE-SINGLE-QUOTES'
```
3. Adjust Heroku <a href="https://help.heroku.com/JZKJJ4NC/how-do-i-set-the-timezone-on-my-dyno"> timezone </a> according to your location(otherwise it defaults to UTC)
```
$ heroku config:add TZ="America/Los_Angeles"
```
4. Add and commit files
```
$ git add .
```

5. Scale worker dyno
```
$ heroku ps:scale worker=1
```

