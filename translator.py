import json
import locale

class Translator:
    def __init__(self):
         # List of country codes corresponding to Spanish-speaking countries
        self.hispanohablante_countries = ['ES', 'MX', 'AR', 'CO', 'CL', 'PE', 'VE', 'EC', 'GT', 'CU', 'BO', 'DO', 'HN', 'PA', 'UY', 'PY', 'SV', 'NI', 'CR', 'PR']
        
         # Fetch the default locale's country code (e.g., "US" for "en_US")
        self.country_code = locale.getdefaultlocale()[0].split('_')[1]

        # Define a dictionary of translations from Spanish to English
        with open('translations.json', 'r') as f:
            self.translations = json.load(f)

    def translate(self, code):
        """
        Translate the text identified by the code based on the user's country.

        Args:
        - code (str): The code identifying the message.

        Returns:
        - str: The translated text in English or Spanish based on the user's country.
        """
        lang = "en"
        if self.country_code in self.hispanohablante_countries:
            lang = "es"
        
        return self.translations.get(code, {}).get(lang, code)