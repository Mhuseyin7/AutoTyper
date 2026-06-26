import time
import win32gui
import win32con
import win32process
import win32api
import ctypes

# DPI awareness to ensure correct cursor scaling and coordinates
try:
    ctypes.windll.shcore.SetProcessDpiAwareness(2) # PROCESS_PER_MONITOR_DPI_AWARE
except Exception:
    try:
        ctypes.windll.user32.SetProcessDPIAware()
    except Exception:
        pass

def get_active_window_title() -> str:
    """Returns the title of the currently focused foreground window."""
    try:
        hwnd = win32gui.GetForegroundWindow()
        if hwnd:
            return win32gui.GetWindowText(hwnd)
    except Exception:
        pass
    return ""

def get_active_window_hwnd() -> int:
    """Returns the HWND of the currently focused foreground window."""
    try:
        return win32gui.GetForegroundWindow()
    except Exception:
        return 0

def get_all_open_windows() -> list[dict]:
    """Returns a list of visible windows with titles and HWNDs."""
    windows = []
    
    def enum_windows_callback(hwnd, extra):
        if win32gui.IsWindowVisible(hwnd):
            title = win32gui.GetWindowText(hwnd)
            if title:
                windows.append({
                    "hwnd": hwnd,
                    "title": title
                })
        return True

    try:
        win32gui.EnumWindows(enum_windows_callback, None)
    except Exception:
        pass
    return sorted(windows, key=lambda x: x["title"].lower())

def focus_window(hwnd: int) -> bool:
    """Brings a window to the foreground and focuses it."""
    if not win32gui.IsWindow(hwnd):
        return False
        
    try:
        # Check if window is minimized
        if win32gui.IsIconic(hwnd):
            win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
        else:
            win32gui.ShowWindow(hwnd, win32con.SW_SHOW)
            
        # SetForegroundWindow can fail if the current thread isn't the foreground window thread.
        # We handle this by sending an ALT key down/up or attaching thread input if necessary.
        curr_thread = win32api.GetCurrentThreadId()
        fore_thread = win32process.GetWindowThreadProcessId(win32gui.GetForegroundWindow())[0]
        
        if curr_thread != fore_thread:
            try:
                win32process.AttachThreadInput(curr_thread, fore_thread, True)
                win32gui.SetForegroundWindow(hwnd)
                win32gui.SetActiveWindow(hwnd)
                win32process.AttachThreadInput(curr_thread, fore_thread, False)
                return True
            except Exception:
                pass
                
        win32gui.SetForegroundWindow(hwnd)
        win32gui.SetActiveWindow(hwnd)
        return True
    except Exception:
        # Fallback using standard shell/alt key tap
        try:
            win32api.keybd_event(win32con.VK_MENU, 0, 0, 0) # Alt
            win32gui.SetForegroundWindow(hwnd)
            win32api.keybd_event(win32con.VK_MENU, 0, win32con.KEYEVENTF_KEYUP, 0)
            return True
        except Exception:
            return False

def simulate_click(x: int | None, y: int | None, button: str = "left", click_type: str = "single"):
    """Simulates a mouse click at specific coordinates or current location.
    
    Args:
        x: X-coordinate, if None current cursor X is used
        y: Y-coordinate, if None current cursor Y is used
        button: "left", "right", "middle"
        click_type: "single", "double", "triple"
    """
    # Move cursor if target coordinates are provided
    if x is not None and y is not None:
        win32api.SetCursorPos((x, y))
    else:
        x, y = win32api.GetCursorPos()

    # Determine event flags
    if button == "left":
        down_flag = win32con.MOUSEEVENTF_LEFTDOWN
        up_flag = win32con.MOUSEEVENTF_LEFTUP
    elif button == "right":
        down_flag = win32con.MOUSEEVENTF_RIGHTDOWN
        up_flag = win32con.MOUSEEVENTF_RIGHTUP
    elif button == "middle":
        down_flag = win32con.MOUSEEVENTF_MIDDLEDOWN
        up_flag = win32con.MOUSEEVENTF_MIDDLEUP
    else:
        raise ValueError(f"Unsupported mouse button: {button}")

    clicks = 1
    if click_type == "double":
        clicks = 2
    elif click_type == "triple":
        clicks = 3

    for _ in range(clicks):
        win32api.mouse_event(down_flag, 0, 0, 0, 0)
        time.sleep(0.01) # Short physical switch delay
        win32api.mouse_event(up_flag, 0, 0, 0, 0)
        if clicks > 1:
            time.sleep(0.05) # Double click separation delay

def get_cursor_position() -> tuple[int, int]:
    """Gets the current global cursor coordinates."""
    return win32api.GetCursorPos()

def send_paste_command():
    """Simulates Ctrl + V keystroke."""
    # Press Ctrl
    win32api.keybd_event(win32con.VK_CONTROL, 0, 0, 0)
    # Press V
    win32api.keybd_event(ord('V'), 0, 0, 0)
    time.sleep(0.01)
    # Release V
    win32api.keybd_event(ord('V'), 0, win32con.KEYEVENTF_KEYUP, 0)
    # Release Ctrl
    win32api.keybd_event(win32con.VK_CONTROL, 0, win32con.KEYEVENTF_KEYUP, 0)
