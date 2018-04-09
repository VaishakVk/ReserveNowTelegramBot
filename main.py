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
		message_url = 'https://api.telegram.org/bot501989919:AAGqYAHmoJy4lIfhhBZfUW6JJ8n2fNA2Nmc/sendMessage?text='+response+'&chat_id='+str(chat_id)
		urllib.urlopen(message_url)
		

app = webapp2.WSGIApplication([
    ('/', MainPage),
], debug=True)
