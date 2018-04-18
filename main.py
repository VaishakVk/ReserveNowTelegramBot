import webapp2
import urllib
import json
import logging
import datetime
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
		self.list_request_date = ['When would you like me to book a table for you today? Please note that we currently do reservations for the same day only.'
								, 'When are you planning to visit us today? Please note that we currently do reservations for the same day only.'
								, 'Can I know when you would be visiting us today? Please note that we currently do reservations for the same day only.']
		'''self.list_request_time = ['And at what time?'
								, 'Around what time can we expect your presence?'
								, 'At what time would you visit us?']'''
		self.list_request_ppl = ['How many persons would be accompanying you ?'
							   , 'How many guests should I expect?'
							   , 'Let me know how many persons are accompanying you.']
		self.list_request_table_type = ['We offer pool view, roof top and In the house. Which one would you prefer?'
									  , 'We have some of the best seats waiting or you - pool view, roof top and In the house. Please select your preference.'
									  , 'How about making a table selection - pool view, roof top and In the house']
		self.list_request_confirmation = ['You have opted for {} table and you would be visiting us at {} today. Can I confirm?'
										, 'Please confirm. The following is your preference - {} table visiting us at {} today']
		
		self.list_response_success = ['Congrats!! We have successfully reserved a table for you. See you there at the restaurant'
									, 'Great News!! You table booking is confirmed. See you there at the restaurant'
									, 'Osm!! We have booked the table for you. See you there at the restaurant']
		self.list_response_no_seats = ['Uh Oh, looks like we do not have the required availability.'
									 , 'Sorry but we are facing heavy demand'
									 , 'Sorry, the bookings are full at the moment']
		self.list_response_decline = ['Oops, but my job is to book a table', 'Sorry, but thats what I am meant to do.']
		self.list_yes = ['Yes', 'Yeah', 'Yup', 'Yupp', 'Sure', 'Yess', 'ok', 'okay', 'fine', 'good', 'yea', 'definitely', 'right', 'aye', 'certainly', 'positive']
		self.list_no = ['No', 'nope', 'Nah', 'Na', 'not', 'negative']
		self.list_time = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12', '13', '14', '15', '16', '17', '18', '19', '20', '21', '22', '23']
		self.list_time_measure = ['o clock', 'am', 'pm' 'a.m.', 'p.m.', 'a m', 'p m', 'oclock']
		self.list_default = ['Sorry, I did not get that']
		self.list_table_type = ['POOL', 'ROOF', 'TOP', 'HOUSE', 'INSIDE']
		self.list_book_confirm = self.list_yes + ['Go ahead', 'book', 'Carry on']
		self.dict_table_type = {'ROOF': 'Roof Top',
								'POOL': 'Pool View',
								'TOP': 'Roof Top',
								'HOUSE': 'In the house',
								'INSIDE': 'In the house'
								}
		
		''',
						  'one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine', 'ten', 'eleven', 'twelve', 'thirteen',
						  'fourteen', 'fifteen', 'sixteen', 'seventeen', 'eighteen', 'nineteen', 'twenty', 'twenty one', 'twenty two', 'twenty three', 'twenty four'] '''
		
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
	
	def parse_date(self):
		time = []
		for i in self.cleaned_message:
			for j in i:
				if j.isnumberic():
					time.append(j)
		if len(time) == 4:
			hr = time[:2]
			min = time[2:]
		elif len(time) == 3:
			hr = time[0]
			min = time[1:]
		elif len(time) == 1 or len(time) == 2:
			hr = ''.join(time)
			min = '00'
		
		UserReservationInsert = ReservationHistory(ChatId = self.chat_id, TableType = 'X', Time = hr + ':' + min)
		UserReservationInsert.put()
		return True
	
	def validate_tbl_type(self):
		for i in self.list_table_type:
			if i in self.cleaned_message.upper().split():
				user_reservation_query = ReservationHistory.query(ReservationHistory.ChatId == self.chat_id).order(-ReservationHistory.CreationDate)
				for j in user_reservation_query:
					user_resv_det = j.key.get()
					user_resv_det.TableType = self.dict_table_type[i]
					user_resv_det.put()
					break
				return True
		return False
	
	def db_cleanup(self):
		DelConv = CurrentConversation.query(CurrentConversation.ChatId == -1 * self.chat_id)
		for i in DelConv:
			i.key.delete()
		
		DelConvUser = CurrentConversation.query(CurrentConversation.ChatId == self.chat_id)
		for i in DelConvUser:
			i.key.delete()
			
	def get_response(self):
		
		TimeInterval = 0
		
		# Check for new Conversation
		conv_count = CurrentConversation.query(CurrentConversation.ChatId == self.chat_id).count()
		logging.debug(conv_count)
		
		# Check if the latest conversation has exceeded timeout - 300 secs
		conv_query_latest = CurrentConversation.query(CurrentConversation.ChatId == self.chat_id).order(-CurrentConversation.CreationDate)
		for i in conv_query_latest:
			TimeInterval = (datetime.datetime.now() - i.CreationDate).seconds
			break
			
		if conv_count == 0 or TimeInterval > 180:
			if TimeInterval > 180:
				self.db_cleanup()
			
			# Check for New User or an Existing User
			user_type = self.get_user_type()
			logging.debug(user_type)

			# Insert user request into database
			Conv = CurrentConversation(ChatId = self.chat_id, Message = self.chat_message)
			Conv.put()
		
			if user_type == 'NEW':
				self.response = 'Hello ' + self.fname + ' ' + self.lname + ', Welcome to ReserveNow !!' + '\n' + 'What would you like to do?'
				Conv = CurrentConversation(ChatId = -1 * self.chat_id, Message = self.response)
				Conv.put()
				return self.response
			elif user_type == 'EXISTING':
				self.response = 'Welcome back ' + self.fname + ' ' + self.lname + ', Hope you are doing well !!' + '\n' + 'What would you like to do?'
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
				logging.debug('Secs')
				logging.debug((datetime.datetime.now() - i.CreationDate).seconds)
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
			
			if 'What would you like to do' in self.latest_response:
				#for i in self.latest_response:
					if 'STATUS' in self.cleaned_message.upper():
						user_reservation_query = ReservationHistory.query(ReservationHistory.ChatId == self.chat_id).order(-ReservationHistory.CreationDate)
						if user_reservation_query.count() > 0:
							for i in user_reservation_query:
								user_resv_time = i.Time
								user_resv_tabletype = i.TableType
								self.response = 'You have booked a {} table at {}'.format(user_resv_tabletype, user_resv_time)
								return self.response
						else:
							return 'Sorry I did not find any table booked.' + '\n' + random.choice(self.list_request_book)
						
					elif 'BOOK' in self.cleaned_message.upper():
						self.response = random.choice(self.list_request_date)
						Conv = CurrentConversation(ChatId = -1 * self.chat_id, Message = self.response)
						Conv.put()
						return self.response 
						
					for i in ['UPDATE', 'MODIFY', 'CHANGE']:
						if i in self.cleaned_message.upper():
							user_reservation_query = ReservationHistory.query(ReservationHistory.ChatId == self.chat_id).order(-ReservationHistory.CreationDate)
							if user_reservation_query.count() > 0:
								for i in user_reservation_query:
									user_resv_time = i.Time
									user_resv_tabletype = i.TableType
									self.response = 'You have booked a {} table at {}. When would you like to modify?'.format(user_resv_tabletype, user_resv_time)
									Conv = CurrentConversation(ChatId = -1 * self.chat_id, Message = self.response)
									Conv.put()
									return self.response
							else:
								return 'Sorry I did not find any table booked.' + '\n' + random.choice(self.list_request_book)
						
					return 'Sorry I did not get that. I can book a table, update or modify any of yout present reservation'
			
			if self.latest_response in self.list_request_book:
				for i in map(lambda x:x.upper(), self.list_yes):
					if i in self.cleaned_message.upper().split():
						self.response = random.choice(self.list_request_date)
						Conv = CurrentConversation(ChatId = -1 * self.chat_id, Message = self.response)
						Conv.put()
						return self.response
				
				for i in map(lambda x:x.upper(), self.list_no):
					if i in self.cleaned_message.upper().split():
						self.response = random.choice(self.list_response_decline)
						Conv = CurrentConversation(ChatId = -1 * self.chat_id, Message = self.response)
						Conv.put()
						return self.response
				
				return random.choice(self.list_default)
			
			if self.latest_response in self.list_request_date or self.latest_response in 'When would you like to modify':
				time = self.parse_date()
				if time:
					self.response = random.choice(self.list_request_table_type)
					Conv = CurrentConversation(ChatId = -1 * self.chat_id, Message = self.response)
					Conv.put()
					return self.response
				else:
					return random.choice(self.list_default)
					
			if self.latest_response in self.list_request_table_type:
				tbl_type = self.validate_tbl_type()
				if tbl_type:
					self.response = random.choice(self.list_request_confirmation).format()
					Conv = CurrentConversation(ChatId = -1 * self.chat_id, Message = self.response)
					Conv.put()
					return self.response
				else:
					return random.choice(self.list_default)
			
			if self.latest_response in self.list_request_confirmation:
				for i in map(lambda x:x.upper(), self.list_book_confirm):
					if i in self.cleaned_message.upper().split():
						self.response = random.choice(self.list_response_success)
						Conv = CurrentConversation(ChatId = -1 * self.chat_id, Message = self.response)
						Conv.put()
						self.db_cleanup()
						return self.response
				
				for i in map(lambda x:x.upper(), self.list_no):
					if i in self.cleaned_message.upper().split():
						self.response = random.choice(self.list_request_date)
						Conv = CurrentConversation(ChatId = -1 * self.chat_id, Message = self.response)
						Conv.put()
						return self.response
				
				return random.choice(self.list_default)
				
			# Check for Greeting
			#greeting = self.check_for_greeting()
			
			#if greeting:
			#	return 'Hello ' + self.fname + ' ' + self.lname + ', Welcome to ReserveNow !!'
				
			return random.choice(self.list_default)
		
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
