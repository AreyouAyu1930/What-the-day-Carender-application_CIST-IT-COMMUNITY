from flask import Flask, render_template, request
import calendar
from datetime import datetime
from google import genai
from pydantic import BaseModel # type: ignore
import os

app = Flask(__name__)

@app.route('/calendar')
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
    daymax = calendar.monthrange(year, month)[1]
    if day < 1:
        day = daymax
        month -= 1
    elif day > daymax:
        day = 1
        month += 1

    
    # カレンダーをHTML形式で作成
    cal = calendar.HTMLCalendar(calendar.SUNDAY)
    calendar_html = cal.formatmonth(year, month)


    # テンプレートにレンダリング
    return render_template('calendar.html', year=year, month=month, calendar_html=calendar_html)

class CustomCalendar(calendar.HTMLCalendar):
    def formatmonth(self, year, month):
        cal_html = super().formatmonth(year, month)
        today = datetime.now().day    

        # 特定の日付を強調する処理（例：今日の日付をハイライト）
        cal_html = cal_html.replace(f'>{today}<', f'><b style="color:red;">{today}</b><')

        return cal_html

#日替わりカレンダー
@app.route('/daycalendar')
def daycalendar():
    #現在の月日を取得
    month = request.args.get('month', default=datetime.now().month, type=int)
    day = request.args.get('day', default=datetime.now().day, type=int)

    # 日の調整
    daymax = max(request.args.get('day',default=datetime.now().day,type=int),1)
    if day < 1:
        day = daymax
        month -= 1
    elif day > daymax:
        day = 1
        month += 1

    # カレンダーをカスタムクラスで生成
    cal = CustomCalendar(calendar.SUNDAY)
    calendar_html = cal.formatmonth(datetime.now().year, month)

    return render_template('datecalendar.html', month=month, day=day, calendar_html=calendar_html)


#AIに聞く機構
@app.route('/gemini')

def gemini():
    class Explanation(BaseModel):
        explanation : list[str]

    client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
    whatday = "{{ month }}月{{ day }}日"

    question = f"{month}月{day}日は何の日ですか？一つ取り上げて軽い説明をしてください。"
    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=question,
        config={
            "response_mime_type": "application/json",
            "response_schema": list[Explanation],
        },
    )
    
    print(response.text)

    return response.text


if __name__ == '__main__':
    app.run(debug=True)
