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
        self.slider_clicked = False

    def handle_events(self) -> bool:
        mouse_pos = pygame.mouse.get_pos()
        mouse_clicked = False

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
                
            # Обработка кликов мыши
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_clicked = True
                
                if self.model.current_menu == "main":
                    for button in self.model.main_menu_buttons:
                        if button.rect.collidepoint(event.pos):
                            self.sounds['click'].play()
                            if button.text == "Начать игру":
                                self.start_game = True
                            elif button.text == "Настройки":
                                self.model.current_menu = "settings"
                            elif button.text == "Выход":
                                return False
                            break  # Обрабатываем только одну кнопку за клик

                elif self.model.current_menu == "settings":
                    # Обработка цветовых пикеров
                    for picker in self.model.color_pickers:
                        if picker.rect.collidepoint(event.pos):
                            self.sounds['click'].play()
                            self.model.active_color_picker = picker
                            self.model.update_color_sliders()
                            self.model.apply_settings_immediately()
                            break
                    
                    # Обработка слайдеров
                    for slider in self.model.settings_sliders:
                        if slider.knob_rect.collidepoint(event.pos):
                            self.sounds['click'].play()
                            self.slider_clicked = True
                            slider.dragging = True
                            break
                    
                    # Обработка кнопок
                    for button in self.model.settings_buttons:
                        if button.rect.collidepoint(event.pos):
                            self.sounds['click'].play()
                            if button.text == "Сброс":
                                self.model.reset_to_default()
                            elif button.text == "Сохранить":
                                self.model.save_settings()
                            elif button.text == "Назад":
                                self.model.current_menu = "main"
                            break
                
                # Обработка RGB слайдеров
                if self.model.active_color_picker:
                    for slider in self.model.color_components:
                        if slider.knob_rect.collidepoint(event.pos):
                            self.sounds['click'].play()
                            self.slider_clicked = True
                            slider.dragging = True
                            break
            
            # Обработка перемещения мыши для слайдеров
            elif event.type == pygame.MOUSEMOTION:
                mouse_pos = event.pos
                
                # Обновление ховер-состояния кнопок
                if self.model.current_menu == "main":
                    for button in self.model.main_menu_buttons:
                        button.check_hover(mouse_pos)
                elif self.model.current_menu == "settings":
                    for button in self.model.settings_buttons:
                        button.check_hover(mouse_pos)
                
                # Обработка перетаскивания слайдеров
                if self.slider_clicked:
                    for slider in self.model.settings_sliders:
                        if slider.dragging:
                            relative_x = mouse_pos[0] - slider.rect.x
                            percentage = max(0, min(1, relative_x / slider.rect.width))
                            slider.value = slider.min + percentage * (slider.max - slider.min)
                            slider.update_knob()
                            self.model.apply_settings_immediately()
                    
                    if self.model.active_color_picker:
                        for slider in self.model.color_components:
                            if slider.dragging:
                                relative_x = mouse_pos[0] - slider.rect.x
                                percentage = max(0, min(1, relative_x / slider.rect.width))
                                slider.value = slider.min + percentage * (slider.max - slider.min)
                                slider.update_knob()
                                
                                # Обновляем цвет
                                r = int(self.model.color_components[0].value)
                                g = int(self.model.color_components[1].value)
                                b = int(self.model.color_components[2].value)
                                self.model.active_color_picker.color = [r, g, b]
                                self.model.apply_settings_immediately()
            
            # Обработка отпускания кнопки мыши
            elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                self.slider_clicked = False
                # Сбрасываем состояние перетаскивания для всех слайдеров
                for slider in self.model.settings_sliders:
                    slider.dragging = False
                for slider in self.model.color_components:
                    slider.dragging = False

        return True

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