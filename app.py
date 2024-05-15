# Required imports
import os
import threading
import time
import tkinter as tk
from tkinter import ttk
from PIL import ImageTk
import queue

# Custom module imports
from ImageClasifier import ImageClassifier
from ImageDetector import ObjectDetector
from ImageWriter import ImageWriter
from Translator import Translator
from ImageUtils import ImageUtils

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
        self.setup_treeview() 
        self.setup_preview_frame()
        # Initialize machine learning models and utility
        self.vit_classifier = ImageClassifier()
        self.detr_detector = ObjectDetector()
        self.image_writer = ImageWriter()
        self.stop_requested = False  # Control variable for stopping a long process
        self.last_selected_folder = None
        self.all_thumbnails = []


    def setup_root(self):
        """Configure the main window properties."""
        self.root.title(self.translator.translate("app_title"))
        self.root.configure(bg=DARK_COLOR)
        self.root.grid_rowconfigure(1, weight=2)
        self.root.grid_columnconfigure(3, weight=0)
        self.root.grid_columnconfigure(0, weight=0, minsize=200)  # Asegura un tamaño mínimo para la columna que contiene el treeview
        self.root.grid_columnconfigure(1, weight=1) 

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

        # Dark theme for Treeview
        style.configure("Treeview", 
                        background=DARK_COLOR, 
                        foreground=TEXT_COLOR, 
                        fieldbackground=DARK_COLOR,
                        insertbackground=TEXT_COLOR)
        
        style.map("Treeview", 
                background=[('selected', LIGHT_DARK_COLOR)])
        
        style.configure("Treeview.Heading", 
                        background=LIGHT_DARK_COLOR, 
                        foreground=TEXT_COLOR, 
                        relief="flat")

        style.map("Treeview.Heading", 
                background=[('active', EVEN_DARKER_COLOR)])
        
        style.configure("Vertical.TScrollbar", 
                gripcount=0,
                background=LIGHT_DARK_COLOR,
                troughcolor=DARK_COLOR,
                arrowcolor=TEXT_COLOR)

        style.map("Vertical.TScrollbar", 
                background=[('pressed', EVEN_DARKER_COLOR), ('active', LIGHT_DARK_COLOR)])

    def setup_widgets(self):
        """Set up the main interface widgets."""
        # Set up widgets like buttons, checkboxes, progress bars, etc.
        self.button_open = tk.Button(self.root, text=self.translator.translate("process_folder_btn"), command=self.process_folder)
        self.apply_dark_theme_to_widget(self.button_open)
        self.button_open.grid(row=0, column=0, pady=10, sticky="w")
        
        self.apply_to_raw = tk.BooleanVar(value=False)
        self.trust_ai = tk.BooleanVar(value=False)
            
        self.raw_option_chk = tk.Checkbutton(self.root, text=self.translator.translate("apply_raw_chk"), variable=self.apply_to_raw, bg=DARK_COLOR, fg=TEXT_COLOR, selectcolor=EVEN_DARKER_COLOR)
        self.raw_option_chk.grid(row=0, column=1, pady=10, sticky="w")
            
        self.trust_ai_chk = tk.Checkbutton(self.root, text=self.translator.translate("trust_ai_chk"), variable=self.trust_ai, bg=DARK_COLOR, fg=TEXT_COLOR, selectcolor=EVEN_DARKER_COLOR)
        self.trust_ai_chk.grid(row=0, column=2, pady=10, sticky="w")

        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(self.root, orient="horizontal", length=300, mode="determinate", variable=self.progress_var)

        self.progress_label = tk.Label(self.root, text="0/0")
        self.apply_dark_theme_to_widget(self.progress_label)


        self.button_stop = tk.Button(self.root, text=self.translator.translate("stop_btn"), command=self.stop_process)
        self.apply_dark_theme_to_widget(self.button_stop)

        self.setup_canvas()

    def stop_process(self):
        """Interrupt the current processing."""
        self.stop_requested = True
        self.button_stop.grid_forget()

    def setup_canvas(self):
        """Set up the canvas and associated scrollbar."""
        self.canvas = tk.Canvas(self.root, bg=DARK_COLOR, highlightbackground=DARK_COLOR)
        self.canvas.grid(row=1, column=1, columnspan=3, sticky="nsew", padx=20, pady=20) 

        self.scrollbar = tk.Scrollbar(self.root, orient="vertical", command=self.canvas.yview)
        self.scrollbar.grid(row=1, column=4, sticky="ns")

        self.canvas.config(yscrollcommand=self.scrollbar.set, scrollregion=self.canvas.bbox("all"))
        self.canvas_frame = tk.Frame(self.canvas, bg=DARK_COLOR)
        self.canvas.create_window((0,0), window=self.canvas_frame, anchor="nw")
        self.canvas_frame.bind("<Configure>", self.on_canvas_configure)

        self.root.bind("<MouseWheel>", self._on_mousewheel) 

    def setup_preview_frame(self):
        """Set up the frame for image previews on the right side."""
        self.preview_frame = tk.Frame(self.root, bg=DARK_COLOR)
        self.preview_frame.grid(row=1, column=5, sticky="nswe", padx=10, pady=10)
        # Initialize with an empty label for image preview
        self.preview_image_label = tk.Label(self.preview_frame, bg=DARK_COLOR)
        self.preview_image_label.pack(pady=20)
        
        # Add labels to display information
        self.file_name_label = tk.Label(self.preview_frame, bg=DARK_COLOR, fg=TEXT_COLOR)
        self.file_name_label.pack(pady=5, anchor="w")

        self.file_path_label = tk.Label(self.preview_frame, bg=DARK_COLOR, fg=TEXT_COLOR)
        self.file_path_label.pack(pady=5, anchor="w")

        self.keywords_label = tk.Label(self.preview_frame, bg=DARK_COLOR, fg=TEXT_COLOR)
        self.keywords_label.pack(pady=5, anchor="w")
        self.setup_keywords_controls()

    def setup_keywords_controls(self):
        """Configura los controles para añadir y seleccionar keywords en el frame de previsualización."""

        self.keywords_title_label = tk.Label(self.preview_frame, text=self.translator.translate("keywords_title"), bg=DARK_COLOR, fg=TEXT_COLOR)
        self.keywords_title_label.pack(pady=5, anchor="w")
        
        self.keyword_entry = tk.Entry(self.preview_frame, bg=DARK_COLOR, fg=TEXT_COLOR)
        self.keyword_entry.pack(pady=5)
        
        self.add_keyword_button = tk.Button(self.preview_frame, text=self.translator.translate("add_keyword_btn"), command=self.add_custom_keyword)
        self.add_keyword_button.pack(pady=5)
        
        self.apply_dark_theme_to_widget(self.add_keyword_button)
        
        self.keywords_checkbuttons_frame = tk.Frame(self.preview_frame, bg=DARK_COLOR)
        self.keywords_checkbuttons_frame.pack(pady=5)
        
        self.apply_keywords_button = tk.Button(
            self.preview_frame, 
            text=self.translator.translate("apply_tags_btn"), 
            command=lambda: (
                self.apply_tags(os.path.basename(self.file_path_label.cget("text")), self.file_path_label.cget("text"), self.keywords_vars),
                self.show_preview(self.file_path_label.cget("text"))
            )
        )

        self.apply_keywords_button.pack(pady=5)
        
        self.apply_dark_theme_to_widget(self.apply_keywords_button)


    def load_keywords_checkboxes(self, keywords):
        """Carga los checkboxes con los keywords actuales."""
        
        for widget in self.keywords_checkbuttons_frame.winfo_children():
            widget.destroy()
        
        self.keywords_vars = {keyword: tk.BooleanVar(value=True) for keyword in keywords}
        
        for idx, keyword in enumerate(keywords):
            chk = tk.Checkbutton(self.keywords_checkbuttons_frame, text=keyword, var=self.keywords_vars[keyword], bg=DARK_COLOR, fg=TEXT_COLOR, selectcolor=EVEN_DARKER_COLOR)
            chk.grid(row=idx // 3, column=idx % 3, sticky="w")


    def add_custom_keyword(self):
        """Add a new keyword and display it as a checkbox."""
        
        new_keyword = self.keyword_entry.get().strip()
        
        if new_keyword and new_keyword not in self.keywords_vars:
            self.keywords_vars[new_keyword] = tk.BooleanVar(value=True)
            chk = tk.Checkbutton(self.keywords_checkbuttons_frame, text=new_keyword, var=self.keywords_vars[new_keyword], bg=DARK_COLOR, fg=TEXT_COLOR, selectcolor=EVEN_DARKER_COLOR)
            chk.grid(row=len(self.keywords_vars) // 3, column=len(self.keywords_vars) % 3, sticky="w")



    def _on_mousewheel(self, event):
        """Scroll the canvas with the mouse wheel."""
        if event.num == 4:
            self.canvas.yview_scroll(-1, "units")
        elif event.num == 5: 
            self.canvas.yview_scroll(1, "units")
        else:
            self.canvas.yview_scroll(-1*(event.delta//120), "units")

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
        """Process all the images in the currently expanded folder in the treeview."""
        
        # Identify the current selected item in the treeview
        item_id = self.folder_tree.focus()
        
        if not item_id:
            return  # Return if no folder is selected

        # Get the folder path from the selected item
        folder_path = self.folder_tree.item(item_id, 'values')[0]
        
        # Check if it's a directory, if not, it might be an image so we get its parent directory
        if not os.path.isdir(folder_path):
            folder_path = os.path.dirname(folder_path)
        
        # List all the image files in that directory
        image_files = [os.path.join(folder_path, f) for f in os.listdir(folder_path) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]

        # Check if there are any image files to process
        if not image_files:
            self.show_toast(self.translator.translate("no_images_message"))
            return
        
        # Clear the canvas to prepare for the results
        self.clear_canvas()

        # Make the "Stop" button visible and disable the "Process Folder" button
        self.button_open.config(state='disabled')
        self.button_stop.grid(row=0, column=5, pady=10, sticky="w")

        # Set up the progress bar
        self.progress_bar.grid(row=0, column=3, pady=10)
        self.progress_label.grid(row=0, column=4, pady=10, padx=5)

        # Start the thread to process the images
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
        
        thumbnail = ImageUtils.generate_thumbnail(image_path)
        self.all_thumbnails.append(thumbnail)
        self.display_on_canvas(thumbnail, image_file, image_path, combined_results)

    def finish_processing(self):
        """Conclude the image processing and clean up."""
        self.button_open.config(state='normal')
        self.progress_bar.grid_forget()
        self.progress_label.grid_forget()
        self.button_stop.grid_forget()

        self.show_toast(self.translator.translate("images_analyzed"), bg_color=SUCCESS_COLOR)
        
    def display_on_canvas(self, thumbnail, image_file, image_path, tags):
        """Display the thumbnail and associated tags on the canvas."""
        frame_bg = DARK_COLOR if len(self.canvas_frame.winfo_children()) % 2 == 0 else EVEN_DARKER_COLOR

        main_frame = tk.Frame(self.canvas_frame, bd=0, relief="flat", bg=frame_bg)  
        main_frame.pack(fill="x", expand=True, padx=0, pady=0)

        thumbnail_tk = ImageTk.PhotoImage(thumbnail)

        img_label = tk.Label(main_frame, image=thumbnail_tk, bg=frame_bg)
        img_label.image = thumbnail_tk
        img_label.pack(side="left", padx=10)
        img_label.bind("<Button-1>", lambda event: self.on_list_item_click(image_path))

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

        apply_btn = tk.Button(right_frame, text=self.translator.translate("apply_all"), command=lambda: self.apply_tags(image_file, image_path,tags_states))
        self.apply_dark_theme_to_widget(apply_btn)
        apply_btn.pack(anchor="w", pady=5)

    def apply_tags(self, image_name, image_path,tags_states):
        """Apply tags to the image metadata."""
        enabled_tags = [tag for tag, state in tags_states.items() if state.get()]

        apply_to_raw_files = self.apply_to_raw.get()

        self.image_writer.writeTagsFromPredictionsInImages([Prediction(image_path,enabled_tags)],apply_to_raw_files,True)
        self.show_toast(f"{self.translator.translate('tags_applied_for')} {image_name}!")

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
        self.all_thumbnails.clear()

    def open_image(self, path):
        """Open image with default viewer."""
        os.startfile(path)

    def setup_treeview(self):
        """Set up the folder treeview and its functionalities."""
        self.folder_frame = tk.Frame(self.root)
        self.folder_frame.grid(row=1, column=0, sticky="nswe", padx=0, pady=10)
        self.folder_tree = ttk.Treeview(self.folder_frame, selectmode="browse")
        self.folder_tree.pack(fill="both", expand=True, side="left")

        # Adding vertical scrollbar
        self.folder_scroll = ttk.Scrollbar(self.folder_frame, orient="vertical", command=self.folder_tree.yview)
        self.folder_scroll.pack(side="right", fill="y")
        self.folder_tree.configure(yscrollcommand=self.folder_scroll.set)

        self.folder_tree.bind("<<TreeviewSelect>>", self.on_folder_select)
        self.folder_tree.bind("<MouseWheel>", self.on_treeview_scroll)

        self.load_top_folders()

    def on_treeview_scroll(self, event):
        """Handle the scroll event on the treeview and stop its propagation."""
        self.folder_tree.yview_scroll(-1*(event.delta//120), "units")
        return "break"

    def on_folder_select(self, event):
        item_id = self.folder_tree.focus()
        folder_path = self.folder_tree.item(item_id, 'values')[0]

        if self.last_selected_folder == folder_path:
            return
        
        self.last_selected_folder = folder_path

        # Handle subfolders
        if self.folder_tree.get_children(item_id) in ((), None) or len(self.folder_tree.get_children(item_id)) == 1:
            self.folder_tree.delete(*self.folder_tree.get_children(item_id))
            try:
                for subfolder in os.listdir(folder_path):
                    full_path = os.path.join(folder_path, subfolder)
                    if os.path.isdir(full_path):
                        self.add_folder(subfolder, item_id)
            except (PermissionError, FileNotFoundError) as e:
                print(f"Error al acceder a {folder_path}: {e}")

        # Clear the canvas for images
        self.clear_canvas()

        # Collect image paths and move the image processing to a separate thread
        image_files = [os.path.join(folder_path, f) for f in os.listdir(folder_path) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]

        # Use a queue to pass image paths between threads
        self.image_queue = queue.Queue()
        for image_path in image_files:
            self.image_queue.put(image_path)

        # Start the thread to process and display images
        threading.Thread(target=self.process_images_from_queue).start()



    def process_images_from_queue(self):
        self.clear_canvas()  # Clear the canvas before displaying the images
        if self.image_queue.empty():  # Check if the queue is empty
            return  # If the queue is empty, simply return without showing the toast
        while not self.image_queue.empty():
            image_path = self.image_queue.get()
            self.root.after_idle(self.display_image_on_canvas, image_path)
            time.sleep(0.05)  # Small delay to allow the UI to refresh
        # Show a toast when all files are listed
        self.show_toast("¡Todas las imágenes han sido listadas!")




    def display_image_on_canvas(self, image_path):
        """Display an image thumbnail on the canvas."""
        thumbnail_img = ImageUtils.generate_thumbnail(image_path)
        thumbnail = ImageTk.PhotoImage(thumbnail_img)
        
        frame_bg = DARK_COLOR if len(self.canvas_frame.winfo_children()) % 2 == 0 else EVEN_DARKER_COLOR

        main_frame = tk.Frame(self.canvas_frame, bd=0, relief="flat", bg=frame_bg)  
        main_frame.pack(fill="x", expand=True, padx=0, pady=0)

        img_label = tk.Label(main_frame, image=thumbnail, bg=frame_bg)
        img_label.image = thumbnail
        img_label.pack(side="left", padx=10)
        img_label.bind("<Button-1>", lambda event: self.on_list_item_click(image_path)) # self.open_image(image_path)

        right_frame = tk.Frame(main_frame, bd=0, relief="flat", bg=frame_bg) 
        right_frame.pack(side="right", fill="both", expand=True)

        tk.Label(right_frame, text=os.path.basename(image_path), bg=frame_bg, fg=TEXT_COLOR).pack(anchor="w")

        # main_frame.bind("<Button-1>", lambda event: self.on_list_item_click(image_path, os.path.basename(image_path)))

    def on_list_item_click(self, image_path):
        """Handles a click on an item in the list."""
        print(f"Clicked on {image_path}")
        # Mostrar la vista previa a la derecha
        self.show_preview(image_path)

    
    def show_preview(self, image_path):
        """Show an enlarged preview of the image in the right frame."""
        larger_thumbnail_img = ImageUtils.generate_thumbnail(image_path, base_size=400)
        larger_thumbnail = ImageTk.PhotoImage(larger_thumbnail_img)
        
        self.preview_image_label.configure(image=larger_thumbnail)
        self.preview_image_label.image = larger_thumbnail 
        self.preview_image_label.bind("<Button-1>", lambda event: self.open_image(image_path))

        # Actualizar las etiquetas con la información adecuada
        self.file_name_label.config(text=os.path.basename(image_path))
        self.file_path_label.config(text=image_path)

        keywords = ImageUtils.get_iptc_keywords(image_path)
        formatted_keywords = [keyword.decode('utf-8') for keyword in keywords] if keywords else []
        self.load_keywords_checkboxes(formatted_keywords)


    def load_top_folders(self):
        """Load the root folders, such as drives on Windows."""
        for drive in [d for d in [drive + ":\\" for drive in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'] if os.path.exists(d)]:
            self.add_folder(drive, "")

    def add_folder(self, folder, parent):
        """Add a folder to the treeview."""
        folder_path = folder if parent == "" else os.path.join(self.folder_tree.item(parent, 'values')[0], folder)
        try:
            folder_id = self.folder_tree.insert(parent, "end", text=folder, values=[folder_path])
            if os.path.isdir(folder_path):
                # Add a dummy child to make this folder expandable
                self.folder_tree.insert(folder_id, "end")
        except PermissionError:
            pass


    def on_folder_expand(self, event):
        item_id = self.folder_tree.focus()
        folder_path = self.folder_tree.item(item_id, 'values')[0]
        self.folder_tree.delete(*self.folder_tree.get_children(item_id))
        
        try:
            for subfolder in os.listdir(folder_path):
                full_path = os.path.join(folder_path, subfolder)
                if os.path.isdir(full_path):
                    self.add_folder(subfolder, item_id)
        except PermissionError:
            pass


if __name__ == "__main__":
    root = tk.Tk()  # Create main window
    app = ImageClassifierApp(root)  # Create the application instance
    root.mainloop()  # Start the main loop
