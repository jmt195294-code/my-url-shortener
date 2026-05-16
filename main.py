from flask import Flask, render_template_string, request, redirect
import string
import random
import json
import os

app = Flask(__name__)

# 링크를 영구 저장할 파일 이름
DB_FILE = "links.json"

def load_database():
    """파일에서 기존에 저장된 단축 링크 데이터를 불러옵니다."""
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r", encoding="utf-8") as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return {}
    return {}

def save_database(data):
    """새로운 단축 링크가 추가되면 파일에 바로 저장합니다."""
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def generate_short_code(url_database, length=5):
    """5자리의 랜덤한 영문+숫자 코드를 만듭니다 (중복 체크 포함)."""
    characters = string.ascii_letters + string.digits
    while True:
        code = ''.join(random.choice(characters) for _ in range(length))
        if code not in url_database:
            return code

# 메인 화면 HTML (UI 디자인 살짝 업그레이드!)
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>영구 저장 단축 링크 만들기</title>
    <style>
        body { font-family: 'Malgun Gothic', sans-serif; text-align: center; margin-top: 50px; background-color: #f9f9f9; }
        .container { max-width: 600px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
        input[type="url"] { width: 70%; padding: 12px; font-size: 16px; border: 1px solid #ddd; border-radius: 5px; }
        input[type="submit"] { padding: 12px 20px; font-size: 16px; background-color: #4CAF50; color: white; border: none; border-radius: 5px; cursor: pointer; }
        input[type="submit"]:hover { background-color: #45a049; }
        .result { margin-top: 30px; padding: 15px; background-color: #e7f3fe; border-left: 6px solid #2196F3; text-align: left; border-radius: 4px; }
        a { color: #2196F3; text-decoration: none; font-weight: bold; }
    </style>
</head>
<body>
    <div class="container">
        <h2>🔒 만료 없는 나만의 단축 URL</h2>
        <p>프로그램을 재시작해도 링크가 영구히 유지됩니다.</p>
        <form method="POST" action="/">
            <input type="url" name="long_url" placeholder="줄이고 싶은 긴 주소를 입력하세요" required>
            <input type="submit" value="주소 줄이기">
        </form>

        {% if short_url %}
            <div class="result">
                <strong>🎉 단축 완료! 언제든 이 링크로 접속하세요:</strong><br><br>
                <a href="{{ short_url }}" target="_blank">{{ short_url }}</a>
            </div>
        {% endif %}
    </div>
</body>
</html>
"""

@app.route("/", methods=["GET", "POST"])
def home():
    short_url = None
    if request.method == "POST":
        long_url = request.form.get("long_url")
        
        # 1. 파일에서 최신 데이터 불러오기
        url_database = load_database()
        
        # 2. 랜덤 코드 생성 및 데이터 추가
        short_code = generate_short_code(url_database)
        url_database[short_code] = long_url
        
        # 3. 파일에 영구 저장!
        save_database(url_database)
        
        short_url = request.host_url + short_code

    return render_template_string(HTML_TEMPLATE, short_url=short_url)

@app.route("/<short_code>")
def redirect_to_long_url(short_code):
    # 접속할 때도 파일에서 데이터를 읽어와 원래 주소를 찾습니다.
    url_database = load_database()
    long_url = url_database.get(short_code)
    
    if long_url:
        return redirect(long_url)
    else:
        return """
        <div style="text-align: center; margin-top: 100px; font-family: Arial, sans-serif;">
            <h2>존재하지 않는 링크입니다. 🔍</h2>
            <p>주소를 다시 확인해 주세요.</p>
            <a href="/">메인으로 가기</a>
        </div>
        """, 404

if __name__ == '__main__':
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
