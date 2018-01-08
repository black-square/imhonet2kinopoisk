import argparse
import shlex

import crawler
import data
import utils

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

    origin_rates = data.LoadFromHtml(args.imhonet_export, args.extra_links)

    print(origin_rates)

    try:
        driver = None
        driver = crawler.CreateDriver()
        crawler.Login(driver, args)

        links = [
            "http://www.kinopoisk.ru/film/45275/",
            "http://www.kinopoisk.ru/film/43911/",
            "http://www.kinopoisk.ru/film/489752/",
            "http://www.kinopoisk.ru/film/40783/"
        ]
        
        for l in links:
            print( vars(crawler.GetItemInfo(driver, l)) )
    except Exception as e:
        print(e)
        if driver:
            utils.DumpHtml(driver)
        raise
    finally:
        if driver is not None:
            driver.close()

if __name__ == '__main__':
    main()
