from flask import Flask
import threading
import time
import os
import signal

app = Flask(__name__)

@app.route('/')
def hello_world():
    return 'Hello, World!!!'

def shutdown_server():
    time.sleep(60)  # 60초 대기
    # 프로세스 ID를 가져와 서버 종료
    os.kill(os.getpid(), signal.SIGINT)

if __name__ == "__main__":
    threading.Thread(target=shutdown_server).start()
    app.run(host='0.0.0.0', port=5000)