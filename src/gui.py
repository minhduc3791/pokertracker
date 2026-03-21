"""Main GUI application for PokerTracker - Tkinter-based cross-platform GUI."""

import os
import sys
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from pathlib import Path

from src.database import DatabaseManager
from src.config import ConfigManager


class PokerTrackerGUI:
    """Main GUI application window."""

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("PokerTracker")
        self.root.geometry("1000x700")
        self.root.minsize(800, 600)

        self.config = ConfigManager()
        self.db = None

        self._create_menu()
        self._create_main_content()
        self._load_data()

        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def _create_menu(self):
        """Create the menu bar."""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)

        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Import Hand Histories...", command=self.import_hand_histories)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.on_closing)

        tracker_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Tracker", menu=tracker_menu)
        tracker_menu.add_command(label="Start HUD", command=self.start_hud)
        tracker_menu.add_command(label="Stop HUD", command=self.stop_hud)
        tracker_menu.add_separator()
        tracker_menu.add_command(label="Start Tracking", command=self.start_tracking)
        tracker_menu.add_command(label="Stop Tracking", command=self.stop_tracking)

        view_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="View", menu=view_menu)
        view_menu.add_command(label="Player Statistics", command=self.show_player_stats)
        view_menu.add_command(label="Dashboard", command=self.show_dashboard)

        settings_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Settings", menu=settings_menu)
        settings_menu.add_command(label="Configure...", command=self.show_config)

        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About", command=self.show_about)

    def _create_main_content(self):
        """Create the main content area."""
        self.main_frame = tk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        self.welcome_label = tk.Label(
            self.main_frame,
            text="PokerTracker",
            font=("Arial", 32, "bold")
        )
        self.welcome_label.pack(pady=20)

        self.subtitle_label = tk.Label(
            self.main_frame,
            text="Real-time Poker Statistics Tracker",
            font=("Arial", 14),
            fg="#666"
        )
        self.subtitle_label.pack(pady=(0, 40))

        self.stats_frame = tk.Frame(self.main_frame)
        self.stats_frame.pack(pady=20)

        self.total_hands_var = tk.StringVar(value="0")
        self.total_players_var = tk.StringVar(value="0")
        self.hud_status_var = tk.StringVar(value="Stopped")
        self.tracking_status_var = tk.StringVar(value="Stopped")

        self._create_stat_card("Total Hands", self.total_hands_var, self.stats_frame, 0)
        self._create_stat_card("Players", self.total_players_var, self.stats_frame, 1)
        self._create_stat_card("HUD Status", self.hud_status_var, self.stats_frame, 2)
        self._create_stat_card("Tracking", self.tracking_status_var, self.stats_frame, 3)

        self.quick_actions_frame = tk.LabelFrame(
            self.main_frame,
            text="Quick Actions",
            font=("Arial", 12, "bold"),
            padx=20,
            pady=20
        )
        self.quick_actions_frame.pack(pady=20, fill=tk.X)

        tk.Button(
            self.quick_actions_frame,
            text="Import Hand Histories",
            command=self.import_hand_histories,
            width=20,
            bg="#4CAF50",
            fg="white",
            font=("Arial", 10)
        ).pack(side=tk.LEFT, padx=10)

        tk.Button(
            self.quick_actions_frame,
            text="View Player Stats",
            command=self.show_player_stats,
            width=20,
            bg="#2196F3",
            fg="white",
            font=("Arial", 10)
        ).pack(side=tk.LEFT, padx=10)

        tk.Button(
            self.quick_actions_frame,
            text="Settings",
            command=self.show_config,
            width=20,
            bg="#FF9800",
            fg="white",
            font=("Arial", 10)
        ).pack(side=tk.LEFT, padx=10)

    def _create_stat_card(self, title, var, parent, index):
        """Create a stat display card."""
        card = tk.Frame(parent, relief=tk.RAISED, borderwidth=1)
        card.grid(row=0, column=index, padx=10, sticky="nsew")

        title_label = tk.Label(card, text=title, font=("Arial", 10), fg="#666")
        title_label.pack(pady=(10, 5))

        value_label = tk.Label(card, textvariable=var, font=("Arial", 24, "bold"), fg="#2196F3")
        value_label.pack(pady=(0, 10))

        parent.grid_columnconfigure(index, weight=1)

    def _load_data(self):
        """Load data from database."""
        try:
            db_path = self.config.get('database_path', 'poker_tracker.db')
            if os.path.exists(db_path):
                self.db = DatabaseManager(db_path)
                self.total_hands_var.set(str(self.db.get_hand_count()))
                self.total_players_var.set(str(self.db.get_player_count()))
        except Exception as e:
            print(f"Error loading data: {e}")

    def _clear_main_content(self):
        """Clear main content area."""
        for widget in self.main_frame.winfo_children():
            widget.destroy()

    def show_dashboard(self):
        """Show the dashboard."""
        self._clear_main_content()
        self._create_main_content()
        self._load_data()

    def show_config(self):
        """Show configuration window."""
        config_win = tk.Toplevel(self.root)
        config_win.title("Settings")
        config_win.geometry("500x400")
        config_win.transient(self.root)
        config_win.grab_set()

        notebook = ttk.Notebook(config_win)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        general_frame = ttk.Frame(notebook)
        notebook.add(general_frame, text="General")

        ttk.Label(general_frame, text="Hero Screen Name:").grid(row=0, column=0, sticky=tk.W, padx=10, pady=10)
        hero_entry = ttk.Entry(general_frame, width=40)
        hero_entry.insert(0, self.config.get('hero_screen_name') or "")
        hero_entry.grid(row=0, column=1, padx=10, pady=10)

        ttk.Label(general_frame, text="Database Path:").grid(row=1, column=0, sticky=tk.W, padx=10, pady=10)
        db_frame = ttk.Frame(general_frame)
        db_frame.grid(row=1, column=1, padx=10, pady=10, sticky=tk.EW)
        db_entry = ttk.Entry(db_frame, width=30)
        db_entry.insert(0, self.config.get('database_path', 'poker_tracker.db'))
        db_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Button(db_frame, text="Browse", command=lambda: self._browse_db(db_entry)).pack(side=tk.LEFT, padx=(5, 0))

        ttk.Label(general_frame, text="Hand History Directory:").grid(row=2, column=0, sticky=tk.W, padx=10, pady=10)
        hh_frame = ttk.Frame(general_frame)
        hh_frame.grid(row=2, column=1, padx=10, pady=10, sticky=tk.EW)
        hh_entry = ttk.Entry(hh_frame, width=30)
        hh_entry.insert(0, self.config.get('hand_history_directory', './hand-histories'))
        hh_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Button(hh_frame, text="Browse", command=lambda: self._browse_hh(hh_entry)).pack(side=tk.LEFT, padx=(5, 0))

        platform_frame = ttk.Frame(notebook)
        notebook.add(platform_frame, text="Platform")

        ttk.Label(platform_frame, text="Process Name:").grid(row=0, column=0, sticky=tk.W, padx=10, pady=10)
        process_entry = ttk.Entry(platform_frame, width=40)
        process_entry.insert(0, self.config.get('natural8_process_name', 'Natural8.exe'))
        process_entry.grid(row=0, column=1, padx=10, pady=10)

        ttk.Label(platform_frame, text="Supported Platforms:").grid(row=1, column=0, sticky=tk.W, padx=10, pady=10)
        platforms = [
            "Natural8 / GGPoker",
            "PokerStars",
            "iPoker Network",
            "PartyPoker"
        ]
        platform_combo = ttk.Combobox(platform_frame, values=platforms, width=37, state="readonly")
        platform_combo.current(0)
        platform_combo.grid(row=1, column=1, padx=10, pady=10)

        def save_config():
            self.config.set('hero_screen_name', hero_entry.get() or None)
            self.config.set('database_path', db_entry.get())
            self.config.set('hand_history_directory', hh_entry.get())
            self.config.set('natural8_process_name', process_entry.get())
            self.config.save()
            messagebox.showinfo("Saved", "Settings saved successfully!")
            config_win.destroy()
            self._load_data()

        btn_frame = ttk.Frame(config_win)
        btn_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=10)

        ttk.Button(btn_frame, text="Save", command=save_config).pack(side=tk.RIGHT, padx=5)
        ttk.Button(btn_frame, text="Cancel", command=config_win.destroy).pack(side=tk.RIGHT)

    def _browse_db(self, entry):
        """Browse for database file."""
        filename = filedialog.asksaveasfilename(
            defaultextension=".db",
            filetypes=[("SQLite Database", "*.db"), ("All Files", "*.*")]
        )
        if filename:
            entry.delete(0, tk.END)
            entry.insert(0, filename)

    def _browse_hh(self, entry):
        """Browse for hand history directory."""
        dirname = filedialog.askdirectory()
        if dirname:
            entry.delete(0, tk.END)
            entry.insert(0, dirname)

    def import_hand_histories(self):
        """Import hand history files."""
        import_win = tk.Toplevel(self.root)
        import_win.title("Import Hand Histories")
        import_win.geometry("600x400")
        import_win.transient(self.root)

        tk.Label(
            import_win,
            text="Select folder containing hand history files:",
            font=("Arial", 11)
        ).pack(pady=10)

        dir_frame = ttk.Frame(import_win)
        dir_frame.pack(fill=tk.X, padx=20, pady=10)

        dir_entry = ttk.Entry(dir_frame)
        dir_entry.insert(0, self.config.get('hand_history_directory', './hand-histories'))
        dir_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)

        ttk.Button(dir_frame, text="Browse", command=lambda: [dir_entry.delete(0, tk.END), dir_entry.insert(0, filedialog.askdirectory() or dir_entry.get())]).pack(side=tk.LEFT, padx=(5, 0))

        progress_var = tk.StringVar(value="Ready to import...")
        progress_label = tk.Label(import_win, textvariable=progress_var, font=("Arial", 10))
        progress_label.pack(pady=10)

        progress_bar = ttk.Progressbar(import_win, mode="determinate")
        progress_bar.pack(fill=tk.X, padx=20, pady=10)

        log_text = tk.Text(import_win, height=10, state=tk.DISABLED)
        log_text.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        def log_message(msg):
            log_text.config(state=tk.NORMAL)
            log_text.insert(tk.END, msg + "\n")
            log_text.see(tk.END)
            log_text.config(state=tk.DISABLED)

        def do_import():
            from src.natural8_parser import Natural8Parser
            from src.stats_engine import StatsEngine

            folder = dir_entry.get()
            if not folder or not os.path.exists(folder):
                messagebox.showerror("Error", "Please select a valid folder")
                return

            progress_var.set("Initializing...")
            log_message("Starting import...")

            try:
                if not self.db:
                    db_path = self.config.get('database_path', 'poker_tracker.db')
                    self.db = DatabaseManager(db_path)

                parser = Natural8Parser()
                stats = StatsEngine(self.db, self.config)

                txt_files = list(Path(folder).rglob("*.txt"))
                total = len(txt_files)
                progress_bar["maximum"] = total

                imported = 0
                for i, file_path in enumerate(txt_files):
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()

                        if parser.can_parse(content):
                            hand = parser.parse_hand(content)
                            if hand:
                                self.db.insert_hand(hand)
                                stats.process_hand(hand)
                                imported += 1

                        progress_bar["value"] = i + 1
                        progress_var.set(f"Processing {i+1}/{total}...")

                        if (i + 1) % 100 == 0:
                            log_message(f"Processed {i+1} files, {imported} imported")

                    except Exception as e:
                        print(f"Error processing {file_path}: {e}")

                log_message(f"\nImport complete! {imported} hands imported.")
                progress_var.set(f"Done! {imported} hands imported.")
                self._load_data()

            except Exception as e:
                log_message(f"Error: {e}")
                messagebox.showerror("Error", str(e))

        ttk.Button(import_win, text="Start Import", command=do_import).pack(pady=10)

    def show_player_stats(self):
        """Show player statistics view with search."""
        stats_win = tk.Toplevel(self.root)
        stats_win.title("Player Statistics")
        stats_win.geometry("900x600")
        stats_win.transient(self.root)

        search_frame = ttk.Frame(stats_win)
        search_frame.pack(fill=tk.X, padx=20, pady=10)

        ttk.Label(search_frame, text="Search Player:").pack(side=tk.LEFT)
        search_entry = ttk.Entry(search_frame, width=30)
        search_entry.pack(side=tk.LEFT, padx=10)
        search_entry.focus()

        paned = ttk.PanedWindow(stats_win, orient=tk.HORIZONTAL)
        paned.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 20))

        list_frame = ttk.Frame(paned)
        paned.add(list_frame, weight=1)

        tk.Label(list_frame, text="Players", font=("Arial", 12, "bold")).pack(pady=5)

        player_listbox = tk.Listbox(list_frame, font=("Arial", 10))
        player_listbox.pack(fill=tk.BOTH, expand=True)

        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=player_listbox.yview)
        player_listbox.config(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        detail_frame = ttk.Frame(paned)
        paned.add(detail_frame, weight=2)

        player_name_var = tk.StringVar(value="Select a player")
        tk.Label(detail_frame, textvariable=player_name_var, font=("Arial", 16, "bold")).pack(pady=10)

        stats_notebook = ttk.Notebook(detail_frame)
        stats_notebook.pack(fill=tk.BOTH, expand=True, padx=10)

        preflop_frame = ttk.Frame(stats_notebook)
        stats_notebook.add(preflop_frame, text="Pre-flop")
        self._create_stat_grid(preflop_frame, ["VPIP", "3BET", "F_TB"])

        postflop_frame = ttk.Frame(stats_notebook)
        stats_notebook.add(postflop_frame, text="Post-flop")
        self._create_stat_grid(postflop_frame, ["CALL_CB", "RAISE_CB", "CB_TURN", "F_CB_T", "C_CB_T", "R_CB_T"])

        showdown_frame = ttk.Frame(stats_notebook)
        stats_notebook.add(showdown_frame, text="Showdown")
        self._create_stat_grid(showdown_frame, ["WTSD", "W$SD"])

        stat_widgets = {}
        for frame, stats in [(preflop_frame, ["VPIP", "3BET", "F_TB"]),
                            (postflop_frame, ["CALL_CB", "RAISE_CB", "CB_TURN", "F_CB_T", "C_CB_T", "R_CB_T"]),
                            (showdown_frame, ["WTSD", "W$SD"])]:
            for stat in stats:
                stat_widgets[stat] = {}

        def load_players():
            player_listbox.delete(0, tk.END)
            if not self.db:
                return

            search_term = search_entry.get().lower()
            players = self.db.get_player_summary()

            for p in players:
                if search_term in p['screen_name'].lower():
                    player_listbox.insert(tk.END, p['screen_name'])

        def on_select(event):
            selection = player_listbox.curselection()
            if not selection:
                return

            name = player_listbox.get(selection[0])
            player_name_var.set(name)

            if not self.db:
                return

            player_id = None
            for p in self.db.get_player_summary():
                if p['screen_name'] == name:
                    player_id = p['id']
                    stats = p['stats']
                    break

            if player_id:
                all_stats = self.db.get_player_stats_all_tables(player_id)
                for stat_name, widgets in stat_widgets.items():
                    stat_data = all_stats.get(stat_name, (0, 0))
                    num, den = stat_data if stat_data else (0, 0)
                    pct = round(num / den * 100) if den else 0
                    widgets['pct'].config(text=f"{pct}%")
                    widgets['raw'].config(text=f"{num} / {den}")
                    self._update_stat_color(widgets['pct'], stat_name, pct)

        def on_search(*args):
            load_players()

        search_entry.bind("<KeyRelease>", on_search)
        player_listbox.bind("<<ListboxSelect>>", on_select)

        self._setup_stat_widgets(preflop_frame, ["VPIP", "3BET", "F_TB"], stat_widgets)
        self._setup_stat_widgets(postflop_frame, ["CALL_CB", "RAISE_CB", "CB_TURN", "F_CB_T", "C_CB_T", "R_CB_T"], stat_widgets)
        self._setup_stat_widgets(showdown_frame, ["WTSD", "W$SD"], stat_widgets)

        load_players()

    def _create_stat_grid(self, parent, stat_names):
        """Create stat display grid."""
        pass

    def _setup_stat_widgets(self, parent, stat_names, stat_widgets):
        """Setup stat widgets for a frame."""
        STAT_LABELS = {
            'VPIP': 'VPIP',
            '3BET': '3-Bet',
            'F_TB': 'Fold to Bet',
            'CALL_CB': 'Call CBet',
            'RAISE_CB': 'Raise CBet',
            'CB_TURN': 'CBet Turn',
            'F_CB_T': 'Fold Turn',
            'C_CB_T': 'Call Turn',
            'R_CB_T': 'Raise Turn',
            'WTSD': 'WTSD',
            'W$SD': 'W$SD'
        }

        for i, stat in enumerate(stat_names):
            row = i // 2
            col = (i % 2) * 2

            frame = tk.Frame(parent)
            frame.grid(row=row, column=col, padx=20, pady=10, sticky="w")

            tk.Label(frame, text=STAT_LABELS.get(stat, stat), font=("Arial", 10, "bold")).pack()

            pct_label = tk.Label(frame, text="—", font=("Arial", 20, "bold"), fg="#2196F3")
            pct_label.pack()

            raw_label = tk.Label(frame, text="0 / 0", font=("Arial", 9), fg="#666")
            raw_label.pack()

            stat_widgets[stat] = {'pct': pct_label, 'raw': raw_label}

    def _update_stat_color(self, label, stat_name, pct):
        """Update stat color based on value."""
        if stat_name == 'VPIP':
            if pct < 20:
                label.config(fg="#3498db")
            elif pct < 35:
                label.config(fg="#2ecc71")
            else:
                label.config(fg="#e74c3c")
        elif stat_name == '3BET':
            if pct < 5:
                label.config(fg="#3498db")
            elif pct < 10:
                label.config(fg="#2ecc71")
            else:
                label.config(fg="#e74c3c")
        elif stat_name in ['WTSD', 'W$SD']:
            if pct < 30:
                label.config(fg="#3498db")
            elif pct < 50:
                label.config(fg="#2ecc71")
            else:
                label.config(fg="#e74c3c")

    def start_hud(self):
        """Start the HUD overlay."""
        messagebox.showinfo("HUD", "HUD functionality requires Windows.\nThis feature is available in the Windows build.")

    def stop_hud(self):
        """Stop the HUD overlay."""
        self.hud_status_var.set("Stopped")

    def start_tracking(self):
        """Start tracking."""
        self.tracking_status_var.set("Running")
        messagebox.showinfo("Tracking", "Hand history tracking started.\nImport hand histories to begin.")

    def stop_tracking(self):
        """Stop tracking."""
        self.tracking_status_var.set("Stopped")

    def show_about(self):
        """Show about dialog."""
        messagebox.showinfo(
            "About PokerTracker",
            "PokerTracker v1.0\n\n"
            "Real-time poker statistics tracker.\n\n"
            "Features:\n"
            "- Import hand histories\n"
            "- Track player statistics\n"
            "- HUD overlay (Windows)\n"
            "- Cross-platform statistics viewer"
        )

    def on_closing(self):
        """Handle window closing."""
        if messagebox.askokcancel("Quit", "Do you want to quit?"):
            if self.db:
                self.db.close()
            self.root.destroy()

    def run(self):
        """Run the application."""
        self.root.mainloop()


def main():
    """Main entry point."""
    app = PokerTrackerGUI()
    app.run()


if __name__ == '__main__':
    main()
