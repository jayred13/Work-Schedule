"""Get Coscto work schedule."""
from __future__ import print_function
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pyautogui
import threading
import re
import datetime
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request


def wait_for(wait_id, wait_type):
    """Wait until element is visible."""
    try:
        #  print('Waiting for ' + wait_id)
        wait = WebDriverWait(browser, 30)
        wait.until(EC.visibility_of_element_located((wait_type, wait_id)))
    except Exception:
        print('Loading Timeout')
        browser.quit()

# I am typing :

def frame_switch(frame_id):
    """Switch frames given name."""
    try:
        browser.switch_to.frame(frame_id)
        # print('@ ' + frame_id)
    except Exception:
        print('Frame switch has failed.')


def login(username, password):
    """Login to ESS and Schedules."""
    def open_employee_portal():
        """Navigate to employee self-service portal."""
        def employee_site():
            print('*** employee_site ***')
            portal_id = 'div.col-sm-6:nth-child(5) > a:nth-child(5)'
            login_elem = browser.find_element_by_css_selector(portal_id)
            login_elem.click()

            browser.close()  # Login opens new tab, close and switch
            browser.switch_to.window(browser.window_handles[0])

        def ess_login():
            print('*** ess_login ***')
            wait_for('#username', By.CSS_SELECTOR)
            user_elem = browser.find_element_by_css_selector('#username')
            user_elem.send_keys(username)
            pass_elem = browser.find_element_by_css_selector('#password')
            pass_elem.send_keys(password)
            pass_elem.submit()

        employee_site()
        ess_login()

    def open_online_schedules():
        """Open online schedules in portal."""
        def nav_to_schedule_link():
            print('*** nav_to_schedule_link ***')
            browser.switch_to.default_content()
            wait_for('#bc0', By.CSS_SELECTOR)
            frame_switch('contentAreaFrame')
            frame_switch('Overview')

            wait_for('Online Schedule', By.PARTIAL_LINK_TEXT)
            sched_elem = browser.find_element_by_partial_link_text(
                'Online Schedule')
            sched_elem.click()

        def schedule_login():
            print('*** schedule_login ***')
            browser.switch_to.default_content()
            wait_for('#contentAreaFrame', By.CSS_SELECTOR)
            frame_switch('contentAreaFrame')
            wait_for('isolatedWorkArea', By.ID)
            frame_switch('isolatedWorkArea')

            wait_for('#CAMUsername', By.CSS_SELECTOR)
            user_elem = browser.find_element_by_css_selector('#CAMUsername')
            user_elem.send_keys(username)

            pass_elem = browser.find_element_by_css_selector('#CAMPassword')
            pass_elem.send_keys(password)
            pass_elem.submit()

        nav_to_schedule_link()
        schedule_login()
    open_employee_portal()
    open_online_schedules()


def get_schedules():
    """Collect online schedules for weeks."""
    def get_week(week_num):
        # print('*** get_week ***')
        browser.switch_to.default_content()
        wait_for('#contentAreaFrame', By.CSS_SELECTOR)
        frame_switch('contentAreaFrame')
        wait_for('isolatedWorkArea', By.ID)
        frame_switch('isolatedWorkArea')

        wait_for('button', By.TAG_NAME)
        weeks_posted = browser.find_elements_by_tag_name('select')
        drop_elem = weeks_posted[-1]
        drop_elem.click()
        option = drop_elem.find_elements_by_tag_name('option')

        if week_num >= len(option):
            return False
        option[week_num].click()
        week_end = datetime.datetime.strptime(option[week_num].text,
                                              '%Y-%m-%d')

        buttons = browser.find_elements_by_tag_name('button')
        buttons[-1].click()
        read_schedule(week_end)
        return True

    def sched_ready(week_end):
        # print('*** sched_ready ***')
        date_id = '#rt_NS_ > tbody > tr:nth-child(1) > td > div:nth-child(2)' \
            ' > span:nth-child(3)'
        wait_for(date_id, By.CSS_SELECTOR)
        date = browser.find_element_by_css_selector(date_id)
        sun_date = datetime.datetime.strptime(date.text, '%m/%d/%Y')

        return week_end == sun_date

    def read_schedule(week_end):
        # print('*** read_schedule ***')
        if not sched_ready(week_end):
            read_schedule(week_end)
        else:
            table_id = '#rt_NS_ > tbody > tr:nth-child(2) > td > div > table >'\
                ' tbody > tr > td > table > tbody > tr:nth-child(2) > td >'\
                ' table > tbody'
            table_elem = browser.find_element_by_css_selector(table_id)

            pattern = re.compile(r"""
                (\d+ / \d+ / \d\d\d\d)              #Date
            \s?  (\d\d : \d\d \s \w\w)              #Start Time
            \s?  (\d\d : \d\d \s \w\w)              #End Time
            \s?  (\d+.\d\d)                         #Duration
            \s?  (\d+.\d\d)
            \s?  ([0-9a-zA-Z]+ [/\s-]?
            [0-9a-zA-Z]+ [\s-]?  [0-9a-zA-Z]+)?     #Department
            \s? (\d+ / \d+ / \d\d\d\d)
            """, re.VERBOSE)

            workdays = re.findall(pattern, table_elem.text)
            if workdays not in work_schedule:
                work_schedule.append(workdays)
                print('Adding...\n', workdays)
            x = threading.Thread(target=add_to_calender(cal_id))
            x.start()

    global cal_id
    cal_id = pyautogui.password(text='Input Calendar ID: ',
                                title='cal_id',
                                default='example@group.calendar.google.com',
                                mask='*')
    i = 0
    while get_week(i):
        i += 1

