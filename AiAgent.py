import tkinter as tk
from tkinter import messagebox
import customtkinter as ctk
from PIL import ImageGrab
import google.generativeai as genai
import threading
import sys

# ==========================================
# CONFIGURATION
# ==========================================
GEMINI_API_KEY = "#######ADD YOUR API KEY HERE#####"

# Configure CustomTkinter theme and color
ctk.set_appearance_mode("System")  # Modes: "System" (standard), "Dark", "Light"
ctk.set_default_color_theme("blue")  # Themes: "blue" (standard), "green", "dark-blue"

class AIQuizSnipper:
    def __init__(self):
        # Setup Main Application Window
        self.root = ctk.CTk()
        self.root.title("AI Quiz Solver")
        self.root.geometry("400x530")
        self.root.resizable(False, False)
        
        # Center the window
        # self.root.eval('tk::PlaceWindow . center') - not supported fully on CTk, do manually
        self.center_window(self.root, 400, 530)
        
        # Configure the Generative AI library
        try:
            genai.configure(api_key=GEMINI_API_KEY)
            self.model = genai.GenerativeModel('gemini-2.5-flash')
        except Exception as e:
            messagebox.showerror("API Configuration Error", f"Failed to configure API: {e}")
            sys.exit(1)
            
        self.build_main_gui()

    def center_window(self, win, width, height):
        screen_width = win.winfo_screenwidth()
        screen_height = win.winfo_screenheight()
        x = int((screen_width/2) - (width/2))
        y = int((screen_height/2) - (height/2))
        win.geometry(f"{width}x{height}+{x}+{y}")

    def build_main_gui(self):
        # Create a container frame
        self.main_frame = ctk.CTkFrame(self.root, corner_radius=15)
        self.main_frame.pack(pady=20, padx=20, fill="both", expand=True)

        # Title Label
        self.lbl_title = ctk.CTkLabel(self.main_frame, text="🧠 AI Quiz Solver", 
                                      font=ctk.CTkFont(family="Segoe UI", size=24, weight="bold"))
        self.lbl_title.pack(pady=(20, 5))
        
        # Subtitle Label
        self.lbl_desc = ctk.CTkLabel(self.main_frame, text="Press the button or hit Ctrl+S to snip a question.", 
                                     font=ctk.CTkFont(family="Segoe UI", size=12), text_color="gray")
        self.lbl_desc.pack(pady=(0, 20))

        # Snip Button with modern styling
        self.btn_snip = ctk.CTkButton(self.main_frame, text="✂️ Start Snipping", 
                                      font=ctk.CTkFont(size=15, weight="bold"), 
                                      height=45, corner_radius=10, 
                                      command=self.start_snipping)
        self.btn_snip.pack(fill="x", padx=40)
        
        # OR Text Box Label
        self.lbl_or = ctk.CTkLabel(self.main_frame, text="--- OR PASTE QUESTION BELOW ---", 
                                   font=ctk.CTkFont(family="Segoe UI", size=10, weight="bold"), text_color="gray")
        self.lbl_or.pack(pady=(15, 5))
        
        # Textbox for pasting question
        self.text_input = ctk.CTkTextbox(self.main_frame, height=80, wrap="word", font=ctk.CTkFont(size=12))
        self.text_input.pack(fill="x", padx=40, pady=(0, 10))
        
        # Submit Text Button
        self.btn_submit_text = ctk.CTkButton(self.main_frame, text="📝 Analyze Text", 
                                             font=ctk.CTkFont(size=15, weight="bold"), 
                                             height=45, corner_radius=10, 
                                             command=self.process_text)
        self.btn_submit_text.pack(fill="x", padx=40)
        
        # Theme Toggle
        self.theme_var = ctk.StringVar(value="System")
        self.seg_button = ctk.CTkSegmentedButton(self.main_frame, values=["Light", "Dark", "System"],
                                                 variable=self.theme_var, command=self.change_theme)
        self.seg_button.pack(pady=(20, 10))
        
        # Shortcuts
        self.root.bind('<Control-s>', lambda e: self.start_snipping())
        self.root.bind('<Control-S>', lambda e: self.start_snipping())

    def change_theme(self, new_appearance_mode: str):
        ctk.set_appearance_mode(new_appearance_mode)

    def start_snipping(self):
        self.root.withdraw() # Hide the main window temporarily
        
        # Snip overlay must be standard Tkinter to use the transparent full-screen crosshair setup robustly
        self.snip_window = tk.Toplevel(self.root)
        self.snip_window.attributes('-fullscreen', True)
        self.snip_window.attributes('-alpha', 0.25)
        self.snip_window.configure(background='black')
        self.snip_window.config(cursor="crosshair")

        # Canvas for drawing the selection rectangle
        self.canvas = tk.Canvas(self.snip_window, cursor="crosshair", bg="black", highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)

        self.start_x = None
        self.start_y = None
        self.rect = None

        # Bind mouse events for snipping
        self.canvas.bind("<ButtonPress-1>", self.on_button_press)
        self.canvas.bind("<B1-Motion>", self.on_move_press)
        self.canvas.bind("<ButtonRelease-1>", self.on_button_release)
        
        # Allow exiting the snipping overlay with Escape key
        self.snip_window.bind("<Escape>", lambda e: self.cancel_snipping())

    def on_button_press(self, event):
        self.start_x = self.canvas.canvasx(event.x)
        self.start_y = self.canvas.canvasy(event.y)
        self.rect = self.canvas.create_rectangle(self.start_x, self.start_y, 1, 1, outline='#00ff00', width=3, fill="")

    def on_move_press(self, event):
        cur_x = self.canvas.canvasx(event.x)
        cur_y = self.canvas.canvasy(event.y)
        if self.rect:
            self.canvas.coords(self.rect, self.start_x, self.start_y, cur_x, cur_y)

    def on_button_release(self, event):
        end_x = self.canvas.canvasx(event.x)
        end_y = self.canvas.canvasy(event.y)
        
        x1 = min(self.start_x, end_x)
        y1 = min(self.start_y, end_y)
        x2 = max(self.start_x, end_x)
        y2 = max(self.start_y, end_y)

        # Remove the snipping overlay immediately
        if hasattr(self, 'snip_window') and self.snip_window.winfo_exists():
            self.snip_window.destroy()
        
        # Prevent capturing if the box is unreasonably small
        if abs(x2 - x1) < 15 or abs(y2 - y1) < 15:
            self.cancel_snipping()
            return

        # Slight delay ensures the transparent window completely vanishes from screen buffer
        self.root.after(150, lambda: self.process_image(x1, y1, x2, y2))

    def cancel_snipping(self):
        if hasattr(self, 'snip_window') and self.snip_window.winfo_exists():
            self.snip_window.destroy()
        self.root.deiconify() # Restore the main CTk window

    def process_image(self, x1, y1, x2, y2):
        try:
            image = ImageGrab.grab(bbox=(x1, y1, x2, y2))
            self.show_loading_window(x2, y2)
            
            thread = threading.Thread(target=self.call_gemini_api, args=(image, x2, y2))
            thread.start()
        except Exception as e:
            messagebox.showerror("Capture Error", f"Failed to capture screen: {e}")
            self.root.deiconify()

    def process_text(self):
        question_text = self.text_input.get("1.0", "end-1c").strip()
        if not question_text:
            messagebox.showwarning("Empty Text", "Please paste or type a question to analyze.")
            return
            
        self.root.withdraw()
        
        # Use center of the screen or close to it for loading window
        x = self.root.winfo_x() + 50
        y = self.root.winfo_y() + 50
        self.show_loading_window(x, y)
        
        thread = threading.Thread(target=self.call_gemini_api_text, args=(question_text,))
        thread.start()

    def call_gemini_api_text(self, question_text):
        try:
            prompt = (
                "Please answer the following question clearly and concisely. "
                "If it's multiple choice, indicate the correct letter and the text.\n\n"
                f"Question: {question_text}"
            )
            response = self.model.generate_content(prompt)
            answer_text = response.text
            
            # Schedule display back on main GUI thread
            self.root.after(0, self.display_answer, answer_text)
        except Exception as e:
            error_msg = f"Error communicating with AI:\n{str(e)}\n\nPlease verify your API key and connection."
            self.root.after(0, self.display_answer, error_msg)

    def show_loading_window(self, x, y):
        self.result_window = ctk.CTkToplevel(self.root)
        self.result_window.title("AI Answering...")
        
        # Keep window near mouse
        self.result_window.geometry(f"450x300+{int(min(x, self.root.winfo_screenwidth()-450))}+{int(min(y, self.root.winfo_screenheight()-300))}") 
        self.result_window.attributes('-topmost', True) 
        self.result_window.protocol("WM_DELETE_WINDOW", self.close_result_window)
        
        self.loading_frame = ctk.CTkFrame(self.result_window, fg_color="transparent")
        self.loading_frame.pack(expand=True, fill="both")

        self.lbl_status = ctk.CTkLabel(self.loading_frame, text="Analyzing Question Snippet...", 
                                       font=ctk.CTkFont(size=16, weight="bold"))
        self.lbl_status.pack(pady=(80, 20))
        
        # Animated Progress Bar
        self.progress = ctk.CTkProgressBar(self.loading_frame, orientation="horizontal", mode="indeterminate")
        self.progress.pack(pady=10, padx=50, fill="x")
        self.progress.start()

    def call_gemini_api(self, image, x, y):
        try:
            prompt = (
                "Identify the question in this image and provide the correct "
                "answer clearly and concisely. If it's multiple choice, indicate "
                "the correct letter and the text."
            )
            response = self.model.generate_content([prompt, image])
            answer_text = response.text
            
            # Schedule display back on main GUI thread
            self.root.after(0, self.display_answer, answer_text)
        except Exception as e:
            error_msg = f"Error communicating with AI:\n{str(e)}\n\nPlease verify your API key and connection."
            self.root.after(0, self.display_answer, error_msg)

    def display_answer(self, text):
        # Stop process if user closed the thinking window
        if not self.result_window.winfo_exists():
            self.root.deiconify()
            return
            
        # Clear loading animation
        self.progress.stop()
        self.loading_frame.destroy()
        
        # Build Results Area
        self.result_frame = ctk.CTkFrame(self.result_window, corner_radius=10)
        self.result_frame.pack(padx=15, pady=15, fill="both", expand=True)
        
        # Scrollable Textbox for Answer
        self.text_area = ctk.CTkTextbox(self.result_frame, wrap="word", font=ctk.CTkFont(size=14))
        self.text_area.insert("0.0", text)
        self.text_area.configure(state="disabled") # Read-only
        self.text_area.pack(padx=10, pady=10, fill="both", expand=True)

        # Buttons Frame
        self.btn_frame = ctk.CTkFrame(self.result_frame, fg_color="transparent")
        self.btn_frame.pack(fill="x", pady=10)
        
        self.btn_copy = ctk.CTkButton(self.btn_frame, text="📄 Copy to Clipboard", 
                                      command=lambda: self.copy_to_clipboard(text),
                                      fg_color="#4CAF50", hover_color="#388E3C",
                                      font=ctk.CTkFont(weight="bold"))
        self.btn_copy.pack(side="left", padx=10, expand=True, fill="x")
        
        self.btn_close = ctk.CTkButton(self.btn_frame, text="❌ Close", 
                                       command=self.close_result_window,
                                       fg_color="#F44336", hover_color="#D32F2F",
                                       font=ctk.CTkFont(weight="bold"))
        self.btn_close.pack(side="right", padx=10, expand=True, fill="x")

    def copy_to_clipboard(self, text):
        self.root.clipboard_clear()
        self.root.clipboard_append(text)
        self.root.update()
        
        # Update button text briefly for interactive feedback
        self.btn_copy.configure(text="✅ Copied!", fg_color="#2E7D32")
        self.root.after(2000, lambda: self.btn_copy.configure(text="📄 Copy to Clipboard", fg_color="#4CAF50"))

    def close_result_window(self):
        if hasattr(self, 'result_window') and self.result_window.winfo_exists():
            self.result_window.destroy()
        self.root.deiconify()

if __name__ == "__main__":
    app = AIQuizSnipper()
    app.root.mainloop()
