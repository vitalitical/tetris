import math
import random
import sys
import pygame

# --- Constants & Configuration ---

# Atmospheric cosmic color schemes
THEMES = {
    "Cosmic Aurora": {
        "bg": (12, 10, 28),
        "text": (180, 220, 245),
        "selected": (0, 255, 190)
    },
    "Antimatter": {
        "bg": (22, 6, 24),
        "text": (235, 190, 255),
        "selected": (255, 20, 147)
    },
    "Supernova": {
        "bg": (28, 12, 8),
        "text": (255, 215, 180),
        "selected": (255, 120, 20)
    },
    "Deep Nebula": {
        "bg": (8, 18, 38),
        "text": (160, 210, 255),
        "selected": (60, 160, 255)
    },
    "Quasar Void": {
        "bg": (8, 8, 12),
        "text": (180, 180, 190),
        "selected": (240, 245, 255)
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


class GamePlay(State):
    def __init__(self, app):
        super().__init__(app)
        
        self.player_x = 0.0
        self.player_y = -1200.0
        self.angle = 0.0 
        
        self.base_speed = 3.0 + (self.app.config["speed"] * 0.5)
        self.current_speed = self.base_speed
        
        self.g_const = 3.5
        self.g_assist = 0.0 
        self.edge_drag = 0.0
        
        self.turn_speed = 0.08         
        
        self.bh_mass = 50000.0          
        self.event_horizon = 85.0
        self.safe_distance = 2000.0
        
        self.camera_x = 0.0
        self.camera_y = 0.0
        self.deadzone_radius = 20 
        self.score = 0.0
        
        self.start_ticks = pygame.time.get_ticks()
        self.elapsed_time = 0.0
        
        self.photon_trail = [] 
        self.max_trail_length = 20
        
        # --- Cinematic State Variables ---
        self.escaping = False
        self.escape_phase = 0
        
        # Staged Collapse: 
        # 1: Slight expansion & shake
        # 2: Sucks in all surrounding photons
        # 3: Violent full screen engulfment
        # 4: Abrupt Game Over screen
        self.consumed = False
        self.consume_phase = 0
        self.consume_radius = self.event_horizon
        self.consume_timer = 0
        self.consume_speed = 3.0
        
        self.fade_alpha = 0.0
        
        # Background stars
        self.stars = []
        for _ in range(800):
            sx = random.uniform(-self.safe_distance - 400, self.safe_distance + 400)
            sy = random.uniform(-self.safe_distance - 400, self.safe_distance + 400)
            base_size = random.uniform(1.0, 3.0)
            twinkle_phase = random.uniform(0.0, math.pi * 2) 
            self.stars.append([sx, sy, base_size, twinkle_phase])

        # Dense swarm of photons near the black hole
        self.bg_photons = []
        for _ in range(800):
            self.bg_photons.append(self._spawn_bg_photon())

    def _spawn_bg_photon(self):
        cluster_factor = random.random() ** 3.2
        d = self.event_horizon + 15 + cluster_factor * (self.safe_distance * 0.75)
        angle = random.uniform(0, math.pi * 2)
        px = math.cos(angle) * d
        py = math.sin(angle) * d

        orbital_speed = math.sqrt(self.bh_mass / max(d, 50.0))

        if random.random() < 0.7:
            vx = -math.sin(angle) * orbital_speed * random.uniform(0.8, 1.2)
            vy = math.cos(angle) * orbital_speed * random.uniform(0.8, 1.2)
        else:
            vx = random.uniform(-orbital_speed, orbital_speed)
            vy = random.uniform(-orbital_speed, orbital_speed)

        if random.random() < 0.5:
            vx, vy = -vx, -vy

        return {
            "x": px, "y": py,
            "vx": vx, "vy": vy,
            "trail": [(px, py)],
            "size": random.uniform(1.0, 2.0),
            "max_trail": random.randint(3, 7)
        }

    def handle_events(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if not self.escaping and not self.consumed and event.key == pygame.K_ESCAPE:
                    self.app.change_state(MainMenu(self.app))
                elif self.escaping and self.escape_phase == 3 and self.fade_alpha > 150:
                    self.app.change_state(MainMenu(self.app))
                # Abrupt game over screen returns to menu on any key press
                elif self.consumed and self.consume_phase == 4:
                    self.app.change_state(MainMenu(self.app))

    def update(self):
        current_ticks = pygame.time.get_ticks()
        if not self.escaping and not self.consumed:
            self.elapsed_time = (current_ticks - self.start_ticks) / 1000.0

        dx = -self.player_x
        dy = -self.player_y
        dist_sq = dx**2 + dy**2
        dist = math.sqrt(dist_sq)

        screen_w, screen_h = self.app.screen.get_size()
        max_screen_radius = math.hypot(screen_w, screen_h)

        if not self.escaping and not self.consumed:
            # --- NORMAL GAMEPLAY PHYSICS ---
            time_velocity = self.base_speed + (self.elapsed_time * 0.15)

            keys = pygame.key.get_pressed()
            if keys[pygame.K_a] or keys[pygame.K_LEFT]:
                self.angle -= self.turn_speed
            if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
                self.angle += self.turn_speed

            # Condition 1: Black hole collision (Starts Collapse Phase 1)
            if dist < self.event_horizon:
                self.consumed = True
                self.consume_phase = 1
                self.consume_timer = 0
                return

            # Condition 2: Escape boundary reached (Starts Escape Sequence)
            elif dist > self.safe_distance:
                self.escaping = True
                self.escape_phase = 1
                return

            # Score Calculation
            distance_factor = self.safe_distance / max(dist, 1.0)
            proximity_multiplier = (distance_factor ** 2) * 0.02
            self.score += proximity_multiplier

            # Directional acceleration (Constant g)
            angle_to_bh = math.atan2(dy, dx)
            alignment = math.cos(self.angle - angle_to_bh)
            self.g_assist = self.g_const * alignment

            distance_ratio = dist / self.safe_distance
            self.edge_drag = (distance_ratio ** 6) * 22.0

            thrust = time_velocity + self.g_assist - self.edge_drag
            thrust = max(0.0, thrust)

            gravity_bend_force = min(4.0, self.bh_mass / max(dist_sq, 1000.0))

            vx = math.cos(self.angle) * thrust
            vy = math.sin(self.angle) * thrust

            vx += (dx / dist) * gravity_bend_force
            vy += (dy / dist) * gravity_bend_force

            self.current_speed = math.hypot(vx, vy)
            
            if self.current_speed > 0.1:
                self.angle = math.atan2(vy, vx)

            self.player_x += vx
            self.player_y += vy
            
            self._update_camera()

        elif self.consumed:
            # --- STAGED BLACK HOLE COLLAPSE ---
            # Center camera smoothly on black hole
            self.camera_x += (0 - self.camera_x) * 0.1
            self.camera_y += (0 - self.camera_y) * 0.1

            # Player photon is absorbed
            self.player_x *= 0.8
            self.player_y *= 0.8

            if self.consume_phase == 1:
                # Stage 1: Slight swell and initial rumbling
                self.consume_radius += 0.9
                if self.consume_radius >= 135.0:
                    self.consume_phase = 2
                    self.consume_timer = 0

            elif self.consume_phase == 2:
                # Stage 2: Sucks in surrounding photons with extreme gravity
                self.consume_timer += 1
                self.consume_radius += 0.4
                if self.consume_timer >= 55:
                    self.consume_phase = 3
                    self.consume_speed = 5.0

            elif self.consume_phase == 3:
                # Stage 3: Violent, exponential expansion engulfing the entire screen
                self.consume_speed += 3.2
                self.consume_radius += self.consume_speed
                
                # When black hole engulfs the view, cut immediately to abrupt Game Over
                if self.consume_radius >= max_screen_radius:
                    self.consume_phase = 4

        elif self.escaping:
            # --- ESCAPE SEQUENCE ---
            if self.escape_phase == 1:
                if self.current_speed < 15.0:
                    self.current_speed += 0.1
                else:
                    self.escape_phase = 2
                    
                self.player_x += math.cos(self.angle) * self.current_speed
                self.player_y += math.sin(self.angle) * self.current_speed
                self._update_camera()
                
            elif self.escape_phase == 2:
                self.current_speed += 0.5
                self.player_x += math.cos(self.angle) * self.current_speed
                self.player_y += math.sin(self.angle) * self.current_speed
                
                px_screen = self.player_x - self.camera_x + (screen_w // 2)
                py_screen = self.player_y - self.camera_y + (screen_h // 2)
                
                if px_screen < -200 or px_screen > screen_w + 200 or py_screen < -200 or py_screen > screen_h + 200:
                    self.escape_phase = 3
                    
            elif self.escape_phase == 3:
                self.fade_alpha = min(255.0, self.fade_alpha + 1.5)

        # --- Background Photons Physics ---
        active_event_horizon = self.consume_radius if self.consumed else self.event_horizon
        for p in self.bg_photons:
            p_dist_sq = p["x"]**2 + p["y"]**2
            p_dist = math.sqrt(p_dist_sq)

            if p_dist < active_event_horizon or p_dist > self.safe_distance * 1.5:
                if not self.consumed:
                    p.update(self._spawn_bg_photon())
                continue

            # In Phase 2, nearby photons get sucked straight inward at high speed
            if self.consumed and self.consume_phase >= 2:
                inward_pull = 28.0
                p["vx"] -= (p["x"] / max(p_dist, 1.0)) * inward_pull
                p["vy"] -= (p["y"] / max(p_dist, 1.0)) * inward_pull
            else:
                force = self.bh_mass / max(p_dist_sq, 1)
                p["vx"] -= (p["x"] / p_dist) * force
                p["vy"] -= (p["y"] / p_dist) * force

            p["x"] += p["vx"]
            p["y"] += p["vy"]

            p["trail"].append((p["x"], p["y"]))
            if len(p["trail"]) > p["max_trail"]:
                p["trail"].pop(0)

        # Trail updates
        if not self.consumed and self.escape_phase < 3:
            self.max_trail_length = int(15 + self.current_speed * 1.5)
            self.photon_trail.append((self.player_x, self.player_y))
            if len(self.photon_trail) > self.max_trail_length:
                self.photon_trail.pop(0)

    def _update_camera(self):
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

        # Dynamic Camera Shake Logic
        shake_x, shake_y = 0, 0
        if self.consumed:
            if self.consume_phase == 1:
                intensity = 7.0
                shake_x = random.uniform(-intensity, intensity)
                shake_y = random.uniform(-intensity, intensity)
            elif self.consume_phase == 2:
                intensity = 15.0
                shake_x = random.uniform(-intensity, intensity)
                shake_y = random.uniform(-intensity, intensity)
            elif self.consume_phase == 3:
                intensity = 30.0
                shake_x = random.uniform(-intensity, intensity)
                shake_y = random.uniform(-intensity, intensity)
            elif self.consume_phase == 4:
                # Total stillness once screen is swallowed
                shake_x, shake_y = 0, 0
        elif (not self.escaping and self.current_speed > 16.0) or (self.escaping and self.escape_phase == 2):
            intensity = 12.0 if self.escape_phase == 2 else (self.current_speed - 16.0) * 0.4
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
                    stretch_factor = self.current_speed * 1.2 if not self.consumed else 1.0
                    tail_x = screen_x - math.cos(self.angle) * stretch_factor
                    tail_y = screen_y - math.sin(self.angle) * stretch_factor
                    
                    star_color = theme["text"]
                    if stretch_factor > 15:
                        star_color = self._get_intermediate_color(theme["text"], (100, 220, 255), min(1.0, stretch_factor/40.0))
                    
                    pygame.draw.line(surface, star_color, (int(screen_x), int(screen_y)), (int(tail_x), int(tail_y)), int(twinkle_size))

        # 2. Draw Background Photons
        bg_photon_color = self._get_intermediate_color(theme["bg"], theme["text"], 0.25)
        for p in self.bg_photons:
            if len(p["trail"]) > 1:
                screen_trail = []
                for tx, ty in p["trail"]:
                    sx = tx - self.camera_x + view_cx
                    sy = ty - self.camera_y + view_cy
                    screen_trail.append((int(sx), int(sy)))
                pygame.draw.lines(surface, bg_photon_color, False, screen_trail, 1)
            
            px_s = p["x"] - self.camera_x + view_cx
            py_s = p["y"] - self.camera_y + view_cy
            pygame.draw.circle(surface, bg_photon_color, (int(px_s), int(py_s)), int(p["size"]))

        bh_screen_x = 0 - self.camera_x + view_cx
        bh_screen_y = 0 - self.camera_y + view_cy
        bh_pos = (int(bh_screen_x), int(bh_screen_y))

        # 3. Cinematic Black Hole Rendering
        current_event_horizon = self.consume_radius if self.consumed else self.event_horizon
        pulse_amount = math.sin(current_time / 400.0) * 12.0 if not self.consumed else 0.0
        glow_radius = int(current_event_horizon * 2.8 + pulse_amount)
        
        if -glow_radius < bh_pos[0] < screen_w + glow_radius and -glow_radius < bh_pos[1] < screen_h + glow_radius:
            glow_surf = pygame.Surface((glow_radius * 2, glow_radius * 2), pygame.SRCALPHA)
            bh_center = (glow_radius, glow_radius)
            base_color = theme["selected"]

            layers = 16
            for i in range(layers):
                factor = i / layers
                radius = int(current_event_horizon + (glow_radius - current_event_horizon) * (1.0 - factor))
                alpha = int(120 * (factor ** 2))
                pygame.draw.circle(glow_surf, (base_color[0], base_color[1], base_color[2], alpha), bh_center, radius)

            pygame.draw.circle(glow_surf, (255, 255, 255, 200), bh_center, int(current_event_horizon + 3), 3)
            pygame.draw.circle(glow_surf, (255, 255, 255, 90), bh_center, int(current_event_horizon + 8), 5)
            pygame.draw.circle(glow_surf, (0, 0, 0, 255), bh_center, int(current_event_horizon))

            surface.blit(glow_surf, (bh_pos[0] - glow_radius, bh_pos[1] - glow_radius))

        # 4. Draw Photon (Player)
        if not self.consumed and self.escape_phase < 3:
            px_screen = self.player_x - self.camera_x + view_cx
            py_screen = self.player_y - self.camera_y + view_cy

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

        # 5. UI Elements
        if not self.escaping and not self.consumed:
            px_screen = self.player_x - self.camera_x + view_cx
            py_screen = self.player_y - self.camera_y + view_cy
            
            dx = bh_screen_x - px_screen
            dy = bh_screen_y - py_screen
            margin = 2 
            
            if dx != 0 or dy != 0:
                tx, ty = float('inf'), float('inf')
                if dx > 0: tx = ((screen_w - margin) - px_screen) / dx
                elif dx < 0: tx = (margin - px_screen) / dx
                if dy > 0: ty = ((screen_h - margin) - py_screen) / dy
                elif dy < 0: ty = (margin - py_screen) / dy
                    
                t = min(tx, ty)
                
                if 0 < t < 1.0:
                    ind_x = px_screen + t * dx
                    ind_y = py_screen + t * dy
                    dash_len = 30
                    if t == tx:
                        pygame.draw.line(surface, theme["selected"], 
                                         (int(ind_x), int(ind_y - dash_len//2)), 
                                         (int(ind_x), int(ind_y + dash_len//2)), 4)
                    else:
                        pygame.draw.line(surface, theme["selected"], 
                                         (int(ind_x - dash_len//2), int(ind_y)), 
                                         (int(ind_x + dash_len//2), int(ind_y)), 4)

            # HUD Panel
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

        # 6. Victory Sequence Text
        if self.escaping and self.escape_phase == 3:
            fade_surf = pygame.Surface((screen_w, screen_h), pygame.SRCALPHA)
            
            title_font = pygame.font.SysFont("Arial", 60, bold=True)
            title_text = title_font.render("VICTORY!", True, (50, 255, 100))
            title_rect = title_text.get_rect(center=(center_x, center_y - 80))
            
            score_font = pygame.font.SysFont("Arial", 40)
            score_text = score_font.render(f"Final Score: {int(self.score)}", True, theme["selected"])
            score_rect = score_text.get_rect(center=(center_x, center_y))
            
            time_text = score_font.render(f"Time: {self.elapsed_time:.1f}s", True, theme["text"])
            time_rect = time_text.get_rect(center=(center_x, center_y + 60))
            
            inst_font = pygame.font.SysFont("Arial", 24)
            inst_text = inst_font.render("Press ANY KEY to return to Menu", True, theme["text"])
            inst_rect = inst_text.get_rect(center=(center_x, center_y + 140))
            
            fade_surf.blit(title_text, title_rect)
            fade_surf.blit(score_text, score_rect)
            fade_surf.blit(time_text, time_rect)
            fade_surf.blit(inst_text, inst_rect)
            
            fade_surf.set_alpha(int(self.fade_alpha))
            surface.blit(fade_surf, (0, 0))

        # 7. Abrupt Game Over Screen (Phase 4: pitch black, zero fade-in, instant display)
        if self.consumed and self.consume_phase == 4:
            surface.fill((0, 0, 0))
            
            title_font = pygame.font.SysFont("Arial", 60, bold=True)
            title_text = title_font.render("SINGULARITY COLLAPSE", True, (255, 50, 50))
            title_rect = title_text.get_rect(center=(center_x, center_y - 80))
            
            reason_font = pygame.font.SysFont("Arial", 26)
            reason_text = reason_font.render("Consumed by the Event Horizon", True, (180, 180, 190))
            reason_rect = reason_text.get_rect(center=(center_x, center_y - 25))
            
            score_font = pygame.font.SysFont("Arial", 40)
            score_text = score_font.render(f"Final Score: {int(self.score)}", True, theme["selected"])
            score_rect = score_text.get_rect(center=(center_x, center_y + 35))
            
            time_text = score_font.render(f"Time Survived: {self.elapsed_time:.1f}s", True, (220, 220, 230))
            time_rect = time_text.get_rect(center=(center_x, center_y + 90))
            
            inst_font = pygame.font.SysFont("Arial", 24)
            inst_text = inst_font.render("Press ANY KEY to return to Menu", True, (140, 140, 150))
            inst_rect = inst_text.get_rect(center=(center_x, center_y + 160))
            
            surface.blit(title_text, title_rect)
            surface.blit(reason_text, reason_rect)
            surface.blit(score_text, score_rect)
            surface.blit(time_text, time_rect)
            surface.blit(inst_text, inst_rect)


class GameApp:
    def __init__(self):
        pygame.init()
        self.config = {
            "res_index": 0,         
            "fullscreen": False,
            "theme": THEME_NAMES[0],
            "speed": 5              
        }
        self.screen = None
        self.apply_display_settings()
        pygame.display.set_caption("Black Hole Escape")
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