# I am typing while the application is running :)

def add_to_calender(cal_id):
    global service

    def authenticate():
        # If modifying these scopes, delete the file token.pickle.
        SCOPES = ['https://www.googleapis.com/auth/calendar']
        creds = None
        # # The file token.pickle stores the user's access and refresh tokens,
        # and is created automatically when the authorization flow completes
        # for the first time.
        if os.path.exists('token.pickle'):
            with open('token.pickle', 'rb') as token:
                creds = pickle.load(token)
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials.json', SCOPES)
                creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open('token.pickle', 'wb') as token:
                pickle.dump(creds, token)

        global service
        service = build('calendar', 'v3', credentials=creds)

    def upcoming_events(num, cal_id):
        # Get start of the week
        now = datetime.datetime.utcnow()
        monday = now - datetime.timedelta(days=now.weekday())
        monday = monday.isoformat() + 'Z'  # 'Z'indicates UTC

        print('Getting the upcoming ' + str(num) + ' events')
        events_result = service.events().list(
            calendarId=cal_id,
            timeMin=monday, maxResults=num, singleEvents=True,
            orderBy='startTime'
            ).execute()
        events = events_result.get('items', [])
        lst_events = []

        if not events:
            print('No upcoming events found.')
        for event in events:
            start = event['start'].get('dateTime', event['start'].get('date'))
            # print(start, event['summary'])
            lst_events.append(start.split('T')[0])

        return lst_events

    def add_event(cal_id, date, dept, startTime, endTime, changeDate):
        event = {
          'summary': dept,
          'location': '',
          'description': 'Changed on: ' + changeDate,
          'start': {
            'dateTime': date + 'T' + startTime,
            'timeZone': 'America/Denver',
          },
          'end': {
            'dateTime': date + 'T' + endTime,
            'timeZone': 'America/Denver',
          },
          'recurrence': [],
          'attendees': [],
          'reminders': {
            'useDefault': True,
            'overrides': [],
          },
        }

        event = service.events().insert(
            calendarId=cal_id,
            body=event).execute()
        print('Event created: %s' % (event.get('htmlLink')))

    def check_change_date():
        print('Checking...')


    authenticate()
    events = upcoming_events(10, cal_id)
    for week in work_schedule:
        for workday in week:
            date = datetime.datetime.strptime(workday[0], '%m/%d/%Y').date()
            startTime = datetime.datetime.strptime(workday[1], '%I:%M %p').time()
            endTime = datetime.datetime.strptime(workday[2], '%I:%M %p').time()
            changeDate = datetime.datetime.strptime(workday[6], '%m/%d/%Y').date()
            if workday[5] == '':
                dept = 'Front End'
            else:
                dept = workday[5]

            if str(date) in events:
                check_change_date()
            else:
                add_event(cal_id, str(date), str(dept), str(startTime),
                    str(endTime), str(changeDate))

# I am typing while the

def main():
    """Get work schedules."""
    # # print("Python version", sys.version)
    # # print("Version info", sys.version_info)
    print('Username: ')
    username = pyautogui.prompt(text='Input username:',
                                title='Username',
                                default='Username')
    print('Password: ')
    password = pyautogui.password(text='Input password:',
                                  title='Password',
                                  default='Example_123',
                                  mask='*')
    global browser, work_schedule
    browser = webdriver.Chrome()  # TODO: expand to multiple Internet sources
    browser.get('https://www.costco.com/employee-website.html')
    login(username, password)
    work_schedule = []
    try:
        get_schedules()
    except Exception as e:
        print(e)
        browser.quit()

    print(work_schedule)
    browser.quit()


main()
