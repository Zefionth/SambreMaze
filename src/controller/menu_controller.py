"""Контроллер для работы с меню"""
import pygame
from src.model.menu_model import MenuModel
from src.view.menu_view import MenuView

class MenuController:
    def __init__(self, screen):
        self.screen = screen
        self.model = MenuModel()
        self.view = MenuView(screen)
        self.active = True
        self.start_game = False

    def handle_events(self) -> bool:
        mouse_pos = pygame.mouse.get_pos()
        mouse_click = pygame.mouse.get_pressed()[0]

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False

            if self.model.current_menu == "main":
                for button in self.model.main_menu_buttons:
                    button.check_hover(mouse_pos)
                    if button.is_clicked(mouse_pos, mouse_click):
                        if button.text == "Начать игру":
                            self.start_game = True
                        elif button.text == "Настройки":
                            self.model.current_menu = "settings"
                        elif button.text == "Выход":
                            return False

            elif self.model.current_menu == "settings":
                # Обработка слайдеров
                slider_changed = False
                for slider in self.model.settings_sliders:
                    if slider.handle_event(event):
                        slider_changed = True
                
                if slider_changed:
                    self.model.apply_settings_immediately()
                    continue
                
                # Обработка сброса
                for button in self.model.settings_buttons:
                    button.check_hover(mouse_pos)
                    if button.is_clicked(mouse_pos, mouse_click):
                        if button.text == "Сброс":
                            self.model.reset_to_default()  # Полный сброс
                            continue
                        elif button.text == "Сохранить":
                            self.model.save_settings()
                        elif button.text == "Назад":
                            self.model.current_menu = "main"

        return True

    def update(self, dt: float):
        """Обновляет состояние меню"""
        pass  # В текущей реализации не требуется

    def draw(self):
        """Отрисовывает меню"""
        self.view.draw(
            current_menu=self.model.current_menu,
            main_buttons=self.model.main_menu_buttons,
            settings_sliders=self.model.settings_sliders,
            color_pickers=self.model.color_pickers,
            settings_buttons=self.model.settings_buttons,
            active_picker=self.model.active_color_picker,
            color_sliders=self.model.color_components,
            colors=self.model.settings['colors']
        )