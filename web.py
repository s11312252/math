import requests
from bs4 import BeautifulSoup


from flask import Flask, render_template,request

from datetime import datetime

import os
import json
import firebase_admin
from firebase_admin import credentials, firestore

# 判斷是在 Vercel 還是本地
if os.path.exists('serviceAccountKey.json'):
    # 本地環境：讀取檔案
    cred = credentials.Certificate('serviceAccountKey.json')
else:
    # 雲端環境：從環境變數讀取 JSON 字串
    firebase_config = os.getenv('FIREBASE_CONFIG')
    cred_dict = json.loads(firebase_config)
    cred = credentials.Certificate(cred_dict)

firebase_admin.initialize_app(cred)


app = Flask(__name__)

@app.route("/")
def index():
    link = "<h1>歡迎來到陳芯霈的網站20260409</h1><hr>"
    link += "<a href=/mis>課程</a><hr>"
    link += "<a href=/today>時間</a><hr>"
    link += "<a href=/me>關於我</a><hr>"
    link += "<a href=/welcome?u=芯霈&d=靜宜資管&c=資訊管理導論>get傳值</a><hr>"    
    link += "<a href=/account>POST傳值</a><hr>"
    link += "<a href=/math>次方與根號計算</a><hr>"
    link += "<br><a href=/read>讀取Firestore資料</a><br>"
    link += "<br><a href=/read3>讀取Firestore資料(關鍵字)</a><br>"
    link += "<br><a href=/read2>讀取Firestore資料(根據姓名關鍵字)</a><br>"
    link += "<br><a href='/spider'>執行爬蟲 (課程資料)</a><hr>"
    link += "<br><a href='/movie1'>爬蟲即將上映電影</a><hr>"

    return link



@app.route("/movie1")
def movie():
    q = request.args.get("q")

    url = "https://www.atmovies.com.tw/movie/next/"
    Data = requests.get(url)
    Data.encoding = "utf-8"
    sp = BeautifulSoup(Data.text, "html.parser")
    result = sp.select(".filmListAllX li")

    R = "<h1>即將上映電影查詢</h1>"
    R += f"""
    <form action="/movie1" method="get">
        <input type="text" name="q" placeholder="輸入片名關鍵字" value="{q if q else ''}">
        <button type="submit">搜尋</button>
    </form>
    <hr>
    """

    found_count = 0
    for item in result:
        try:
            alt_text = item.find("img").get("alt")
            
            if not q or q in alt_text:
                found_count += 1
                R += "電影名稱：" + alt_text + "<br>"
                R += "介紹連結：<a href='https://www.atmovies.com.tw" + item.find("a").get("href") + "'>點我觀看</a><br>"
                R += "<img src='https://www.atmovies.com.tw" + item.find("img").get("src") + "' width='150'><br><br>"
        except:
            continue

    if found_count == 0 and q:
        R += f"找不到關於「{q}」的電影。<br>"
    
    R += "<br><a href='/'>回首頁</a>"
    return R 

@app.route("/spider")
def spider():
    url = "https://www1.pu.edu.tw/~tcyang/course.html"
    Data = requests.get(url)
    Data.encoding = "utf-8"
    
    sp = BeautifulSoup(Data.text, "html.parser")
    result = sp.select(".team-box a") 
    
    content = "<h2>子青老師課程爬蟲結果</h2>"
    content += "<table border='1'><tr><th>課程名稱</th><th>課程連結</th></tr>"
    
    for i in result:
        name = i.text
        link = i.get("href")
        content += f"<tr><td>{name}</td><td><a href='{link}' target='_blank'>{link}</a></td></tr>"
    
    content += "</table>"
    content += "<br><a href='/'>返回首頁</a>"
    
    return content
@app.route("/read2", methods=["GET", "POST"])
def read2():
    if request.method == "POST":
        keyword = request.form.get("keyword")
        db = firestore.client()
        collection_ref = db.collection("靜宜資管")
        docs = collection_ref.get()
        
        results = []
        for doc in docs:
            teacher = doc.to_dict()
            if "name" in teacher and keyword in teacher["name"]:
                results.append(teacher)
        
        return render_template("searchteacher.html", keyword=keyword, results=results)
    
    return render_template("searchteacher.html", keyword=None, results=None)
        
    return Result

@app.route("/read3")
def read3():
    Result = ""
    keyword = "楊"
    db = firestore.client()
    collection_ref = db.collection("靜宜資管")
    docs = collection_ref.get()
    for doc in docs:        
        teacher = doc.to_dict()
        if "name" in teacher and keyword in teacher["name"]:
            Result += f"姓名：{teacher.get('name')}，研究室：{teacher.get('lab')}，郵件：{teacher.get('mail')}<br>"
   
    if Result == "":
        Result = "抱歉查無此關鍵字姓名之老師資料"
   
    return Result + "<br><a href=/>返回首頁</a>"

@app.route("/read")
def read():
    Result = ""
    db = firestore.client()
    collection_ref = db.collection("靜宜資管")    
    docs = collection_ref.get()    
    
    data_list = []
    for doc in docs:
        data_list.append(doc.to_dict())
    
    sorted_data = sorted(data_list, key=lambda x: x.get('lab', 0), reverse=True)
    
    for item in sorted_data:
        Result += str(item) + "<br>"
        
    return Result

@app.route("/mis")
def course():
    return "<h1>資訊管理導論</h1><a href=/>返回首頁</a>"

@app.route("/today")
def today():
    now = datetime.now()
    return render_template("today.html", datetime = str(now))

@app.route("/me")
def me():
    return render_template("2026b.html")


@app.route("/welcome", methods=["GET"])
def welcome():
    user = request.values.get("u")
    d = request.values.get("d")
    c = request.values.get("c")
    return render_template("welcome.html",name = user,dep = d,course = c)

@app.route("/account", methods=["GET", "POST"])
def account():
    if request.method == "POST":
        user = request.form["user"]
        pwd = request.form["pwd"]
        result = "您輸入的帳號是：" + user + "; 密碼為：" + pwd 
        return result
    else:
        return render_template("account.html")

@app.route("/math", methods=["GET", "POST"])
def math():
    result = None
    if request.method == "POST":
        try:
            x = float(request.form.get("x"))
            y = float(request.form.get("y"))
            opt = request.form.get("opt")

            if opt == "∧":
                result = x ** y
            elif opt == "√":
                if y == 0:
                    result = "錯誤：數學上不能開 0 次方"
                else:
                    result = x ** (1/y)
            else:
                result = "請選擇正確的運算符號"
        except ValueError:
            result = "請輸入有效的數字"

    return render_template("math.html", result=result)






if __name__ == "__main__":
    app.run(debug=True)
