import os

def create_directory_structure():
    # Create folders
    if not os.path.exists('templates'):
        os.makedirs('templates')

    if not os.path.exists('static'):
        os.makedirs('static')

    # Create files with initial content
    with open('app.py', 'w') as f:
        f.write("""from flask import Flask, render_template
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.offline import plot
from fredapi import Fred
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

app = Flask(__name__)
fred = Fred(api_key="da18519988a01043d2992cfcfc046ef7")

def prepare_data(data):
    data_shifted = data.shift(1)
    data = pd.concat([data, data_shifted], axis=1)
    data.dropna(inplace=True)
    X = data.iloc[:, 1:]
    y = data.iloc[:, 0]
    return X, y

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/labor_market')
def labor_market():
    indicators = ['UNRATE', 'CIVPART', 'EMRATIO']
    plot_divs = []

    for code in indicators:
        data = fred.get_series(code)
        data = pd.DataFrame(data)
        X, y = prepare_data(data)
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, shuffle=False)
        
        scaler = StandardScaler()
        X_train = scaler.fit_transform(X_train)
        X_test = scaler.transform(X_test)
        
        rf = RandomForestRegressor(n_estimators=100)
        rf.fit(X_train, y_train)
        y_pred_rf = rf.predict(X_test)

        fig = go.Figure()
        fig.add_trace(go.Scatter(x=np.arange(len(y_test)), y=y_test, mode='lines', name='Actual'))
        fig.add_trace(go.Scatter(x=np.arange(len(y_test)), y=y_pred_rf, mode='lines', name='Random Forest Predicted'))
        
        fig.update_layout(title=f"{code} - Actual vs Predicted", xaxis_title='Time', yaxis_title='Value')
        plot_html = plot(fig, output_type='div')
        plot_divs.append(plot_html)

    return render_template('labor_market.html', plots=plot_divs)

if __name__ == '__main__':
    app.run(debug=True)
""")

    with open('templates/index.html', 'w') as f:
        f.write("""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Home Page</title>
    <link rel="stylesheet" href="{{ url_for('static', filename='style.css') }}">
</head>
<body>
    <h1>Economic Areas</h1>
    <ul>
        <li><a href="/labor_market">Labor Market</a></li>
    </ul>
</body>
</html>
""")

    with open('templates/labor_market.html', 'w') as f:
        f.write("""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Labor Market</title>
    <link rel="stylesheet" href="{{ url_for('static', filename='style.css') }}">
</head>
<body>
    <h1>Labor Market</h1>
    <div class="quadrant">
        {{ plots[0]|safe }}
    </div>
    <div class="quadrant">
        {{ plots[1]|safe }}
    </div>
    <div class="quadrant">
        {{ plots[2]|safe }}
    </div>
    <a href="/">Back to Home</a>
</body>
</html>
""")

    with open('static/style.css', 'w') as f:
        f.write("""body {
    font-family: Arial, sans-serif;
    background-color: #f4f4f4;
    margin: 40px;
}

h1 {
    color: #333;
}

ul {
    list-style-type: none;
}

.quadrant {
    width: 48%;
    display: inline-block;
    vertical-align: top;
    margin-right: 2%;
    background-color: white;
    padding: 20px;
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
}
""")

# Run the function to generate the folders and files
create_directory_structure()
