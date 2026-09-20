import sys
import pygame

# --- Constants & Configuration ---

# Dictionary containing various color schemes
THEMES = {
    "Dark": {
        "bg": (25, 25, 35),
        "text": (200, 200, 200),
        "selected": (255, 215, 0)
    },
    "Light": {
        "bg": (235, 235, 240),
        "text": (40, 40, 40),
        "selected": (200, 50, 50)
    },
    "Matrix": {
        "bg": (5, 15, 5),
        "text": (0, 180, 0),
        "selected": (150, 255, 150)
    },
    "Ocean": {
        "bg": (15, 30, 50),
        "text": (150, 200, 220),
        "selected": (0, 255, 200)
    },
    "Retro": {
        "bg": (30, 10, 40),
        "text": (0, 255, 255),
        "selected": (255, 0, 255)
    }
}
THEME_NAMES = list(THEMES.keys())

RESOLUTIONS = [
    # Десктопы, ноутбуки и внешние мониторы
    (1280, 720),    # HD (720p)
    (1366, 768),    # WXGA (популярно на бюджетных ноутбуках)
    (1440, 900),    # WXGA+
    (1536, 864),    # Распространённый масштаб Windows на HD-экранах
    (1600, 900),    # HD+
    (1680, 1050),   # WSXGA+
    (1920, 1080),   # Full HD (FHD) — самый популярный в мире
    (1920, 1200),   # WUXGA (16:10)
    (2560, 1440),   # 2K / QHD / WQHD
    (2560, 1600),   # WQXGA (16:10, популярно в MacBook)
    (3440, 1440),   # UWQHD (ультраширокие 21:9)
    (3840, 2160),   # 4K UHD

    # Классические / устаревшие (4:3)
    (800, 600),     # SVGA
    (1024, 768),    # XGA
    (1280, 1024),   # SXGA (5:4)
]


AUTHOR_LIST = {
    "CEO": "Vitalitical",
    "Lead Programmer": "Vitalitical",
    "Art Director": "Vitalitical",
    "Sound Designer": "Maxim Serebriakov",
    "QA Tester": "Vitalitical",
    "Special Thanks": "FOR ME MAN :>!"
}

# --- State Classes ---

class State:
    """Base class for different screens/states in the application."""
    def __init__(self, app):
        self.app = app
        self.font = pygame.font.SysFont("Arial", 40)

    def handle_events(self, events):
        """Processes input events. To be overridden by subclasses."""
        pass

    def update(self):
        """Processes game logic updates."""
        pass

    def draw(self, surface):
        """Renders the state to the screen. To be overridden by subclasses."""
        pass

