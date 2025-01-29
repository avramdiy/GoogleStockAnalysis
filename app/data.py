from flask import Flask, jsonify
import pandas as pd
import matplotlib.pyplot as plt
from flask import send_file
import io
import mplfinance as mpf  # Import mplfinance for candlestick charts

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

@app.route('/line_chart', methods=['GET'])
def line_chart():
    try:
        # Resample the data to weekly frequency and calculate the average open and close prices
        weekly_data = dataframe.resample('W', on='Date').mean()
        
        # Create a line chart
        plt.figure(figsize=(10, 6))
        plt.plot(weekly_data.index, weekly_data['Open'], label='Weekly Average Open Price', color='green')
        plt.plot(weekly_data.index, weekly_data['Close'], label='Weekly Average Close Price', color='red')
        plt.xlabel('Week', fontsize=12)
        plt.ylabel('Price', fontsize=12)
        plt.title('Weekly Average Open and Close Prices', fontsize=14)
        plt.legend()
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

@app.route('/candlestick_chart', methods=['GET'])
def candlestick_chart():
    try:
        # Resample the data to weekly frequency
        ohlc_data = dataframe.resample('W', on='Date').agg({
            'Open': 'first',  # First value of the week for "Open"
            'Close': 'last',  # Last value of the week for "Close"
            'Volume': 'sum'   # Sum of the "Volume" for the week
        }).dropna()

        # Assuming Open is used for low and Close for high as placeholders
        ohlc_data['High'] = ohlc_data[['Open', 'Close']].max(axis=1)
        ohlc_data['Low'] = ohlc_data[['Open', 'Close']].min(axis=1)

        # Generate the candlestick chart
        img = io.BytesIO()
        mpf.plot(
            ohlc_data,
            type='candle',
            volume=True,
            style='yahoo',
            savefig=dict(fname=img, format='png')
        )
        img.seek(0)
        
        return send_file(img, mimetype='image/png')
    except Exception as e:
        return f"Error generating candlestick chart: {e}", 500


if __name__ == '__main__':
    app.run(debug=True)
