import firebase_admin
from firebase_admin import credentials, db
from flask import Flask, render_template, request
from datetime import datetime

app = Flask(__name__)

# Firebase ile bağlantı kuruyoruz
cred = credentials.Certificate('serviceAccountKey.json')  # Firebase service account key dosyasının yolu
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://siken-f8bb0-default-rtdb.firebaseio.com/'  # Firebase Realtime Database URL
})

# Firebase'den 'last_completed_job_date' verisini al
def get_last_completed_job_date():
    ref = db.reference('job')
    date_str = ref.get()  # Firebase'den alınan tarih verisi
    if date_str:
        return datetime.strptime(date_str, "%Y-%m-%d %H:%M")  # Firebase'den alınan veriyi datetime formatına çevir
    else:
        return datetime(2025, 2, 10, 10, 0)  # Varsayılan değer

# Firebase'e 'last_completed_job_date' verisini güncelle
def update_last_completed_job_date(date):
    ref = db.reference('job')
    ref.set(date.strftime("%Y-%m-%d %H:%M"))  # Firebase'e tarih formatında veri gönder

@app.route('/', methods=['GET', 'POST'])
def index():
    # Firebase'den işin son yapılma tarihini alıyoruz
    last_completed_job_date = get_last_completed_job_date()
    
    # Eğer POST isteği gelirse, formdan tarih ve saat bilgisi al
    if request.method == 'POST':
        date_input = request.form.get('job_date')
        time_input = request.form.get('job_time')
        
        # Tarih ve saati birleştirip datetime formatında işliyoruz
        try:
            last_completed_job_date = datetime.strptime(f"{date_input} {time_input}", "%Y-%m-%d %H:%M")
            update_last_completed_job_date(last_completed_job_date)  # Firebase'de güncelle
        except ValueError:
            # Geçersiz tarih ve saat formatı durumunda
            return render_template('index.html', error="Geçersiz tarih veya saat formatı. Lütfen doğru formatta giriniz.", last_completed_job_date=last_completed_job_date)

    # Şu anki zamanı alıyoruz
    now = datetime.now()

    # İşin üzerinden geçen zamanı hesaplıyoruz
    time_diff = now - last_completed_job_date
    hours_diff = time_diff.total_seconds() // 3600
    minutes_diff = time_diff.total_seconds() // 60
    days_diff = time_diff.days

    return render_template('index.html', hours_diff=hours_diff, minutes_diff=minutes_diff, days_diff=days_diff, last_completed_job_date=last_completed_job_date)


if __name__ == '__main__':
    app.run(debug=True)
