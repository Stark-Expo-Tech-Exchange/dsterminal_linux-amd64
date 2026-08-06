"""
PDF Copy Protection Tool - Working Version
Converts PDF to images to prevent text copying
"""

import os
import io
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from pypdf import PdfReader, PdfWriter

# Check if required libraries are installed
try:
    import fitz  # PyMuPDF
    from PIL import Image
    PYMUPDF_AVAILABLE = True
except ImportError:
    PYMUPDF_AVAILABLE = False
    print("âš ï¸ PyMuPDF not installed. Run: pip install PyMuPDF pillow")

def protect_pdf_by_image_conversion(input_pdf_path, output_pdf_path, dpi=200):
    """
    Convert PDF pages to images to prevent text selection/copying
    This is the most reliable method
    """
    if not PYMUPDF_AVAILABLE:
        return False, "PyMuPDF not installed. Please install: pip install PyMuPDF pillow"
    
    try:
        # Open the PDF
        doc = fitz.open(input_pdf_path)
        writer = PdfWriter()
        total_pages = len(doc)
        
        for page_num in range(total_pages):
            page = doc[page_num]
            
            # Render page to image with high quality
            mat = fitz.Matrix(dpi/72, dpi/72)
            pix = page.get_pixmap(matrix=mat, colorspace=fitz.csRGB)
            
            # Convert to PIL Image
            img_data = pix.tobytes("png")
            img = Image.open(io.BytesIO(img_data))
            
            # Convert PIL Image to PDF page
            img_byte_arr = io.BytesIO()
            img.save(img_byte_arr, format='PDF', quality=95)
            img_byte_arr.seek(0)
            
            img_pdf = PdfReader(img_byte_arr)
            writer.add_page(img_pdf.pages[0])
            
            # Update progress (if callback provided)
            if hasattr(protect_pdf_by_image_conversion, 'progress_callback'):
                progress = (page_num + 1) / total_pages * 100
                protect_pdf_by_image_conversion.progress_callback(progress)
        
        doc.close()
        
        # Save the protected PDF
        with open(output_pdf_path, "wb") as f:
            writer.write(f)
        
        return True, "PDF protected successfully!"
        
    except Exception as e:
        return False, f"Error: {str(e)}"

class PDFProtectorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("PDF Copy Protection Tool")
        self.root.geometry("750x600")
        self.root.resizable(False, False)
        self.root.configure(bg="#f0f0f0")
        
        # Variables
        self.input_path = tk.StringVar()
        self.output_path = tk.StringVar()
        self.dpi = tk.IntVar(value=200)
        self.is_processing = False
        
        self.setup_ui()
        self.check_libraries()
    
    def check_libraries(self):
        """Check if required libraries are installed"""
        if not PYMUPDF_AVAILABLE:
            messagebox.showwarning(
                "Missing Library",
                "PyMuPDF is not installed.\n\n"
                "Please install it using:\n"
                "pip install PyMuPDF pillow\n\n"
                "The application will still work with overlay method."
            )
    
    def setup_ui(self):
        """Setup the user interface"""
        # Header
        header = tk.Frame(self.root, bg="#2196F3", height=90)
        header.pack(fill="x")
        header.pack_propagate(False)
        
        tk.Label(header, text="ðŸ”’ PDF Copy Protection", 
                font=("Segoe UI", 22, "bold"), bg="#2196F3", fg="white").pack(pady=15)
        
        tk.Label(header, text="Convert PDF to images to prevent text selection and copying", 
                font=("Segoe UI", 10), bg="#2196F3", fg="white").pack()
        
        # Main content
        main_frame = tk.Frame(self.root, bg="#f0f0f0", padx=25, pady=20)
        main_frame.pack(fill="both", expand=True)
        
        # Step 1: Select PDF
        step1_frame = tk.LabelFrame(main_frame, text="ðŸ“ Step 1: Select PDF File", 
                                    font=("Segoe UI", 11, "bold"), bg="#f0f0f0",
                                    padx=10, pady=10)
        step1_frame.pack(fill="x", pady=5)
        
        file_select_frame = tk.Frame(step1_frame, bg="#f0f0f0")
        file_select_frame.pack(fill="x", pady=5)
        
        tk.Button(file_select_frame, text="ðŸ“‚ Browse PDF", 
                 command=self.browse_file,
                 bg="#4CAF50", fg="white", font=("Segoe UI", 10, "bold"),
                 padx=15, pady=8, cursor="hand2").pack(side="left")
        
        self.file_label = tk.Label(file_select_frame, text="No file selected", 
                                   font=("Segoe UI", 9), fg="gray", bg="#f0f0f0")
        self.file_label.pack(side="left", padx=15)
        
        # File info
        self.file_info_frame = tk.Frame(step1_frame, bg="#f0f0f0")
        self.file_info_frame.pack(fill="x", pady=5)
        self.file_info_frame.pack_forget()
        
        self.file_size_label = tk.Label(self.file_info_frame, text="", 
                                        font=("Segoe UI", 9), fg="gray", bg="#f0f0f0")
        self.file_size_label.pack(side="left", padx=10)
        
        self.page_count_label = tk.Label(self.file_info_frame, text="", 
                                         font=("Segoe UI", 9), fg="gray", bg="#f0f0f0")
        self.page_count_label.pack(side="left", padx=20)
        
        # Step 2: Settings
        step2_frame = tk.LabelFrame(main_frame, text="âš™ï¸ Step 2: Settings", 
                                    font=("Segoe UI", 11, "bold"), bg="#f0f0f0",
                                    padx=10, pady=10)
        step2_frame.pack(fill="x", pady=10)
        
        # DPI setting
        dpi_frame = tk.Frame(step2_frame, bg="#f0f0f0")
        dpi_frame.pack(fill="x", pady=5)
        
        tk.Label(dpi_frame, text="Image Quality (DPI):", 
                font=("Segoe UI", 10), bg="#f0f0f0").pack(side="left")
        
        dpi_options = [100, 150, 200, 300]
        for dpi in dpi_options:
            rb = tk.Radiobutton(dpi_frame, text=str(dpi), variable=self.dpi, 
                               value=dpi, bg="#f0f0f0", font=("Segoe UI", 9))
            rb.pack(side="left", padx=10)
        
        tk.Label(dpi_frame, text="(Higher DPI = Better quality, Larger file)", 
                font=("Segoe UI", 8), fg="gray", bg="#f0f0f0").pack(side="left", padx=10)
        
        # Method info
        method_frame = tk.Frame(step2_frame, bg="#f0f0f0")
        method_frame.pack(fill="x", pady=5)
        
        tk.Label(method_frame, text="ðŸ”’ Method: Convert to Images", 
                font=("Segoe UI", 10, "bold"), fg="#2196F3", bg="#f0f0f0").pack(side="left")
        
        tk.Label(method_frame, text="(Text becomes completely unselectable)", 
                font=("Segoe UI", 9), fg="gray", bg="#f0f0f0").pack(side="left", padx=10)
        
        # Step 3: Output
        step3_frame = tk.LabelFrame(main_frame, text="ðŸ’¾ Step 3: Output Location", 
                                    font=("Segoe UI", 11, "bold"), bg="#f0f0f0",
                                    padx=10, pady=10)
        step3_frame.pack(fill="x", pady=5)
        
        output_frame = tk.Frame(step3_frame, bg="#f0f0f0")
        output_frame.pack(fill="x", pady=5)
        
        tk.Entry(output_frame, textvariable=self.output_path, 
                font=("Segoe UI", 9), width=50).pack(side="left", padx=5)
        
        tk.Button(output_frame, text="ðŸ“‚ Browse", 
                 command=self.browse_output,
                 bg="#2196F3", fg="white", font=("Segoe UI", 9),
                 padx=10, pady=5, cursor="hand2").pack(side="left", padx=5)
        
        # Progress
        progress_frame = tk.Frame(main_frame, bg="#f0f0f0")
        progress_frame.pack(fill="x", pady=15)
        
        self.progress = ttk.Progressbar(progress_frame, length=500, mode='determinate')
        self.progress.pack(pady=5)
        self.progress.pack_forget()
        
        self.progress_label = tk.Label(progress_frame, text="", 
                                       font=("Segoe UI", 9), bg="#f0f0f0")
        self.progress_label.pack()
        self.progress_label.pack_forget()
        
        # Action buttons
        button_frame = tk.Frame(main_frame, bg="#f0f0f0")
        button_frame.pack(pady=15)
        
        self.protect_btn = tk.Button(button_frame, text="ðŸ”’ Protect PDF (Disable Copying)", 
                                     command=self.protect_pdf,
                                     bg="#FF5722", fg="white", font=("Segoe UI", 13, "bold"),
                                     padx=40, pady=12, state="disabled", cursor="hand2",
                                     relief="raised", bd=0)
        self.protect_btn.pack(side="left", padx=5)
        
        self.clear_btn = tk.Button(button_frame, text="ðŸ—‘ï¸ Clear All", 
                                   command=self.clear_all,
                                   bg="#757575", fg="white", font=("Segoe UI", 10),
                                   padx=15, pady=12, cursor="hand2",
                                   relief="raised", bd=0)
        self.clear_btn.pack(side="left", padx=5)
        
        # Status
        self.status_label = tk.Label(main_frame, text="Ready", 
                                     font=("Segoe UI", 10), fg="gray", bg="#f0f0f0")
        self.status_label.pack(pady=5)
        
        # Info box
        info_frame = tk.LabelFrame(main_frame, text="â„¹ï¸ How it works", 
                                   font=("Segoe UI", 9, "bold"), bg="#f0f0f0",
                                   fg="#666", padx=10, pady=5)
        info_frame.pack(fill="x", pady=10)
        
        info_text = """â€¢ Each page is converted to a high-quality image
â€¢ Text becomes part of the image - cannot be selected or copied
â€¢ PDF remains viewable and printable
â€¢ No passwords required - opens like any normal PDF
â€¢ Choose DPI: Higher = Better quality but larger file size"""
        
        tk.Label(info_frame, text=info_text, font=("Segoe UI", 8), 
                justify="left", fg="gray", bg="#f0f0f0").pack(padx=10, pady=5)
        
        # Footer
        footer = tk.Label(self.root, text="âš ï¸ Note: Prevents casual copying. Determined users may use OCR tools.", 
                         font=("Segoe UI", 8), fg="gray", bg="#f0f0f0")
        footer.pack(side="bottom", pady=5)
    
    def browse_file(self):
        """Browse for input PDF file"""
        file_path = filedialog.askopenfilename(
            title="Select PDF File",
            filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")]
        )
        if file_path:
            self.input_path.set(file_path)
            self.file_label.config(text=os.path.basename(file_path), fg="black")
            
            # Show file info
            try:
                size = os.path.getsize(file_path) / (1024 * 1024)
                self.file_size_label.config(text=f"Size: {size:.2f} MB")
                
                # Get page count
                doc = fitz.open(file_path)
                pages = len(doc)
                doc.close()
                self.page_count_label.config(text=f"Pages: {pages}")
                self.file_info_frame.pack(fill="x", pady=5)
            except:
                self.file_info_frame.pack_forget()
            
            # Auto-generate output path
            base, ext = os.path.splitext(file_path)
            self.output_path.set(f"{base}_protected_no_copy{ext}")
            
            self.protect_btn.config(state="normal")
            self.status_label.config(text="âœ… File loaded. Ready to protect.", fg="green")
    
    def browse_output(self):
        """Browse for output PDF location"""
        file_path = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")],
            initialfile=os.path.basename(self.output_path.get()) if self.output_path.get() else "protected.pdf"
        )
        if file_path:
            self.output_path.set(file_path)
    
    def clear_all(self):
        """Clear all selections"""
        self.input_path.set("")
        self.output_path.set("")
        self.file_label.config(text="No file selected", fg="gray")
        self.file_info_frame.pack_forget()
        self.protect_btn.config(state="disabled")
        self.status_label.config(text="Ready", fg="gray")
        self.progress.pack_forget()
        self.progress_label.pack_forget()
    
    def update_progress(self, value):
        """Update progress bar"""
        self.progress['value'] = value
        self.progress_label.config(text=f"Processing... {int(value)}%")
        self.root.update()
    
    def protect_pdf(self):
        """Start PDF protection process"""
        if not self.input_path.get():
            messagebox.showerror("Error", "Please select a PDF file")
            return
        
        if not self.output_path.get():
            messagebox.showerror("Error", "Please specify output location")
            return
        
        if not PYMUPDF_AVAILABLE:
            messagebox.showerror("Missing Library", 
                "PyMuPDF is not installed.\n\n"
                "Please install it using:\n"
                "pip install PyMuPDF pillow")
            return
        
        # Check if input and output are the same
        if self.input_path.get() == self.output_path.get():
            if not messagebox.askyesno("Warning", 
                "Input and output files are the same.\nThis will overwrite the original file.\n\nContinue?"):
                return
        
        # Disable buttons
        self.is_processing = True
        self.protect_btn.config(state="disabled")
        self.clear_btn.config(state="disabled")
        
        # Show progress
        self.progress.pack(fill="x", pady=5)
        self.progress_label.pack()
        self.progress['value'] = 0
        self.progress_label.config(text="Starting...")
        self.status_label.config(text="ðŸ”„ Processing...", fg="blue")
        self.root.update()
        
        # Register progress callback
        protect_pdf_by_image_conversion.progress_callback = self.update_progress
        
        # Run in separate thread
        thread = threading.Thread(target=self._do_protect)
        thread.daemon = True
        thread.start()
    
    def _do_protect(self):
        """Actual protection logic (runs in thread)"""
        input_path = self.input_path.get()
        output_path = self.output_path.get()
        dpi = self.dpi.get()
        
        try:
            success, message = protect_pdf_by_image_conversion(input_path, output_path, dpi)
            
            # Update GUI in main thread
            self.root.after(0, self._protection_done, success, message)
            
        except Exception as e:
            self.root.after(0, self._protection_done, False, f"Error: {str(e)}")
    
    def _protection_done(self, success, message):
        """Called when protection is complete"""
        self.is_processing = False
        self.protect_btn.config(state="normal" if self.input_path.get() else "disabled")
        self.clear_btn.config(state="normal")
        
        self.progress.pack_forget()
        self.progress_label.pack_forget()
        
        if success:
            self.status_label.config(text="âœ… Protection complete!", fg="green")
            self.progress['value'] = 100
            
            # Show success dialog with options
            result = messagebox.askyesno(
                "Success! ðŸŽ‰",
                f"âœ… PDF protected successfully!\n\n"
                f"ðŸ“ Output: {os.path.basename(self.output_path.get())}\n\n"
                f"ðŸ”’ Text selection and copying has been disabled.\n\n"
                f"Would you like to open the folder containing the protected PDF?"
            )
            
            if result:
                # Open folder
                folder = os.path.dirname(self.output_path.get())
                if os.name == 'nt':  # Windows
                    os.startfile(folder)
                elif os.name == 'posix':  # Mac/Linux
                    import subprocess
                    if os.uname().sysname == 'Darwin':  # Mac
                        subprocess.run(['open', folder])
                    else:  # Linux
                        subprocess.run(['xdg-open', folder])
            
        else:
            self.status_label.config(text=f"âŒ {message}", fg="red")
            messagebox.showerror("Error", f"Failed to protect PDF:\n\n{message}")

