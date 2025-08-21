import tkinter as tk
from tkinter import messagebox, ttk
from nim import train, Nim
import winsound  # For Windows sound effects
import random
import time
class NimGUI:
    def __init__(self, root, ai):
        self.root = root
        self.root.title("Nim Game: Human vs AI")
        self.ai = ai
        
        # Custom colors
        self.bg_color = "#f0f0f0"
        self.button_color = "#4a7a8c"
        self.button_text = "white"
        self.pile_colors = ["#8c4a4a", "#4a8c5e", "#4a5e8c", "#7a4a8c"]
        
        # Configure root window
        self.root.configure(bg=self.bg_color)
        self.root.geometry("800x600")
        
        # Sound effects flag
        self.sound_enabled = True
        
        # Create menu bar
        self.create_menu()
        
        # Game info frame
        self.info_frame = tk.Frame(root, bg=self.bg_color)
        self.info_frame.pack(pady=10)
        
        # Current player indicator
        self.current_player = "human"
        self.info_label = tk.Label(
            self.info_frame, 
            text="Your Turn!", 
            font=("Helvetica", 16, "bold"),
            bg=self.bg_color
        )
        self.info_label.pack(side=tk.LEFT, padx=20)
        
        # Move history
        self.history_label = tk.Label(
            self.info_frame,
            text="Move History:",
            font=("Helvetica", 10),
            bg=self.bg_color
        )
        self.history_label.pack(side=tk.LEFT, padx=20)
        
        # History text box with scrollbar
        self.history_frame = tk.Frame(root, bg=self.bg_color)
        self.history_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        self.history_scroll = tk.Scrollbar(self.history_frame)
        self.history_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.history_text = tk.Text(
            self.history_frame,
            height=8,
            yscrollcommand=self.history_scroll.set,
            wrap=tk.WORD,
            bg="white",
            font=("Consolas", 10)
        )
        self.history_text.pack(fill=tk.BOTH, expand=True)
        self.history_scroll.config(command=self.history_text.yview)
        
        # Piles frame
        self.pile_frame = tk.Frame(root, bg=self.bg_color)
        self.pile_frame.pack(pady=20)
        
        # Control buttons
        self.control_frame = tk.Frame(root, bg=self.bg_color)
        self.control_frame.pack(pady=10)
        
        self.restart_button = tk.Button(
            self.control_frame,
            text="Restart Game",
            command=self.restart_game,
            bg=self.button_color,
            fg=self.button_text,
            font=("Helvetica", 10, "bold"),
            state=tk.DISABLED
        )
        self.restart_button.pack(side=tk.LEFT, padx=10)
        
        self.sound_button = tk.Button(
            self.control_frame,
            text="🔈 Sound: ON",
            command=self.toggle_sound,
            bg=self.button_color,
            fg=self.button_text,
            font=("Helvetica", 10)
        )
        self.sound_button.pack(side=tk.LEFT, padx=10)
        
        # Initialize game
        self.start_new_game()
    
    def create_menu(self):
        menubar = tk.Menu(self.root)
        
        # Game menu
        game_menu = tk.Menu(menubar, tearoff=0)
        game_menu.add_command(label="New Game", command=self.prompt_player_order)
        game_menu.add_command(label="Exit", command=self.root.quit)
        menubar.add_cascade(label="Game", menu=game_menu)
        
        self.root.config(menu=menubar)
    
    def prompt_player_order(self):
        popup = tk.Toplevel(self.root)
        popup.title("Who goes first?")
        popup.geometry("300x150")
        popup.resizable(False, False)
        popup.grab_set()  # Make it modal
        
        tk.Label(
            popup, 
            text="Who should make the first move?",
            font=("Helvetica", 12)
        ).pack(pady=10)
        
        frame = tk.Frame(popup)
        frame.pack(pady=10)
        
        tk.Button(
            frame, 
            text="Human", 
            command=lambda: self.set_player_order(True, popup),
            width=10
        ).pack(side=tk.LEFT, padx=10)
        
        tk.Button(
            frame, 
            text="AI", 
            command=lambda: self.set_player_order(False, popup),
            width=10
        ).pack(side=tk.LEFT, padx=10)
    
    def set_player_order(self, human_first, popup):
        popup.destroy()
        self.start_new_game(human_first)
    
    def start_new_game(self, human_first=True):
        self.game = Nim()
        self.current_player = "human" if human_first else "ai"
        self.history_text.delete(1.0, tk.END)
        self.add_to_history("New game started!")
        self.add_to_history(f"{'Human' if human_first else 'AI'} goes first")
        self.restart_button.config(state=tk.DISABLED)
        self.draw_piles()
        
        if not human_first:
            self.info_label.config(text="AI's Turn...")
            self.root.after(800, self.ai_move)
        else:
            self.info_label.config(text="Your Turn!")
    
    def draw_piles(self):
    # Clear previous widgets
     for widget in self.pile_frame.winfo_children():
        widget.destroy()
    
     self.pile_buttons = []
    
     for i, count in enumerate(self.game.piles):
        pile_color = self.pile_colors[i % len(self.pile_colors)]
        
        frame = tk.Frame(self.pile_frame, bg=self.bg_color)
        frame.grid(row=0, column=i, padx=15, pady=10)
        
        # Pile graphic (visual representation with circles)
        canvas = tk.Canvas(
            frame, 
            width=60, 
            height=150, 
            bg="white",
            highlightthickness=0
        )
        canvas.pack()
        
        # Draw circles representing objects in the pile
        for j in range(count):
            y_pos = 140 - (j * 20)  # Draw from bottom up
            canvas.create_oval(10, y_pos, 50, y_pos-15, fill=pile_color, outline="black")
        
        # Label showing pile number and count
        label = tk.Label(
            frame, 
            text=f"Pile {i}\n({count} left)",
            font=("Helvetica", 10, "bold"),
            bg=self.bg_color
        )
        label.pack()
        
        # Create move selection system for all piles
        if count > 0:
            options = list(range(1, count + 1))
            selected = tk.IntVar(value=options[0])
            
            dropdown = ttk.Combobox(
                frame,
                textvariable=selected,
                values=options,
                state="readonly",
                width=4
            )
            dropdown.pack(pady=5)
            
            take_button = tk.Button(
                frame,
                text="Take",
                command=lambda p=i, var=selected: self.make_move(p, var.get()),
                bg=self.button_color,
                fg=self.button_text,
                font=("Helvetica", 9),
                width=6
            )
            take_button.pack(pady=2)
            self.pile_buttons.append(take_button)
    
    def make_move(self, pile, count):
        if self.game.piles[pile] >= count:
            self.play_sound("move")
            self.game.move((pile, count))
            self.add_to_history(f"Human took {count} from pile {pile}")
            self.check_game_end()
            self.draw_piles()
            if not self.is_game_over():
                self.info_label.config(text="AI's Turn...")
                self.root.after(800, self.ai_move)
    
    def ai_move(self):
        action = self.ai.choose_action(self.game.piles.copy(), epsilon=False)
        self.play_sound("move")
        self.game.move(action)
        self.add_to_history(f"AI took {action[1]} from pile {action[0]}")
        self.check_game_end()
        self.draw_piles()
        if not self.is_game_over():
            self.info_label.config(text="Your Turn!")
    
    def is_game_over(self):
        return all(pile == 0 for pile in self.game.piles)
    
    def check_game_end(self):
        if self.is_game_over():
            winner = "AI" if self.current_player == "human" else "Human"
            self.play_sound("win" if winner == "Human" else "lose")
            self.add_to_history(f"Game Over! {winner} wins!")
            self.info_label.config(text=f"Game Over! {winner} wins!")
            self.disable_all_buttons()
            self.restart_button.config(state=tk.NORMAL)
        else:
            self.current_player = "ai" if self.current_player == "human" else "human"
    
    def disable_all_buttons(self):
        for btn in self.pile_buttons:
            btn.config(state=tk.DISABLED)
    
    def restart_game(self):
        self.play_sound("restart")
        self.start_new_game(self.current_player == "ai")
    
    def toggle_sound(self):
        self.sound_enabled = not self.sound_enabled
        self.sound_button.config(text="🔈 Sound: ON" if self.sound_enabled else "🔇 Sound: OFF")
    
    def play_sound(self, sound_type):
     if not self.sound_enabled:
        return
    
     try:
        if sound_type == "move":
            # Short neutral "click" sound
            winsound.Beep(1200, 80)
            
        elif sound_type == "win":
            # Victory fanfare (cheerful ascending pattern)
            for freq, dur in [(784,150), (1046,150), (1318,300)]:
                winsound.Beep(freq, dur)
                time.sleep(0.03)
            
        elif sound_type == "lose":
            # "Game over" sound (descending "sad" pattern)
            for freq, dur in [(659,200), (587,200), (523,400)]:
                winsound.Beep(freq, dur)
                time.sleep(0.05)
            
        elif sound_type == "restart":
            # Reset sound (two quick "alert" beeps)
            winsound.Beep(900, 100)
            time.sleep(0.05)
            winsound.Beep(900, 100)
            
     except:
        # Fallback to system sounds if beeps fail
        try:
            if sound_type == "win":
                winsound.PlaySound("SystemExclamation", winsound.SND_ALIAS)
            elif sound_type == "lose":
                winsound.PlaySound("SystemHand", winsound.SND_ALIAS)
            elif sound_type == "move":
                winsound.PlaySound("SystemQuestion", winsound.SND_ALIAS)
            elif sound_type == "restart":
                winsound.PlaySound("SystemAsterisk", winsound.SND_ALIAS)
        except:
            pass  # Silent if all fails
    
    def add_to_history(self, message):
        self.history_text.insert(tk.END, message + "\n")
        self.history_text.see(tk.END)  # Auto-scroll to bottom

if __name__ == "__main__":
    print("Training AI on 10000 games...")
    ai = train(10000)
    print("AI trained!")
    
    root = tk.Tk()
    app = NimGUI(root, ai)
    root.mainloop()