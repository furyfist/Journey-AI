from fastapi import FastAPI

app = FastAPI (
    title='Journey AI tools',
    description="Api endpooints for the tools used by the journey AI Agent",
    version="1.0.0"
)

@app.get("/")
def read_root():
    """Check server status"""
    return {"status": "Journey ai backend is working"}

