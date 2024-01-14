
# Chatwoot Agent Bot using Marino

This is an implementation of agent bot capabilities in chatwoot using [marino](https://github/act-gpt/marino) . Marino is an AI-powered chatbot meticulously crafted for fostering love and knowledge management.

Follow the given steps to get your agent bot integration up and running. 


##  Get your chatwoot up and create an agent bot

go to your chatwoot directory and ensure your local server is running.  Start a rails console in your directory.

```
bundle exec rails c
```

Inside the rails console, type the following commands to create an agent bot and get its access token. Save the retrieved token as you would need it in further step.

```
bot = AgentBot.create!(name: "Rasa Bot", outgoing_url: "http://localhost:8000")
bot.access_token.token
```

Connect Agent Bot to your inbox by running the following command

```
AgentBotInbox.create!(inbox: Inbox.first, agent_bot: bot)
```

## Clone this repo into your machine and config the environment. 


clone repo using the following command. 

```
git clone git@github.com:act-gpt/chatwoot_agent.git
```

copy `.env.example` to `.env` and change the follow values with appropriate ones

MARINO, MARINO_ID, MARINO_TOKEN and CHATWOOT_TOKEN.

## Using Python

run `pip install -r requirements.txt` and `python main.puy` to start server


## Connect to your chatwoot webwidget and start a conversation. 

if you are on your local machine, you can access the widget through the test page

```
http://localhost:3000/widget_tests
```
