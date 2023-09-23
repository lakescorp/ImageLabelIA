# Required imports
import os
import threading
import tkinter as tk
from tkinter import filedialog, ttk
from PIL import Image, ImageTk, ExifTags

# Custom module imports
from vit_image_classifier import ViTImageClassifier
from detr_object_detector import DetrObjectDetector
from ImageWriter import ImageWriter
from translator import Translator

# Define some UI color constants
DARK_COLOR = "#333"
LIGHT_DARK_COLOR = "#555"
EVEN_DARKER_COLOR = "#222"
TOAST_COLOR = "#777"
TEXT_COLOR = "#FFF"
SUCCESS_COLOR = "#006400"

class Prediction:
    def __init__(self, path, keywords):
        self.path = path
        self.keywords = keywords


class ImageClassifierApp:
    
    def __init__(self, root):
        self.root = root
        self.translator = Translator()  # Initialize the translator
        # Set up the app
        self.setup_root()
        self.setup_styles()
        self.setup_widgets()
        # Initialize machine learning models and utility
        self.vit_classifier = ViTImageClassifier()
        self.detr_detector = DetrObjectDetector()
        self.image_writer = ImageWriter()
        self.stop_requested = False  # Control variable for stopping a long process


    def setup_root(self):
        """Configure the main window properties."""
        self.root.title("Image Classifier")
        self.root.configure(bg=DARK_COLOR)
        self.root.grid_rowconfigure(1, weight=1)
        self.root.grid_columnconfigure(3, weight=0)
        self.root.grid_columnconfigure(0, weight=1)

    def setup_styles(self):
        """Define styles for the ttk widgets."""
        style = ttk.Style()
        style.theme_use("clam")
        # Set up various widget styles
        style.configure("TLabel", background=DARK_COLOR, foreground=TEXT_COLOR)
        style.configure("TButton", background=LIGHT_DARK_COLOR, foreground=TEXT_COLOR, bordercolor=DARK_COLOR)
        style.configure("TFrame", background=DARK_COLOR)
        style.configure("TProgressbar", troughcolor=DARK_COLOR, background=LIGHT_DARK_COLOR)
        style.configure("TScrollbar", background=DARK_COLOR)

    def setup_widgets(self):
        """Set up the main interface widgets."""
        # Set up widgets like buttons, checkboxes, progress bars, etc.
        self.button_open = tk.Button(self.root, text=self.translator.translate("Procesar carpeta"), command=self.process_folder)
        self.apply_dark_theme_to_widget(self.button_open)
        self.button_open.grid(row=0, column=0, pady=10, sticky="w")
        
        self.apply_to_raw = tk.BooleanVar(value=False)
        self.trust_ai = tk.BooleanVar(value=False)
            
        self.raw_option_chk = tk.Checkbutton(self.root, text=self.translator.translate("Aplicar a archivos raw"), variable=self.apply_to_raw, bg=DARK_COLOR, fg=TEXT_COLOR, selectcolor=EVEN_DARKER_COLOR)
        self.raw_option_chk.grid(row=0, column=1, pady=10, sticky="w")
            
        self.trust_ai_chk = tk.Checkbutton(self.root, text=self.translator.translate("Confiar en IA"), variable=self.trust_ai, bg=DARK_COLOR, fg=TEXT_COLOR, selectcolor=EVEN_DARKER_COLOR)
        self.trust_ai_chk.grid(row=0, column=2, pady=10, sticky="w")

        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(self.root, orient="horizontal", length=300, mode="determinate", variable=self.progress_var)

        self.progress_label = tk.Label(self.root, text="0/0")
        self.apply_dark_theme_to_widget(self.progress_label)


        self.button_stop = tk.Button(self.root, text=self.translator.translate("Detener"), command=self.stop_process)
        self.apply_dark_theme_to_widget(self.button_stop)

        self.setup_canvas()

    def stop_process(self):
        """Interrupt the current processing."""
        self.stop_requested = True
        self.button_stop.grid_forget()

    def setup_canvas(self):
        """Set up the canvas and associated scrollbar."""
        self.canvas = tk.Canvas(self.root, bg=DARK_COLOR, highlightbackground=DARK_COLOR)
        self.canvas.grid(row=1, column=0, columnspan=3, sticky="nsew", padx=20, pady=20) 

        self.scrollbar = tk.Scrollbar(self.root, orient="vertical", command=self.canvas.yview)
        self.scrollbar.grid(row=1, column=5, sticky="ns")

        self.canvas.config(yscrollcommand=self.scrollbar.set, scrollregion=self.canvas.bbox("all"))
        self.canvas_frame = tk.Frame(self.canvas, bg=DARK_COLOR)
        self.canvas.create_window((0,0), window=self.canvas_frame, anchor="nw")
        self.canvas_frame.bind("<Configure>", self.on_canvas_configure)

        self.root.bind("<MouseWheel>", self._on_mousewheel) 

    def _on_mousewheel(self, event):
        """Scroll the canvas with the mouse wheel."""
        if event.num == 4:
            self.canvas.yview_scroll(-1, "units")
        elif event.num == 5: 
            self.canvas.yview_scroll(1, "units")
        else:
            self.canvas.yview_scroll(-1*(event.delta//120), "units")

    def apply_dark_theme(self):
        """Apply dark theme to certain widgets."""
        widgets_to_theme = [self.button_open, self.progress_label, self.canvas_frame]
        for widget in widgets_to_theme:
            self.apply_dark_theme_to_widget(widget)

        # Other widgets:
        self.canvas.configure(bg=DARK_COLOR, highlightbackground=DARK_COLOR)
        self.scrollbar.configure(bg=LIGHT_DARK_COLOR, troughcolor=DARK_COLOR, activebackground=LIGHT_DARK_COLOR)

    def apply_dark_theme_to_widget(self, widget):
        """Apply dark theme to a specific widget."""
        widget_type = widget.winfo_class()
        if widget_type in ["Button", "TButton"]:
            widget.configure(bg=LIGHT_DARK_COLOR, fg=TEXT_COLOR, activebackground=DARK_COLOR, activeforeground=TEXT_COLOR)
        elif widget_type in ["Label", "TLabel", "Frame", "TFrame"]:
            widget.configure(bg=DARK_COLOR, fg=TEXT_COLOR)

    def on_canvas_configure(self, event):
        """Adjust the scrollable region of the canvas."""
        self.canvas.config(scrollregion=self.canvas.bbox("all"))


    def process_folder(self):
        """Choose a folder and process its image files."""
        folder_path = filedialog.askdirectory()
        if not folder_path:
            return
        
        self.clear_canvas()

        self.button_open.config(state='disabled')
        self.button_stop.grid(row=0, column=5, pady=10, sticky="w")  
        image_files = [f for f in os.listdir(folder_path) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
        
        self.progress_bar.grid(row=0, column=3, pady=10)
        self.progress_label.grid(row=0, column=4, pady=10, padx=5)

        threading.Thread(target=self._process_images_in_folder, args=(folder_path, image_files)).start()

    def _process_images_in_folder(self, folder_path, image_files):
        """Classify and detect objects in images within a folder."""
        total_images = len(image_files)
        self.progress_bar["maximum"] = total_images
        
        for idx, image_file in enumerate(image_files):

            if self.stop_requested:
                self.stop_requested = False  
                self.root.after(0, self.finish_processing)
                return

            image_path = os.path.join(folder_path, image_file)
            classes = self.vit_classifier.classify(image_path)
            detected_objects = self.detr_detector.detect(image_path)

            self.root.after(0, self.update_progress_and_canvas, idx, total_images, image_path, image_file, classes + detected_objects)

            if self.trust_ai.get():
                tags_states = {tag: tk.BooleanVar(value=True) for tag in classes + detected_objects}
                self.apply_tags(image_file,image_path, tags_states)

        self.root.after(0, self.finish_processing)

    def update_progress_and_canvas(self, idx, total_images, image_path, image_file, combined_results):
        """Update the progress bar and add new results to the canvas."""
        self.progress_var.set(idx + 1)
        self.progress_label["text"] = f"{idx + 1}/{total_images}"
        
        thumbnail = self.generate_thumbnail(image_path)
        self.display_on_canvas(thumbnail, image_file, image_path, combined_results)

    def finish_processing(self):
        """Conclude the image processing and clean up."""
        self.button_open.config(state='normal')
        self.progress_bar.grid_forget()
        self.progress_label.grid_forget()
        self.button_stop.grid_forget()

        self.show_toast(self.translator.translate("¡Todas las imágenes han sido analizadas!"), bg_color=SUCCESS_COLOR)

    def generate_thumbnail(self, image_path):
        """Generate a thumbnail for the given image."""
        img = Image.open(image_path)
        exif = img._getexif()
        img = img.convert("RGB")
                
        # Attempt to get the orientation tag from the image's EXIF data
        try:
            for orientation in ExifTags.TAGS.keys():
                if ExifTags.TAGS[orientation] == 'Orientation':
                    break
            if exif is not None and orientation in exif:
                if exif[orientation] == 2:
                    img = img.transpose(Image.FLIP_LEFT_RIGHT)
                elif exif[orientation] == 3:
                    img = img.rotate(180)
                elif exif[orientation] == 4:
                    img = img.rotate(180).transpose(Image.FLIP_LEFT_RIGHT)
                elif exif[orientation] == 5:
                    img = img.rotate(-90, expand=True).transpose(Image.FLIP_LEFT_RIGHT)
                elif exif[orientation] == 6:
                    img = img.rotate(-90, expand=True)
                elif exif[orientation] == 7:
                    img = img.rotate(90, expand=True).transpose(Image.FLIP_LEFT_RIGHT)
                elif exif[orientation] == 8:
                    img = img.rotate(90, expand=True)
        except (AttributeError, KeyError, IndexError):
            # Cases where the image doesn't have EXIF data
            print(f"No hay exif para {image_path}")
            pass
        
        img = img.resize((75, 75))
        return ImageTk.PhotoImage(img)
        
    def display_on_canvas(self, thumbnail, image_file, image_path, tags):
        """Display the thumbnail and associated tags on the canvas."""
        frame_bg = DARK_COLOR if len(self.canvas_frame.winfo_children()) % 2 == 0 else EVEN_DARKER_COLOR

        main_frame = tk.Frame(self.canvas_frame, bd=0, relief="flat", bg=frame_bg)  
        main_frame.pack(fill="x", expand=True, padx=0, pady=0)

        img_label = tk.Label(main_frame, image=thumbnail, bg=frame_bg)
        img_label.image = thumbnail
        img_label.pack(side="left", padx=10)
        img_label.bind("<Button-1>", lambda event: self.open_image(image_path))

        right_frame = tk.Frame(main_frame, bd=0, relief="flat", bg=frame_bg) 
        right_frame.pack(side="right", fill="both", expand=True)

        tk.Label(right_frame, text=image_file, bg=frame_bg, fg=TEXT_COLOR).pack(anchor="w")

        tags_frame = tk.Frame(right_frame, bg=frame_bg)  
        tags_states = {}
        for idx, tag in enumerate(tags):
            tags_states[tag] = tk.BooleanVar(value=True)
            
            chk = tk.Checkbutton(tags_frame, text=tag, var=tags_states[tag], bg=frame_bg, fg=TEXT_COLOR, selectcolor=EVEN_DARKER_COLOR)
            chk.grid(row=idx // 3, column=idx % 3, sticky="w")

        tags_frame.pack(anchor="w", pady=5, expand=True, fill="both")

        apply_btn = tk.Button(right_frame, text=self.translator.translate("Aplicar todo"), command=lambda: self.apply_tags(image_file, image_path,tags_states))
        self.apply_dark_theme_to_widget(apply_btn)
        apply_btn.pack(anchor="w", pady=5)

    def apply_tags(self, image_name, image_path,tags_states):
        """Apply tags to the image metadata."""
        enabled_tags = [tag for tag, state in tags_states.items() if state.get()]

        apply_to_raw_files = self.apply_to_raw.get()

        self.image_writer.writeTagsFromPredictionsInImages([Prediction(image_path,enabled_tags)],apply_to_raw_files,True)
        self.show_toast(f"{self.translator.translate('Etiquetas aplicadas para')} {image_name}!")

    def show_toast(self, message, duration=2000, bg_color=None):
        """Show a passive popup message for a specified duration."""
        if not bg_color:
            bg_color = TOAST_COLOR  

        toast = tk.Toplevel(self.root)
        toast.configure(bg=bg_color)
        toast.overrideredirect(True)  # Remove window decorations
        tk.Label(toast, text=message, bg=bg_color, fg=TEXT_COLOR, padx=10, pady=5).pack()
        
        # Center the toast message on the main window
        x = self.root.winfo_x() + (self.root.winfo_width() // 2) - (toast.winfo_reqwidth() // 2)
        y = self.root.winfo_y() + (self.root.winfo_height() // 2) - (toast.winfo_reqheight() // 2)
        toast.geometry(f"+{x}+{y}")

        # Destroy the toast after the specified duration
        self.root.after(duration, toast.destroy)


    def clear_canvas(self):
        """Clear all items from the canvas."""
        for widget in self.canvas_frame.winfo_children():
            widget.destroy()
        self.canvas.configure(scrollregion=(0, 0, 0, 0))

    def open_image(self, path):
        """Open image with default viewer."""
        os.startfile(path)


if __name__ == "__main__":
    root = tk.Tk()  # Create main window
    app = ImageClassifierApp(root)  # Create the application instance
    root.mainloop()  # Start the main loop
