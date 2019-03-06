#!/usr/bin/env python
import requests
import lxml.html
import itertools
from collections import OrderedDict
from operator import itemgetter
import random
import argparse
import json
import csv
import sys
import re

DEST = "schedule/nicar-2019-schedule"

SCHEDULE_URL = "https://www.ire.org/events-and-training/conferences/nicar-2019/schedule"
USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.13; rv:65.0) Gecko/20100101 Firefox/65.0"

DATES = [
    "2019-03-06",
    "2019-03-07",
    "2019-03-08",
    "2019-03-09",
    "2019-03-10",
]

def extract_speakers(description):
    """
    If speakers are listed in the first paragraph of the description,
    extract them.
    """
    speaker_pat = re.compile(r"^(Speakers?:\s+([^\n]+))?(.*)$", re.DOTALL)
    match = re.match(speaker_pat, description)
    graf, names, rest = match.groups()
    return names

def convert_time(ts):
    """
    Convert IRE time string (e.g., "12:30 pm", "8 am") to 24-hour time. Assmes that nothing's happening between midnight and 1am.
    """
    nums, suffix = ts.split(" ")
    if suffix == "pm":
        is_pm = True
    elif suffix == "am":
        is_pm = False
    else:
        raise ValueError("Can't parse " + ts)
    if nums.count(":") == 0:
        nums += ":00"
    hours, minutes = list(map(int, nums.split(":")))
    hours += (is_pm and hours != 12) * 12
    return "{0:02d}:{1:02d}".format(hours, minutes)

def calculate_length(start, end):
    s_hours, s_mins = list(map(int, start.split(":")))
    e_hours, e_mins = list(map(int, end.split(":")))
    return (((e_hours * 60) + e_mins) - ((s_hours * 60) + s_mins)) / 60

def parse_session(el, date):
    """
    Given an HTML element containing one session and the date of the session,
    extract the key information.
    """

    def get_text(sel):
        matches = el.cssselect(sel)
        stripped = [ el.text_content().strip() for el in matches ]
        return "\n\n".join(el for el in stripped if len(el)) or None

    speakers_raw = get_text(".event-speakers")
    if speakers_raw is None:
        s_speakers = None
    else:
        s_speakers = re.sub(r"^Speakers?:\s+", "", speakers_raw)

    s_time = get_text(".event-meta p")
    time_start, time_end = map(convert_time, s_time.split(" - "))

    s_href = el.cssselect(".event-title a")[0].attrib["href"]
    s_id = "/".join(s_href.split("/")[-3:-1])

    return OrderedDict([
        ("title", get_text(".event-title")),
        ("type", get_text(".event-type")),
        ("description", get_text(".event-content p:not(.event-speakers)")),
        ("speakers", s_speakers),
        ("date", date),
        ("time_start", time_start),
        ("time_end", time_end),
        ("length_in_hours", round(calculate_length(time_start, time_end), 3)),
        ("room", get_text(".event-meta h4")),
        ("event_id", s_id),
        ("event_url", "https://ire.org" + s_href),
    ])
    
def parse_day(el, date):
    """
    Given an HTML element containing a day's worth of sessions,
    pass each session element to the parser and return the results.
    """
    session_els = list(el)
    sessions_data = [ parse_session(s, date) for s in session_els ]
    return sessions_data

def fix_encoding(string):
    """
    Fix embedded utf-8 bytestrings.
    Solution via http://bit.ly/1DEpdmQ
    """
    pat = r"[\xc2-\xf4][\x80-\xbf]+"
    fix = lambda m: m.group(0).encode("latin-1").decode("utf-8")
    return re.sub(pat, fix, string.decode("utf-8"))

def get_sessions():
    """
    Fetch and parse the schedule HTML from the NICAR webpage.
    """
    html = fix_encoding(requests.get(
        SCHEDULE_URL,
        params = {
            "r": random.random()
        },
        headers = {
            "User-Agent": USER_AGENT
        }
    ).content)
    dom = lxml.html.fromstring(html)
    day_els = dom.cssselect("ul.schedule-list.pane")
    days_zipped = zip(day_els, DATES)
    sessions_nested = [ parse_day(el, date) for el, date in days_zipped ]
    sessions = itertools.chain.from_iterable(sessions_nested)
    return list(sorted(sessions, key=itemgetter(
        "date",
        "time_start",
        "time_end",
        "title"
    )))

def save_json(sessions):
    with open(DEST + ".json", "w") as f:
        json.dump(sessions, f, indent=4)
    
def save_csv(sessions):
    columns = [
        "event_id",
        "type",
        "date",
        "time_start",
        "time_end",
        "room",
        "title",
        "speakers",
        "description",
        "event_url",
        "length_in_hours",
    ]

    with open(DEST + ".csv", "w") as f:
        writer = csv.DictWriter(f, fieldnames = columns)
        writer.writeheader()
        writer.writerows(sessions)

def main():
    """
    Get the data and print it.
    """
    sessions = get_sessions()
    save_json(sessions)
    save_csv(sessions)

if __name__ == "__main__":
    main()
