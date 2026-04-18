
import tkinter as tk
from ui import LedgerApp


def main():
    root = tk.Tk()
    app = LedgerApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
