from flask import Flask, render_template, request
import calendar
from datetime import datetime
from google import genai
from pydantic import BaseModel # type: ignore
import os

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
    
    # 日の調整
    daymax = max(request.args.get('day',default=datetime.now().day,type=int),1)
    if day < 1:
        day = daymax
        month -= 1
    elif day > daymax:
        day = 1
        month += 1

    
    # カレンダーをHTML形式で作成
    cal = calendar.HTMLCalendar(calendar.SUNDAY)
    calendar_html = cal.formatmonth(year, month)
    datecalendar_html = cal.formatday(month,day)

    # テンプレートにレンダリング
    return render_template('calendar.html', year=year, month=month, calendar_html=calendar_html)
    return render_template('datecalendar.html', month=month, day=day, datecalendar_html=datecalendar_html)

#AIに聞く機構
@app.route('/')
def gemini():
    class Explanation(BaseModel):
        explanation : list[str]

    client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
    whatday = "{{ month }}月{{ day }}日"
    response = client.models.generate_content(
          model="gemini-2.0-flash",
          contents="{{ whatday }}は何の日ですか？一つ取り上げて軽い説明をしてください。",
          config={
              "response_mime_type": "application/json",
              "response_schema": list[Explanation],
          },
      )
    
    print(response.text)

    return response.text

if __name__ == '__main__':
    app.run(debug=True)