def quick_protect(input_file, output_file=None, dpi=200):
    """
    Quick function to protect a PDF from command line
    
    Args:
        input_file (str): Path to input PDF
        output_file (str): Path to output PDF (optional)
        dpi (int): Image quality (default: 200)
    
    Returns:
        str: Path to protected PDF or None if failed
    """
    if not os.path.exists(input_file):
        print(f"âŒ File not found: {input_file}")
        return None
    
    if not output_file:
        base, ext = os.path.splitext(input_file)
        output_file = f"{base}_protected_no_copy{ext}"
    
    print(f"ðŸ”„ Protecting: {os.path.basename(input_file)}")
    print(f"ðŸ“ Output: {os.path.basename(output_file)}")
    print("â³ This may take a moment...")
    
    success, message = protect_pdf_by_image_conversion(input_file, output_file, dpi)
    
    if success:
        print("âœ… Protection complete!")
        print("ðŸ”’ Text selection and copying has been disabled")
        print(f"ðŸ“ Saved as: {output_file}")
        return output_file
    else:
        print(f"âŒ Failed: {message}")
        return None

def main():
    """Main entry point"""
    # Check if running with command line arguments
    import sys
    if len(sys.argv) > 1:
        # Command line mode
        input_file = sys.argv[1]
        output_file = sys.argv[2] if len(sys.argv) > 2 else None
        quick_protect(input_file, output_file)
    else:
        # GUI mode
        root = tk.Tk()
        app = PDFProtectorApp(root)
        root.mainloop()

if __name__ == "__main__":
    main()