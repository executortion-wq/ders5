from flask import Flask, request, jsonify
from flask_cors import CORS
import psycopg2, os

app = Flask(__name__)
CORS(app)

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://burhan:tWnM75JYoQU4O0604xomkQhk4S1VCYRJ@dpg-d3tjfk3e5dus73912vg0-a.oregon-postgres.render.com/ders1_db"
)

def connect_db():
    return psycopg2.connect(DATABASE_URL)

@app.route("/ziyaretciler", methods=["GET", "POST"])
def ziyaretciler():
    try:
        conn = connect_db()
        cur = conn.cursor()

        # Tabloyu oluştur (idempotent)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS ziyaretciler (
                id SERIAL PRIMARY KEY,
                isim TEXT,
                sehir TEXT
            )
        """)

        # POST isteğiyle gelen veriyi kaydet
        if request.method == "POST":
            data = request.get_json()
            isim = data.get("isim")
            sehir = data.get("sehir")

            if isim and sehir:
                cur.execute("INSERT INTO ziyaretciler (isim, sehir) VALUES (%s, %s)", (isim, sehir))
                conn.commit()

        # Son 10 kişiyi getir (isim + şehir birlikte)
        cur.execute("SELECT isim, sehir FROM ziyaretciler ORDER BY id DESC LIMIT 10")
        kayitlar = [f"{row[0]} - {row[1]}" for row in cur.fetchall()]

        cur.close()
        conn.close()

        return jsonify(kayitlar)

    except Exception as e:
        print("Veritabanı hatası:", e)
        return jsonify({"hata": str(e)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001)
