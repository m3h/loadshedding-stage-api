#!/usr/bin/env python3
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
import re
from enum import Enum, auto
import dateparser

import urllib.request


def cot_status(date=None, stage_schedule=None):
    if stage_schedule is None:
        stage_schedule = scrape_cot()
    if date is None:
        date = datetime.now()

    for block in stage_schedule:
        if block['start'] <= date <= block['end']:
            return block['stage']

    # if not in the schedule, assume stage 0
    return 0


COT_URL = 'https://www.capetown.gov.za/Family%20and%20home/residential-utility-services/residential-electricity-services/load-shedding-and-outages'


def scrape_cot(url=COT_URL):

    with urllib.request.urlopen(COT_URL) as response:
        html = response.read()
        return scrape_text(html)


def scrape_text(http_text):
    soup = BeautifulSoup(http_text, "html.parser")

    soup = soup.find_all("p", class_="lrg")[0]
    lines = [x.strip() for x in soup.get_text().splitlines()]
    lines = [x for x in lines if x != '']

    def error_extract(pattern, string):
        match = re.fullmatch(pattern, string)
        if match is None:
            raise Exception(f'error_extract: did not find pattern "{pattern}" in strings "{string}"')
        return match.groups()

    def dateparse(str, first_date=None, prefer_dates_from='future'):
        settings = {
            'PREFER_DATES_FROM': prefer_dates_from
        }
        if first_date is not None:
            settings['RELATIVE_BASE'] = first_date
        return dateparser.parse(str, settings=settings)

    i = 0
    # Find date range of stages
    if 'suspended' in lines[0]:
        return list()

    date_range_str, = error_extract(r'Eskom load-shedding: (.*)', lines[i])
    day_start, day_end, month, year = error_extract(r'(.*) - (.*) (.*) (.*)', date_range_str)
    print(day_start, day_end, month, year)

    # If something is date A, it is from the beginning of A
    start_date = dateparse(f'{day_start} {month} {year}') - timedelta(milliseconds=1)
    # If something is till B, it is till the end of B
    end_date = dateparse(f'{day_end} {month} {year}') + timedelta(days=1)

    print('start_date', start_date)
    print('end_date', end_date)

    i += 1

    i = lines.index('Eskom-supplied customers:', i); i += 1
    # TODO - process eskom-supplied section
    i = lines.index('City-supplied customers:', i); i += 1

    def process_date(line, first_date=None):
        try:
            date_str, = error_extract(r'(.*):', line)
        except Exception:
            return False, None

        return True, dateparse(date_str, first_date=first_date) 
        return True, dateparser.parse(date_str, first_date=first_date)

    def process_stage(line, first_date=None):

        try: 
            stage_str, start_str, end_str = error_extract(r'Stage (.*) from (.*) until (.*).', line)
        except Exception:
            stage_str, end_str = error_extract(r'Stage (.*) until (.*).', line)
            start_str = first_date.isoformat()

        start_date = dateparse(start_str, first_date=first_date)
        end_date = dateparse(end_str, first_date=start_date)

        stage_int = int(stage_str) 
        return start_date, end_date, stage_int

    def process_city_stages(lines, first_date):

        blocks = list()

        for line in lines:
            if line == 'Check the schedule for areas and times affected, and be prepared for outages.':
                # Done
                return blocks
            elif 'suspended' in line:
                continue

            is_date_line, date = process_date(line, first_date)
            if is_date_line:
                first_date = date
                print("new_context", first_date)
            else:
                start, end, stage = process_stage(line, first_date)
                print("new_stage", stage, start, end)
                blocks.append({
                    'start': start,
                    'end': end,
                    'stage': stage
                })

        return blocks
    blocks = process_city_stages(lines[i:], start_date)

    return blocks

