import argparse
import shlex
from enum import Enum, unique
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchFrameException
from selenium.common.exceptions import NoSuchElementException  
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
      
DELAY = 20

def DumpHtml(driver):
    with open("dump.html", "w", encoding='utf-8') as text_file:
        text_file.write(driver.execute_script("return document.documentElement.outerHTML"))

def OuterHTML(element):
    return loginMenu.get_attribute('outerHTML')

class presence_of_frame_and_element(object):
    def __init__(self, frame_locator, elem_locator):
        self.frame_locator = frame_locator
        self.elem_locator = elem_locator

    def __call__(self, driver):
        try:
            if self.frame_locator:
                driver.switch_to.frame(driver.find_element(*self.frame_locator))
            else:
                driver.switch_to.default_content()
            return driver.find_element(*self.elem_locator)
        except NoSuchFrameException:
            return False

def wait_page_to_load(driver):
    state = driver.execute_script('return document.readyState') 
    return state == 'complete'

def IfExists( fnc, *args ):
    try:
        return fnc(*args)
    except NoSuchElementException:
        return None

# Abstract struct class       
class Struct:
    def __init__ (self, *argv, **argd):
        if len(argd):
            # Update by dictionary
            self.__dict__.update (argd)
        else:
            # Update by position
            attrs = filter (lambda x: x[0:2] != "__", dir(self))
            for n in range(len(argv)):
                setattr(self, attrs[n], argv[n])

def CreateDriver():   
    #mobile_emulation = { "deviceName": "Nexus 6" }

    mobile_emulation = {
        "deviceMetrics": { 
            "width": 360, "height": 640, "pixelRatio": 3.0, 
            #Workaround for:
            #   https://bugs.chromium.org/p/chromedriver/issues/detail?id=2172
            #   https://bugs.chromium.org/p/chromedriver/issues/detail?id=2103 
            "touch": False 
        },
        "userAgent": "Mozilla/5.0 (Linux; Android 4.2.1; en-us; Nexus 5 Build/JOP40D) AppleWebKit/535.19 (KHTML, like Gecko) Chrome/18.0.1025.166 Mobile Safari/535.19" 
    }
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_experimental_option("mobileEmulation", mobile_emulation)
 
    capa = DesiredCapabilities.CHROME
    capa["pageLoadStrategy"] = "none"

    service_args = []
    #service_args.extend(["--verbose", "--log-path=chromedriver.log"])

    return webdriver.Chrome("/usr/local/bin/chromedriver", 
        chrome_options=chrome_options, 
        desired_capabilities=capa, 
        service_args=service_args
    )

def Login(driver, args):
    driver.get("https://www.kinopoisk.ru")

    WebDriverWait(driver, DELAY).until( wait_page_to_load )

    loginMenu = WebDriverWait(driver, DELAY).until(
        EC.element_to_be_clickable((By.CLASS_NAME,'header__log-in'))
    )

    loginMenu.click()

    loginInput = WebDriverWait(driver, DELAY).until(presence_of_frame_and_element(
        (By.NAME,'kp2-authapi-iframe'),
        (By.NAME, 'login')
    ))

    loginInput.clear()
    loginInput.send_keys(args.user)

    passInput = driver.find_element_by_name('password')
    passInput.clear()
    passInput.send_keys(args.password)

    submit = WebDriverWait(driver, DELAY).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR,'button.auth__signin'))
    )

    submit.click()
    driver.switch_to.default_content()

    WebDriverWait(driver, DELAY).until(
        EC.element_to_be_clickable((By.CLASS_NAME,'header__auth-status'))
    )


@unique
class Rating(Enum):
    WATCHED = -1
    R1 = 1
    R2 = 2
    R3 = 3
    R4 = 4
    R5 = 5
    R6 = 6
    R7 = 7
    R8 = 8
    R9 = 9
    R10 = 10

class ItemInfo(Struct):
    title = None
    year = None
    rating = None
    folders = None

def GetItemInfo(driver, url):
    driver.get(url)

    title = WebDriverWait(driver, DELAY).until(
        EC.element_to_be_clickable((By.CLASS_NAME,'movie-header__title'))
    )

    res = ItemInfo()

    res.title = title.text
    res.year = driver.find_element_by_class_name('movie-header__years').text

    rating = IfExists(driver.find_element_by_css_selector, '.user-rating__rating')
    watched = IfExists(driver.find_element_by_css_selector, '.user-rating__icon-eye')

    if watched:
        res.rating = Rating.WATCHED
    elif rating:
        res.rating  = Rating(int(rating.text))

    folders = IfExists(driver.find_element_by_css_selector, '.folder-button_filled')

    if folders:
        driver.find_element_by_class_name('movie-header__folder').click()
        WebDriverWait(driver, DELAY).until(
            EC.element_to_be_clickable((By.CLASS_NAME, 'folders-menu__section'))
        )

        folderItems = driver.find_elements_by_class_name('folders-menu__section')

        res.folders = []

        for idx, item in enumerate(folderItems):
            if IfExists(item.find_element_by_css_selector, '.folders-menu__icon-folder_filled'):
                res.folders.append(idx)

    return res

DESCRIPTION = '''\
Imhonet to Kinopoisk
'''

EPILOG = '''\

Additional info:
 - Arguments can be stored in a text file and the name of this file can be 
   passes as an argument with prefix '@', e.g.:

        taf.py @base_args.conf @my_args.conf --osd Log

   The file allows breaking arguments on multiple lines and supports 
   comments starting with '#'
'''

def main():
    def sh_split(arg_line):
        for arg in shlex.split(arg_line, comments=True):
            yield arg

    parser = argparse.ArgumentParser( fromfile_prefix_chars='@', description=DESCRIPTION, epilog=EPILOG, formatter_class=argparse.RawDescriptionHelpFormatter )
    parser.convert_arg_line_to_args = sh_split

    parser.add_argument( '-u', '--user', metavar='NAME', required=True,  help="Username on Kinopoisk" )
    parser.add_argument( '-p', '--password', metavar='PASS', required=True,  help="Password on Kinopoisk" )

    args = parser.parse_args()

    try:
        driver = None
        driver = CreateDriver()
        Login(driver, args)

        links = [
            "http://www.kinopoisk.ru/film/45275/",
            "http://www.kinopoisk.ru/film/43911/",
            "http://www.kinopoisk.ru/film/489752/",
            "http://www.kinopoisk.ru/film/40783/"
        ]
        
        for l in links:
            print( vars(GetItemInfo(driver, l)) )

    except Exception as e:
        print(e)
        if driver:
            DumpHtml(driver)
        raise
    finally:
        if driver is not None:
            driver.close()

if __name__ == '__main__':
    main()