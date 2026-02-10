# Digital Nomads

Flask web application for [your project description].

## Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/aidarrbekk/digitalnomads.git
   cd digitalnomads
```

from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

if __name__ == '__main__':
    app.run(debug=True)