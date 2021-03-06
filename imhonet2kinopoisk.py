import argparse
import logging
import shlex

import crawler
import data
import utils

from pathlib import Path

def InitLogging():
    log = logging.getLogger()
    log.setLevel(0)

    logging.getLogger('selenium.webdriver.remote.remote_connection').setLevel(logging.INFO)

    format = logging.Formatter("%(asctime)s %(levelname)8s: %(message)s")

    ch = logging.StreamHandler()
    ch.setFormatter(format)
    log.addHandler(ch)

    fh = logging.FileHandler("imhonet2kinopoisk.log", mode='w', encoding='UTF8')
    fh.setFormatter(format)
    log.addHandler(fh)

def ProcessPageImpl(driver, link, origin):
    if not link:
        logging.error('Link is not specified for %s', origin )
        return

    curr = crawler.GetItemInfo(driver, link)

    nonmatches = []

    if utils.normalize_caseless(origin.title) != utils.normalize_caseless(curr.title):
        nonmatches.append('Titles')

    if origin.year != curr.year:
        nonmatches.append('Years')

    if nonmatches:
        logging.warning( '%s don\'t match "%s" != "%s"', ' and '.join(nonmatches), origin.snippet(), curr.snippet() )

    if origin.rating != curr.rating:
        logging.info('Rating for %s is changing to %s...', curr, origin.rating)
        crawler.ChangeRating( driver, origin.rating )

    if origin.folders != curr.folders:
        logging.info('Folders for %s is changing to %s...', curr, origin.folders)
        crawler.ChangeFolders( driver, origin.folders )

def ProcessPage(driver, link, origin):
    try:
        ProcessPageImpl(driver, link, origin)
    except Exception as e:
        ProcessException(driver, e)

def ProcessException(driver, e):
    logging.critical("Exception found: {}".format(str(e)), exc_info=e)

    ProcessException.counter += 1  

    if driver:
        utils.Pause(driver)
        driver.save_screenshot('dump_{}.png'.format(ProcessException.counter))
        utils.DumpHtml(driver, 'dump_{}.html'.format(ProcessException.counter))
        logging.info('Dumps are stored under index {}'.format(ProcessException.counter))
        
ProcessException.counter = 0

def DeleteDumpFiles():
    for p in Path(".").glob("dump_*.*"):
        p.unlink()

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

    parser.add_argument( 'imhonet_export', metavar='HTML_FILE',  help="HTML file obtained from imhonet.ru" )
    parser.add_argument( '-u', '--user', metavar='NAME', required=True,  help="Username on Kinopoisk" )
    parser.add_argument( '-p', '--password', metavar='PASS', required=True,  help="Password on Kinopoisk" )
    parser.add_argument( '-l', '--extra_links', metavar='JSON_DICT',  help="Additional dictionary to find missed links to kinopoisk" )
    parser.add_argument( '-s', '--stop_on_exception', action='store_true',  help="Stot script execution on exception" )
    parser.add_argument( '-i', '--start_from_idx', metavar='INDEX', type=int, default=1, help="Start export from entity %(metavar)s" )

    args = parser.parse_args()

    InitLogging()
    DeleteDumpFiles()

    logging.info('Loading original data from "%s"...', args.imhonet_export)
    origin_rates = data.LoadFromHtml(args.imhonet_export, args.extra_links)
    logging.info('Loading compleate. Found %s entries', len(origin_rates))
  
    try:
        driver = None
        logging.info('Create driver...')
        driver = crawler.CreateDriver(args)

        logging.info('Login as "%s"...', args.user)
        crawler.Login(driver, args)
        logging.info('Login complete')

        for idx, (link, origin) in enumerate(origin_rates[args.start_from_idx - 1:], start = args.start_from_idx):
            logging.debug('Getting info for #%s %s from "%s"...', idx, origin, link)   
            ProcessPage(driver, link, origin)

        logging.info('All entries has been processe. %s exceptions have been found', ProcessException.counter)   

    except Exception as e:
        ProcessException(driver, e)   
        raise
    finally:
        if driver is not None:
            driver.close()

if __name__ == '__main__':
    main()
