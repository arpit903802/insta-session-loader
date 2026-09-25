import os
import time
import json
from fastapi import FastAPI, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

app = FastAPI(title="Instagram Session Injector")

templates_dir = os.path.join(os.path.dirname(__file__), "templates")
templates = Jinja2Templates(directory=templates_dir)

@app.get("/", response_class=HTMLResponse)
async def read_index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/api/inject")
async def inject_cookie(cookie_data: str = Form(...), username: str = Form(...)):
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-blink-features=AutomationControlled")

    driver = webdriver.Chrome(options=options)

    try:
        driver.get("https://www.instagram.com")
        time.sleep(3)

        cookies = json.loads(cookie_data)
        for cookie in cookies:
            formatted_cookie = {
                'name': cookie.get('name'),
                'value': cookie.get('value'),
                'domain': '.instagram.com',
                'path': cookie.get('path', '/'),
                'secure': cookie.get('secure', True),
                'httpOnly': cookie.get('httpOnly', True)
            }
            if 'expiry' in cookie:
                formatted_cookie['expiry'] = int(cookie['expiry'])
            driver.add_cookie(formatted_cookie)

        driver.refresh()
        time.sleep(5)

        current_url = driver.current_url
        if "accounts/login" in current_url:
            driver.quit()
            return JSONResponse(status_code=400, content={"success": False, "message": "Session expired or invalid cookies."})

        return JSONResponse(content={"success": True, "message": f"Successfully bypassed login for session target: {username}"})

    except Exception as e:
        driver.quit()
        raise HTTPException(status_code=500, detail=str(e))
                                       
