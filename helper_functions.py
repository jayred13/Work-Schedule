from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class HelperFunctions:
    def __init__(self, driver):
        self.driver = driver


    """Wait until element is visible."""
    def wait_for(self, wait_id, wait_type):
        try:
            #  print('Waiting for ' + wait_id)
            wait = WebDriverWait(self.driver, 120)
            wait.until(EC.visibility_of_element_located((wait_type, wait_id)))
        except Exception:
            print('Loading Timeout')
            self.driver.quit()

    """Switch frames to given name."""
    def frame_switch(self, frame_id):
        try:
            self.driver.switch_to.frame(frame_id)
            # print('@ ' + frame_id)
        except Exception:
            print('Frame switch has failed.')