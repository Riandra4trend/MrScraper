import requests
import pandas as pd
import argparse
import json
import logging
import os
from dotenv import load_dotenv
from io import StringIO

# Muat variabel lingkungan (untuk GOOGLE_API_KEY)
load_dotenv()

# Konfigurasi logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# STRUKTUR DATA BARU: Memetakan semua kemungkinan lokasi dan kodenya
# Berdasarkan pola yang Anda temukan (Negara|KodeProvinsi)
LOCATION_DATA = {
    "united states": {
        "api_code": "United States",
        "provinces": {
            "alabama": "AL", "arizona": "AZ", "arkansas": "AR", "california": "CA",
            "colorado": "CO", "delaware": "DE", "florida": "FL", "georgia": "GA",
            "idaho": "ID", "illinois": "IL", "indiana": "IN", "iowa": "IA",
            "kansas": "KS", "kentucky": "KY", "louisiana": "LA", "maine": "ME",
            "maryland": "MD", "michigan": "MI", "minnesota": "MN", "mississippi": "MS",
            "missouri": "MO", "montana": "MT", "nebraska": "NE", "nevada": "NV",
            "new hampshire": "NH", "new jersey": "NJ", "new mexico": "NM", "new york": "NY",
            "north carolina": "NC", "north dakota": "ND", "ohio": "OH", "oklahoma": "OK",
            "oregon": "OR", "pennsylvania": "PA", "south carolina": "SC", "south dakota": "SD",
            "tennessee": "TN", "texas": "TX", "utah": "UT", "virginia": "VA",
            "washington": "WA", "wisconsin": "WI", "wyoming": "WY"
        }
    },
    "canada": {
        "api_code": "Canada",
        "provinces": {
            "alberta": "AB", "ontario": "ON", "quebec": "QC", "saskatchewan": "SK"
        }
    },
    "argentina": {
        "api_code": "Argentina",
        "provinces": {} # Argentina tidak memiliki provinsi dalam daftar
    }
}

class AIProcessor:
    """Menggunakan LLM untuk mengubah bahasa alami menjadi parameter pencarian terstruktur."""
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv('GOOGLE_API_KEY')
        self.model = None
        if self.api_key:
            try:
                import google.generativeai as genai
                genai.configure(api_key=self.api_key)
                self.model = genai.GenerativeModel('gemini-1.5-flash')
                logging.info("✅ Google AI (Gemini) berhasil diinisialisasi.")
            except Exception as e:
                logging.error(f"❌ Gagal menginisialisasi Google AI: {e}")
        else:
            logging.warning("⚠️ GOOGLE_API_KEY tidak ditemukan. Fitur AI tidak akan berfungsi.")

    def interpret_command(self, user_command: str) -> dict:
        """Mengonversi perintah pengguna menjadi objek JSON terstruktur."""
        if not self.model:
            return {"error": "AI model not available."}

        # Prompt ini dirancang ulang sepenuhnya untuk tugas baru kita: mem-parsing query, bukan membuat aksi Selenium.
        prompt = f"""
        You are a query parser for a cattle ranch directory. Your task is to extract structured information from a user's natural language command.
        The available locations are: {json.dumps(list(LOCATION_DATA.keys()))} and their respective provinces/states.

        Your goal is to return a SINGLE JSON object with three keys: "country", "province", and "name".
        - "country" and "province" must be lowercase.
        - If a piece of information is not mentioned, its value must be `null`.
        - If the user says "all" for a country (e.g., "all of Canada"), set province to `null`.

        Examples:
        - User: "Find ranches in Alberta, Canada" -> {{"country": "canada", "province": "alberta", "name": null}}
        - User: "Show me all breeders in the US" -> {{"country": "united states", "province": null, "name": null}}
        - User: "Search for 'Circle M' in Texas" -> {{"country": "united states", "province": "texas", "name": "Circle M"}}
        - User: "Any ranches in Argentina?" -> {{"country": "argentina", "province": null, "name": null}}
        - User: "sullivan farms in kansas" -> {{"country": "united states", "province": "kansas", "name": "sullivan farms"}}

        Now, parse the following user command. Return only the JSON object.

        User Command: "{user_command}"
        """
        try:
            response = self.model.generate_content(prompt)
            cleaned_response = response.text.strip().replace("```json", "").replace("```", "")
            return json.loads(cleaned_response)
        except Exception as e:
            logging.error(f"❌ Gagal memproses perintah AI: {e}")
            return {"error": f"Failed to parse AI response: {e}"}

