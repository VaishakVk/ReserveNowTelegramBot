# ReserveNowTelegramBot
Chat bot to reserve a table using Telegram Bot. Google App engine is used to Webhook the telegram Bot messages. WebHook: https://reservernow.appspot.com

Data is stored using Google Cloud Datastore.

## Dependencies
1. webapp2
2. json
3. urllib
4. logging
5. datetime
6. google.appengine
7. random

## Steps to Run
- Login to Telegram
- Search for ReserveNowBot
- Send a Hello and you are ready to go. 

## Assumptions
- Unlimited hotel area

## Database Tables
- CurrentConversation - to store conversations in a session
- UserDetail - Users table
- ReservationHistory - Reservations base table
