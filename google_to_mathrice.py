#!/usr/bin/env python3

# virtualenv -p python3 env
# source env/bin/activate
# pip install --upgrade google-api-python-client icalendar django unidecode

from oauth2client.service_account import ServiceAccountCredentials
from httplib2 import Http
from apiclient.discovery import build
from icalendar import Calendar, Event
from django.utils.feedgenerator import SyndicationFeed
import datetime
import time
from unidecode import unidecode
import json

LABORATORY_NAME = "LPSM"

__all__ = (
    'MathriceFeed',
    'DefaultFeed',
)

FEED_FIELD_MAP = (
    ('product_id',          'prodid'),
    ('method',              'method'),
    ('title',               'x-wr-calname'),
    ('description',         'x-wr-caldesc'),
    ('timezone',            'x-wr-timezone'),
    ('ttl',                 'x-published-ttl'),
)

ITEM_EVENT_FIELD_MAP = (
    # PARAM              -> ICS FIELD
    ('unique_id',           'uid'),
    ('summary',               'summary'),
    ('description',         'description'),
    ('start_datetime',      'dtstart'),
    ('end_datetime',        'dtend'),
    ('updateddate',         'last-modified'),
    ('created',             'created'),
    ('timestamp',           'dtstamp'),
    ('transparency',        'transp'),
    ('location',            'location'),
    ('geolocation',         'geo'),
    ('link',                'url'),
    ('organizer',           'organizer'),
    ('attendee',            'attendee'),
    ('status',              'status'),
    ('method',              'method'),
)


class MathriceFeed(SyndicationFeed):

    mime_type = 'text/calendar; charset=utf8'

    def write(self, outfile, encoding):
        cal = Calendar()
        cal.add('version', '2.0')
        cal.add('prodid', '-//SEMINAIRES/'+ LABORATORY_NAME + '/ICS v1.0//FR')
        cal.add('calscale', 'GREGORIAN')
        #cal.add('method', 'PUBLISH')
        for ifield, efield in FEED_FIELD_MAP:
            val = self.feed.get(ifield)
            if val is not None:
                cal.add(efield, val)
        self.write_items(cal)
        to_ical = getattr(cal, 'as_string', None)
        if not to_ical:
            to_ical = cal.to_ical
        outfile.write(to_ical())

    def write_items(self, calendar):
        for item in self.items:
            event = Event()
            for ifield, efield in ITEM_EVENT_FIELD_MAP:
                val = item.get(ifield)
                if val is not None:
                    event.add(efield, val)
            calendar.add_component(event)

DefaultFeed = MathriceFeed

# laboratoire.psm@gmail.com

#from pprint import pprint

"""
CALENDAR_ID = "laboratoire.psm@gmail.com"
CALENDAR_URL= "https://calendar.google.com/calendar/embed?src=laboratoire.psm%40gmail.com&ctz=Europe/Paris"

event = {
      "summary": "TITRE DE L'EVENEMENT",
      "location": "LPSM - 4 place Jussieu, 75005 Paris, FRANCE",
      "description": "Evenement de test.",
      "start": {
              "dateTime": "2017-07-21T09:00:00-07:00",
              "timeZone": "Europe/Paris"
      },
      "end": {
              "dateTime": "2017-07-21T17:00:00-07:00",
              "timeZone": "Europe/Paris"
      },
      "attendees": [
              {
                  "displayName": "Intervenant #1",
                  "email": "intervenant1@example.com"
              },
              {
                  "displayName": "Intervenant #2",
                  "email": "intervenant2@example.com"
              },
      ],
      "reminders": {
              "useDefault": False,
              "overrides": [
                        {"method": "email", "minutes": 1440 },
                        {"method": "popup", "minutes": 10 }
              ]
      }
}
"""



scopes = ["https://www.googleapis.com/auth/calendar"]
credentials = ServiceAccountCredentials.from_json_keyfile_name(
    "client_secret_service_account.json", scopes)
http_auth = credentials.authorize(Http())
service = build("calendar", "v3", credentials=credentials)


def calendar_create(calendar_summary):
    calendar = {
            'summary': calendar_summary,
            'timeZone': 'Europe/Paris'
    }
    response = service.calendars().insert(body=calendar).execute()
    return (response)

def calendar_list():
    page_token = None
    while True:
        calendar_list = service.calendarList().list(pageToken=page_token).execute()
        #for calendar_list_entry in calendar_list['items']:
        #    print(calendar_list_entry['summary'])
        page_token = calendar_list.get('nextPageToken')
        if not page_token:
            break
    return (calendar_list['items'])

