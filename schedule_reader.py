from datetime import datetime
from helper_functions import *
from selenium.webdriver.common.by import By
import pandas as pd

class ScheduleReader:
    def __init__(self, driver):
        self.driver = driver
        self.helper = HelperFunctions(self.driver)
        self.df = pd.DataFrame()

    """Open/select dropdown for week selection"""
    def get_week(self, week_num):
        print('*** get_week ***')
        self.driver.switch_to.default_content()
        self.helper.wait_for('#contentAreaFrame', By.CSS_SELECTOR)
        self.helper.frame_switch('contentAreaFrame')
        self.helper.wait_for('isolatedWorkArea', By.ID)
        self.helper.frame_switch('isolatedWorkArea')

        self.helper.wait_for('button', By.TAG_NAME)
        weeks_posted = self.driver.find_elements(By.TAG_NAME, 'select')
        drop_elem = weeks_posted[-1]
        drop_elem.click()
        option = drop_elem.find_elements(By.TAG_NAME, 'option')

        if week_num >= len(option):
            driver.quit() #prevent out-of-bounds
        option[week_num].click()
        week_end = datetime.strptime(option[week_num].text, '%Y-%m-%d')
        try:
            buttons = self.driver.find_elements(By.TAG_NAME, 'button')
            buttons[-1].click()
        except:
            buttons = self.driver.find_elements(By.TAG_NAME, 'button')
            buttons[-1].click()
        return week_end

    """Get date info when schedule becomes visible"""
    def sched_ready(self, week_end):
        # print('*** sched_ready ***')
        date_id = '#rt_NS_ > tbody > tr:nth-child(1) > td > div:nth-child(2)' \
            ' > span:nth-child(3)'
        self.helper.wait_for(date_id, By.CSS_SELECTOR)
        try:
            date = self.driver.find_element_by_css_selector(date_id)
            sun_date = datetime.strptime(date.text, '%m/%d/%Y')
        except:
            date = self.driver.find_element_by_css_selector(date_id)
            sun_date = datetime.strptime(date.text, '%m/%d/%Y')

        return week_end == sun_date


    """ Finds correct html table element and creates clean pandas dataframe. """
    def read_schedule(self, week_end):
        if not self.sched_ready(week_end): #repeated calls untill table visible
            self.read_schedule(week_end)
        else:
            pd.set_option('display.max_columns', None)
            tables = pd.read_html( self.driver.page_source )
            df = tables[10]

            new_header = df.iloc[1] #grab the first row for the header
            df = df[2:-1] #take the data less the header row and exclue last row
            df.columns = new_header #set the header row as the df header

            df = df[df['Start Time'].notna()] # Filter days-off
            df = df.dropna(axis=1, how='all')

            df['Date'] = pd.to_datetime(df['Date'], format='%m/%d/%Y').dt.strftime('%Y-%m-%d') # Change datetime format and type
            df['Changed On'] = pd.to_datetime(df['Changed On'], format='%m/%d/%Y').dt.strftime('%Y-%m-%d')
            df['Start Time'] = pd.to_datetime(df['Start Time'], format='%I:%M %p').dt.strftime('%H:%M:%S')
            df['End Time'] = pd.to_datetime(df['End Time'], format='%I:%M %p').dt.strftime('%H:%M:%S')

            df = df.drop(columns=['Shift Hours'])
            df = df.reset_index(drop=True) 
            for i in range(len(df)):
                if i == len(df)-1:
                    break
                if df['Day'][i] == df['Day'][i+1]:
                    df['End Time'][i] = df['End Time'][i+1] # TODO: Fix Warning
                    df['Daily Hours'][i] = df['Daily Hours'][i+1]
            df = df.drop_duplicates( keep='first', subset='Day' )
            df = df.reset_index(drop=True)  
            self.df=df

    def get_df(self):
        return self.df