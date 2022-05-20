import time
from helper_functions import *
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

class ScheduleOpener:
	def __init__(self, driver, username, password):
		self.driver = driver
		self.username = username
		self.password = password
		self.helper = HelperFunctions(self.driver)

	"""Open online schedules in portal"""
	def nav_to_schedule_link(self):
		print('*** nav_to_schedule_link ***')
		self.driver.switch_to.default_content()
		self.helper.wait_for('#bc0', By.CSS_SELECTOR)
		self.helper.frame_switch('contentAreaFrame')
		self.helper.frame_switch('Overview')

		self.helper.wait_for('Online Schedule', By.PARTIAL_LINK_TEXT)
		sched_elem = self.driver.find_element_by_partial_link_text('Online Schedule')
		sched_elem.click()

	"""Input Credentials (again :/)."""
	def schedule_login(self):
		print('*** schedule_login ***')
		self.driver.switch_to.default_content()
		self.helper.wait_for('#contentAreaFrame', By.CSS_SELECTOR)
		self.helper.frame_switch('contentAreaFrame')
		self.helper.wait_for('isolatedWorkArea', By.ID)
		self.helper.frame_switch('isolatedWorkArea')

		self.helper.wait_for('#CAMUsername', By.CSS_SELECTOR)
		user_elem = self.driver.find_element_by_css_selector('#CAMUsername')
		user_elem.send_keys(self.username)

		time.sleep(1)
		pass_elem = self.driver.find_element_by_css_selector('#CAMPassword')
		pass_elem.send_keys(self.password)
		pass_elem.submit()

