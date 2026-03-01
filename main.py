import asyncio
import requests
from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse

app = FastAPI()

# URLs ko store karne ke liye list
ping_list = []

# Background Task: Har 5 minute mein jagane wala function
async def keep_awake():
    while True:
        for url in ping_list:
            try:
                # Sirf ping karna hai, data download nahi karna
                requests.get(url, timeout=5)
                print(f"Pinged successfully: {url}")
            except Exception as e:
                print(f"Error pinging {url}: {e}")
        
        # 300 seconds (5 minute) ka wait, taaki Render block na kare
        await asyncio.sleep(300)

# Server start hote hi pinging chalu
@app.on_event("startup")
async def startup_event():
    asyncio.create_task(keep_awake())

# HTML Dashboard UI
@app.get("/", response_class=HTMLResponse)
async def dashboard():
    html_content = """
    <html>
        <head>
            <title>My Uptime Robot</title>
            <meta name="viewport" content="width=device-width, initial-scale=1">
            <style>
                body { font-family: Arial, sans-serif; padding: 20px; background-color: #f4f4f9; }
                .container { max-width: 500px; margin: auto; background: white; padding: 20px; border-radius: 10px; box-shadow: 0px 0px 10px rgba(0,0,0,0.1); }
                input[type="url"] { width: 100%; padding: 10px; margin: 10px 0; border: 1px solid #ccc; border-radius: 5px; }
                button { background: #28a745; color: white; border: none; padding: 10px 15px; cursor: pointer; border-radius: 5px; width: 100%; }
                button:hover { background: #218838; }
                ul { background: #eee; padding: 15px; border-radius: 5px; }
            </style>
        </head>
        <body>
            <div class="container">
                <h2 style="text-align: center;">🚀 API Uptime Robot</h2>
                <form action="/add" method="post">
                    <input type="url" name="url" placeholder="https://your-api.onrender.com" required>
                    <button type="submit">Keep It Awake (Add URL)</button>
                </form>
                <h3>Active URLs:</h3>
                <ul>
    """
    if not ping_list:
        html_content += "<li>No URLs added yet!</li>"
    else:
        for u in ping_list:
            html_content += f"<li>{u}</li>"
            
    html_content += """
                </ul>
            </div>
        </body>
    </html>
    """
    return html_content

# Naya URL list mein add karne ka logic
@app.post("/add", response_class=HTMLResponse)
async def add_url(url: str = Form(...)):
    if url not in ping_list:
        ping_list.append(url)
        return f"<h3>URL Added Successfully!</h3><p>{url} will now be pinged every 5 minutes.</p><a href='/'>Go Back</a>"
    return f"<h3>URL is already in the list!</h3><a href='/'>Go Back</a>"
