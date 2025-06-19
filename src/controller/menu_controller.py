"""Контроллер для работы с меню"""
import pygame
from src.model.menu_model import MenuModel
from src.view.menu_view import MenuView

class MenuController:
    def __init__(self, screen, sounds):
        self.screen = screen
        self.sounds = sounds
        self.model = MenuModel()
        self.view = MenuView(screen)
        self.active = True
        self.start_game = False

    def handle_events(self) -> bool:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            
            mouse_pos = pygame.mouse.get_pos()
            
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                self._handle_mouse_click(mouse_pos)
                
            elif event.type == pygame.MOUSEMOTION:
                self._handle_mouse_motion(mouse_pos)
                
            elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                self._reset_dragging_states()

        return True

    def _handle_mouse_click(self, mouse_pos):
        """Обрабатывает клик мыши"""
        if self.model.current_menu == "main":
            self._handle_main_menu_click(mouse_pos)
        elif self.model.current_menu == "settings":
            self._handle_settings_menu_click(mouse_pos)

    def _handle_main_menu_click(self, mouse_pos):
        """Обрабатывает клики в главном меню"""
        for button in self.model.main_menu_buttons:
            if button.rect.collidepoint(mouse_pos):
                self.sounds['click'].play()
                if button.text == "Начать игру":
                    self.start_game = True
                elif button.text == "Настройки":
                    self.model.current_menu = "settings"
                elif button.text == "Выход":
                    pygame.event.post(pygame.event.Event(pygame.QUIT))
                break

    def _handle_settings_menu_click(self, mouse_pos):
        """Обрабатывает клики в меню настроек"""
        # Обработка цветовых пикеров
        for picker in self.model.color_pickers:
            if picker.rect.collidepoint(mouse_pos):
                self.sounds['click'].play()
                self.model.active_color_picker = picker
                self.model.update_color_sliders()
                self.model.apply_settings_immediately()
                return
        
        # Обработка слайдеров настроек
        for slider in self.model.settings_sliders:
            if slider.knob_rect.collidepoint(mouse_pos):
                self.sounds['click'].play()
                slider.dragging = True
                return
        
        # Обработка RGB слайдеров
        if self.model.active_color_picker:
            for slider in self.model.color_components:
                if slider.knob_rect.collidepoint(mouse_pos):
                    self.sounds['click'].play()
                    slider.dragging = True
                    return
        
        # Обработка кнопок настроек
        for button in self.model.settings_buttons:
            if button.rect.collidepoint(mouse_pos):
                self.sounds['click'].play()
                if button.text == "Сброс":
                    self.model.reset_to_default()
                elif button.text == "Сохранить":
                    self.model.save_settings()
                elif button.text == "Назад":
                    self.model.current_menu = "main"
                break

    def _handle_mouse_motion(self, mouse_pos):
        """Обрабатывает движение мыши"""
        # Обновление состояния наведения для кнопок
        buttons = (
            self.model.main_menu_buttons if self.model.current_menu == "main"
            else self.model.settings_buttons
        )
        for button in buttons:
            button.check_hover(mouse_pos)
        
        # Обработка перетаскивания слайдеров
        self._update_dragging_sliders(mouse_pos)

    def _update_dragging_sliders(self, mouse_pos):
        """Обновляет позицию перетаскиваемых слайдеров"""
        # Слайдеры основных настроек
        for slider in self.model.settings_sliders:
            if slider.dragging:
                self._update_slider_value(slider, mouse_pos)
                self.model.apply_settings_immediately()
                return
        
        # RGB слайдеры
        if self.model.active_color_picker:
            for slider in self.model.color_components:
                if slider.dragging:
                    self._update_slider_value(slider, mouse_pos)
                    self._update_color_from_sliders()
                    return

    def _update_slider_value(self, slider, mouse_pos):
        """Обновляет значение слайдера на основе позиции мыши"""
        relative_x = mouse_pos[0] - slider.rect.x
        percentage = max(0, min(1, relative_x / slider.rect.width))
        slider.value = slider.min + percentage * (slider.max - slider.min)
        slider.update_knob()

    def _update_color_from_sliders(self):
        """Обновляет цвет из RGB слайдеров"""
        r = int(self.model.color_components[0].value)
        g = int(self.model.color_components[1].value)
        b = int(self.model.color_components[2].value)
        self.model.active_color_picker.color = [r, g, b]
        self.model.apply_settings_immediately()

    def _reset_dragging_states(self):
        """Сбрасывает состояние перетаскивания для всех слайдеров"""
        for slider in self.model.settings_sliders:
            slider.dragging = False
        for slider in self.model.color_components:
            slider.dragging = False

    def update(self, dt: float):
        """Обновляет состояние меню (заглушка)"""
        pass

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
            colors={}
        )