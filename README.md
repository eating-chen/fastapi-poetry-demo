# fastapi-poetry-demo

## 目錄架構

```text
app
├── api              
│   └── routes       - 底下定義所有api 路徑
├── models
│   └── schemas      - interface
└── main.py          - 整合routes裡定義的api
```

## 安裝 Poetry
- 官方建議利用 `pipx` 來安裝
    
    ```powershell
    >> pipx install poetry
    ```
    
- `official installer` 安裝，以下為`windows`版的安裝方式與設定環境變數(位置名稱記得改)，開啟`powershell`
    
    ```powershell
    >> (Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | python -
    >> $Env:Path += ";C:\Users\lucaschen\AppData\Roaming\Python\Scripts"; setx PATH "$Env:Path"
    ```
    - 重啟 `powershell` 可以輸入 `poetry` 看有沒有安裝成功


## 安裝套件
```
>> cd fastapi-poetry-demo
>> poetry install
```

## 執行
```
>> poetry shell
>> uvicorn app.main:app
```
- 可於網址輸入 `http://127.0.0.1:8000/docs` 有看到東西就算成功

## docker 
```
>> docker build -t fastapi_demo .
>> docker run -d --name fastapi_demo_container -p 80:80 fastapi_demo
```
- 可於網址輸入 `http://127.0.0.1/docs` 有看到東西就算成功
