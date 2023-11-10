import requests
from bs4 import BeautifulSoup
import pandas as pd

#### Functions
# URL to scrape
mmsi_data = []
def get_url_mmsi(mmsi):
    return f'https://www.myshiptracking.com/vessels/{mmsi}'

# Send HTTP request to the URL
def scrape_data_mmsi(mmsi_data, mmsi):
    table_data = {}
    url = get_url_mmsi(mmsi)
    response = requests.get(url)
    # Parse the HTML content
    soup = BeautifulSoup(response.text, 'html.parser')
    try:

        # Find the table you want to scrape
        table = soup.find('table', class_='table table-sm my-2')
        strong_tag = soup.find('strong')
        if strong_tag:
            strong_value = strong_tag.get_text()
            table_data["shipname"] = strong_value
            #print(strong_value)
    
        

        # Iterate through each row in the table
        for row in table.find_all('tr'):
            # Extract the text from the <th> and <td> elements
            header = row.find('th').get_text(strip=True) if row.find('th') else None
            value = row.find('td').get_text(strip=True) if row.find('td') else None
            
            # Sometimes the cell might have other tags like <div> or <img>; handle that if needed
            # For instance, if you want the 'src' attribute of an <img> tag inside a <td>, you might do:
            if header == 'Flag' and row.find('td'):
                img = row.find('td').find('img')
                if img:
                    value = img['src']  # Get the src attribute of the img tag
            
            # Store the data in your dictionary
            if header and value:
                table_data[header] = value

        # Now 'table_data' dictionary contains the extracted information
        mmsi_data.append(table_data)

        
        print(f"Found vessel information for mmsi {mmsi}")
    except:
        print(f"No data found for mmsi {mmsi}")
    

def main():
    missing_mmsi = pd.read_csv("mmsi_of_missing_imo.csv")
    all_mmsi = list(missing_mmsi["mmsi"].unique())
    for mmsi in all_mmsi:
        scrape_data_mmsi(mmsi_data, mmsi)
    df = pd.DataFrame(mmsi_data)
    df.to_csv("scraped_missing_imo.csv")

if __name__ == '__main__':
    main()
