import json
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import requests
import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget, QLineEdit, QPushButton, QMessageBox, QListWidget, QListWidgetItem

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Haber Başlığı Oluşturucu")
        self.setGeometry(100, 100, 400, 200)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.layout = QVBoxLayout()
        self.central_widget.setLayout(self.layout)

        self.label = QLabel("Haber başlıkları için bir anahtar kelime girin:")
        self.layout.addWidget(self.label)

        self.entry = QLineEdit()
        self.layout.addWidget(self.entry)

        self.email_label = QLabel("E-posta adresinizi girin:")
        self.layout.addWidget(self.email_label)

        self.email_entry = QLineEdit()
        self.layout.addWidget(self.email_entry)

        self.button = QPushButton("Haber Başlıklarını Göster ve E-posta Gönder", self)
        self.button.clicked.connect(self.show_news)
        self.button.setStyleSheet("background-color: red; color: white;")  # Butonun rengini ayarla
        self.layout.addWidget(self.button)

        self.news_list = QListWidget()
        self.layout.addWidget(self.news_list)




    def get_api_key(self):
        with open('config.json') as config_file:
            config = json.load(config_file)
            return config['api_key']

    def fetch_news(self, query):
        api_key = self.get_api_key()
        url = f'https://newsapi.org/v2/everything?q={query}&apiKey={api_key}'

        try:
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()

            news_titles = [article['title'] for article in data['articles']]
            return news_titles

        except requests.exceptions.RequestException as e:
            print('Hata:', e)
            return []

    def send_email(self, subject, body, to_email):
        with open('config.json') as config_file:
            config = json.load(config_file)
            gmail_user = config['email_settings']['gmail_user']
            gmail_password = config['email_settings']['gmail_password']

        msg = MIMEMultipart()
        msg['From'] = gmail_user
        msg['To'] = to_email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))

        try:
            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls()
            server.login(gmail_user, gmail_password)
            text = msg.as_string()
            server.sendmail(gmail_user, to_email, text)
            print('E-posta başarıyla gönderildi!')
        except Exception as e:
            print('E-posta gönderme hatası:', e)
        finally:
            server.quit()

    def show_news(self):
        news_query = self.entry.text()
        news_titles = self.fetch_news(news_query)

        if news_titles:
            self.news_list.clear()
            for title in news_titles:
                item = QListWidgetItem(title)
                self.news_list.addItem(item)

            subject = f'{news_query.capitalize()} İle İlgili Haber Başlıkları'
            body = f'İşte {news_query} ile ilgili son haber başlıkları:\n\n{", ".join(news_titles)}'
            to_email = self.email_entry.text()
            self.send_email(subject, body, to_email)
            QMessageBox.information(self, "Bilgi", "E-posta başarıyla gönderildi!")
        else:
            QMessageBox.critical(self, "Hata", "Haber başlıkları alınamadı.")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
