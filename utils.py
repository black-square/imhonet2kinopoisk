from selenium.common.exceptions import NoSuchElementException, NoSuchFrameException

def DumpHtml(driver):
    with open("dump.html", "w", encoding='utf-8') as text_file:
        text_file.write(driver.execute_script("return document.documentElement.outerHTML"))

def OuterHTML(element):
    return element.get_attribute('outerHTML')

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
