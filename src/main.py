import math
import random
import sys
import pygame

# --- Constants & Configuration ---

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
    (1280, 720), (1366, 768), (1440, 900), (1536, 864),
    (1600, 900), (1680, 1050), (1920, 1080), (1920, 1200),
    (2560, 1440), (2560, 1600), (3440, 1440), (3840, 2160),
    (800, 600), (1024, 768), (1280, 1024),
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
    def __init__(self, app):
        self.app = app
        self.font = pygame.font.SysFont("Arial", 40)
        self.hud_font = pygame.font.SysFont("Consolas", 22, bold=True)

    def handle_events(self, events):
        pass

    def update(self):
        pass

    def draw(self, surface):
        pass

class MainMenu(State):
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
            self.app.change_state(GamePlay(self.app))
        elif chosen == "Settings":
            self.app.change_state(SettingsMenu(self.app))
        elif chosen == "Author":
            self.app.change_state(AuthorMenu(self.app))
        elif chosen == "Exit":
            self.app.quit_app()

    def draw(self, surface):
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
    def __init__(self, app):
        super().__init__(app)
        self.pending_config = app.config.copy()
        self.options = ["Resolution", "Display Mode", "Theme", "Difficulty", "Save Settings", "Back"]
        self.selected_index = 0

    def handle_events(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    self.selected_index = (self.selected_index - 1) % len(self.options)
                elif event.key == pygame.K_DOWN:
                    self.selected_index = (self.selected_index + 1) % len(self.options)
                elif event.key == pygame.K_LEFT:
                    self._change_value(-1)
                elif event.key == pygame.K_RIGHT:
                    self._change_value(1)
                elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                    if self.selected_index in (0, 1, 2, 3) and event.key == pygame.K_SPACE:
                        self._change_value(1)
                    else:
                        self._execute_action()
                elif event.key == pygame.K_ESCAPE:
                    self.app.change_state(MainMenu(self.app))

    def _change_value(self, direction):
        if self.selected_index == 0:
            current_idx = self.pending_config["res_index"]
            self.pending_config["res_index"] = (current_idx + direction) % len(RESOLUTIONS)
        elif self.selected_index == 1:
            self.pending_config["fullscreen"] = not self.pending_config["fullscreen"]
        elif self.selected_index == 2:
            current_idx = THEME_NAMES.index(self.pending_config["theme"])
            new_idx = (current_idx + direction) % len(THEME_NAMES)
            self.pending_config["theme"] = THEME_NAMES[new_idx]
        elif self.selected_index == 3:
            current_speed = self.pending_config["speed"]
            new_speed = current_speed + direction
            self.pending_config["speed"] = max(1, min(10, new_speed))

    def _execute_action(self):
        if self.selected_index == 4:
            self.app.config = self.pending_config.copy()
            self.app.apply_display_settings()
            self.app.change_state(MainMenu(self.app))
        elif self.selected_index == 5:
            self.app.change_state(MainMenu(self.app))

    def draw(self, surface):
        theme = THEMES[self.pending_config["theme"]]
        surface.fill(theme["bg"])

        res = RESOLUTIONS[self.pending_config["res_index"]]
        mode_str = "Fullscreen" if self.pending_config["fullscreen"] else "Windowed"
        
        lines = [
            f"Resolution:  < {res[0]}x{res[1]} >",
            f"Display Mode:  < {mode_str} >",
            f"Theme:  < {self.pending_config['theme']} >",
            f"Difficulty:  < {self.pending_config['speed']} >",
            "Save Settings",
            "Back"
        ]

        screen_w, screen_h = surface.get_size()
        start_y = screen_h // 2 - 150
        step_y = 60

        for i, text in enumerate(lines):
            color = theme["selected"] if i == self.selected_index else theme["text"]
            rendered_text = self.font.render(text, True, color)
            rect = rendered_text.get_rect(center=(screen_w // 2, start_y + i * step_y))
            surface.blit(rendered_text, rect)


class AuthorMenu(State):
    def __init__(self, app):
        super().__init__(app)
        self.authors = [f"{role}: {name}" for role, name in AUTHOR_LIST.items()]
        screen_h = self.app.screen.get_size()[1]
        self.y_offset = float(screen_h)
        self.base_speed = 1.0
        self.speed_multiplier = 3.0

    def handle_events(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.app.change_state(MainMenu(self.app))

    def update(self):
        keys = pygame.key.get_pressed()
        if any(keys):
            current_speed = self.base_speed * self.speed_multiplier
        else:
            current_speed = self.base_speed
        self.y_offset -= current_speed

    def draw(self, surface):
        theme = THEMES[self.app.config["theme"]]
        surface.fill(theme["bg"])
        
        screen_w = surface.get_size()[0]
        step_y = 60
        
        for i, text in enumerate(self.authors):
            rendered_text = self.font.render(text, True, theme["text"])
            pos_y = self.y_offset + (i * step_y)
            rect = rendered_text.get_rect(center=(screen_w // 2, pos_y))
            surface.blit(rendered_text, rect)
            
        instruction = self.font.render("Press ESC to return. Hold any key to speed up.", True, theme["text"])
        inst_rect = instruction.get_rect(topleft=(10, 10))
        scaled_instruction = pygame.transform.smoothscale(instruction, (int(inst_rect.w * 0.5), int(inst_rect.h * 0.5)))
        surface.blit(scaled_instruction, (10, 10))


class GameOver(State):
    """Screen displayed when the player dies OR wins."""
    def __init__(self, app, score, time_survived, reason, is_win=False):
        super().__init__(app)
        self.score = int(score)
        self.time_survived = time_survived
        self.reason = reason
        self.is_win = is_win

    def handle_events(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN:
                self.app.change_state(MainMenu(self.app))

    def draw(self, surface):
        theme = THEMES[self.app.config["theme"]]
        surface.fill(theme["bg"])
        
        screen_w, screen_h = surface.get_size()
        center_x = screen_w // 2
        center_y = screen_h // 2
        
        # Win/Loss colors and text
        title_text_str = "VICTORY!" if self.is_win else "GAME OVER"
        title_color = (50, 255, 100) if self.is_win else (255, 100, 100)
        
        title_font = pygame.font.SysFont("Arial", 60, bold=True)
        title_text = title_font.render(title_text_str, True, title_color)
        title_rect = title_text.get_rect(center=(center_x, center_y - 80))
        surface.blit(title_text, title_rect)
        
        reason_font = pygame.font.SysFont("Arial", 30)
        reason_text = reason_font.render(self.reason, True, theme["text"])
        reason_rect = reason_text.get_rect(center=(center_x, center_y - 20))
        surface.blit(reason_text, reason_rect)
        
        score_text = self.font.render(f"Final Score: {self.score}", True, theme["selected"])
        score_rect = score_text.get_rect(center=(center_x, center_y + 40))
        surface.blit(score_text, score_rect)

        time_text = self.font.render(f"Time: {self.time_survived:.1f}s", True, theme["selected"])
        time_rect = time_text.get_rect(center=(center_x, center_y + 90))
        surface.blit(time_text, time_rect)
        
        inst_text = reason_font.render("Press ANY KEY to return to Menu", True, theme["text"])
        inst_rect = inst_text.get_rect(center=(center_x, center_y + 160))
        surface.blit(inst_text, inst_rect)


class GamePlay(State):
    """
    Survival game mode: Steer a photon around a black hole and try to escape!
    """
    def __init__(self, app):
        super().__init__(app)
        
        self.player_x = 0.0
        self.player_y = -1200.0
        self.angle = 0.0 
        
        # Speed dynamics
        self.base_speed = 3.0 + (self.app.config["speed"] * 0.5)
        self.current_speed = self.base_speed
        self.g_assist = 0.0 
        self.edge_drag = 0.0
        
        self.turn_speed = 0.08         
        
        self.bh_mass = 50000.0          
        self.event_horizon = 45.0      
        self.ideal_distance = 250.0    
        self.safe_distance = 2000.0    # Orbit boundary (Win zone)
        
        self.camera_x = 0.0
        self.camera_y = 0.0
        self.deadzone_radius = 20 
        self.score = 0.0
        
        self.start_ticks = pygame.time.get_ticks()
        self.elapsed_time = 0.0
        
        self.photon_trail = [] 
        self.max_trail_length = 20
        
        # 1. Background stars (Twinkling)
        self.stars = []
        for _ in range(800):
            sx = random.uniform(-self.safe_distance - 400, self.safe_distance + 400)
            sy = random.uniform(-self.safe_distance - 400, self.safe_distance + 400)
            base_size = random.uniform(1.0, 3.0)
            twinkle_phase = random.uniform(0.0, math.pi * 2) 
            self.stars.append([sx, sy, base_size, twinkle_phase])

        # 2. Background little photons falling into the BH
        self.bg_photons = []
        for _ in range(60):
            a = random.uniform(0, math.pi * 2)
            d = random.uniform(self.event_horizon, self.safe_distance)
            s = random.uniform(1.5, 4.0)
            sz = random.uniform(1.0, 2.5)
            self.bg_photons.append({"a": a, "d": d, "s": s, "sz": sz})

    def handle_events(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.app.change_state(MainMenu(self.app))

    def update(self):
        current_ticks = pygame.time.get_ticks()
        self.elapsed_time = (current_ticks - self.start_ticks) / 1000.0
        
        # Base engine power grows over time
        time_velocity = self.base_speed + (self.elapsed_time * 0.15)

        keys = pygame.key.get_pressed()
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            self.angle -= self.turn_speed
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            self.angle += self.turn_speed

        dx = -self.player_x
        dy = -self.player_y
        dist_sq = dx**2 + dy**2
        dist = math.sqrt(dist_sq)

        # 1. Death / Win Conditions
        if dist < self.event_horizon:
            self.app.change_state(GameOver(self.app, self.score, self.elapsed_time, "Consumed by the Black Hole!", False))
            return
        elif dist > self.safe_distance:
            self.app.change_state(GameOver(self.app, self.score, self.elapsed_time, "You Escaped the System!", True))
            return

        # 2. Score Calculation
        distance_factor = self.safe_distance / max(dist, 1.0)
        proximity_multiplier = (distance_factor ** 2) * 0.02
        if abs(dist - self.ideal_distance) < 30:
            proximity_multiplier *= 2.0
        self.score += proximity_multiplier

        # --- 3. DYNAMIC GRAVITY & EDGE DRAG PHYSICS ---
        angle_to_bh = math.atan2(dy, dx)
        alignment = math.cos(self.angle - angle_to_bh)
        
        gravity_pull = (self.bh_mass / max(dist, 1)) * 0.02
        self.g_assist = gravity_pull * alignment

        # Massive resistance as you approach the red circle (Edge map)
        distance_ratio = dist / self.safe_distance
        self.edge_drag = (distance_ratio ** 6) * 22.0 # Power of 6 makes it feel like a wall

        # Thrust can be cancelled completely by the edge drag
        thrust = time_velocity + self.g_assist - self.edge_drag
        thrust = max(0.0, thrust) # You can't thrust backwards

        # Gravity continually bends your vector and pulls you inwards
        gravity_bend_force = self.bh_mass / max(dist_sq, 1)

        vx = math.cos(self.angle) * thrust
        vy = math.sin(self.angle) * thrust

        # Add gravitational fall
        vx += (dx / dist) * gravity_bend_force
        vy += (dy / dist) * gravity_bend_force

        # Update actual speed and nose orientation
        self.current_speed = math.hypot(vx, vy)
        
        # If thrust dropped to 0 (at the edge), gravity takes over and turns your nose towards the hole
        if self.current_speed > 0.1:
            self.angle = math.atan2(vy, vx)

        self.player_x += vx
        self.player_y += vy

        # --- 4. Update Background Photons ---
        for p in self.bg_photons:
            # Orbital motion: speed / distance = angular velocity
            angular_velocity = (p["s"] / max(p["d"], 1)) * 4.0
            p["a"] += angular_velocity
            # Fall inwards over time
            p["d"] -= p["s"] * 0.6 

            # If eaten by black hole, respawn near the outer edge
            if p["d"] < self.event_horizon:
                p["d"] = random.uniform(self.safe_distance - 200, self.safe_distance)
                p["a"] = random.uniform(0, math.pi * 2)

        # Dynamic visual trail
        self.max_trail_length = int(15 + self.current_speed * 1.5)
        self.photon_trail.append((self.player_x, self.player_y))
        if len(self.photon_trail) > self.max_trail_length:
            self.photon_trail.pop(0)

        # Camera tracking
        cam_dist_x = self.player_x - self.camera_x
        if cam_dist_x > self.deadzone_radius:
            self.camera_x = self.player_x - self.deadzone_radius
        elif cam_dist_x < -self.deadzone_radius:
            self.camera_x = self.player_x + self.deadzone_radius
            
        cam_dist_y = self.player_y - self.camera_y
        if cam_dist_y > self.deadzone_radius:
            self.camera_y = self.player_y - self.deadzone_radius
        elif cam_dist_y < -self.deadzone_radius:
            self.camera_y = self.player_y + self.deadzone_radius


    def _get_intermediate_color(self, c1, c2, factor):
        return (
            int(c1[0] + (c2[0] - c1[0]) * factor),
            int(c1[1] + (c2[1] - c1[1]) * factor),
            int(c1[2] + (c2[2] - c1[2]) * factor)
        )

    def draw(self, surface):
        theme = THEMES[self.app.config["theme"]]
        surface.fill(theme["bg"])
        
        screen_w, screen_h = surface.get_size()
        center_x = screen_w // 2
        center_y = screen_h // 2
        current_time = pygame.time.get_ticks()

        # Camera Shake
        shake_x, shake_y = 0, 0
        if self.current_speed > 16.0:
            intensity = (self.current_speed - 16.0) * 0.4
            shake_x = random.uniform(-intensity, intensity)
            shake_y = random.uniform(-intensity, intensity)
            
        view_cx = center_x + int(shake_x)
        view_cy = center_y + int(shake_y)

        # 1. Draw Starfield
        for star in self.stars:
            sx, sy, base_size, phase = star
            screen_x = sx - self.camera_x + view_cx
            screen_y = sy - self.camera_y + view_cy
            
            if 0 <= screen_x <= screen_w and 0 <= screen_y <= screen_h:
                twinkle_size = max(0, base_size + math.sin((current_time / 300.0) + phase))
                if twinkle_size > 0:
                    stretch_factor = self.current_speed * 1.2
                    tail_x = screen_x - math.cos(self.angle) * stretch_factor
                    tail_y = screen_y - math.sin(self.angle) * stretch_factor
                    
                    star_color = theme["text"]
                    if stretch_factor > 15:
                        star_color = self._get_intermediate_color(theme["text"], (100, 220, 255), min(1.0, stretch_factor/40.0))
                    
                    pygame.draw.line(surface, star_color, (int(screen_x), int(screen_y)), (int(tail_x), int(tail_y)), int(twinkle_size))

        bh_screen_x = 0 - self.camera_x + view_cx
        bh_screen_y = 0 - self.camera_y + view_cy
        bh_pos = (int(bh_screen_x), int(bh_screen_y))

        # 2. Draw Background Photons (Swarm falling into BH)
        for p in self.bg_photons:
            px = 0 - self.camera_x + view_cx + math.cos(p["a"]) * p["d"]
            py = 0 - self.camera_y + view_cy + math.sin(p["a"]) * p["d"]
            
            if 0 <= px <= screen_w and 0 <= py <= screen_h:
                color = self._get_intermediate_color(theme["bg"], theme["text"], 0.25) # Faint color
                pygame.draw.circle(surface, color, (int(px), int(py)), int(p["sz"]))
                
                # Tiny orbital tail for each background photon
                tail_a = p["a"] - math.pi/2 + 0.15 
                tx = px - math.cos(tail_a) * (p["s"] * 3)
                ty = py - math.sin(tail_a) * (p["s"] * 3)
                pygame.draw.line(surface, color, (int(px), int(py)), (int(tx), int(ty)), 1)


        px_screen = self.player_x - self.camera_x + view_cx
        py_screen = self.player_y - self.camera_y + view_cy

        # 3. Draw Boundaries
        warning_color = self._get_intermediate_color(theme["bg"], (255, 50, 50), 0.6)
        pygame.draw.circle(surface, warning_color, bh_pos, int(self.safe_distance), 2)
        
        ideal_color = self._get_intermediate_color(theme["bg"], (50, 255, 100), 0.5)
        pygame.draw.circle(surface, ideal_color, bh_pos, int(self.ideal_distance), 1)

        # 4. Draw Black Hole
        pulse_amount = math.sin(current_time / 400.0) * 10.0
        disk_radius = self.event_horizon + 60 + pulse_amount
        layers = 8
        for i in range(layers):
            factor = 1.0 - (i / layers)
            current_color = self._get_intermediate_color(theme["bg"], theme["selected"], factor)
            current_radius = int(self.event_horizon + (disk_radius - self.event_horizon) * (1.0 - factor))
            if current_radius > 0:
                pygame.draw.circle(surface, current_color, bh_pos, current_radius)

        pygame.draw.circle(surface, (0, 0, 0), bh_pos, int(self.event_horizon))

        # 5. Draw Photon (Player)
        if len(self.photon_trail) > 1:
            for i in range(len(self.photon_trail) - 1):
                wx1, wy1 = self.photon_trail[i]
                wx2, wy2 = self.photon_trail[i+1]
                
                sx1 = wx1 - self.camera_x + view_cx
                sy1 = wy1 - self.camera_y + view_cy
                sx2 = wx2 - self.camera_x + view_cx
                sy2 = wy2 - self.camera_y + view_cy
                
                thickness = max(1, int((i / len(self.photon_trail)) * 4))
                pygame.draw.line(surface, theme["selected"], (int(sx1), int(sy1)), (int(sx2), int(sy2)), thickness)

        pygame.draw.circle(surface, theme["text"], (int(px_screen), int(py_screen)), 5)

        # 6. HUD
        hud_width, hud_height = 240, 165
        hud_surface = pygame.Surface((hud_width, hud_height), pygame.SRCALPHA)
        hud_surface.fill((0, 0, 0, 160)) 
        
        score_text = self.hud_font.render(f"Score:    {int(self.score)}", True, theme["selected"])
        time_text = self.hud_font.render(f"Time:     {self.elapsed_time:.1f}s", True, theme["text"])
        speed_text = self.hud_font.render(f"Speed:    {self.current_speed:.1f}c", True, theme["text"])
        
        g_color = theme["selected"] if self.g_assist >= 0 else (255, 100, 100)
        g_assist_text = self.hud_font.render(f"G-Assist: {self.g_assist:+.1f}", True, g_color)
        
        drag_color = (255, 100, 100) if self.edge_drag > 2.0 else theme["text"]
        drag_text = self.hud_font.render(f"Drag:     {self.edge_drag:.1f}", True, drag_color)
        
        hud_surface.blit(score_text, (15, 15))
        hud_surface.blit(time_text, (15, 45))
        hud_surface.blit(speed_text, (15, 75))
        hud_surface.blit(g_assist_text, (15, 105))
        hud_surface.blit(drag_text, (15, 135))
        
        surface.blit(hud_surface, (20, 20))


class GameApp:
    def __init__(self):
        pygame.init()
        self.config = {
            "res_index": 0,         
            "fullscreen": False,
            "theme": "Dark",
            "speed": 5              
        }
        self.screen = None
        self.apply_display_settings()
        pygame.display.set_caption("Black Hole Survival")
        self.clock = pygame.time.Clock()
        self.running = True
        self.current_state = MainMenu(self)

    def apply_display_settings(self):
        res = RESOLUTIONS[self.config["res_index"]]
        flags = pygame.FULLSCREEN if self.config["fullscreen"] else 0
        self.screen = pygame.display.set_mode(res, flags)

    def change_state(self, new_state):
        self.current_state = new_state

    def quit_app(self):
        self.running = False

    def run(self):
        while self.running:
            events = pygame.event.get()
            for event in events:
                if event.type == pygame.QUIT:
                    self.quit_app()

            self.current_state.handle_events(events)
            self.current_state.update()
            
            if self.screen:
                self.current_state.draw(self.screen)

            pygame.display.flip()
            self.clock.tick(60) 

        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    app = GameApp()
    app.run()