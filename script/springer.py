import os
import time
import sys
import bibtexparser
from selenium import webdriver
from selenium.webdriver.firefox.options import Options

class Springer():
    @staticmethod
    def _get_reference(browser: webdriver, id: int) -> str | None:
        jsscript = """
    var ref = document.querySelector("#ref-CR" + arguments[0]);
    if (ref == null) {
        return '';
    }
    var content = ref.textContent.trim();
    return content;
"""
        result  = browser.execute_script(jsscript, str(id))
        if result == '':
            return None
        return result

    @staticmethod
    def get_references(browser: webdriver) -> list[str]:
        id = 1
        ret = []
        while True:
            ref = Springer._get_reference(browser, id)
            if ref is None:
                break
            ret.append(ref)
            id += 1
        return ret

if __name__ == "__main__":
    myoptions = Options()
    myoptions.add_argument("-headless") # Enable headless mode

    bibfile  = os.path.join("..", "dataset", "springer.bib")
    lib = bibtexparser.load(open(bibfile, 'r'))
    logfile = open("springer.log", 'w')
    reffile = open("springer.txt", 'w')

    for entry in lib.entries:
        if 'doi' not in entry:
            continue
        doi  = entry['doi']
        print(doi, file=sys.stderr)
        url = 'https://link.springer.com/article/' + doi
        references = []

        browser = webdriver.Firefox(options=myoptions)
        try:
            browser.get(url)
            references = Springer.get_references(browser)
        except:
            logfile.write(f"Error: {doi}\n")
        browser.quit()

        for ref in references:
            reffile.write(ref + "\n")
        if len(references) == 0:
            logfile.write(f"No reference: {doi}\n")
        reffile.flush()
        time.sleep(1)
        del references
        del browser

    logfile.close()
    reffile.close()
