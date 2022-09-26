from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from anticaptchaofficial.imagecaptcha import *

# Import ---------------------------

def solvecaptcha():
    filename = 'captcha.png'

    solver = imagecaptcha()
    solver.set_verbose(1)
    solver.set_key("KEY")

    # Specify softId to earn 10% commission with your app.
    # Get your softId here: https://anti-captcha.com/clients/tools/devcenter
    solver.set_soft_id(0)

    captcha_text = solver.solve_and_return_solution(filename)
    if captcha_text != 0:
        print ("g-response: "+ captcha_text)
    else:
        print ("task finished with error "+solver.error_code)

    return captcha_text

# Solve Captcha ---------------------------------------


def getdriver():
    try:
        s = Service(ChromeDriverManager().install())
        options = webdriver.ChromeOptions()
        options.add_argument(
            'user-agent=Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.5005.63 Safari/537.36.')
        options.add_argument("--disable-blink-features=AutomationControlled")
        # options.add_argument('headless')
        driver = webdriver.Chrome(service=s, options=options)
        return driver
    except Exception as ex:
        print(f'Error {ex} in selenium settings')



