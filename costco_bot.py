""" Costco Schedule Retriever

    By Jayred Loyda https://github/jayred13
"""
from __future__ import print_function
from datetime import datetime
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from employee_portal_opener import PortalOpener
from online_schedule_opener import ScheduleOpener
from schedule_reader import ScheduleReader
from gcalendar_helper import GCalanderHelper


def main():
    driver = webdriver.Chrome("./chromedriver")  # TODO: Fix depreciation & expand to multiple Internet sources
    driver.get('https://www.costco.com/employee-website.html')
    driver.minimize_window()

    username = "INSERT_USERNAME_HERE"
    print(f'Username: {username}')
    password = "INSERT_PASSWORD_HERE"
    print(f'Password: {password}')

    ess = PortalOpener(driver, username, password)
    ess.to_employee_site()
    ess.login()

    ess = ScheduleOpener(driver, username, password)
    ess.nav_to_schedule_link()
    ess.schedule_login()

    cal_id = "INSERT_CALENDAR_ID_HERE (Ex: **********@group.calendar.google.com)"
    gcal = GCalanderHelper(cal_id)
    gcal.authenticate()
    events = gcal.upcoming_events(15) 
    getter = ScheduleReader(driver)

    for i in range(3): # TODO: Remove hard coded value of 3 weeks.
        week_end = getter.get_week(i)
        getter.read_schedule(week_end)
        df = getter.get_df()
        print(df)

        for index, row in df.iterrows():
            curr_event = gcal.event_exists(events, row['Date'])
            if curr_event: 
                gcal.delete_event(curr_event)
                gcal.add_event(row['Date'], "Costco", row['Start Time'], row['End Time'], row['Changed On'])
            else:
                gcal.add_event(row['Date'], "Costco", row['Start Time'], row['End Time'], row['Changed On'])

main()
