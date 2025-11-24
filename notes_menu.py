
import pygame

class Notes_Menu:
    """
    Single-line notes input for pygame 2.x.
    - Enter commits note (saved in self.notes and appended to notes.txt)
    - Backspace deletes one char
    - Characters handled via TEXTINPUT (preferred) + KEYDOWN unicode fallback
    """
    def __init__(self, x, y, width=600, height=300, font_size=28):
        # Layout
        self.rect = pygame.Rect(x, y, width, height)
        pad = 20
        self.input_rect = pygame.Rect(x + pad, y + pad, width - 2*pad, 48)
        self.notes_area = pygame.Rect(x + pad, y + pad + 60, width - 2*pad, height - (60 + pad))

        # Visuals
        self.bg_color = (20, 20, 20)
        self.border_color = (180, 180, 180)
        self.input_bg = (35, 35, 35)
        self.input_border = (220, 220, 220)

        # Text/caret
        self.font = pygame.font.SysFont("arial", font_size)
        self.text = ""
        self.cursor_visible = True
        self.cursor_timer = 0
        self.cursor_interval_ms = 500

        # Saved notes
        self.notes = []

    # ----- Input handling -----
    def handle_key(self, event: pygame.event.Event):
        """
        Handle control keys (Enter, Backspace) and printable fallback.
        """
        if event.key == pygame.K_RETURN:
            t = self.text.strip()
            if t:
                self.notes.append(t)
                self.text = ""
                # Optional persistence
                try:
                    with open("notes.txt", "a", encoding="utf-8") as f:
                        f.write(t + "\n")
                except Exception:
                    pass

        elif event.key == pygame.K_BACKSPACE:
            self.text = self.text[:-1]

    def handle_text(self, text: str):
        """
        Handle printable characters from TEXTINPUT (preferred).
        """
        if text:
            self.text += text


    # ----- Update / draw -----
    def update(self, dt_ms: int):
        self.cursor_timer += dt_ms
        if self.cursor_timer >= self.cursor_interval_ms:
            self.cursor_visible = not self.cursor_visible
            self.cursor_timer = 0

    def draw(self, surface: pygame.Surface):
        # Panel
        pygame.draw.rect(surface, self.bg_color, self.rect, border_radius=8)
        pygame.draw.rect(surface, self.border_color, self.rect, 2, border_radius=8)

        # Input box
        pygame.draw.rect(surface, self.input_bg, self.input_rect, border_radius=6)
        pygame.draw.rect(surface, self.input_border, self.input_rect, 2, border_radius=6)

        # Current text
        txt_surf = self.font.render(self.text, True, (255, 255, 255))
        surface.blit(txt_surf, (self.input_rect.x + 8, self.input_rect.y + 10))

        # Caret
        if self.cursor_visible:
            cursor_x = self.input_rect.x + 8 + txt_surf.get_width() + 2
            cursor_y1 = self.input_rect.y + 8
            cursor_y2 = self.input_rect.y + self.input_rect.height - 8
            pygame.draw.line(surface, (255, 255, 255), (cursor_x, cursor_y1), (cursor_x, cursor_y2), 2)

        # Title
        title = self.font.render("Notes", True, (255, 255, 0))
        surface.blit(title, (self.rect.x + 20, self.rect.y + self.rect.height - 40))

        # Notes preview
        line_h = self.font.get_height() + 6
        max_lines = max(1, (self.notes_area.height // line_h) - 1)
        to_show = self.notes[-max_lines:] if max_lines > 0 else self.notes

        y_line = self.notes_area.y
        for note in to_show:
            note_surf = self.font.render(f"• {note}", True, (255,255,255))
            surface.blit(note_surf, (self.notes_area.x, y_line))
            y_line += line_h