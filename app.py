from flask import Flask

app = Flask(__name__)

@app.route('/')
def render():
    return render_template('mycode.py')

if __name__ == '__main__':
    app.run()
