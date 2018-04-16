import webapp2
import urllib
import json
import logging
from google.appengine.ext import ndb
import random

class CurrentConversation(ndb.Model):
	ChatId = ndb.IntegerProperty()
	Message = ndb.StringProperty()
	CreationDate = ndb.DateTimeProperty(auto_now_add=True)

class UserDetail(ndb.Model):
	ChatId = ndb.IntegerProperty()
	FirstName = ndb.StringProperty()
	LastName = ndb.StringProperty()
	CreationDate = ndb.DateTimeProperty(auto_now_add=True)
	
class ReservationHistory(ndb.Model):
	ChatId = ndb.IntegerProperty()
	TableType = ndb.StringProperty()
	Date = ndb.StringProperty()
	Time = ndb.StringProperty()
	CreationDate = ndb.DateTimeProperty(auto_now_add=True)
	
class BotInstructions():
	def __init__(self, fname, lname, chat_id, chat_message):
		self.fname = fname
		self.lname = lname
		self.chat_id = chat_id
		self.chat_message = chat_message
		self.response = None
		self.cleaned_message = chat_message
		self.latest_user_conv = None
		self.latest_response = None
		
		# Requests and Responses
		self.list_greetings = ['HELLO', 'HI', 'HII', 'HOWDY', 'OI', 'EY', 'HEY', 'HEYY', 'OII', 'GREETINGS', 'WELCOME', 'HI-YA', 'SUP']
		
		self.list_request_book = ['Shall I book a table for you?'
								, 'Would you like me to book a table for you?']
		self.list_request_date = ['When would you like me to book a table for you?'
								, 'When are you planning to visit us again?'
								, 'Can I know when you would be visiting us?']
		self.list_request_time = ['And at what time?'
								, 'Around what time can we expect your presence?'
								, 'At what time would you visit us?']
		self.list_request_ppl = ['How many persons would be accompanying you ?'
							   , 'How many guests should we expect?'
							   , 'Let me know how many persons are accompanying you.']
		self.list_request_table_type = ['We offer pool view, roof top and In the house. Which one would you prefer?'
									  , 'We have some of the best seats waiting or you - pool view, roof top and In the house. Please select your preference.'
									  , 'How about making a selection - pool view, roof top and In the house']
		self.list_request_confirmation = ['You have opted for {type} table and you would be visiting us on {date} at {time}. Can I confirm?'
										, 'Please confirm. The following is your preference - {type} table visiting us on {date} at {time}']
		
		self.list_response_success = ['Congrats!! We have successfully reserved a table for you. See you there at the restaurant'
									, 'Great News!! You table booking is confirmed. See you there at the restaurant'
									, 'Osm!! We have booked the table for you. See you there at the restaurant']
		self.list_response_no_seats = ['Uh Oh, looks like we do not have the required availability.'
									 , 'Sorry but we are facing heavy demand'
									 , 'Sorry, the bookings are full at the moment']
		self.list_response_decline = ['Oops, but my job is to book a table', 'Sorry, but thats what I am meant to do.']
		self.list_yes = ['Yes', 'Yeah', 'Yup', 'Yupp', 'Sure', 'Yess', 'ok', 'okay', 'fine', 'good', 'yea', 'definitely', 'right', 'aye', 'certainly', 'positive']
		self.list_no = ['No', 'nope', 'Nah', 'Na', 'not', 'negative']
		
		#Junk characters
		self.list_junk_char = [',', '.', '-', '!', '$', '=', '#', '%', '^', '*', '(', ')','"']
	
	def get_user_type(self):
		user_query = UserDetail.query(UserDetail.ChatId == self.chat_id)
		#logging.debug(user_query.count())
		if user_query.count() > 0:
			return 'EXISTING'
		else:
			UserInsert = UserDetail(ChatId = self.chat_id, FirstName = self.fname, LastName = self.lname)
			UserInsert.put()
			return 'NEW'
	
	def remove_junk(self):
		for i in self.list_junk_char:
			self.cleaned_message = self.cleaned_message.replace(i, '')
			#logging.debug(i + ' ' + self.cleaned_message)
		return self.cleaned_message.strip()
	
	def check_for_greeting(self):
		for i in self.list_greetings:
			if i in self.cleaned_message.upper().split():
				return True	
				
	def get_response(self):
		
		# Check for new Conversation
		conv_count = CurrentConversation.query(CurrentConversation.ChatId == self.chat_id).count()
		logging.debug(conv_count)
	
		if conv_count == 0:
			# Check for New User or an Existing User
			user_type = self.get_user_type()
			logging.debug(user_type)

			# Insert user request into database
			Conv = CurrentConversation(ChatId = self.chat_id, Message = self.chat_message)
			Conv.put()
		
			if user_type == 'NEW':
				self.response = 'Hello ' + self.fname + ' ' + self.lname + ', Welcome to ReserveNow !!' + '\n' + random.choice(self.list_request_book)
				Conv = CurrentConversation(ChatId = -1 * self.chat_id, Message = self.response)
				Conv.put()
				return self.response
			elif user_type == 'EXISTING':
				self.response = 'Welcome back ' + self.fname + ' ' + self.lname + ', Hope you are doing well !!' + '\n' + random.choice(self.list_request_book)
				Conv = CurrentConversation(ChatId = -1 * self.chat_id, Message = self.response)
				Conv.put()
				return self.response
		
		else:
			# Remove Junk Characters from text
			self.cleaned_message = self.remove_junk()
			logging.debug('Inside Else')
			#Retrieve Latest request
			conv_query = CurrentConversation.query(CurrentConversation.ChatId == self.chat_id).order(-CurrentConversation.CreationDate)
			logging.debug(conv_query.count())
			for i in conv_query:
				self.latest_user_conv = i.Message
				#logging.debug(i.key)
				#i.key.delete()
				break
			
			#Retrieve Latest response --, CurrentConversation.Message != 'Sorry, I didnt get that.'
			conv_query_response = CurrentConversation.query(CurrentConversation.ChatId == -1 * self.chat_id).order(-CurrentConversation.CreationDate)
			logging.debug(conv_query_response.count())
			for i in conv_query_response:
				self.latest_response = i.Message
				#logging.debug(i.key)
				#i.key.delete()
				break
			
			if self.latest_response.startswith('Welcome') or self.latest_response.startswith('Hello'):
				for i in map(lambda x:x.upper(), self.list_yes):
					if i in self.cleaned_message.upper().split():
						return random.choice(self.list_request_date)
				
				for i in map(lambda x:x.upper(), self.list_no):
					if i in self.cleaned_message.upper().split():
						return random.choice(self.list_response_decline)
				
				return 'Sorry, I didnt get that.'
			
			if self.latest_response in self.list_request_date:
				pass
			# Check for Greeting
			#greeting = self.check_for_greeting()
			
			#if greeting:
			#	return 'Hello ' + self.fname + ' ' + self.lname + ', Welcome to ReserveNow !!'
				
			return 'Sorry, I didnt get that.'
		
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
		message_url = 'https://api.telegram.org/bot501989919:AAGqYAHmoJy4lIfhhBZfUW6JJ8n2fNA2Nmc/sendMessage?text='+response+'&chat_id='+str(chat_id)
		urllib.urlopen(message_url)
		

app = webapp2.WSGIApplication([
    ('/', MainPage),
], debug=True)