def event_create(calendar_id, event):
    response = service.events().insert(calendarId=calendar_id, body=event).execute()
    return (response)

def event_delete(calendar_id, event_id):
    response = service.events().delete(calendarId=calendar_id, eventId=event_id).execute()
    return (response)


def event_list(calendar_id):
    page_token = None
    while True:
        events = service.events().list(calendarId=calendar_id, pageToken=page_token).execute()
        #for event in events["items"]:
            #pprint(event["summary"])
            #pprint("du " + event['start']['dateTime'] + " au " + event['end']['dateTime'])
            #pprint(event["description"])
            #pprint("")
            #print(event)
        page_token = events.get("nextPageToken")
        if not page_token:
            break
    return (events["items"])


def ics_add_event(feed, event):

    start = str(event['start']['dateTime']).split('T')
    start = start[0].split('-') + start[1].split(':')

    start = datetime.datetime(int(start[0]), int(start[1]), int(start[2]), int(start[3]), int(start[4]))
    end = str(event['end']['dateTime']).split('T')
    end = end[0].split('-') + end[1].split(':')
    end = datetime.datetime(int(end[0]), int(end[1]), int(end[2]), int(end[3]), int(end[4]))


    feed.add_item(
        unique_id=str(str(time.time()) + '-EVENT#' + str(event['id']) + '-@'+  LABORATORY_NAME),
        title=str(event['summary']),
        link=str(event['htmlLink']),
        description=str(event['description']),
        status=str(event['status']).upper(),
        location=str(event['location']),
        organizer=str(event['organizer']),
        attendee=str(event['attendees']),
        timestamp=start,
        start_datetime=start,
        end_datetime=end,
    )
    return (feed)

def json_add_event(event):
    new_event = {
        "id"        : event['id'],
        "startDate" : {
            "date": event['start']['dateTime'].split('T')[0].replace('-', ''),
            "time": event['start']['dateTime'].split('T')[1],
            "tz": "Europe/Paris"
        },
        "endDate" : {
            "date": event['end']['dateTime'].split('T')[0].replace('-', ''),
            "time": event['end']['dateTime'].split('T')[1],
            "tz": "Europe/Paris"
        },
        "description": str(event['description']),
        "chairs":
        {
            "id": 1,
            "fullName": event['attendees'],
            "affiliation": event['organizer']
        },
        "url": event['htmlLink'],
        "location": event['location'],
        "timezone": "Europe/Paris"
    }
    return (new_event)

def ics_create(fichier, title, url, desc, lang, events):
    feed = MathriceFeed(
        title=title,
        link=url,
        description=desc,
        language=lang,
     )
    for event in events:
        feed = ics_add_event(feed, event)
        fd = open(unidecode(fichier), 'wb')
        feed.write(fd, 'utf-8')
        fd.close()
    print("Fichier '" + fichier + "' genere (" + str(len(events)) + " events).")

def json_create(fichier, sem_id, title, url, desc, lang, events):
    feed = {}

    feed['count'] = len(events)
    feed['additionalInfo'] = {
        "path": {
            "url" : url,
            "name": title,
            "id"  : sem_id
        }
    }
    feed['results'] = []
    for event in events:
        feed['results'] = feed['results'] + [json_add_event(event)]
    try:
        tmp = bytes(json.dumps(feed, indent=4, sort_keys=False, ensure_ascii=False).encode('utf-8'), 'utf-8')
    except:
        tmp = bytes(unidecode(json.dumps(feed, indent=4, sort_keys=False, ensure_ascii=False)), 'latin1')
    fd = open(unidecode(fichier), 'wb')
    fd.write(tmp)
    fd.close()
    print("Fichier '" + fichier + "' genere (" + str(len(events)) + " events).")



def mathrice():
    calendars = calendar_list()
    for c in calendars:
        print('\n' + "Calendrier: " + c['summary'])
        url = "https://calendar.google.com/calendar/embed?src=" + c['id'] + "&ctz=" + c['timeZone']
        title = c['summary']
        events = event_list(c['id'])
        ics_create("export/ics/" + title + ".ics",
                   c['description'],
                   url,
                   c['description'],
                   r"fr",
                   events)
        json_create("export/json/" + title + ".json",
                    c['id'],
                    c['description'],
                    url,
                    c['description'],
                    u"fr",
                    events)


if __name__ == '__main__':

    mathrice()
