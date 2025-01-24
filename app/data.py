from flask import Flask, jsonify
import pandas as pd
import matplotlib.pyplot as plt
from flask import send_file
import io

app = Flask(__name__)

# Load the CSV file and store it in a global variable
dataframe = None

def load_csv(file_path):
    global dataframe
    try:
        dataframe = pd.read_csv(file_path)
        # Filter the data to include only "Date", "Volume", "Open", and "Close" columns
        dataframe = dataframe[["Date", "Volume", "Open", "Close"]]
        dataframe["Date"] = pd.to_datetime(dataframe["Date"])
        
        # Scale Volume back to its original values (multiply by 1e6 for millions)
        dataframe["Volume"] *= 1e6
        
        print("CSV file loaded and filtered successfully.")
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

@app.route('/volume_chart', methods=['GET'])
def volume_chart():
    try:
        # Resample the data to weekly frequency and calculate the average volume
        weekly_data = dataframe.resample('W', on='Date').mean()
        
        # Create a bar chart
        plt.figure(figsize=(10, 6))
        plt.bar(weekly_data.index, weekly_data['Volume'], color='blue', alpha=0.7)
        plt.xlabel('Week', fontsize=12)
        plt.ylabel('Average Volume', fontsize=12)
        plt.title('Weekly Average Volume', fontsize=14)
        plt.xticks(rotation=45)
        plt.tight_layout()

        # Save the plot to a BytesIO object
        img = io.BytesIO()
        plt.savefig(img, format='png')
        img.seek(0)
        plt.close()
        
        return send_file(img, mimetype='image/png')
    except Exception as e:
        return f"Error generating chart: {e}", 500

if __name__ == '__main__':
    app.run(debug=True)