class ShorthornApiScraper:
    """Scraper yang menggunakan pemanggilan API langsung dan pemrosesan NLP."""
    def __init__(self):
        self.base_url = "https://shorthorn.digitalbeef.com/modules/DigitalBeef-Landing/ajax/search_results_ranch.php"
        self.ai_processor = AIProcessor()

    def search(self, command: str) -> dict:
        """Menerima perintah bahasa alami, mem-parsingnya, dan memanggil API."""
        logging.info(f"Menerima perintah: '{command}'")
        parsed_query = self.ai_processor.interpret_command(command)

        if not parsed_query or "error" in parsed_query:
            return {"error": "Gagal menafsirkan perintah.", "details": parsed_query.get("error")}

        logging.info(f"Perintah berhasil diparsing oleh AI: {parsed_query}")

        # Membangun parameter API dari hasil parsing AI
        params = {'l': '', 'v': parsed_query.get('name') or ''}
        country = parsed_query.get('country')
        province = parsed_query.get('province')

        if country:
            country_data = LOCATION_DATA.get(country.lower())
            if not country_data:
                return {"error": f"Negara tidak dikenal: {country}"}
            
            location_string = country_data['api_code']
            if province:
                province_code = country_data['provinces'].get(province.lower())
                if not province_code:
                    return {"error": f"Provinsi/Negara Bagian tidak dikenal '{province}' untuk {country}"}
                location_string += f"|{province_code}"
            else:
                location_string += "|" # Untuk pencarian "All" di suatu negara
            params['l'] = location_string
        
        return self._call_api(params)

    def _call_api(self, params: dict) -> dict:
        """Fungsi internal untuk memanggil API dan mem-parsing hasilnya."""
        logging.info(f"Mengirim permintaan ke API dengan parameter: {params}")
        try:
            response = requests.get(self.base_url, params=params)
            response.raise_for_status()

            html_content = response.text
            
            # Check for various "no results" indicators
            no_results_indicators = [
                "No records found matching your criteria",
                "No records found",
                "No results found",
                "0 records found"
            ]
            
            if any(indicator in html_content for indicator in no_results_indicators):
                logging.warning("API tidak mengembalikan data (No records found).")
                return {"header": [], "data": []}

            # Fix the FutureWarning by using StringIO
            df_list = None
            parse_error = None
            
            # Try different HTML parsers
            parsers = ['html5lib', 'bs4', 'lxml']
            for parser in parsers:
                try:
                    df_list = pd.read_html(StringIO(html_content), flavor=parser)
                    break
                except Exception as e:
                    parse_error = e
                    continue
            
            # If all parsers failed, try without specifying flavor
            if df_list is None:
                try:
                    df_list = pd.read_html(StringIO(html_content))
                except Exception as e:
                    parse_error = e
            
            # If still no tables found, check if it's really a "no results" case
            if df_list is None or len(df_list) == 0:
                # Check if the HTML contains typical "empty result" patterns
                html_lower = html_content.lower()
                if any(pattern in html_lower for pattern in ['no data', 'empty', 'no results', 'not found']):
                    logging.warning("Tidak ada tabel ditemukan, kemungkinan tidak ada hasil.")
                    return {"header": [], "data": []}
                else:
                    # If it's not a "no results" case, then it's a real parsing error
                    logging.error(f"Gagal mem-parsing HTML. Error: {parse_error}")
                    logging.debug(f"HTML content preview: {html_content[:500]}...")
                    return {"error": f"Gagal mem-parsing tabel dari respons API: {str(parse_error)}"}
                
            results_df = df_list[0]
            logging.info(f"✅ Berhasil mengambil {len(results_df)} baris data dari API.")

            # Get actual column names from the DataFrame
            header = [str(col) for col in results_df.columns]
            data = results_df.astype(str).values.tolist()
            
            # Debug: Print actual headers for troubleshooting
            logging.info(f"🔍 Header yang ditemukan: {header}")
            
            return {"header": header, "data": data}

        except requests.exceptions.RequestException as e:
            return {"error": f"Gagal menghubungi API: {e}"}
        except Exception as e:
            logging.error(f"Unexpected error dalam _call_api: {e}")
            return {"error": f"Error tidak terduga: {str(e)}"}

def main():
    parser = argparse.ArgumentParser(description="Scraper Cerdas berbasis API untuk Shorthorn Digital Beef.")
    parser.add_argument("-c", "--command", required=True, type=str, help="Perintah pencarian dalam bahasa alami.")
    args = parser.parse_args()

    scraper = ShorthornApiScraper()
    results = scraper.search(args.command)

    print("\n--- Hasil Scraping Cerdas dari API ---")
    print(json.dumps(results, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()