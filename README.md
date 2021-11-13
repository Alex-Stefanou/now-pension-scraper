# 'NOW: Pensions' Scraper


## Motivation
[NOW: Pensions](https://www.nowpensions.com/) is a UK workplace pension provider. Unfortunately their online dashboard is feature poor.
 - No clear indication of when the most recent contribution arrived.
 - No historical tracking of pension value so you can monitor your pension's growth.

It really is just a page with a number; the current value of your pension.

Therefore I created this project to scrape the dashboard daily for my pension value and save it to be displayed graphically.

## Solution
This project is a Python Lambda function configured with the [Serverless Framework](https://www.serverless.com/) and triggered by a cron job. Scraped data is then writen to a Google Sheet.

![Architecture Diagram](./assets/architecture_diagram.png?raw=true "Architecture Diagram")

### Why Python?
I wanted to practice. But also I wanted it to be simple and light weight.

### Why Serverless?
This project lends itself perfectly to serverless functions.
 - Running a single function once a day is magnitudes cheaper than an always on instance.
 - No need for maintenance and will always run (as opposed to local hosting which would stop when my computer is off).

### Why use Google Sheets as a database?
Although not its intended purpose Google Sheets suits this project well.
- Free
- Always on, cloud storage will always be able to keep up with the serverless function.
- Built in data processing and graphing.
- Google Sheets has an API on GCP that makes read/write easy.


# Usage
To run the project for yourself follow these steps


## Installations
All that is needed to deploy this Lambda function is the Serverless framework. You can find [Serverless installation instructions here](https://www.serverless.com/framework/docs/getting-started). One installation option is with npm:
```
npm install -g serverless
```

Once you have Serverless installed one plugin is required, [Serverless Python Requirements](https://www.npmjs.com/package/serverless-python-requirements), which is installed with:
```
serverless plugin install -n serverless-python-requirements
```

While this is a Python Lambda function, no python libraries are needed unless you want to run the file locally. Serverless will automatically bundle the required python packages from the `Pipfile` on deployment using the Serverless Python Requirements plugin.


## Configuration
If you have any difficulties with the following configuration instructions, consider taking a look at [this Fireship video](https://youtu.be/K6Vcfm7TA5U) which sets up a very similar project.

### Google Cloud Platform
Using your desired Google account sign into [Google Cloud Platform (GCP)](https://console.cloud.google.com/). If you do not already have a personal project, set one up.

In the search bar of GCP, search "Google Sheets API", navigate to the page, and if not enabled click the blue "Enable" button. When enabled there will be a green tick and the text "API Enabled".

Next, in the search bar, search "Service accounts", this should take you to the service accounts page of IAM & Admin. This is the account that will be writing to the google sheet on your behalf. If you do not have one, set up an account using the "+ Create Service Account" button at the top of the page. Name it sensibly, but you need not grant the service account access to the project/roles or user access.

When clicking done you will return to the list of service accounts and the new account will be shown. **Copy the service account email for later use**. On the far right under "Actions" click the three dots for the service account to open a menu of actions, and select "Manage keys".

Finally click the "ADD KEY" drop down and click "Create new key". Leave the Key type as the recommended JSON and click create. Save the resulting download in the root directory of this project (same level as serverless.yml) and name it `GCP_service_credentials.json`

### Google Sheet
Create the Google Sheet for the script to save to by making a copy of the following template:

https://docs.google.com/spreadsheets/d/14P3R9ayf7ZeRhkiypUo0vdHmt1-_PwPwoZg_OpOIP80/edit?usp=sharing

This can be done with `File -> Make a copy`  and saving your version on your own Google Drive.

Once you have your own copy click share in the top right. In the "Add people and groups" input field, paste in the email address of the service account you created earlier. This will allow the service accoutn to edit the sheet on your behalf.

Lastly from the URL of your sheet extract the Sheet ID. This is the code that follows the /d/ in the URL and ends on the next /. So for example using the link to the template sheet above, the id between the /d/ and the next / would be "`14P3R9ayf7ZeRhkiypUo0vdHmt1-_PwPwoZg_OpOIP80`". Save this value for later.

### Environment variables
In order to keep login credentials safe they are stored in a .env file. To configure your own file, duplicate the .env.example file that comes with this project. Rename it to `.env` and ensure it is still in the root level of the project. Fill in the three blank fields:
 - NP_USERNAME - The email address you would use to sign into your Now:pensions account.
 - NP_USERNAME - The password you would use to sign into your Now:pensions account.
 - SHEET_ID - The ID of the google sheet you obtained in the previous step.

### Serverless.yml
Lastly you can optionally configure the `serverless.yml` found in the root of the project. Options you may wish to configure are:
- region - (Line 9) The aws region that the Lambda function will run on (this may affect pricing).
- schedule - (Line 20) The frequency with which the job will run (will affect pricing if run too frequently). There is no need to run the function more than once per day.

## Deployment

With all the configuration out the way, deployment is now as simple as:

```
serverless login
```
to connect serverless to your aws account. Then deploy with :
```
serverless deploy
```

After running deploy, you should see output similar to:

```bash
Serverless: Packaging service...
Serverless: Excluding development dependencies...
Serverless: Uploading CloudFormation file to S3...
Serverless: Uploading artifacts...
Serverless: Uploading service now-pension-scraper.zip file to S3 (84.82 KB)...
Serverless: Validating template...
Serverless: Updating Stack...
Serverless: Checking Stack update progress...
........................
Serverless: Stack update finished...
Service Information
service: now-pension-scraper
stage: production
region: eu-west-1
stack: now-pension-scraper-production
resources: 16
api keys:
  None
endpoints:
  None
functions:
  cron-scrape: now-pension-scraper-production-cron-scrape
layers:
  None
Serverless: Publishing service to the Serverless Dashboard...
Serverless: Successfully published your service to the Serverless Dashboard: https://app.serverless.com/xxxx/apps/xxxx/now-pension-scraper/production/eu-west-1
```

There is no additional step required. Your defined schedules becomes active right away after deployment.

### Local invocation

In order to test out your functions locally, you can invoke them with the following command:

```
serverless invoke local --function cron-scrape
```

After invocation, you should see output similar to:

```bash
INFO:handler:Your cron function now-pension-scraper-production-cron-scrape ran at 15:02:43.203145
```


# Cost
This project was desingned to be as buget as possible and so is very cheap to run.
- GCP service account: free
- Google Sheets as Database: free
- Lambda function: At maximum useage it will run daily. That is 30 invocations per month at <1000 ms per invocation. This is well within AWS free tier of 1 000 000 invokations and 400 000 GB-seconds of compute time per month. Even outside of the free tier the pricing calculator does not even register a cost due to the tiny monthly compute time. So it is either free or pennies per year to run.

### Things I would do differently next time
The only significant change I would make is hosting the script as a Cloud function on GCP rather than a Lambda function on AWS, since it is already using a GCP service account for writting to the sheet. However this is only for tidiness and grouping the architecture, it would not change performance.