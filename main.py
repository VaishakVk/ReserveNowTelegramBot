import webapp2
import urllib
import json
import logging
from google.appengine.ext import ndb

class CurrentConversation(ndb.Model):
	ChatId = ndb.IntegerProperty()
	Message = ndb.StringProperty()
	CreationDate = ndb.DateTimeProperty(auto_now_add=True)
	
class BotInstructions():
	def __init__(self, fname, lname, chat_id, chat_message):
		self.fname = fname
		self.lname = lname
		self.chat_id = chat_id
		self.chat_message = chat_message
		self.response = None
		self.cleaned_message = chat_message
		self.latest_conversation = None
		
		# Requests and Responses
		self.list_greetings = ['Hello', 'Hi', 'Hii', 'Howdy', 'Oi', 'Ey', 'Hey', 'Heyy', 'Oii']
		
		self.list_request_date = ['When would you like me to book a table for you?', 'When are you planning to visit us again?', 'Can I know when you would be visiting us?']
		self.list_request_time = ['And at what time?', 'Around what time can we expect your presence?', 'At what time would you visit us?']
		self.list_request_ppl = ['How many persons would be accompanying you ?', 'How many guests should we expect?', 'Let me know how many persons are accompanying you.']
		self.list_request_table_type = ['We offer pool view, roof top and In the house. Which one would you prefer?', 'We have some of the best seats waiting or you - pool view, roof top and In the house. Please select your preference.', 'How about making a selection - pool view, roof top and In the house']
		self.list_request_confirmation = ['You have opted for {type} table and you would be visiting us on {date} at {time}. Can I confirm', 'Please confirm. The following is your preference - {type} table visiting us on {date} at {time}']
		
		self.list_response_success = ['Congrats!! We have successfully reserved a table for you.', 'Great News!! You table booking is confirmed.', 'Well!! We have booked the required table for you.']
		self.list_response_no_seats = ['Uh Oh, looks like we do not have the required availability.', 'Sorry but we are facing heavy demand', 'Sorry, the bookings are full at the moment']
		
		#Junk characters
		self.list_junk_char = [',', '.', '-', '!', '$', '=', '#', '%', '^', '*', '(', ')','"']
	
	def remove_junk(self):
		for i in self.list_junk_char:
			self.cleaned_message = self.cleaned_message.replace(i, '')
			#logging.debug(i + ' ' + self.cleaned_message)
		return self.cleaned_message.strip()
	
	def check_for_greeting():
		for i in self.list_greetings:
			if i in self.cleaned_message.split():
				return True
	
	def get_response(self):
		self.cleaned_message = self.remove_junk()
		#self.response = 'Hello ' + self.fname + ' ' + self.lname + ', Welcome to ReserveNow !!'
		conv_query = CurrentConversation.query(CurrentConversation.ChatId == self.chat_id) ##.order(-CurrentConversation.CreationDate)
		logging.debug(len(conv_query))
		for i in conv_query:
			self.latest_conversation = i.Message
			break
		
		greeting = check_for_greeting()
		
		if greeting:
			return 'Hello ' + self.fname + ' ' + self.lname + ', Welcome to ReserveNow !!'
		# Insert data into database
		Conv = CurrentConversation(ChatId = self.chat_id, Message = self.chat_message)
		Conv.put()
		return latest_conversation
		
class MainPage(webapp2.RequestHandler):
	
	def post(self):

		# Convert to JSON
		data_json = json.loads(self.request.body)
		
		# Basic Attribues of sender
		f_name = data_json['message']['chat']['first_name']
		l_name = data_json['message']['chat']['last_name']
		
		# Chat attributes
		chat_id = data_json['message']['chat']['id']
		chat_message = data_json['message']['text']
		
		# Send message
		bot_response = BotInstructions(fname = f_name, lname = l_name, chat_id = chat_id, chat_message = chat_message)
		response = bot_response.get_response()
		
		#response = 'Hello ' + f_name + ' ' + l_name + ', Welcome to ReserveNow !!'
		message_url = 'https://api.telegram.org/bot/sendMessage?text='+response+'&chat_id='+str(chat_id)
		urllib.urlopen(message_url)
		

app = webapp2.WSGIApplication([
    ('/', MainPage),
], debug=True)
