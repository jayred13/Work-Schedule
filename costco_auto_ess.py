"""Costco schedule retrival automation."""
from selenium import webdriver
from selenium.webdriver.common.by import By
from browser_helper import browser_helper
import datetime
import re


class CostcoBot():
    """Costco schedule class."""

    def __init__(self, min_win_res):
        """Initialize automation."""
        self.browser = webdriver.Chrome()
        self.min_win_res = min_win_res

    def open_employee_site(self):
        """Open employee_site in new browser."""
        print('*** employee_site ***')
        if self.min_win_res == 'Yes':
            self.browser.minimize_window()
        self.browser.get('https://www.costco.com/employee-website.html')

    def ess_login(self, username, password):
        """Navigate to login and send info."""
        portal_id = 'div.col-sm-6:nth-child(5) > a:nth-child(5)'
        self.browser.find_element_by_css_selector(portal_id).click()
        self.browser.close()  # Login opens new tab, close and switch
        self.browser.switch_to.window(self.browser.window_handles[0])
        if self.min_win_res == 'Yes':
            self.browser.minimize_window()

        print('*** ess_login ***')
        helper = browser_helper(self.browser)
        helper.login('#username', username, '#password', password)

    def open(self, link):
        """Open online schedules in portal."""
        print('*** nav_to ***')
        self.browser.switch_to.default_content()
        helper = browser_helper(self.browser)
        helper.wait_for('#bc0', By.CSS_SELECTOR)
        helper.frame_switch('contentAreaFrame')
        helper.frame_switch('Overview')

        def online_schedules(self):
            helper.wait_for('Online Schedule', By.PARTIAL_LINK_TEXT)
            self.browser.find_element_by_partial_link_text(
                'Online Schedule').click()

        def pay_stubs(self):
            helper.wait_for('Pay Stubs', By.PARTIAL_LINK_TEXT)
            self.browser.find_element_by_partial_link_text('Pay Stubs').click()

        def job_bank(self):
            helper.wait_for('Employee Job Bank', By.PARTIAL_LINK_TEXT)
            self.browser.find_element_by_partial_link_text(
                'Employee Job Bank').click()

        def benefits(self):
            helper.wait_for('Benefits', By.PARTIAL_LINK_TEXT)
            self.browser.find_element_by_partial_link_text('Benefits').click()

        switcher = {
            'online_schedules': online_schedules,
            'pay_stubs': pay_stubs,
            'job_bank': job_bank,
            'benefits': benefits
        }
        switcher[link](self)

    def schedule_login(self, username, password):
        """Login to online schedules."""
        print('*** schedule_login ***')
        self.browser.switch_to.default_content()
        helper = browser_helper(self.browser)

        helper.wait_for('#contentAreaFrame', By.CSS_SELECTOR)
        helper.frame_switch('contentAreaFrame')
        helper.wait_for('isolatedWorkArea', By.ID)
        helper.frame_switch('isolatedWorkArea')

        helper.login('#CAMusername', username, '#CAMpassword', password)

    def get_week(self, week_num):
        """Collect online schedules for given week."""
        print('*** get_week ***')
        self.browser.switch_to.default_content()
        helper = browser_helper(self.browser)
        helper.wait_for('#contentAreaFrame', By.CSS_SELECTOR)
        helper.frame_switch('contentAreaFrame')
        helper.wait_for('isolatedWorkArea', By.ID)
        helper.frame_switch('isolatedWorkArea')

        helper.wait_for('button', By.TAG_NAME)
        weeks_posted = self.browser.find_elements_by_tag_name('select')
        drop_elem = weeks_posted[-1]
        drop_elem.click()
        options = drop_elem.find_elements_by_tag_name('option')

        if week_num >= len(options):
            return None
        else:
            options[week_num].click()
            week_end = datetime.datetime.strptime(
                options[week_num].text, '%Y-%m-%d')

            buttons = self.browser.find_elements_by_tag_name('button')
            buttons[-1].click()
            return week_end

    def sched_ready(self, week_end):
        """Check if schedule ready for scraping."""
        # print('*** sched_ready ***')
        try:
            date_id = '#rt_NS_ > tbody > tr:nth-child(1) > td > div:nth-child(2)' \
                ' > span:nth-child(3)'
            helper = browser_helper(self.browser)
            helper.wait_for(date_id, By.CSS_SELECTOR)
            date = self.browser.find_element_by_css_selector(date_id)
            sun_date = datetime.datetime.strptime(date.text, '%m/%d/%Y')
            return (week_end == sun_date)
        except Exception:
            print('\n*** Stale Element ***')
            self.sched_ready(week_end)

    def read_schedule(self, week_end):
        """Scrape schedule."""
        #print('*** read_schedule ***')
        if not self.sched_ready(week_end):
            print('.', end='')
            self.read_schedule(week_end)
        elif self.sched_ready(week_end):
            print('Here')
            table_id = '#rt_NS_ > tbody > tr:nth-child(2) > td > div > table >'\
                ' tbody > tr > td > table > tbody > tr:nth-child(2) > td >'\
                ' table > tbody'
            table_elem = self.browser.find_element_by_css_selector(table_id)

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
            print('costcobot', workdays)
            return workdays
        else:
            print('WTF?')
        #return workdays

    def kill(self):
        """End automation."""
        self.browser.quit()
