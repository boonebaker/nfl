import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTextEdit
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtCore import QTimer, Qt, QUrl
import requests

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Streaming Video App with Sidebar and Ticker")
        self.showFullScreen()

        # Layouts
        main_layout = QVBoxLayout()
        top_layout = QHBoxLayout()

        # Embedded browser
        self.browser = QWebEngineView()
        self.browser.load(QUrl("https://www.mlb.com/"))
        top_layout.addWidget(self.browser, stretch=3)

        # Sidebar
        self.sidebar = QTextEdit()
        self.sidebar.setReadOnly(True)
        top_layout.addWidget(self.sidebar, stretch=1)

        main_layout.addLayout(top_layout)

        # Ticker
        self.ticker_label = QLabel("Loading sports scores...")
        self.ticker_label.setStyleSheet("background-color: black; color: white; font-size: 18px;")
        self.ticker_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        main_layout.addWidget(self.ticker_label)

        self.setLayout(main_layout)

        # Timers
        self.sidebar_timer = QTimer()
        self.sidebar_timer.timeout.connect(self.update_sidebar)
        self.sidebar_timer.start(30000)

        self.ticker_timer = QTimer()
        self.ticker_timer.timeout.connect(self.update_ticker)
        self.ticker_timer.start(15000)

        self.update_sidebar()
        self.update_ticker()

    def update_sidebar(self):
        try:
            response = requests.get("https://jsonplaceholder.typicode.com/posts/1")
            data = response.json()
            content = f"Title: {data['title']}\n\n{data['body']}"
        except Exception as e:
            content = f"Failed to load sidebar data: {e}"
        self.sidebar.setText(content)

    def update_ticker(self):
        try:
            response = requests.get("https://www.thesportsdb.com/api/v1/json/1/eventspastleague.php?id=4328")
            data = response.json()
            events = data.get("events", [])
            scores = [f"{e['strEvent']} ({e['intHomeScore']} - {e['intAwayScore']})" for e in events[:5]]
            ticker_text = " | ".join(scores)
        except Exception as e:
            ticker_text = f"Failed to load sports scores: {e}"
        self.ticker_label.setText(ticker_text)

# Run the app
app = QApplication(sys.argv)
window = MainWindow()
window.show()
sys.exit(app.exec_())
