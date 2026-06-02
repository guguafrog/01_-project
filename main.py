from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from openai import OpenAI
from dotenv import load_dotenv
import os

# 初始化 FastAPI
app = FastAPI()
load_dotenv()
# 连接 DeepSeek —— 把你的 key 填这里
client = OpenAI(
    api_key=os.getenv('DEEPSEEK_API_KEY'),
    base_url="https://api.deepseek.com"
)

# 接口数据格式
class ChatRequest(BaseModel):
    question: str

# ----------------------
# 1. AI 对话接口
# ----------------------
@app.post("/chat")
def chat(request: ChatRequest):
    try:
        response = client.chat.completions.create(
            model="deepseek-v4-pro",
            messages=[{"role": "user", "content": request.question}]
        )
        answer = response.choices[0].message.content
        return {"code": 200, "question": request.question, "answer": answer}
    except Exception as e:
        return {"code": 500, "error": str(e)}

# ----------------------
# 2. 网页聊天界面（自带）
# ----------------------
@app.get("/", response_class=HTMLResponse)
def index():
    return """
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>AI 聊天助手</title>
    <style>
        body{max-width:600px;margin:20px auto;font-family:Arial}
        .box{border:1px solid #ddd;padding:15px;border-radius:10px;margin-bottom:10px}
        .input-box{display:flex;gap:10px}
        input{flex:1;padding:10px;border-radius:8px;border:1px solid #ccc}
        button{padding:10px 16px;background:#007bff;color:white;border:none;border-radius:8px}
        .msg{margin:10px 0;padding:10px;border-radius:8px}
        .user{background:#e3f2fd;text-align:right}
        .bot{background:#f5f5f5;text-align:left}
    </style>
</head>
<body>
    <h2>AI 聊天助手</h2>
    <div id="messages"></div>

    <div class="input-box">
        <input id="question" placeholder="输入问题..." autocomplete="off">
        <button onclick="send()">发送</button>
    </div>

    <script>
        async function send() {
            let q = document.getElementById("question").value.trim()
            if (!q) return

            let msg = document.getElementById("messages")
            msg.innerHTML += `<div class='msg user'>你：${q}</div>`

            let res = await fetch("/chat", {
                method: "POST",
                headers:{"Content-Type":"application/json"},
                body: JSON.stringify({question: q})
            })

            let data = await res.json()
            msg.innerHTML += `<div class='msg bot'>AI：${data.answer}</div>`
            document.getElementById("question").value = ""
        }
    </script>
</body>
</html>
    """