"""Application entry point."""
import tkinter as tk
from gui import AssistiveApp
from logger import get_logger

if __name__ == "__main__":
    logger = get_logger()
    logger.info("Application launch")
    root = tk.Tk()
    app = AssistiveApp(root)
    root.mainloop()
    logger.info("Application closed")
