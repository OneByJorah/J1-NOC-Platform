from fastapi import FastAPI
app = FastAPI(title='J1 NOC Platform')

@app.get('/health')
def health():
    return {'status':'ok'}
