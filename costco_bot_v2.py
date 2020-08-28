from costco_auto_ess import CostcoBot
from google_cal import google_cal
import pyautogui
import threading
import datetime
import time

class Prompter():
    """Prompt class."""

    def prompt_cal():
        """Prompt Google calendar."""
        response = pyautogui.confirm(
            text='Would you like application to add to Google Calander?',
            title='Google Calendar?',
            buttons=['Yes', 'No'])

        if response == 'Yes':
            work_cal_id = pyautogui.prompt(
                text='Please enter Google calanderId: ',
                title='calanderId',
                default='')
            g_cal = google_cal()
            x = threading.Thread(target=g_cal.build(), args=())
            x.start()
            return work_cal_id, g_cal
        else:
            return None, None

    def prompt_min_win():
        """Prompt application background prefence."""
        return pyautogui.confirm(
            text='Would you like application to run in the background?',
            title='Max or Min',
            buttons=['Yes', 'No'])

    def prompt_creds():
        """Prompt user for credentials in case of failed login."""
        username = pyautogui.prompt(
            text='Please enter Username:',
            title='Username',
            default='')
        if username is None:
            quit()
        password = pyautogui.password(
            text='Incorrect Username/Password. Please enter Username:',
            title='Password',
            default='',
            mask='*')
        if password is None:
            quit()

        return username, password

def workdays_to_events(workdays, week):
    g_cal.week_events(work_cal_id, week)
    events = g_cal.get_event_dates()

    for workday in workdays:
        date = datetime.datetime.strptime(workday[0], '%m/%d/%Y').date()
        startTime = datetime.datetime.strptime(workday[1], '%I:%M %p').time()
        endTime = datetime.datetime.strptime(workday[2], '%I:%M %p').time()
        changeDate = datetime.datetime.strptime(workday[6], '%m/%d/%Y').date()
        if workday[5] == '':
            dept = 'Front End'
        else:
            dept = workday[5]

        if str(date) in events:
            print('Nah Brah!')
        else:
            g_cal.add_event(work_cal_id,
                            str(date),
                            str(dept),
                            str(startTime),
                            str(endTime),
                            str(changeDate))


def automation():
    """Automation for Costco ESS."""
    costcobot = CostcoBot(Prompter.prompt_min_win())
    username, password = Prompter.prompt_creds()
    costcobot.open_employee_site()
    costcobot.ess_login(username, password)
    costcobot.open('online_schedules')
    costcobot.schedule_login(username, password)

    i = 0
    while i < 5:
        week = costcobot.get_week(i)
        print('week', week)
        if week is None: break
        else:
            workdays = costcobot.read_schedule(week)
            print('test.py', workdays)
            if workdays is not None:
                i += 1
        #schedule.append(workdays)
        # if work_cal_id is not None:
        #     workdays_to_events(workdays, week)

    #costcobot.kill()


def main():
    """Run main."""
    global g_cal, work_cal_id, schedule
    schedule = []

    work_cal_id, g_cal = Prompter.prompt_cal()
    automation()


main()
