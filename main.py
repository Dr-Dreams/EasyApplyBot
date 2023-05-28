import os

import pyautogui
import yaml
from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.edge.options import Options as EdgeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from validate_email import validate_email
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager
from webdriver_manager.microsoft import EdgeChromiumDriverManager

from linkedineasyapply import LinkedinEasyApply


def init_browser(browser_name):
    driver = None

    if browser_name.lower() == 'chrome':
        options = ChromeOptions()
        options.add_argument('--disable-blink-features')
        options.add_argument('--no-sandbox')
        # options.add_argument('--start-maximized')
        options.add_argument('--disable-extensions')
        options.add_argument('--ignore-certificate-errors')
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_argument('--remote-debugging-port=9222')
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    elif browser_name.lower() == 'firefox':
        options = FirefoxOptions()
        options.add_argument('--disable-blink-features')
        options.add_argument('--no-remote')
        options.add_argument('--disable-extensions')
        options.set_preference("browser.tabs.remote.autostart", False)
        options.set_preference("browser.tabs.remote.autostart.1", False)
        options.set_preference("browser.tabs.remote.autostart.2", False)
        options.add_argument('--remote-debugging-port=9222')
        options.set_preference("devtools.jsonview.enabled", True)
        profile = webdriver.FirefoxProfile()
        profile.accept_untrusted_certs = True
        driver = webdriver.Firefox(service=Service(GeckoDriverManager().install()), options=options,
                                   firefox_profile=profile)

    elif browser_name.lower() == 'edge':
        options = EdgeOptions()
        options.add_argument('--disable-blink-features')
        options.add_argument('--disable-extensions')
        options.add_argument('--remote-debugging-port=9222')
        driver = webdriver.Edge(service=Service(EdgeChromiumDriverManager().install()), options=options,
                                capabilities={"acceptInsecureCerts": True})

    if driver:
        driver.get("https://www.google.com")
        screen_width, screen_height = pyautogui.size()
        screen_width = screen_width / 4
        screen_height = 1
        driver.set_window_position(screen_width, screen_height)
        # driver.set_window_position(0, 0)
        # driver.maximize_window()

    return driver


def validate_yaml():
    with open("config copy.yaml", 'r') as stream:
        try:
            parameters = yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            raise exc

    mandatory_params = ['email', 'password', 'disableAntiLock', 'remote', 'experienceLevel', 'jobTypes', 'date',
                        'positions', 'locations', 'distance', 'outputFileDirectory', 'checkboxes', 'universityGpa',
                        'languages', 'experience', 'personalInfo', 'eeo', 'uploads']

    for mandatory_param in mandatory_params:
        if mandatory_param not in parameters:
            raise Exception(mandatory_param + ' is not inside the yml file!')

    assert validate_email(parameters['email'])
    assert len(str(parameters['password'])) > 0

    assert isinstance(parameters['disableAntiLock'], bool)

    assert isinstance(parameters['remote'], bool)

    # assert len(parameters['experienceLevel']) > 0
    # experience_level = parameters.get('experienceLevel', [])
    # at_least_one_experience = False
    # for key in experience_level.keys():
    #     if experience_level[key]:
    #         at_least_one_experience = True
    # assert at_least_one_experience

    # assert len(parameters['jobTypes']) > 0
    # job_types = parameters.get('jobTypes', [])
    # at_least_one_job_type = False
    # for key in job_types.keys():
    #     if job_types[key]:
    #         at_least_one_job_type = True
    # assert at_least_one_job_type

    assert len(parameters['date']) > 0
    date = parameters.get('date', [])
    at_least_one_date = False
    for key in date.keys():
        if date[key]:
            at_least_one_date = True
    assert at_least_one_date

    approved_distances = {0, 5, 10, 25, 50, 100, 1000}
    assert parameters['distance'] in approved_distances

    assert len(parameters['positions']) > 0
    # assert len(parameters['locations']) > 0

    # assert len(parameters['uploads']) >= 1 and 'resume' in parameters['uploads']

    assert len(parameters['checkboxes']) > 0

    checkboxes = parameters.get('checkboxes', [])
    assert isinstance(checkboxes['driversLicence'], bool)
    assert isinstance(checkboxes['requireVisa'], bool)
    assert isinstance(checkboxes['legallyAuthorized'], bool)
    assert isinstance(checkboxes['urgentFill'], bool)
    assert isinstance(checkboxes['commute'], bool)
    assert isinstance(checkboxes['backgroundCheck'], bool)
    assert 'degreeCompleted' in checkboxes

    assert isinstance(parameters['universityGpa'], (int, float))

    languages = parameters.get('languages', [])
    language_types = {'none', 'conversational', 'professional', 'native or bilingual'}
    for language in languages:
        assert languages[language].lower() in language_types

    experience = parameters.get('experience', [])

    for tech in experience:
        assert isinstance(experience[tech], int)
    assert 'default' in experience

    assert len(parameters['personalInfo'])
    personal_info = parameters.get('personalInfo', [])
    for info in personal_info:
        assert personal_info[info] != ''

    assert len(parameters['eeo'])
    eeo = parameters.get('eeo', [])
    for survey_question in eeo:
        assert eeo[survey_question] != ''

    return parameters


def remove_csv_files():
    current_dir = os.getcwd()  # Get the current directory

    # Iterate over all files in the current directory
    for file in os.listdir(current_dir):
        if file.startswith("unprepared_"):
            continue
        elif file.endswith(".csv"):  # Check if the file is a CSV file
            file_path = os.path.join(current_dir, file)  # Get the full path of the file
            os.remove(file_path)  # Remove the file


if __name__ == '__main__':

    # removing all previous csv files
    remove_csv_files()

    # validating yaml file
    parameters = validate_yaml()

    # checking browser types
    browser_type = ""
    browser_level = parameters.get('Browser', [])

    if browser_level['chrome']:
        browser_type = 'chrome'
    elif browser_level['firefox']:
        browser_type = 'firefox'
    elif browser_level['edge']:
        browser_type = 'edge'
    else:
        print("Please Select your browser type")
        exit()

    # init browser
    browser = init_browser(browser_type)
    bot = LinkedinEasyApply(parameters, browser)
    bot.login()
    bot.security_check()
    bot.start_applying()
    os.system('cls' if os.name == 'nt' else 'clear')
    print(
        "..........................................Please Check your CSV files..........................................")
