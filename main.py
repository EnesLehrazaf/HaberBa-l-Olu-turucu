import json
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import tkinter as tk
from tkinter import messagebox
import requests

def get_api_key():
    # config.json dosyasını oku
    with open('config.json') as config_file:
        config = json.load(config_file)
        return config['api_key']

def fetch_news(query):
    api_key = get_api_key()
    url = f'https://newsapi.org/v2/everything?q={query}&apiKey={api_key}'

    try:
        response = requests.get(url)
        response.raise_for_status()  # Hata durumlarını kontrol et
        data = response.json()

        news_titles = [article['title'] for article in data['articles']]
        return '\n'.join(news_titles)

    except requests.exceptions.RequestException as e:
        print('Hata:', e)
        return None

def send_email(subject, body, to_email):
    # Gmail hesap bilgilerini al
    with open('config.json') as config_file:
        config = json.load(config_file)
        gmail_user = config['email_settings']['gmail_user']
        gmail_password = config['email_settings']['gmail_password']

    # E-posta başlığını ve içeriğini oluştur
    msg = MIMEMultipart()
    msg['From'] = gmail_user
    msg['To'] = to_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    # SMTP sunucusuna bağlan ve e-postayı gönder
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

def show_news():
    news_query = entry.get()
    news_title = fetch_news(news_query)

    if news_title:
        subject = f'{news_query.capitalize()} İle İlgili Haber Başlıkları'
        body = f'İşte {news_query} ile ilgili son haber başlıkları:\n\n{news_title}'
        to_email = email_entry.get()
        send_email(subject, body, to_email)
        messagebox.showinfo("Bilgi", "E-posta başarıyla gönderildi!")
    else:
        messagebox.showerror("Hata", "Haber başlıkları alınamadı.")

# Tkinter arayüzü oluşturma
root = tk.Tk()
root.title("Haber Başlığı Ol uşturucu")

label = tk.Label(root, text="Haber başlıkları için bir anahtar kelime girin:")
label.pack(pady=10)

entry = tk.Entry(root, width=100)
entry.pack(pady=10)

email_label = tk.Label(root, text="E-posta adresinizi girin:")
email_label.pack(pady=10)

email_entry = tk.Entry(root, width=100)
email_entry.pack(pady=10)

button = tk.Button(root, text="Haber Başlıklarını Göster ve E-posta Gönder", command=show_news)
button.pack(pady=10)

root.mainloop()
