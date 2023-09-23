import locale

class Translator:
    def __init__(self):
         # List of country codes corresponding to Spanish-speaking countries
        self.hispanohablante_countries = ['ES', 'MX', 'AR', 'CO', 'CL', 'PE', 'VE', 'EC', 'GT', 'CU', 'BO', 'DO', 'HN', 'PA', 'UY', 'PY', 'SV', 'NI', 'CR', 'PR']
        
         # Fetch the default locale's country code (e.g., "US" for "en_US")
        self.country_code = locale.getdefaultlocale()[0].split('_')[1]

        # Define a dictionary of translations from Spanish to English
        self.translations = {
            "Procesar carpeta": "Process Folder",
            "Aplicar a archivos raw": "Apply to raw files",
            "Confiar en IA": "Trust AI",
            "Detener": "Stop",
            "¡Todas las imágenes han sido analizadas!": "All images have been analyzed!",
            "Etiquetas aplicadas para ": "Tags applied for ",
            "Aplicar todo": "Apply all"
            # ... (agregar otras traducciones necesarias aquí)
        }

    def translate(self, text):
        """
        Translate the text to English if the user's country is not Spanish-speaking.

        Args:
        - text (str): The Spanish text to be translated.

        Returns:
        - str: The translated text in English or the original text if the country is Spanish-speaking.
        """
        if self.country_code not in self.hispanohablante_countries:
            return self.translations.get(text, text)  # Devuelve la traducción si existe, de lo contrario devuelve el texto original
        return text
