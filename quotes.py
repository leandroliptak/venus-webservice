#!/usr/bin/env python
# -*- coding: utf-8 -*-

from InstagramAPI import InstagramAPI

import pickle
import time

from googleapiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools
from oauth2client.tools import argparser

from PIL import Image, ImageDraw, ImageFont

# If modifying these scopes, delete the file token.json.
SCOPES = 'https://www.googleapis.com/auth/spreadsheets.readonly'

# The ID and range of a sample spreadsheet.
SAMPLE_SPREADSHEET_ID = '1HVrfM28RwDpwi2Gb_xUk96wEoCWa9w-eG9A6PAxyQ2A'
SAMPLE_RANGE_NAME = 'Frases para Storys!A%i:A%i'

args = argparser.parse_args()
args.noauth_local_webserver = True    

store = file.Storage('token.json')
creds = store.get()
if not creds or creds.invalid:
    flow = client.flow_from_clientsecrets('credentials.json', SCOPES)
    creds = tools.run_flow(flow, store, args)
service = build('sheets', 'v4', http=creds.authorize(Http()))

def get_quote(i):
    sheet = service.spreadsheets()
    result = sheet.values().get(spreadsheetId=SAMPLE_SPREADSHEET_ID,
                                range=SAMPLE_RANGE_NAME % (i,i)).execute()
    values = result.get('values', [])

    if not values:
        return False
    return values[0][0]

def create_quote_img(sentence):
    #variables for image size
    x1 = 1080
    y1 = 1920

    fnt = ImageFont.truetype('SpecialElite-Regular.ttf', 60)

    img = Image.new('RGB', (x1, y1), color = (255, 255, 255))
    d = ImageDraw.Draw(img)

    #find the average size of the letter
    sum = 0
    for letter in sentence:
      sum += d.textsize(letter, font=fnt)[0]

    average_length_of_letter = sum/len(sentence)

    #find the number of letters to be put on each line
    number_of_letters_for_each_line = (x1/2)/average_length_of_letter
    incrementer = 0
    fresh_sentence = ''

    #add some line breaks
    for letter in sentence:
      if(letter == '-'):
        fresh_sentence += '\n\n' + letter
      elif(incrementer < number_of_letters_for_each_line):
        fresh_sentence += letter
      else:
        if(letter == ' '):
          fresh_sentence += '\n'
          incrementer = 0
        else:
          fresh_sentence += letter
      incrementer+=1

    #print fresh_sentence

    #render the text in the center of the box
    dim = d.textsize(fresh_sentence, font=fnt)
    x2 = dim[0]
    y2 = dim[1]

    qx = (x1/2 - x2/2)
    qy = (y1/2-y2/2)

    d.multiline_text((qx,qy), fresh_sentence ,align="center",  font=fnt, fill=(100,100,100))

    img.save('quote.jpg')

if __name__ == '__main__':
    session_filename = "session"

    try:
        api = pickle.load(open(session_filename))
        print "API Loaded from previous session"
    except IOError:
        api = InstagramAPI("astro.venus.saturno", "vivaelverano")
        if not api.login():
            print "Login error."
            quit()
        else:
            pickle.dump(api, open(session_filename, "w"))
            print "API session saved to", session_filename

    last_quote = 1

    while True:
        quote = get_quote(last_quote)
        if quote:
            print "Quote:", quote
            create_quote_img(quote)
            api.uploadPhoto("quote.jpg", story=True)
            last_quote = last_quote + 1
        time.sleep(24 * 60 * 60)