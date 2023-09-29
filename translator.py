import locale

class Translator:
    def __init__(self):
         # List of country codes corresponding to Spanish-speaking countries
        self.hispanohablante_countries = ['ES', 'MX', 'AR', 'CO', 'CL', 'PE', 'VE', 'EC', 'GT', 'CU', 'BO', 'DO', 'HN', 'PA', 'UY', 'PY', 'SV', 'NI', 'CR', 'PR']
        
         # Fetch the default locale's country code (e.g., "US" for "en_US")
        self.country_code = locale.getdefaultlocale()[0].split('_')[1]

        # Define a dictionary of translations from Spanish to English
        self.translations = {
            "process_folder_btn": {
                "es": "Procesar carpeta",
                "en": "Process Folder"
            },
            "apply_raw_chk": {
                "es": "Aplicar a archivos raw",
                "en": "Apply to raw files"
            },
            "trust_ai_chk": {
                "es": "Confiar en IA",
                "en": "Trust AI"
            },
            "stop_btn": {
                "es": "Detener",
                "en": "Stop"
            },
            "all_images_analyzed": {
                "es": "¡Todas las imágenes han sido analizadas!",
                "en": "All images have been analyzed!"
            },
            "tags_applied_for": {
                "es": "Etiquetas aplicadas para",
                "en": "Tags applied for"
            },
            "apply_all": {
                "es": "Aplicar todo",
                "en": "Apply all"
            }, 
            "app_title": {
                "es": "ImageLabelIA",
                "en": "ImageLabelAI"
            },
            "process_folder_btn": {
                "es": "Procesar carpeta",
                "en": "Process Folder"
            },
            "apply_raw_chk": {
                "es": "Aplicar a archivos raw",
                "en": "Apply to raw files"
            },
            "trust_ai_chk": {
                "es": "Confiar en IA",
                "en": "Trust AI"
            },
            "stop_btn": {
                "es": "Detener",
                "en": "Stop"
            },
            "progress_label_default": {
                "es": "0/0",
                "en": "0/0"
            },
            "all_images_analyzed": {
                "es": "¡Todas las imágenes han sido analizadas!",
                "en": "All images have been analyzed!"
            },
            "keywords_title": {
                "es": "Keywords",
                "en": "Keywords"
            },
            "add_keyword_btn": {
                "es": "Añadir",
                "en": "Add"
            },
            "apply_tags_btn": {
                "es": "Aplicar",
                "en": "Apply"
            },
            "no_images_message":{
                "es":"No hay imágenes en la carpeta seleccionada.",
                "en":"There are no images in the selected folder."
            },
            "images_analyzed":{
                "es":"¡Todas las imágenes han sido analizadas!",
                "en":"All images have been analysed!"
            }
        }

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
