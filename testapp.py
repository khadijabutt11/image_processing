import unittest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

class TestForgeryDetection(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Set up Chrome options for headless mode
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--window-size=1920x1080')

        # Initialize WebDriver with Chrome
        cls.driver = webdriver.Chrome(options=chrome_options)
        cls.driver.implicitly_wait(10)

    def test_forgery_detection_page(self):
        # Test if the forgery detection page is accessible
        self.driver.get("http://ec2-34-207-183-212.compute-1.amazonaws.com/forgery_detection")
        self.assertIn("Forgery Detection", self.driver.title)

    def test_forgery_detection_process(self):
        # Test the forgery detection process with a sample image (replace with actual image path)
        self.driver.get("http://ec2-34-207-183-212.compute-1.amazonaws.com/forgery_detection")

        # Upload a sample image
        upload_input = self.driver.find_element_by_name("file")
        upload_input.send_keys("/path/to/sample/image.jpg")

        # Submit the form
        submit_button = self.driver.find_element_by_name("submit_button")
        submit_button.click()

        # Check for success message
        success_message = self.driver.find_element_by_class_name("alert-success").text
        self.assertIn("Image uploaded and processed successfully!", success_message)

    @classmethod
    def tearDownClass(cls):
        # Close the browser window after all tests are done
        cls.driver.quit()

class TestUserAuthentication(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Set up Chrome options for headless mode
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--window-size=1920x1080')

        # Initialize WebDriver with Chrome
        cls.driver = webdriver.Chrome(options=chrome_options)
        cls.driver.implicitly_wait(10)

    def test_login_successful(self):
        # Test if the login process is successful with valid credentials
        self.driver.get("http://ec2-34-207-183-212.compute-1.amazonaws.com/login")

        # Enter valid username and password
        username_input = self.driver.find_element_by_name("username")
        password_input = self.driver.find_element_by_name("password")
        login_button = self.driver.find_element_by_name("login_button")

        username_input.send_keys("valid_username")
        password_input.send_keys("valid_password")
        login_button.click()

        # Check for success message
        success_message = self.driver.find_element_by_class_name("alert-success").text
        self.assertIn("Login successful!", success_message)

    def test_login_invalid_credentials(self):
        # Test if the login process fails with invalid credentials
        self.driver.get("http://ec2-34-207-183-212.compute-1.amazonaws.com/login")

        # Enter invalid username and password
        username_input = self.driver.find_element_by_name("username")
        password_input = self.driver.find_element_by_name("password")
        login_button = self.driver.find_element_by_name("login_button")

        username_input.send_keys("invalid_username")
        password_input.send_keys("invalid_password")
        login_button.click()

        # Check for error message
        error_message = self.driver.find_element_by_class_name("alert-error").text
        self.assertIn("Invalid username or password", error_message)

    @classmethod
    def tearDownClass(cls):
        # Close the browser window after all tests are done
        cls.driver.quit()

if __name__ == '__main__':
    unittest.main()
