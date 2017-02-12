import sys

import requests
from bs4 import BeautifulSoup

from PyQt5.QtWidgets import QApplication, QGridLayout, QLineEdit, QWidget
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtCore import QUrl

class UrlInput(QLineEdit):
    def __init__(self, browser):
        super(UrlInput, self).__init__()
        self.browser = browser
        # add event listener on "enter" pressed
        self.returnPressed.connect(self._return_pressed)

    def _return_pressed(self):
        url = QUrl(self.text())
        # load url into browser frame
        browser.load(url)




url = 'http://www.saltybet.com/authenticate?signin=1'

if __name__ == "__main__":
    app = QApplication(sys.argv)

    grid = QGridLayout()
    brower = QWebEngineView()

    url_input = UrlInput(browser)
    grid.addWidget(url_input, 1, 0)
    grid.addWidget(browser, 2, 0)
    
    main_frame = QWidget()
    main_frame.setLayout(grid)
    main_frame.show()

    # close app when user closes window
    sys.exit(app.exec_())

    


