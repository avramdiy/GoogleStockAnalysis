from flask import Flask, jsonify
import pandas as pd

app = Flask(__name__)

# Load the CSV file and store it in a global variable
dataframe = None

def load_csv(file_path):
    global dataframe
    try:
        dataframe = pd.read_csv(file_path)
        print("CSV file loaded successfully.")
    except Exception as e:
        print(f"Error loading CSV file: {e}")

# Path to your CSV file
csv_path = r"C:\\Users\\Ev\\Desktop\\TRG8\\Google_stock.csv"
load_csv(csv_path)

if dataframe is None:
    raise Exception("Failed to load the CSV file.")

@app.route('/data', methods=['GET'])
def get_data():
    # Convert the DataFrame to JSON
    data_json = dataframe.to_dict(orient='records')
    return jsonify(data_json)

if __name__ == '__main__':
    app.run(debug=True)
