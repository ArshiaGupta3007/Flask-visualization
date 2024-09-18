from flask import Flask, send_file, render_template, jsonify
from flask_cors import CORS
import pandas as pd
import matplotlib.pyplot as plt
import os

app = Flask(__name__)
CORS(app)  # Allow cross-origin requests

# Ensure plots directory exists
PLOT_DIR = 'plots'
if not os.path.exists(PLOT_DIR):
    os.makedirs(PLOT_DIR)

# Load the data once for use in all routes
df = pd.read_csv("data/data.csv")
df['Timestamp'] = pd.to_datetime(df['Timestamp'])
df['Expiry Date'] = pd.to_datetime(df['Expiry Date'])

# Define functions to generate plots
def generate_pie_chart():
    category_stock = df.groupby('Category')['Quantity In Stock'].sum()
    colors = ['lightblue', 'lightgreen', 'lightcoral', 'lightpink', 'lightskyblue']

    plt.figure(figsize=(8, 8))
    wedges, texts  = plt.pie(category_stock, startangle=90, colors=colors, autopct=None,
                                       wedgeprops={'linewidth': 1, 'edgecolor': 'black'})
    
    # Add the legend with category names
    plt.legend(wedges, category_stock.index, title="Categories", loc="center left", bbox_to_anchor=(1, 0, 0.5, 1))
    plt.title('Category-wise Stock Distribution')

    # Save the plot to the 'plots' directory
    plt.savefig(os.path.join(PLOT_DIR, 'pie_chart.png'), bbox_inches='tight')
    plt.close()

def generate_time_series_plot():
    top_5_medicines = df.groupby('Medicine Name')['Quantity Purchased'].sum().nlargest(5).index
    df_top_5 = df[df['Medicine Name'].isin(top_5_medicines)]

    plt.figure(figsize=(10, 6))
    for medicine in df_top_5['Medicine Name'].unique():
        medicine_data = df_top_5[df_top_5['Medicine Name'] == medicine]
        plt.plot(medicine_data['Timestamp'], medicine_data['Quantity In Stock'], marker='o', label=medicine)

    plt.title('Stock Level Over Time (Top 5 Sold Medicines)')
    plt.xlabel('Timestamp')
    plt.ylabel('Quantity In Stock')

    # Add the legend for time series plot
    plt.legend(title='Medicine Name', loc="upper left")
    plt.grid(True)
    plt.xticks(rotation=45)
    plt.tight_layout()

    # Save the plot to the 'plots' directory
    plt.savefig(os.path.join(PLOT_DIR, 'time_series.png'))
    plt.close()

def generate_expiry_plot():
    plt.figure(figsize=(10, 6))
    expiry_distribution = df['Expiry Date'].dt.year.value_counts().sort_index()

    # Plot bar chart and add the label
    expiry_distribution.plot(kind='bar', color='skyblue')
    
    plt.xlabel('Year')
    plt.ylabel('Number of Medicines')
    plt.title('Medicines Expiry Distribution by Year')
    
    # Add the legend to the bar chart
    plt.legend(['Number of Medicines'], loc="upper right")

    # Save the plot to the 'plots' directory
    plt.savefig(os.path.join(PLOT_DIR, 'expiry_chart.png'))
    plt.close()

# Flask Routes
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/generate_report', methods=['GET'])
def generate_report():
    try:
        # Generate the plots
        generate_pie_chart()
        generate_time_series_plot()
        generate_expiry_plot()

        # Return the list of plot filenames
        files = ['pie_chart.png', 'time_series.png', 'expiry_chart.png']
        return jsonify(plots=files)
    except Exception as e:
        return jsonify(error=str(e))

@app.route('/plot/<plot_name>', methods=['GET'])
def get_plot(plot_name):
    try:
        plot_path = f'plots/{plot_name}'
        return send_file(plot_path, mimetype='image/png')
    except Exception as e:
        return jsonify(error=str(e))

if __name__ == '__main__':
    app.run(debug=True)
