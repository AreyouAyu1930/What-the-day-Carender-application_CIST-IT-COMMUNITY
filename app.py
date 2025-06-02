from flask import Flask, render_template, request
import calendar
from datetime import datetime

app = Flask(__name__)

@app.route('/')
def calendar_view():
    # 現在の年と月を取得
    year = request.args.get('year', default=datetime.now().year, type=int)
    month = request.args.get('month', default=datetime.now().month, type=int)
    day = request.args.get('day', default=datetime.now().day, type=int)

    # 月の調整
    if month < 1:
        month = 12
        year -= 1
    elif month > 12:
        month = 1
        year += 1

    
    # カレンダーをHTML形式で作成
    cal = calendar.HTMLCalendar(calendar.SUNDAY)
    calendar_html = cal.formatmonth(year, month)

    # テンプレートにレンダリング
    return render_template('calendar.html', year=year, month=month, calendar_html=calendar_html)
    return render_template('datecalendar.html', month=month, day=day, )

@app.route('/')
def whatday():
    client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
    response = client.models.generate_content(
          model="gemini-2.0-flash",
          contents=f"{}を使った料理を教えてください",
          config={
              "response_mime_type": "application/json",
              "response_schema": list[Recipe],
          },
      )

if __name__ == '__main__':
    app.run(debug=True)