class MainMenu(State):
    """Main menu screen handling start, settings, author, and exit."""
    def __init__(self, app):
        super().__init__(app)
        self.options = ["Start", "Settings", "Author", "Exit"]
        self.selected_index = 0

    def handle_events(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    self.selected_index = (self.selected_index - 1) % len(self.options)
                elif event.key == pygame.K_DOWN:
                    self.selected_index = (self.selected_index + 1) % len(self.options)
                elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                    self._execute_action()

    def _execute_action(self):
        chosen = self.options[self.selected_index]
        if chosen == "Start":
            print("Action: Start Game")
        elif chosen == "Settings":
            self.app.change_state(SettingsMenu(self.app))
        elif chosen == "Author":
            self.app.change_state(AuthorMenu(self.app))
        elif chosen == "Exit":
            self.app.quit_app()

    def draw(self, surface):
        # Fetch current applied theme from app config
        theme = THEMES[self.app.config["theme"]]
        surface.fill(theme["bg"])

        screen_w, screen_h = surface.get_size()
        start_y = screen_h // 2 - 80
        step_y = 60

        for i, text in enumerate(self.options):
            color = theme["selected"] if i == self.selected_index else theme["text"]
            rendered_text = self.font.render(text, True, color)
            rect = rendered_text.get_rect(center=(screen_w // 2, start_y + i * step_y))
            surface.blit(rendered_text, rect)

class SettingsMenu(State):
    """Settings screen with deferred application (changes apply only on Save)."""
    def __init__(self, app):
        super().__init__(app)
        # Create a temporary copy of config to store unapplied changes
        self.pending_config = app.config.copy()
        self.options = ["Resolution", "Display Mode", "Theme", "Save Settings", "Back"]
        self.selected_index = 0

    def handle_events(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    self.selected_index = (self.selected_index - 1) % len(self.options)
                elif event.key == pygame.K_DOWN:
                    self.selected_index = (self.selected_index + 1) % len(self.options)
                
                # Adjust setting value backwards
                elif event.key == pygame.K_LEFT:
                    self._change_value(-1)
                
                # Adjust setting value forwards
                elif event.key == pygame.K_RIGHT:
                    self._change_value(1)
                
                # Execute action or adjust value
                elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                    # If pointing at a parameter, SPACE acts like a RIGHT arrow
                    if self.selected_index in (0, 1, 2) and event.key == pygame.K_SPACE:
                        self._change_value(1)
                    else:
                        self._execute_action()

                # Quick exit to main menu without saving
                elif event.key == pygame.K_ESCAPE:
                    self.app.change_state(MainMenu(self.app))

    def _change_value(self, direction):
        """Modifies the currently selected parameter in pending_config."""
        if self.selected_index == 0:  # Resolution
            current_idx = self.pending_config["res_index"]
            self.pending_config["res_index"] = (current_idx + direction) % len(RESOLUTIONS)
        
        elif self.selected_index == 1:  # Display Mode
            self.pending_config["fullscreen"] = not self.pending_config["fullscreen"]
        
        elif self.selected_index == 2:  # Theme
            current_idx = THEME_NAMES.index(self.pending_config["theme"])
            new_idx = (current_idx + direction) % len(THEME_NAMES)
            self.pending_config["theme"] = THEME_NAMES[new_idx]

    def _execute_action(self):
        """Applies configuration if 'Save' is chosen, or returns if 'Back'."""
        if self.selected_index == 3:  # Save Settings
            # Override actual app config with pending modifications
            self.app.config = self.pending_config.copy()
            self.app.apply_display_settings()
            self.app.change_state(MainMenu(self.app))
        
        elif self.selected_index == 4:  # Back (discard changes)
            self.app.change_state(MainMenu(self.app))

    def draw(self, surface):
        # Draw using pending theme to preview colors instantly before saving
        theme = THEMES[self.pending_config["theme"]]
        surface.fill(theme["bg"])

        res = RESOLUTIONS[self.pending_config["res_index"]]
        mode_str = "Fullscreen" if self.pending_config["fullscreen"] else "Windowed"
        
        # Format string elements for the settings menu
        lines = [
            f"Resolution:  < {res[0]}x{res[1]} >",
            f"Display Mode:  < {mode_str} >",
            f"Theme:  < {self.pending_config['theme']} >",
            "Save Settings",
            "Back"
        ]

        screen_w, screen_h = surface.get_size()
        start_y = screen_h // 2 - 120
        step_y = 60

        for i, text in enumerate(lines):
            color = theme["selected"] if i == self.selected_index else theme["text"]
            rendered_text = self.font.render(text, True, color)
            rect = rendered_text.get_rect(center=(screen_w // 2, start_y + i * step_y))
            surface.blit(rendered_text, rect)

class AuthorMenu(State):
    """Credits screen displaying scrolling authors list."""
    def __init__(self, app):
        super().__init__(app)
        
        # Format dictionary into a list of strings for rendering
        self.authors = [f"{role}: {name}" for role, name in AUTHOR_LIST.items()]
        
        # Start the text below the bottom edge of the screen
        screen_h = self.app.screen.get_size()[1]
        self.y_offset = float(screen_h)
        
        # Movement speeds (pixels per frame)
        self.base_speed = 1.0
        self.speed_multiplier = 3.0

    def handle_events(self, events):
        """Handle single trigger events like exiting."""
        for event in events:
            if event.type == pygame.KEYDOWN:
                # Exit back to main menu only on ESCAPE
                if event.key == pygame.K_ESCAPE:
                    self.app.change_state(MainMenu(self.app))

    def update(self):
        """Update physics and continuous key holds."""
        # get_pressed() returns a tuple of booleans for all keyboard keys
        keys = pygame.key.get_pressed()
        
        # Check if ANY key is currently being held down
        # any() returns True if at least one value in the tuple is True
        if any(keys):
            current_speed = self.base_speed * self.speed_multiplier
        else:
            current_speed = self.base_speed
            
        # Move text UP (decreases Y coordinate) to simulate scrolling down the list
        self.y_offset -= current_speed

    def draw(self, surface):
        """Render the scrolling text."""
        theme = THEMES[self.app.config["theme"]]
        surface.fill(theme["bg"])
        
        screen_w = surface.get_size()[0]
        step_y = 60
        
        for i, text in enumerate(self.authors):
            rendered_text = self.font.render(text, True, theme["text"])
            
            # Calculate dynamic Y position for each line
            pos_y = self.y_offset + (i * step_y)
            rect = rendered_text.get_rect(center=(screen_w // 2, pos_y))
            
            surface.blit(rendered_text, rect)
            
        # Optional: draw an instruction at the top or bottom
        instruction = self.font.render("Press ESC to return. Hold any key to speed up.", True, theme["text"])
        # Scale down instruction font slightly by creating a new font object just for it, 
        # or simply blit it at the top-left corner
        inst_rect = instruction.get_rect(topleft=(10, 10))
        # Draw instruction slightly smaller if needed, here we just scale it using pygame.transform
        scaled_instruction = pygame.transform.smoothscale(instruction, (int(inst_rect.w * 0.5), int(inst_rect.h * 0.5)))
        surface.blit(scaled_instruction, (10, 10))




class GameApp:
    """Core class managing the game loop, events, and state machine."""
    def __init__(self):
        pygame.init()
        
        # Primary application configuration
        self.config = {
            "res_index": 0,         # Index for 800x600 resolution
            "fullscreen": False,
            "theme": "Dark"
        }
        
        self.screen = None
        self.apply_display_settings()
        pygame.display.set_caption("Game UI Structure")
        
        self.clock = pygame.time.Clock()
        self.running = True
        
        # Set the initial active state
        self.current_state = MainMenu(self)

    def apply_display_settings(self):
        """Re-initializes the display surface with current config."""
        res = RESOLUTIONS[self.config["res_index"]]
        flags = pygame.FULLSCREEN if self.config["fullscreen"] else 0
        self.screen = pygame.display.set_mode(res, flags)

    def change_state(self, new_state):
        """Replaces the active view with a new state object."""
        self.current_state = new_state

    def quit_app(self):
        """Flags the main loop to terminate."""
        self.running = False

    def run(self):
        """Primary execution loop mapping inputs and rendering."""
        while self.running:
            events = pygame.event.get()
            for event in events:
                if event.type == pygame.QUIT:
                    self.quit_app()

            # Delegate event handling to the active state
            self.current_state.handle_events(events)
            
            # Delegate game logic
            self.current_state.update()
            
            # Delegate rendering
            if self.screen:
                self.current_state.draw(self.screen)

            pygame.display.flip()
            self.clock.tick(60)

        # Clean shutdown routine
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    app = GameApp()
    app.run()