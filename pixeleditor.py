import pygame
import pygame_gui

def pixelEditor():
    class PixelEditor:
        def __init__(self, screen, manager):
            self.manager = manager
            self.screen = screen
            self.scale = 1
            self.pixelscale = 1
            self.grid_size = 8
            self.color = (255, 0, 0)

            self.pixel_size = 80  # initial: 640 / 8 = 80
            self.grid_width = self.grid_height = self.grid_size
            self.pixels = [[(0, 0, 0) for _ in range(self.grid_width)] for _ in range(self.grid_height)]

            self.setup_ui()

        def setup_ui(self):
            self.r_slider = pygame_gui.elements.UIHorizontalSlider(
                relative_rect=pygame.Rect((10, 660), (200, 20)),
                start_value=255, value_range=(0, 255), manager=self.manager
            )
            self.g_slider = pygame_gui.elements.UIHorizontalSlider(
                relative_rect=pygame.Rect((10, 690), (200, 20)),
                start_value=0, value_range=(0, 255), manager=self.manager
            )
            self.b_slider = pygame_gui.elements.UIHorizontalSlider(
                relative_rect=pygame.Rect((10, 720), (200, 20)),
                start_value=0, value_range=(0, 255), manager=self.manager
            )

            self.color_preview = pygame_gui.elements.UIPanel(
                relative_rect=pygame.Rect((220, 660), (60, 80)),
                starting_height=1, manager=self.manager
            )

            self.scale_dropdown = pygame_gui.elements.UIDropDownMenu(
                options_list=["1x", "2x", "3x"],
                starting_option="1x",
                relative_rect=pygame.Rect((300, 660), (100, 30)),
                manager=self.manager
            )

            self.scale_input = pygame_gui.elements.UITextEntryLine(
                relative_rect=pygame.Rect((410, 660), (50, 30)),
                manager=self.manager
            )
            self.scale_input.set_text("1")
            self.scale_input.set_allowed_characters("0123456789")
        def update_color(self):
            self.color = (
                int(self.r_slider.get_current_value()),
                int(self.g_slider.get_current_value()),
                int(self.b_slider.get_current_value())
            )

        def update_preview(self):
            preview_surface = pygame.Surface((60, 80))
            preview_surface.fill(self.color)
            self.color_preview.set_image(preview_surface)

        def draw(self):
            for y, row in enumerate(self.pixels):
                for x, color in enumerate(row):
                    pygame.draw.rect(
                        self.screen, color,
                        (x * self.pixel_size, y * self.pixel_size,
                         self.pixel_size, self.pixel_size)
                    )

        def edit_pixel(self, pos):
            x, y = pos
            pixel_x = x // self.pixel_size
            pixel_y = y // self.pixel_size
            if 0 <= pixel_x < self.grid_width and 0 <= pixel_y < self.grid_height:
                self.pixels[pixel_y][pixel_x] = self.color

        def export_to_bs(self, filename="exported_pixels.bs"):
            with open(filename, "w") as f:
                f.write("// Exported pixel data from Pixel Editor\n\nwindowSize = 8,8;\nwindow;\n\n")
                s = self.pixel_size
                for y in range(self.grid_height):
                    for x in range(self.grid_width):
                        r, g, b = self.pixels[y][x]
                        if (r, g, b) != (0, 0, 0):
                            f.write(f"pixel {x},{y},{r},{g},{b},{s};\n")
            print(f"Exported to {filename}")

        def change_scale(self, factor):
            self.scale = int(factor[0])
            new_size = 640 * self.scale
            pygame.display.set_mode((new_size, 800))
            self.pixel_size = new_size // self.grid_size

        def changePixelScale(self, factor):
            self.pixelscale = self.scale_input.get_text()
            if self.pixelscale.isdigit():
                self.pixelscale = int(self.pixelscale)
                if self.pixelscale < 1:
                    self.pixelscale = 1
           

    # Setup
    pygame.init()
    screen = pygame.display.set_mode((640, 800))
    pygame.display.set_caption("Pixel Editor for BScript (Beta)")
    clock = pygame.time.Clock()
    manager = pygame_gui.UIManager((640, 800))
    editor = PixelEditor(screen, manager)
    running = True

    while running:
        time_delta = clock.tick(60) / 1000.0
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1 and event.pos[1] < 640 * editor.scale:
                    editor.edit_pixel(event.pos)

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_s:
                    editor.export_to_bs()

            elif event.type == pygame_gui.UI_DROP_DOWN_MENU_CHANGED:
                if event.ui_element == editor.scale_dropdown:
                    editor.change_scale(event.text)

            manager.process_events(event)

        editor.update_color()
        editor.update_preview()

        screen.fill((30, 30, 30))
        editor.draw()
        manager.update(time_delta)
        manager.draw_ui(screen)
        pygame.display.flip()

    pygame.quit()