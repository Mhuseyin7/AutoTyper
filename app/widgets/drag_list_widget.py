import customtkinter as ctk
import tkinter as tk
from typing import List, Dict, Any, Callable, Optional

class DragListWidget(ctk.CTkScrollableFrame):
    """A premium drag-and-drop style scrollable list showing timeline steps with reordering and double-click edit hooks."""
    def __init__(self, master, on_list_changed: Callable[[List[Dict[str, Any]]], None], 
                 on_edit_item: Optional[Callable[[int, Dict[str, Any]], None]] = None, **kwargs):
        kwargs.setdefault("label_text", "Macro Action Timeline")
        kwargs.setdefault("label_font", ctk.CTkFont(family="Inter", size=12, weight="bold"))
        super().__init__(master, **kwargs)
        
        self.on_list_changed = on_list_changed
        self.on_edit_item = on_edit_item
        self.events: List[Dict[str, Any]] = []
        self.item_widgets: List[ctk.CTkFrame] = []
        
        self.grid_columnconfigure(0, weight=1)
        self._drag_start_idx: int | None = None

    def set_events(self, events: List[Dict[str, Any]]):
        """Populates the widget list with action items."""
        self.events = events
        self.refresh_list()

    def refresh_list(self):
        """Clears and rebuilds the visual listing of timeline blocks."""
        # Cleanup existing widgets
        for w in self.item_widgets:
            w.destroy()
        self.item_widgets.clear()
        
        if not self.events:
            empty_lbl = ctk.CTkLabel(
                self,
                text="No Actions in Timeline. Click buttons below to add steps.",
                font=ctk.CTkFont(family="Inter", size=11, slant="italic"),
                text_color=("#888888", "#666666")
            )
            empty_lbl.grid(row=0, column=0, padx=10, pady=20, sticky="ew")
            self.item_widgets.append(empty_lbl)
            return

        for idx, event in enumerate(self.events):
            item_frame = ctk.CTkFrame(
                self,
                corner_radius=8,
                border_width=1,
                border_color=("#E5E5E5", "#2D2D2D"),
                fg_color=("#FDFDFD", "#1C1C22")
            )
            item_frame.grid(row=idx, column=0, padx=5, pady=4, sticky="ew")
            item_frame.grid_columnconfigure(1, weight=1)
            
            # Icon / Label description
            desc, icon = self._get_event_description(event)
            
            lbl_icon = ctk.CTkLabel(
                item_frame, text=icon, font=ctk.CTkFont(size=14), width=30
            )
            lbl_icon.grid(row=0, column=0, padx=(10, 5), pady=8, sticky="w")
            
            lbl_desc = ctk.CTkLabel(
                item_frame,
                text=f"{idx + 1:02d}. {desc}",
                font=ctk.CTkFont(family="Consolas", size=11),
                anchor="w",
                justify="left"
            )
            lbl_desc.grid(row=0, column=1, padx=5, pady=8, sticky="ew")

            # Drag Bindings (clicking description starts drag reorder)
            for widget in (lbl_desc, lbl_icon, item_frame):
                widget.bind("<ButtonPress-1>", lambda e, i=idx: self._start_drag(i))
                widget.bind("<B1-Motion>", lambda e, i=idx: self._on_drag_motion(e, i))
                widget.bind("<ButtonRelease-1>", lambda e: self._stop_drag())
                
                # Double-click parameter edit hook
                if self.on_edit_item:
                    widget.bind("<Double-Button-1>", lambda e, i=idx: self.on_edit_item(i, self.events[i]))

            # Controls Panel
            controls_frame = ctk.CTkFrame(item_frame, fg_color="transparent")
            controls_frame.grid(row=0, column=2, padx=10, pady=4, sticky="e")
            
            # Up
            btn_up = ctk.CTkButton(
                controls_frame, text="▲", width=20, height=20, font=ctk.CTkFont(size=9),
                fg_color="transparent", text_color=("#444444", "#AAAAAA"),
                hover_color=("#E0E0E0", "#33333F"),
                command=lambda i=idx: self._move_item(i, -1)
            )
            btn_up.pack(side="left", padx=2)
            
            # Down
            btn_down = ctk.CTkButton(
                controls_frame, text="▼", width=20, height=20, font=ctk.CTkFont(size=9),
                fg_color="transparent", text_color=("#444444", "#AAAAAA"),
                hover_color=("#E0E0E0", "#33333F"),
                command=lambda i=idx: self._move_item(i, 1)
            )
            btn_down.pack(side="left", padx=2)
            
            # Delete
            btn_del = ctk.CTkButton(
                controls_frame, text="✕", width=20, height=20, font=ctk.CTkFont(size=9, weight="bold"),
                fg_color="transparent", text_color="#E74C3C",
                hover_color=("#FADBD8", "#3C1F1F"),
                command=lambda i=idx: self._delete_item(i)
            )
            btn_del.pack(side="left", padx=2)
            
            self.item_widgets.append(item_frame)

    def _get_event_description(self, event: Dict[str, Any]) -> tuple[str, str]:
        etype = event["type"]
        if etype == "move":
            return f"Mouse Move -> X:{event['x']} Y:{event['y']}", "🖱"
        elif etype == "click":
            state = "Down" if event.get("pressed", True) else "Up"
            return f"Mouse Click -> {event.get('button', 'left').upper()} ({state}) X:{event['x']} Y:{event['y']}", "🖱"
        elif etype == "key_down":
            return f"Key Press -> '{event['key']}' (KeyDown)", "⌨"
        elif etype == "key_up":
            return f"Key Release -> '{event['key']}' (KeyUp)", "⌨"
        elif etype == "delay":
            return f"Delay Wait -> {event.get('delay_ms', 1000)}ms", "⏱"
        return f"Unknown event: {etype}", "❓"

    def _move_item(self, idx: int, direction: int):
        target_idx = idx + direction
        if 0 <= target_idx < len(self.events):
            self.events[idx], self.events[target_idx] = self.events[target_idx], self.events[idx]
            self.refresh_list()
            self.on_list_changed(self.events)

    def _delete_item(self, idx: int):
        if 0 <= idx < len(self.events):
            self.events.pop(idx)
            self.refresh_list()
            self.on_list_changed(self.events)

    def _start_drag(self, idx: int):
        self._drag_start_idx = idx

    def _on_drag_motion(self, event, current_idx: int):
        if self._drag_start_idx is None:
            return
            
        y = event.y_root - self.winfo_rooty()
        target_idx = -1
        for idx, widget in enumerate(self.item_widgets):
            w_y = widget.winfo_y()
            w_h = widget.winfo_height()
            if w_y <= y <= w_y + w_h:
                target_idx = idx
                break
                
        if target_idx != -1 and target_idx != self._drag_start_idx:
            start = self._drag_start_idx
            self.events[start], self.events[target_idx] = self.events[target_idx], self.events[start]
            self._drag_start_idx = target_idx
            self.refresh_list()
            self.on_list_changed(self.events)

    def _stop_drag(self):
        self._drag_start_idx = None
