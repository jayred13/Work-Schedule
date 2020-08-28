"""Help with browser commands."""
import pyautogui
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class browser_helper():
    """Helper Class."""

    def __init__(self, browser):
        """Initialize browser."""
        self.browser = browser

    def wait_for(self, wait_id, wait_type):
        """Wait until element is visible."""
        try:
            #  print('Waiting for ' + wait_id)
            wait = WebDriverWait(self.browser, 30)
            wait.until(EC.visibility_of_element_located((wait_type, wait_id)))
        except TimeoutError:
            print('Loading Timeout')
            self.browser.quit()

    def frame_switch(self, frame_id):
        """Switch frames to given name."""
        try:
            self.browser.switch_to.frame(frame_id)
            # print('@ ' + frame_id)
        except Exception:
            print('Frame switch has failed.')

    def login(self, user_id, username, pass_id, password):
        """Login."""
        self.wait_for(user_id, By.CSS_SELECTOR)
        user_elem = self.browser.find_element_by_css_selector(user_id)
        pass_elem = self.browser.find_element_by_css_selector(pass_id)

        try:
            user_elem.clear()
            pass_elem.clear()
        except Exception:
            pass

        if (username is not None) and (password is not None):
            user_elem.send_keys(username)
            pass_elem.send_keys(password)
            pass_elem.submit()

        try:
            user_elem = self.browser.find_element_by_css_selector(user_id)
            self.incorrect_login(user_id, pass_id)
        except Exception:
            pass

    def incorrect_login(self, user_id, pass_id):
        """Prompt user for credentials in case of failed login."""
        username = pyautogui.prompt(
            text='Incorrect Username/Password. Please enter Username:',
            title='Username',
            default='Username')
        password = pyautogui.password(
            text='Incorrect Username/Password. Please enter Username:',
            title='Password',
            default='Example_123',
            mask='*')
        self.login(user_id, username, pass_id, password)
