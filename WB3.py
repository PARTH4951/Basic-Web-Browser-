import sys
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtWebEngineWidgets import *
from PyQt5.QtGui import QIcon, QKeySequence

class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()

        # Initialize dark mode state
        self.dark_mode = False
        
        # Set window properties
        self.setWindowTitle('PyBrowser')
        self.setWindowIcon(QIcon('E:/Study/Sem 5/Python/Python code/WB1/icon.png'))  # Ensure icon.png exists in the specified directory

        # Initialize search history and bookmarks
        self.history = []
        self.bookmarks = []

        # Initialize private browsing state
        self.private_browsing = False

        # Initialize search engines and home pages
        self.search_engines = {
            'Google': 'https://www.google.com/search?q=',
            'Yahoo': 'https://search.yahoo.com/search?p=',
            'DuckDuckGo': 'https://duckduckgo.com/?q=',
            'Bing': 'https://www.bing.com/search?q=',
            'Brave': 'https://search.brave.com/search?q='
        }
        self.current_search_engine = 'Google'
        self.home_pages = {
            'Google': 'https://www.google.com',
            'Yahoo': 'https://www.yahoo.com',
            'DuckDuckGo': 'https://duckduckgo.com',
            'Bing': 'https://www.bing.com',
            'Brave': 'https://search.brave.com'
        }
        self.current_home_page = 'Google'
        self.load_home_page_setting()

        # Create tab widget
        self.tabs = QTabWidget()
        self.tabs.setTabsClosable(True)
        self.tabs.setMovable(True)
        self.tabs.tabCloseRequested.connect(self.close_tab)
        self.setCentralWidget(self.tabs)

        # Create toolbar
        toolbar = QToolBar()
        self.addToolBar(toolbar)

        # Add toolbar buttons
        self.add_toolbar_buttons(toolbar)

        # Add first tab
        self.add_tab()

        # Add shortcuts
        self.add_shortcuts()

        # Add tab context menu
        self.tabs.setContextMenuPolicy(Qt.CustomContextMenu)
        self.tabs.customContextMenuRequested.connect(self.show_tab_context_menu)

        # Add settings menu
        self.add_settings_menu()

        # Load bookmarks
        self.load_bookmarks()

    def add_toolbar_buttons(self, toolbar):
        try:
            # Add back button with custom icon
            back_btn = QAction(QIcon('E:/Study/Sem 5/Python/Python code/WB1/back.png'), 'Back', self)
            back_btn.triggered.connect(lambda: self.current_browser().back())
            toolbar.addAction(back_btn)

            # Add forward button with custom icon
            forward_btn = QAction(QIcon('E:/Study/Sem 5/Python/Python code/WB1/next.png'), 'Forward', self)
            forward_btn.triggered.connect(lambda: self.current_browser().forward())
            toolbar.addAction(forward_btn)

            # Add reload button with custom icon
            reload_btn = QAction(QIcon('E:/Study/Sem 5/Python/Python code/WB1/reload.png'), 'Reload', self)
            reload_btn.triggered.connect(lambda: self.current_browser().reload())
            toolbar.addAction(reload_btn)

            # Add home button with custom icon
            home_btn = QAction(QIcon('E:/Study/Sem 5/Python/Python code/WB1/home.png'), 'Home', self)
            home_btn.triggered.connect(self.navigate_home)
            toolbar.addAction(home_btn)

            # Add new tab button with custom icon
            add_tab_btn = QAction(QIcon('E:/Study/Sem 5/Python/Python code/WB1/newtab.png'), 'New Tab', self)
            add_tab_btn.triggered.connect(self.add_tab)
            toolbar.addAction(add_tab_btn)

            # Add search engine selection combo box
            self.search_engine_combo = QComboBox()
            self.search_engine_combo.addItems(self.search_engines.keys())
            self.search_engine_combo.currentTextChanged.connect(self.change_search_engine)
            toolbar.addWidget(self.search_engine_combo)

            # Add bookmark button with custom icon
            bookmark_btn = QAction(QIcon('E:/Study/Sem 5/Python/Python code/WB1/bookmark.png'), 'Bookmark', self)
            bookmark_btn.triggered.connect(self.add_bookmark)
            toolbar.addAction(bookmark_btn)

            # Add bookmarks menu
            self.bookmarks_menu = QMenu('Bookmarks', self)
            toolbar.addAction(self.bookmarks_menu.menuAction())

            # Add private browsing button with custom icon
            private_browsing_btn = QAction(QIcon('E:/Study/Sem 5/Python/Python code/WB1/private.png'), 'Private Browsing', self)
            private_browsing_btn.triggered.connect(self.toggle_private_browsing)
            toolbar.addAction(private_browsing_btn)

            # Add chatbot button with custom icon
            chatbot_btn = QAction(QIcon('E:/Study/Sem 5/Python/Python code/WB1/chatbot.png'), 'Chatbot', self)
            chatbot_btn.triggered.connect(self.open_chatbot_dialog)
            toolbar.addAction(chatbot_btn)

        except Exception as e:
            print(f"Error adding toolbar buttons: {e}")

    def add_shortcuts(self):
        QShortcut(QKeySequence('Shift+N'), self).activated.connect(self.add_tab)
        QShortcut(QKeySequence('Shift+W'), self).activated.connect(lambda: self.close_tab(self.tabs.currentIndex()))
        QShortcut(QKeySequence('Shift+R'), self).activated.connect(lambda: self.current_browser().reload())
        QShortcut(QKeySequence('Shift+B'), self).activated.connect(lambda: self.current_browser().back())
        QShortcut(QKeySequence('Shift+F'), self).activated.connect(lambda: self.current_browser().forward())

    def add_settings_menu(self):
        settings_menu = QMenu("Settings", self.menuBar())
        self.menuBar().addMenu(settings_menu)

        history_action = QAction('History', self)
        history_action.triggered.connect(self.show_history)
        settings_menu.addAction(history_action)

        dark_mode_action = QAction('Dark Mode', self)
        dark_mode_action.triggered.connect(self.toggle_dark_mode)
        settings_menu.addAction(dark_mode_action)

        settings_btn = QAction('Home Page Settings', self)
        settings_btn.triggered.connect(self.show_settings_dialog)
        settings_menu.addAction(settings_btn)

    def open_chatbot_dialog(self):
        self.chatbot_dialog = QDialog(self)
        self.chatbot_dialog.setWindowTitle("Chatbot")
        layout = QVBoxLayout()

        self.chatbox = QTextEdit()
        self.chatbox.setReadOnly(True)
        layout.addWidget(self.chatbox)

        self.user_input = QLineEdit()
        self.user_input.returnPressed.connect(self.process_user_input)
        layout.addWidget(self.user_input)

        self.chatbot_dialog.setLayout(layout)
        self.chatbot_dialog.exec_()

    def process_user_input(self):
        try:
            user_message = self.user_input.text()
            self.chatbox.append(f"You: {user_message}")
            self.user_input.clear()

            response = self.generate_chatbot_response(user_message)
            self.chatbox.append(f"Chatbot: {response}")
        except Exception as e:
            self.chatbox.append(f"Chatbot: Sorry, an error occurred: {e}")

    def generate_chatbot_response(self, message):
        try:
            if 'open' in message.lower():
                url = message.split('open')[-1].strip()
                if not url.startswith('http://') and not url.startswith('https://'):
                    url = self.search_engines[self.current_search_engine] + url
                self.current_browser().setUrl(QUrl(url))
                return f"Opening {url}."
            elif 'history' in message.lower():
                self.show_history()
                return "Showing history."
            elif 'home' in message.lower():
                self.navigate_home()
                return "Navigating to home page."
            elif 'bookmark' in message.lower():
                self.add_bookmark()
                return "Bookmark added."
            elif 'dark mode' in message.lower():
                self.toggle_dark_mode()
                return "Toggling dark mode."
            elif 'private' in message.lower():
                self.toggle_private_browsing()
                return "Toggling private browsing."
            else:
                return "Sorry, I didn't understand that command."
        except Exception as e:
            return f"Sorry, an error occurred: {e}"

    def toggle_private_browsing(self):
        try:
            self.private_browsing = not self.private_browsing
            if self.private_browsing:
                self.statusBar().showMessage("Private Browsing Mode On")
                self.apply_private_browsing_stylesheet()
            else:
                self.statusBar().showMessage("Private Browsing Mode Off")
                self.remove_private_browsing_stylesheet()
            self.update_private_tabs()
        except Exception as e:
            print(f"Error toggling private browsing: {e}")

    def apply_private_browsing_stylesheet(self):
        self.setStyleSheet("""
        QMainWindow { background-color: #d3d3d3; color: black; }
        QToolBar { background-color: #b0b0b0; }
        QTabWidget::pane { border: 1px solid #a0a0a0; }
        QTabBar::tab { background: #c0c0c0; color: black; border: 1px solid #a0a0a0; }
        QTabBar::tab:selected, QTabBar::tab:hover { background: #a0a0a0; }
        QLineEdit { background-color: #e0e0e0; color: black; border: 1px solid #c0c0c0; }
        """)
        for i in range(self.tabs.count()):
            browser = self.tabs.widget(i)
            browser.page().runJavaScript('document.documentElement.style.filter = "invert(0)";')

    def remove_private_browsing_stylesheet(self):
        self.setStyleSheet("")
        for i in range(self.tabs.count()):
            browser = self.tabs.widget(i)
            browser.page().runJavaScript('document.documentElement.style.filter = "";')

    def update_private_tabs(self):
        for i in range(self.tabs.count()):
            browser = self.tabs.widget(i)
            if isinstance(browser, QWebEngineView):
                browser.setProperty("private_browsing", self.private_browsing)

    def add_tab(self, url=None):
        try:
            browser = QWebEngineView()
            browser.setProperty("private_browsing", self.private_browsing)

            if url:
                browser.setUrl(QUrl(url))
            else:
                browser.setUrl(QUrl(self.home_pages[self.current_home_page]))

            index = self.tabs.addTab(browser, 'New Tab')
            self.tabs.setCurrentIndex(index)
            self.update_tab_title(browser)

            browser.titleChanged.connect(lambda: self.update_tab_title(browser))
            browser.urlChanged.connect(lambda url, browser=browser: self.update_url(url) if self.tabs.currentWidget() == browser else None)

            if self.dark_mode:
                browser.page().runJavaScript('document.documentElement.style.filter = "invert(1) hue-rotate(180deg)";')
        except Exception as e:
            print(f"Error adding tab: {e}")

    def update_tab_title(self, browser):
        try:
            index = self.tabs.indexOf(browser)
            title = browser.title()
            self.tabs.setTabText(index, title if title else 'Untitled')
        except Exception as e:
            print(f"Error updating tab title: {e}")

    def update_url(self, url):
        try:
            self.url_bar.setText(url.toString())
        except Exception as e:
            print(f"Error updating URL: {e}")

    def navigate_to_url(self):
        try:
            url = self.url_bar.text()
            if not url.startswith('http://') and not url.startswith('https://'):
                url = self.search_engines[self.current_search_engine] + url
            self.current_browser().setUrl(QUrl(url))
        except Exception as e:
            print(f"Error navigating to URL: {e}")

    def navigate_home(self):
        try:
            self.current_browser().setUrl(QUrl(self.home_pages[self.current_home_page]))
        except Exception as e:
            print(f"Error navigating home: {e}")

    def change_search_engine(self, engine_name):
        self.current_search_engine = engine_name

    def show_history(self):
        history_dialog = QDialog(self)
        history_dialog.setWindowTitle("History")
        layout = QVBoxLayout()

        history_list = QListWidget()
        history_list.addItems(self.history)
        layout.addWidget(history_list)

        clear_history_btn = QPushButton('Clear History')
        clear_history_btn.clicked.connect(self.clear_history)
        layout.addWidget(clear_history_btn)

        history_dialog.setLayout(layout)
        history_dialog.exec_()

    def clear_history(self):
        try:
            self.history = []
            self.save_history()
        except Exception as e:
            print(f"Error clearing history: {e}")

    def save_history(self):
        try:
            with open('history.txt', 'w') as file:
                for entry in self.history:
                    file.write(entry + '\n')
        except IOError as e:
            print(f"Error saving history: {e}")

    def load_history(self):
        try:
            with open('history.txt', 'r') as file:
                self.history = file.read().splitlines()
        except FileNotFoundError:
            self.history = []

    def show_settings_dialog(self):
        settings_dialog = QDialog(self)
        settings_dialog.setWindowTitle("Home Page Settings")
        layout = QVBoxLayout()

        self.home_page_combo = QComboBox()
        self.home_page_combo.addItems(self.home_pages.keys())
        self.home_page_combo.setCurrentText(self.current_home_page)
        layout.addWidget(self.home_page_combo)

        save_btn = QPushButton('Save')
        save_btn.clicked.connect(self.save_home_page_setting)
        layout.addWidget(save_btn)

        settings_dialog.setLayout(layout)
        settings_dialog.exec_()

    def save_home_page_setting(self):
        try:
            self.current_home_page = self.home_page_combo.currentText()
            self.save_home_page()
        except Exception as e:
            print(f"Error saving home page setting: {e}")

    def load_home_page_setting(self):
        try:
            with open('home_page.txt', 'r') as file:
                self.current_home_page = file.read().strip()
        except FileNotFoundError:
            self.current_home_page = 'Google'

    def save_home_page(self):
        try:
            with open('home_page.txt', 'w') as file:
                file.write(self.current_home_page)
        except IOError as e:
            print(f"Error saving home page setting: {e}")

    def add_bookmark(self):
        try:
            url = self.current_browser().url().toString()
            if url not in self.bookmarks:
                self.bookmarks.append(url)
                self.save_bookmarks()
                self.update_bookmarks_menu()
        except Exception as e:
            print(f"Error adding bookmark: {e}")

    def load_bookmarks(self):
        try:
            with open('bookmarks.txt', 'r') as file:
                self.bookmarks = file.read().splitlines()
            self.update_bookmarks_menu()
        except FileNotFoundError:
            self.bookmarks = []

    def save_bookmarks(self):
        try:
            with open('bookmarks.txt', 'w') as file:
                for bookmark in self.bookmarks:
                    file.write(bookmark + '\n')
        except IOError as e:
            print(f"Error saving bookmarks: {e}")

    def update_bookmarks_menu(self):
        try:
            self.bookmarks_menu.clear()
            for bookmark in self.bookmarks:
                action = QAction(bookmark, self)
                action.triggered.connect(lambda checked, url=bookmark: self.current_browser().setUrl(QUrl(url)))
                self.bookmarks_menu.addAction(action)
        except Exception as e:
            print(f"Error updating bookmarks menu: {e}")

    def close_tab(self, index):
        if self.tabs.count() > 1:
            self.tabs.removeTab(index)

    def current_browser(self):
        return self.tabs.currentWidget()

    def toggle_dark_mode(self):
        try:
            self.dark_mode = not self.dark_mode
            if self.dark_mode:
                self.setStyleSheet("QMainWindow { background-color: #2E2E2E; color: white; }")
                self.statusBar().showMessage("Dark Mode On")
                for i in range(self.tabs.count()):
                    browser = self.tabs.widget(i)
                    browser.page().runJavaScript('document.documentElement.style.filter = "invert(1) hue-rotate(180deg)";')
            else:
                self.setStyleSheet("")
                self.statusBar().showMessage("Dark Mode Off")
                for i in range(self.tabs.count()):
                    browser = self.tabs.widget(i)
                    browser.page().runJavaScript('document.documentElement.style.filter = "";')
        except Exception as e:
            print(f"Error toggling dark mode: {e}")

    def show_tab_context_menu(self, pos):
        menu = QMenu(self)
        new_tab_action = menu.addAction('New Tab')
        new_tab_action.triggered.connect(self.add_tab)
        close_tab_action = menu.addAction('Close Tab')
        close_tab_action.triggered.connect(lambda: self.close_tab(self.tabs.currentIndex()))
        menu.exec_(self.tabs.mapToGlobal(pos))

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.load_history()
    window.show()
    sys.exit(app.exec_())
