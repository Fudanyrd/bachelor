"""
DESCRIPTION
    Export reference list and cited by list of a given article.
"""
import os
import sys
import time
import bibtexparser
from seleniumbase import Driver

class ACM():
    @staticmethod
    def get_references(browser: Driver) -> list[str]: 
        with open('acm.js', 'r') as f:
            lib: str = f.read()
        script = lib + \
"""
return export_references();
"""
        return browser.execute_script(script).splitlines()

    @staticmethod
    def get_cited_by(browser: Driver) -> list[str]:
        with open('acm.js', 'r') as f:
            lib: str = f.read()
        script = lib + \
"""
return export_cited_by();
"""
        result = browser.execute_script(script)
        return [] if result is None else result.splitlines()


if __name__ == "__main__":
    browser = None# Driver(headless=False, uc = True)

    bibfile = os.path.join("..", "dataset", "acm.bib")
    bibfile = 'test.bib'
    lib = bibtexparser.load(open(bibfile, 'r', encoding = 'utf-8'))
    logfile = open("acm.log", 'w', encoding = 'utf-8')
    reffile = open("acm.txt", 'w', encoding = 'utf-8')

    for entry in lib.entries:
        if 'url' not in entry:
            continue
        url = entry['url']
        browser = Driver(headless=False, uc = True)
        refereces_success = False
        all_success = False
        try:
            browser.uc_open_with_reconnect(url, reconnect_time=10)
            references = ACM.get_references(browser)
            refereces_success = True 
            time.sleep(2)
            cited_by = ACM.get_cited_by(browser)
            all_success = True
        except Exception as e:
            print(e, file=sys.stderr)
            logfile.write(f"Error: {url}\n")
            logfile.flush()
        browser.quit()
        time.sleep(1)
        if refereces_success:
            for ref in references:
                reffile.write(ref + "\n")
            del references
        if all_success:
            for ref in cited_by:
                reffile.write(ref + "\n")
            del cited_by
        reffile.flush()
    reffile.close()
    logfile.close()
