import argparse
import logging
import shlex

import crawler
import data
import utils


def initLogging():
    log = logging.getLogger()
    log.setLevel(0)

    logging.getLogger('selenium.webdriver.remote.remote_connection').setLevel(logging.INFO)

    format = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

    ch = logging.StreamHandler()
    ch.setFormatter(format)
    log.addHandler(ch)

    fh = logging.FileHandler("imhonet2kinopoisk.log", mode='w', encoding='UTF8')
    fh.setFormatter(format)
    log.addHandler(fh)

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

    args = parser.parse_args()

    initLogging()

    logging.info('Loading original data from "%s"...', args.imhonet_export)
    origin_rates = data.LoadFromHtml(args.imhonet_export, args.extra_links)
    logging.info('Loading compleate. Found %s entries', len(origin_rates))
  
    try:
        driver = None
        logging.info('Create driver...')
        driver = crawler.CreateDriver()

        logging.info('Login as "%s"...', args.user)
        crawler.Login(driver, args)
        logging.info('Login complete')

        for link, origin in origin_rates:
            if not link:
                logging.error('Link is not specified for %s', origin )
                continue
        
            logging.debug('Getting info for %s from "%s"...', origin, link)     
            curr = crawler.GetItemInfo(driver, link)

            nonmatches = []

            if utils.normalize_caseless(origin.title) != utils.normalize_caseless(curr.title):
                nonmatches.append('Titles')

            if origin.year != curr.year:
                nonmatches.append('Years')

            if nonmatches:
                logging.warning( '%s don\'t match "%s" != "%s"', ' and '.join(nonmatches), origin.snippet(), curr.snippet() )

    except Exception as e:
        logging.critical("Exception found", exc_info=e)
        if driver:
            utils.DumpHtml(driver)
        raise
    finally:
        if driver is not None:
            driver.close()

if __name__ == '__main__':
    main()
