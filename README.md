## Table of contents

- <a href="https://github.com/sshantel/planter-ropot#-about-"> About
- <a href="https://github.com/sshantel/planter-ropot#-external-setup-"> External Setup
- <a href="https://github.com/sshantel/planter-ropot#-deployment-"> Deployment

<h4> About </h4>

<a href="https://chantelyip.com/2020/11/24/scraping-craigslist-to-find-my-perfect-planter-with-slackbot-and-twilio/"> Blog Post </a>
<br>

<a href="https://youtu.be/SA28uVbT2xw"> Video </a>

Utilizes Python Requests and Beautiful Soup libraries to scrape Craigslist postings by keyword search. Listings are written to CSV, and posted to a Slack channel with Slack’s API. A text message is sent using Twilio's REST API if the listing is located in the user's city. Deployed on Heroku’s Cloud service.
![](static/images/planter-ropot-demo.gif)
<i> Note: Per my conversation with Slack's support team, there is a bug where Slackbot posts with unfurled images show as "edited". Their team is currently working on getting this fixed.</i>
![](static/images/slackbot_text.gif)

<h4> External Setup </h4>

- <a href= "https://slack.com/create#email"> Slack workspace </a>
- An <a href= "https://api.slack.com/apps"> App </a> on workspace
- Add `chat:write` `links:write` OAuth Token scopes under Add Features and Functionality --> Permissions:
  - ![](static/images/slackbot_oath_scopes.png "slackbot_oath_scopes")
- Install App to workspace
- <a href="https://slack.com/help/articles/201402297-Create-a-channel"> Create Channel </a> for bot to post into
- Add bot to channel:
  - ![](static/images/add_app_slack.png "add_app_slack.png")
- Store Slack API in secrets.sh file:
  - `export SLACK_API_TOKEN='INSERT-TOKEN-HERE'`
- Twilio <a href="https://www.twilio.com/docs/usage/api"> REST API </a>

<b> Running Planter-Ropot locally on your computer </b>

1. Clone repository:

```
$ git clone https://github.com/sshantel/Planter-Ropot
```

2. Install dependencies:

```
$ pip install -r requirements.txt
```

3. For a scraping of items outside of planters in the SF Bay Area, `region` and `term` in line 204 of `scraper.py` will need to be updated to fit your desired needs. The URL in line 62 can be adjusted according to the Craigslist link you wish to scrape.

4. Source the Slackbot and Twilio API by running the following command:

```
$ source secrets.sh
```

5. Final command to run Planter-Ropot locally:

```
$ python3 scraper.py
```

Listings will post on the desired Slack channel if such listings in your Craigslist region with keywords exist.

<h4> Deployment </h4>

1. Download and Install <a href="https://devcenter.heroku.com/articles/heroku-cli#download-and-install"> Heroku </a>

2. Create Heroku <a href="https://devcenter.heroku.com/articles/creating-apps"> app </a>

3. Store the Slack and Twilio API using the following commands

```
heroku config:set SLACK_API_TOKEN='INSERT-TOKEN-BETWEEN-THESE-SINGLE-QUOTES'
```

```
heroku config:set twilio_api='INSERT-TOKEN-BETWEEN-THESE-SINGLE-QUOTES'
```

```
heroku config:set twilio_auth='INSERT-TOKEN-BETWEEN-THESE-SINGLE-QUOTES'
```

4. Store personal phone number

```
heroku config:set my_phone_number='INSERT-PHONE-NUMBER-BETWEEN-THESE-SINGLE-QUOTES'
```

5. Adjust Heroku <a href="https://help.heroku.com/JZKJJ4NC/how-do-i-set-the-timezone-on-my-dyno"> timezone </a> according to your location(otherwise it defaults to UTC)

```
$ heroku config:add TZ="America/Los_Angeles"
```

6. Add and commit files

```
$ git add .
```

7. Scale worker dyno

```
$ heroku ps:scale worker=1
```
