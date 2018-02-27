# Sarip Bot
Indomie at your fingertips.

## Requirements
- Python 3.6.4

## How to Run
1. Setup virtual environment
```
virtualenv venv
```

2. Activate virtual environment

On Posix systems:
```
source venv/bin/activate
```

On Windows:
```
venv\Scripts\activate
```

3. Install dependencies
```
pip install -r requirements.txt
```

4. Copy .env.example to .env and make any changes
```
cp .env.example .env
```

5. Run application
```
python app.py
```

## How to Develop on Local Machine
1. Create your own channel for LINE Messaging API
2. Adjust your `.env` file according to your own channel settings
3. Download and start [ngrok](https://ngrok.com) on your local machine
4. Update Webhook URL of your own channel to be `https://[URL of your ngrok]/callback` (e.g.: `https://70f2ce7a.ngrok.io/callback`)
5. Make any changes on the code
6. Run application
```
python app.py
```
7. Run ngrok using the same port you use for the flask app (see .env file)
```
ngrok http your_port
```
8. Test your changes on the code using bot from your own channel
