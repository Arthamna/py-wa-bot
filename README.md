# WhatsApp Scheduler Bots with Python

This is a WhatsApp bot using the Meta (formerly Facebook) Cloud API, Python and Flask.  
## Table of Contents

- [WhatsApp Scheduler Bots with Python](#whatsapp-scheduler-bots-with-python)
  - [Table of Contents](#table-of-contents)
  - [Command List](#command-list)
  - [Prerequisites](#prerequisites)
  - [Get Started](#get-started)
  - [Step 1: Select Phone Numbers](#step-1-select-phone-numbers)
  - [Step 2: Send Messages with the API](#step-2-send-messages-with-the-api)
  - [Step 3: Test Webhooks Locally to Receive Messages](#step-3-test-webhooks-locally-to-receive-messages)
      - [Start your app](#start-your-app)
      - [Launch ngrok](#launch-ngrok)
      - [Integrate WhatsApp](#integrate-whatsapp)
  - [Final Step: Deploy to vercel](#final-step-deploy-to-vercel)
      - [Option A: Vercel CLI](#option-a-vercel-cli)
      - [Option B: Vercel Dashboard](#option-b-vercel-dashboard)
      - [Configure Environment Variables](#configure-environment-variables)
  - [Suplementary : Uptime Monitoring](#suplementary-uptime-monitoring)

## Command List
All of the command is written in indonesian language. To configure it, go to [here](https://github.com/Arthamna/py-wa-bot/blob/main/app/utils/whatsapp_utils.py).

- **Tambah [aktivitas] jam [HH:MM] tanggal [DD] [Bulan (Opsional)]**  
  Add a new activity at the specified time and date; month is optional.

- **jadwal hari ini**  
  Display today’s schedule.

- **jadwal minggu ini**  
  Display this week’s schedule.

- **ganti nama [aktivitas lama] menjadi [aktivitas baru] tanggal [DD (Opsional)] [Bulan (Opsional)]**  
  Rename an existing activity to a new name; you can optionally specify a day and/or month.

- **ganti tanggal [aktivitas] dari [tanggal lama] menjadi [tanggal baru] [Bulan (Opsional)]**  
  Change an activity’s date from the old date to a new date; month is optional.

- **hapus [aktivitas] tanggal [(Opsional)] [Bulan (Opsional)]**  
  Delete an activity on the given date; use current date and month if empty.


## Prerequisites

1. A Meta developer account — If you don’t have one, you can [create a Meta developer account here](https://developers.facebook.com/).
2. A business app — If you don't have one, you can [learn to create a business app here](https://developers.facebook.com/docs/development/create-an-app/). If you don't see an option to create a business app, select **Other** > **Next** > **Business**.
3. Familiarity with Python to follow the tutorial.
4. Knowledge with relational database, preferably PostgreSQL. 
5. Once your database is initialized, set the following environment variables :
  ```env
  DB_PASS
  DB_HOST
  DB_USER
  DB_PORT
  DB_NAME 
  ```

## Get Started

1. **Overview & Setup**: Begin your journey [here](https://developers.facebook.com/docs/whatsapp/cloud-api/get-started).
2. **Locate Your Bots**: Your bots can be found [here](https://developers.facebook.com/apps/).
3. **WhatsApp API Documentation**: Familiarize yourself with the [official documentation](https://developers.facebook.com/docs/whatsapp).
4. **Helpful Guide**: Here's a [Python-based guide](https://developers.facebook.com/blog/post/2022/10/24/sending-messages-with-whatsapp-in-your-python-applications/) for sending messages.
5. **API Docs for Sending Messages**: Check out [this documentation](https://developers.facebook.com/docs/whatsapp/cloud-api/guides/send-messages).

## Step 1: Select Phone Numbers

- Make sure WhatsApp is added to your App.
- You begin with a test number that you can use to send messages to up to 5 numbers.
- Go to API Setup and locate the test number from which you will be sending messages.
- Here, you can also add numbers to send messages to. Enter your **own WhatsApp number**.
- You will receive a code on your phone via WhatsApp to verify your number.

## Step 2: Send Messages with the API

You have two options here :
1. Obtain a 24-hour access token from the API access section.
2. Creating an access that works longer then 24 hours :

- Create a [system user at the Meta Business account level](https://business.facebook.com/settings/system-users).
- On the System Users page, configure the assets for your System User, assigning your WhatsApp app with full control. Don't forget to click the Save Changes button.
   - [Create system user](https://github.com/Arthamna/py-wa-bot/blob/main/img_docs/create%20system%20user.jpg)
   - [Assign assets](https://github.com/Arthamna/py-wa-bot/blob/main/img_docs/assign%20assets.jpg)
- Now click `Generate new token` and select the app, and then choose how long the access token will be valid. You can choose 60 days or never expire.
- Select all the permissions, as I was running into errors when I only selected the WhatsApp ones.
- Confirm and copy the access token.

Find the following information on the **App Dashboard**, add it into your environtment file:

- **APP_ID**: "<YOUR-WHATSAPP-BUSINESS-APP_ID>" (Found at App Dashboard)
- **APP_SECRET**: "<YOUR-WHATSAPP-BUSINESS-APP_SECRET>" (Found at App Dashboard=>App Settings=>Basics)
- **RECIPIENT_WAID**: "<YOUR-RECIPIENT-TEST-PHONE-NUMBER>" (This is your WhatsApp ID, i.e., phone number. Make sure it is added to the account as shown in the example test message.)
- **VERSION**: "v22.0" (For example, use the latest version of the Meta Graph API)
- **ACCESS_TOKEN**: "<YOUR-SYSTEM-USER-ACCESS-TOKEN>" (Created in the previous step)

> You can only send a template type message as your first message to a user. That's why you have to send a reply first before we continue.


## Step 3: Test Webhooks Locally to Receive Messages

#### Start your app
- Make you have a python installation or environment and install the requirements: `pip install -r requirements.txt`
- Run your Flask app locally by executing ```waitress-serve --host=0.0.0.0 --port=8000 run:app```

#### Launch ngrok

The steps below are taken from the [ngrok documentation](https://ngrok.com/docs/integrations/whatsapp/webhooks/).

> You need a static ngrok domain because Meta validates your ngrok domain and certificate!

Once your app is running successfully on localhost, let's get it on the internet securely using ngrok!

1. If you're not an ngrok user yet, just sign up for ngrok for free.
2. Download the ngrok agent.
3. Go to the ngrok dashboard, click Your [Authtoken](https://dashboard.ngrok.com/get-started/your-authtoken), and copy your Authtoken.
4. Follow the instructions to authenticate your ngrok agent. You only have to do this once.
5. On the left menu, expand Cloud Edge and then click Domains.
6. On the Domains page, click + Create Domain or + New Domain. (here everyone can start with [one free domain](https://ngrok.com/blog-post/free-static-domains-ngrok-users))
7. Start ngrok by running the following command in a terminal on your local desktop:
```
ngrok http 8000 --domain your-domain.ngrok-free.app
```
8. ngrok will display a URL where your localhost application is exposed to the internet (copy this URL for use with Meta).


#### Integrate WhatsApp

In the Meta App Dashboard, go to WhatsApp > Configuration, then click the Edit button.
1. In the Edit webhook's callback URL popup, enter the URL provided by the ngrok agent to expose your application to the internet in the Callback URL field, with /webhook at the end (i.e. https://myexample.ngrok-free.app/webhook).
2. Enter a verification token. This string is set up by you when you create your webhook endpoint. You can pick any string you like. Make sure to update this in your `VERIFY_TOKEN` environment variable.
3. After you add a webhook to WhatsApp, WhatsApp will submit a validation post request to your application through ngrok. Confirm your localhost app receives the validation get request and logs `WEBHOOK_VERIFIED` in the terminal.
4. Back to the Configuration page, click Manage.
5. On the Webhook fields popup, click Subscribe to the **messages** field. Tip: You can subscribe to multiple fields.
6. If your Flask app and ngrok are running, you can click on "Test" next to messages to test the subscription. You recieve a test message in upper case. If that is the case, your webhook is set up correctly.

## Final Step: Deploy to vercel

#### Option A: Vercel CLI  
- Check out the CLI guide: https://vercel.com/docs/cli  
- From your project root (with `vercel.json`), run:  
  ```bash
  vercel --prod 
  ```
#### Option B: Vercel Dashboard
- Go to https://vercel.com, log in, and import your Git repo.
- Follow the prompts to deploy.

#### Configure Environment Variables
1. In your Vercel Dashboard, select your project.
2. In your Vercel project, go to Settings → Environment Variables
3. Add each key from your local .env, then save it:


Wait for the project to build, and voila! Your scheduler bot is ready to use. Just use the command you set up!  

## Suplementary: Uptime Monitoring
Keep your service awake with [UptimeRobot](https://uptimerobot.com/).
Monitor the /check endpoint to prevent timeouts.



