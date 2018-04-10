# Copyright 2016 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import webapp2
import urllib
import urllib2
import json
#import requests


class MainPage(webapp2.RequestHandler):
    def post(self):
		list_request_date = ['When would you like me to book a table for you?', 'When are you planning to visit us again?', 'Can I know when you would be visiting us?']
		list_request_time = ['And at what time?', 'Around what time can we expect your presence?', 'At what time would you visit us?']
		list_request_ppl = ['How many persons would be accompanying you ?', 'How many guests should we expect?', 'Let me know how many persons are accompanying you.']
		list_request_table_type = ['We offer pool view, roof top and In the house. Which one would you prefer?', 'We have some of the best seats waiting or you - pool view, roof top and In the house. Please select your preference.', 'How about making a selection - pool view, roof top and In the house']
		list_request_confirmation = ['You have opted for {type} table and you would be visiting us on {date} at {time}. Can I confirm', 'Please confirm. The following is your preference - {type} table visiting us on {date} at {time}']
		
		list_response_success = ['Congrats!! We ave successfully reserved a table for you.', 'Great News!! You table booking is confirmed.', 'Well!! We have booked the required table for you.']
		list_response_no_seats = ['Uh Oh, looks like we do not have the required availability.', 'Sorry but we are facing heavy demand', 'Sorry, the bookings are full at the moment']


		# Convert to JSON
		data_json = json.loads(self.request.body)
		
		# Basic Attribues of sender
		f_name = data_json['message']['chat']['first_name']
		l_name = data_json['message']['chat']['last_name']
		
		# Chat attributes
		chat_id = data_json['message']['chat']['id']
		chat_message = data_json['message']['text']
		
		# Send message
		response = 'Hello ' + f_name + ' ' + l_name + ', Welcome to ReserveNow !!'
		message_url = 'https://api.telegram.org/bot/sendMessage?text='+response+'&chat_id='+str(chat_id)
		urllib.urlopen(message_url)
		

app = webapp2.WSGIApplication([
    ('/', MainPage),
], debug=True)
