import logging
import tkinter as tk
import customtkinter as ctk
from typing import Optional

logger = logging.getLogger("AutoTyperPro")

try:
    from CTkMessagebox import CTkMessagebox
except ImportError:
    logger.warning("CTkMessagebox module not found. Falling back to standard tkinter messagebox.")
    CTkMessagebox = None

class NotificationService:
    """Provides application-wide visual cues, modal message boxes, and non-blocking toast overlays."""
    def __init__(self, root: Optional[ctk.CTk] = None):
        self.root = root

    def set_root(self, root: ctk.CTk):
        self.root = root

    def show_info(self, title: str, message: str):
        logger.info(f"Notification Alert (Info): {title} - {message}")
        if CTkMessagebox:
            CTkMessagebox(title=title, message=message, icon="info")
        else:
            tk.messagebox.showinfo(title, message)

    def show_warning(self, title: str, message: str):
        logger.warning(f"Notification Alert (Warning): {title} - {message}")
        if CTkMessagebox:
            CTkMessagebox(title=title, message=message, icon="warning")
        else:
            tk.messagebox.showwarning(title, message)

    def show_error(self, title: str, message: str):
        logger.error(f"Notification Alert (Error): {title} - {message}")
        if CTkMessagebox:
            CTkMessagebox(title=title, message=message, icon="cancel")
        else:
            tk.messagebox.showerror(title, message)

    def show_toast(self, message: str, level: str = "info", duration_ms: int = 3000):
        """Displays a modern, styled overlay toast inside the active main window."""
        if not self.root:
            logger.info(f"Toast (No window): {message}")
            return

        logger.debug(f"Toast: {message}")
        
        # Color mapping based on theme aesthetics
        colors = {
            "info": ("#1F6AA5", "#242424"),      # Sleek blue
            "success": ("#2ED573", "#1B2F22"),   # Vibrant green
            "warning": ("#FFA502", "#352A18"),   # Warm orange
            "error": ("#FF4757", "#3C1E22")      # Premium red
        }
        
        fg_color, bg_color = colors.get(level, colors["info"])
        
        # Create float frame
        toast_frame = ctk.CTkFrame(
            master=self.root,
            corner_radius=10,
            border_width=1,
            border_color=fg_color,
            fg_color=bg_color
        )
        
        label = ctk.CTkLabel(
            master=toast_frame,
            text=message,
            font=ctk.CTkFont(family="Inter", size=13, weight="bold"),
            text_color="#FFFFFF"
        )
        label.pack(padx=20, pady=10)
        
        # Placement calculation (top center overlay)
        toast_frame.update_idletasks()
        
        # Position toast at bottom-right or top-center. Top-center is very clean.
        def position_toast():
            try:
                win_width = self.root.winfo_width()
                toast_width = toast_frame.winfo_reqwidth()
                x_pos = (win_width - toast_width) // 2
                toast_frame.place(x=x_pos, y=25)
            except Exception:
                pass
                
        position_toast()
        
        # Fade-out / destroy scheduled
        def destroy_toast():
            try:
                toast_frame.destroy()
            except Exception:
                pass
                
        self.root.after(duration_ms, destroy_toast)
