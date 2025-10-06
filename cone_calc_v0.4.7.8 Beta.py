# === КОНФИГУРАЦИЯ И ИМПОРТЫ ===
import os
os.environ['KIVY_NO_ARGS'] = '1'

from kivy.config import Config
Config.set('graphics', 'multisamples', '0')
Config.set('kivy', 'log_level', 'warning')
Config.set('graphics', 'minimum_width', '320')
Config.set('graphics', 'minimum_height', '480')

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition
from kivy.uix.popup import Popup
from kivy.uix.progressbar import ProgressBar
from kivy.metrics import dp, sp
from kivy.clock import Clock
from kivy.graphics import Color, RoundedRectangle, Rectangle
from kivy.graphics.texture import Texture
from kivy.storage.jsonstore import JsonStore
from kivy.animation import Animation
from kivy.core.window import Window
from kivy.utils import get_color_from_hex
import math
import random
from datetime import datetime
import json
import sys
import traceback

# === КОНФИГУРАЦИЯ ПРИЛОЖЕНИЯ ===
class AppConfig:
    """Централизованная конфигурация приложения"""
    VERSION = "0.4.7.8"
    APP_NAME = "КАЛЬКУЛЯТОР КОНУСА"
    
    # Цветовая палитра (единая для Kivy и PyGame)
    COLORS = {
        'primary': (0.2, 0.5, 0.8, 1),
        'secondary': (0.3, 0.3, 0.5, 1),
        'success': (0.2, 0.7, 0.3, 1),
        'warning': (0.8, 0.5, 0.2, 1),
        'danger': (0.8, 0.3, 0.3, 1),
        'dark': (0.1, 0.1, 0.2, 1),
        'light': (0.9, 0.9, 1, 1),
        'background': (0.08, 0.12, 0.18, 1)
    }
    
    # Настройки производительности
    PERFORMANCE = {
        'fps_active': 60,
        'fps_idle': 30,
        'fps_background': 10,
        'max_particles_small': 20,
        'max_particles_medium': 35,
        'max_particles_large': 50,
        'texture_cache_size': 5
    }
    
    # Ограничения данных
    LIMITS = {
        'max_history_items': 100,
        'max_segments': 36,
        'min_segments': 8,
        'max_diameter': 10000,
        'min_diameter': 1
    }

# === УЛУЧШЕННАЯ СИСТЕМА ЛОГИРОВАНИЯ ===
class ErrorLogger:
    """Умная система логирования с автовосстановлением"""
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ErrorLogger, cls).__new__(cls)
            cls._instance._setup()
        return cls._instance
    
    def _setup(self):
        """Инициализация системы логирования"""
        self.log_file = 'cone_calculator_errors.log'
        self._session_errors = 0
        self._max_errors_per_session = 50
        
        # Создаем лог-файл если не существует
        try:
            if not os.path.exists(self.log_file):
                with open(self.log_file, 'w', encoding='utf-8') as f:
                    f.write(f"=== CALCULATOR LOG FILE ===\n")
                    f.write(f"Created: {datetime.now()}\n")
                    f.write(f"Version: {AppConfig.VERSION}\n\n")
        except Exception as e:
            print(f"CRITICAL: Cannot create log file: {e}")
    
    def log_event(self, message, level="INFO"):
        """Запись события в лог с уровнем важности"""
        try:
            if self._session_errors >= self._max_errors_per_session:
                return  # Прекращаем логирование при превышении лимита
                
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            log_entry = f"[{timestamp}] [{level}] {message}\n"
            
            with open(self.log_file, 'a', encoding='utf-8') as f:
                f.write(log_entry)
                
        except Exception as e:
            print(f"LOG FAILED: {e}")
    
    def log_error(self, error, context="", recoverable=True):
        """Запись ошибки с автоматическим восстановлением"""
        self._session_errors += 1
        
        error_msg = f"{context}: {str(error)}"
        self.log_event(error_msg, "ERROR")
        
        # Логируем traceback для невосстановимых ошибок
        if not recoverable:
            traceback_msg = traceback.format_exc()
            if traceback_msg:
                self.log_event(f"Traceback: {traceback_msg}", "CRITICAL")
        
        # Автоматическое восстановление для recoverable ошибок
        if recoverable and hasattr(self, '_recovery_callback'):
            try:
                self._recovery_callback()
            except Exception as recovery_error:
                self.log_event(f"Recovery failed: {recovery_error}", "CRITICAL")
    
    def set_recovery_callback(self, callback):
        """Установка callback для автоматического восстановления"""
        self._recovery_callback = callback

# Инициализация логгера
error_logger = ErrorLogger()

# === АДАПТИВНЫЕ МЕТРИКИ ПРОФЕССИОНАЛЬНОГО УРОВНЯ ===
class AdaptiveMetrics:
    """Умная система адаптации под разные экраны"""
    
    # Золотое сечение для идеальных пропорций
    GOLDEN_RATIO = 1.618
    
    @staticmethod
    def get_screen_profile():
        """Детальный профиль экрана для точной адаптации"""
        try:
            width, height = Window.size
            diagonal = math.sqrt(width**2 + height**2) / 96  # Диагональ в дюймах
            
            profiles = {
                "small": {"max_diagonal": 5.0, "scale": 0.7, "base_font": 12},
                "medium": {"max_diagonal": 8.0, "scale": 0.85, "base_font": 14},
                "large": {"max_diagonal": 13.0, "scale": 1.0, "base_font": 16},
                "xlarge": {"max_diagonal": float('inf'), "scale": 1.15, "base_font": 18}
            }
            
            for profile_name, profile in profiles.items():
                if diagonal <= profile["max_diagonal"]:
                    return {
                        "name": profile_name,
                        "scale_factor": profile["scale"],
                        "base_font_size": profile["base_font"],
                        "width": width,
                        "height": height,
                        "diagonal": diagonal
                    }
                    
            return profiles["large"]
        except Exception as e:
            error_logger.log_error(e, "AdaptiveMetrics.get_screen_profile")
            return {"name": "large", "scale_factor": 1.0, "base_font_size": 16}
    
    @staticmethod
    def get_scale_factor():
        """Коэффициент масштабирования с учетом плотности пикселей"""
        profile = AdaptiveMetrics.get_screen_profile()
        return profile["scale_factor"]
    
    @staticmethod
    def adaptive_dp(value):
        """Адаптивная dp с золотым сечением"""
        base_value = value * AdaptiveMetrics.get_scale_factor()
        return dp(round(base_value * AdaptiveMetrics.GOLDEN_RATIO) / AdaptiveMetrics.GOLDEN_RATIO)
    
    @staticmethod
    def adaptive_sp(value):
        """Адаптивная sp с идеальной читаемостью"""
        profile = AdaptiveMetrics.get_screen_profile()
        base_size = profile["base_font_size"] * (value / 16)
        return sp(base_size * AdaptiveMetrics.get_scale_factor())
    
    @staticmethod
    def get_padding():
        """Идеальные отступы по золотому сечению"""
        profile = AdaptiveMetrics.get_screen_profile()
        base_paddings = {"small": 10, "medium": 14, "large": 18, "xlarge": 22}
        base = base_paddings.get(profile["name"], 16)
        return AdaptiveMetrics.adaptive_dp(base)
    
    @staticmethod
    def get_button_height():
        """Идеальная высота кнопок для touch-интерфейса"""
        return AdaptiveMetrics.adaptive_dp(50)

# === УМНАЯ СИСТЕМА РЕНДЕРИНГА KIVY + PYGAME ===
class UnifiedRenderer:
    """Объединяет Kivy и PyGame в единую систему рендеринга"""
    
    def __init__(self):
        self._kivy_textures = {}
        self._pygame_surfaces = {}
        self._current_fps = AppConfig.PERFORMANCE['fps_active']
        self._is_animating = False
        self._frame_count = 0
        
    def get_kivy_texture(self, name, size):
        """Кэширование Kivy текстур"""
        key = f"{name}_{size[0]}_{size[1]}"
        if key not in self._kivy_textures:
            texture = Texture.create(size=size)
            self._kivy_textures[key] = texture
            # Ограничение размера кэша
            if len(self._kivy_textures) > AppConfig.PERFORMANCE['texture_cache_size']:
                oldest_key = next(iter(self._kivy_textures))
                del self._kivy_textures[oldest_key]
        return self._kivy_textures[key]
    
    def optimize_fps(self, is_user_active=True, has_animations=False):
        """Автоматическая оптимизация FPS"""
        old_fps = self._current_fps
        
        if not is_user_active:
            self._current_fps = AppConfig.PERFORMANCE['fps_background']
        elif has_animations:
            self._current_fps = AppConfig.PERFORMANCE['fps_active']
        else:
            self._current_fps = AppConfig.PERFORMANCE['fps_idle']
        
        if old_fps != self._current_fps:
            error_logger.log_event(f"FPS optimized: {old_fps} -> {self._current_fps}")
        
        return self._current_fps

# === БАЗОВЫЙ КЛАСС ЭКРАНА ПРОФЕССИОНАЛЬНОГО УРОВНЯ ===
class ProfessionalScreen(Screen):
    """Базовый экран с идеальной интеграцией Kivy + PyGame"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._renderer = UnifiedRenderer()
        self._keyboard = None
        self._is_active = False
        
        # Единая система анимаций
        self._animations = {}
        self._particle_systems = []
        
        self.setup_ui()
        self._setup_interactions()
    
    def _setup_interactions(self):
        """Настройка интерактивных элементов"""
        self._keyboard = Window.request_keyboard(self._keyboard_closed, self)
        self._keyboard.bind(on_key_down=self._on_keyboard_down)
        
        # Оптимизация производительности при изменении активности
        Window.bind(mouse_pos=self._on_mouse_move)
    
    def _keyboard_closed(self):
        """Корректное закрытие клавиатуры"""
        if self._keyboard:
            self._keyboard.unbind(on_key_down=self._on_keyboard_down)
            self._keyboard = None
    
    def _on_keyboard_down(self, keyboard, keycode, text, modifiers):
        """Умная обработка горячих клавиш"""
        try:
            key = keycode[1]
            
            # Динамическое переключение FPS при активности
            self._renderer.optimize_fps(is_user_active=True, has_animations=True)
            
            hotkeys = {
                'escape': self.on_back_press,
                'enter': self._trigger_calculation,
                'f1': self.show_help,
                's': self._trigger_export if 'ctrl' in modifiers else None
            }
            
            handler = hotkeys.get(key)
            if handler:
                handler()
                return True
                
            return False
            
        except Exception as e:
            error_logger.log_error(e, "ProfessionalScreen._on_keyboard_down")
            return False
    
    def _on_mouse_move(self, instance, pos):
        """Отслеживание активности пользователя для оптимизации"""
        self._renderer.optimize_fps(is_user_active=True, has_animations=bool(self._animations))
    
    def _trigger_calculation(self):
        """Умный триггер расчета"""
        if hasattr(self, 'calculate') and hasattr(self, 'calc_btn'):
            if not self.calc_btn.disabled:
                self.calculate(None)
    
    def _trigger_export(self):
        """Умный триггер экспорта"""
        if hasattr(self, 'export_calculation'):
            self.export_calculation(None)
    
    def on_enter(self):
        """При активации экрана"""
        self._is_active = True
        self._renderer.optimize_fps(is_user_active=True, has_animations=True)
    
    def on_leave(self):
        """При деактивации экрана"""
        self._is_active = False
        self._renderer.optimize_fps(is_user_active=False, has_animations=False)
        
        # Останавливаем анимации для экономии ресурсов
        for anim in self._animations.values():
            anim.cancel(self)
    
    def create_professional_button(self, text, color_name, on_press=None, size_hint=(1, None)):
        """Создание кнопки профессионального уровня"""
        btn = AnimatedButton(
            text=text,
            size_hint=size_hint,
            height=AdaptiveMetrics.get_button_height(),
            background_color=AppConfig.COLORS[color_name],
            background_normal='',
            font_size=AdaptiveMetrics.adaptive_sp(16),
            bold=True
        )
        
        if on_press:
            btn.bind(on_press=on_press)
            
        return btn
    
    def show_toast(self, message, duration=2.0, message_type="info"):
        """Улучшенная система уведомлений"""
        try:
            toast_color = {
                "info": (0.2, 0.5, 0.8, 0.95),
                "success": (0.2, 0.7, 0.3, 0.95),
                "warning": (0.8, 0.5, 0.2, 0.95),
                "error": (0.8, 0.3, 0.3, 0.95)
            }.get(message_type, (0.2, 0.5, 0.8, 0.95))
            
            toast = Toast(
                text=message,
                background_color=toast_color,
                duration=duration
            )
            
            toast.show(self)
            return toast
            
        except Exception as e:
            error_logger.log_error(e, "ProfessionalScreen.show_toast")

# === УЛУЧШЕННЫЙ КОМПОНЕНТ TOAST ===
class Toast(FloatLayout):
    """Профессиональные уведомления с физикой"""
    
    def __init__(self, text="", background_color=None, duration=2.0, **kwargs):
        super().__init__(**kwargs)
        
        self.size_hint = (None, None)
        self.size = (AdaptiveMetrics.adaptive_dp(300), AdaptiveMetrics.adaptive_dp(50))
        self.pos_hint = {'center_x': 0.5, 'top': 0.95}
        self.duration = duration
        
        with self.canvas.before:
            Color(*background_color if background_color else AppConfig.COLORS['primary'])
            self.rect = RoundedRectangle(
                pos=self.pos, 
                size=self.size,
                radius=[AdaptiveMetrics.adaptive_dp(25)]
            )
        
        self.label = Label(
            text=text,
            color=AppConfig.COLORS['light'],
            font_size=AdaptiveMetrics.adaptive_sp(14),
            bold=True,
            size=self.size,
            text_size=(self.size[0] - AdaptiveMetrics.adaptive_dp(20), None),
            halign='center',
            valign='middle'
        )
        
        self.add_widget(self.label)
        self.bind(pos=self._update_rect, size=self._update_rect)
    
    def _update_rect(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size
        self.label.size = self.size
        self.label.text_size = (self.size[0] - AdaptiveMetrics.adaptive_dp(20), self.size[1])
    
    def show(self, parent):
        """Показ с физической анимацией"""
        parent.add_widget(self)
        
        # Анимация с физикой (пружина)
        initial_pos = [self.center_x, self.center_y + 100]
        self.center = initial_pos
        
        anim = Animation(
            center_x=self.center_x,
            center_y=self.center_y - 100,
            duration=0.3,
            transition='out_back'
        )
        anim += Animation(
            center_x=self.center_x,
            center_y=self.center_y,
            duration=0.2,
            transition='in_out_circ'
        )
        
        anim.start(self)
        
        # Автоматическое скрытие
        Clock.schedule_once(lambda dt: self.dismiss(), self.duration)
    
    def dismiss(self):
        """Плавное скрытие"""
        anim = Animation(
            center_y=self.center_y + 100,
            opacity=0,
            duration=0.3,
            transition='in_back'
        )
        anim.bind(on_complete=lambda *args: self.parent.remove_widget(self) if self.parent else None)
        anim.start(self)

# === ПРОДВИНУТАЯ АНИМИРОВАННАЯ КНОПКА ===
class AnimatedButton(Button):
    """Кнопка с тактильной обратной связью и физикой"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.original_color = self.background_color[:] if self.background_color else [0.5, 0.5, 0.5, 1]
        self.original_size = self.size[:] if self.size else [100, 50]
        self.minimum_height = AdaptiveMetrics.get_button_height()
        
        # Физические свойства
        self._is_pressed = False
        self._animation = None
        
    def on_press(self):
        """Тактильная анимация нажатия"""
        if self._animation:
            self._animation.cancel(self)
        
        self._is_pressed = True
        
        # Комплексная анимация с физикой
        self._animation = (
            Animation(
                background_color=[c * 0.7 for c in self.original_color],
                size=(self.width * 0.95, self.height * 0.95),
                duration=0.08,
                transition='in_out_circ'
            ) +
            Animation(
                background_color=self.original_color,
                size=self.original_size,
                duration=0.12,
                transition='out_back'
            )
        )
        
        self._animation.start(self)
        self._play_click_feedback()
        super().on_press()
    
    def _play_click_feedback(self):
        """Тактильная обратная связь"""
        try:
            # В будущем можно добавить виброотклик для мобильных устройств
            pass
        except Exception as e:
            error_logger.log_error(e, "AnimatedButton._play_click_feedback", recoverable=True)

# === УЛУЧШЕННЫЙ PYGAME РЕНДЕРЕР С ИНТЕГРАЦИЕЙ KIVY ===
class HybridPyGameRenderer(FloatLayout):
    """Идеальная интеграция PyGame в Kivy с единым циклом рендеринга"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.size_hint = (1, 1)
        
        # Единая система управления ресурсами
        self._renderer = UnifiedRenderer()
        self._texture = None
        self._last_size = (0, 0)
        
        # Умные частицы
        self._particles = []
        self._particle_timer = 0
        self._max_particles = self._get_optimal_particle_count()
        
        # Анимации
        self._animation_phase = 0
        self._is_rendering = False
        
        # Данные для визуализации
        self.calculation_data = None
        self.visualization_mode = "cone"  # cone, development, hybrid
        
        # Запуск единого цикла рендеринга
        Clock.schedule_once(self._initialize, 0.1)
    
    def _get_optimal_particle_count(self):
        """Автоматическая оптимизация количества частиц"""
        screen_profile = AdaptiveMetrics.get_screen_profile()
        screen_size = screen_profile["name"]
        
        particle_limits = {
            "small": AppConfig.PERFORMANCE['max_particles_small'],
            "medium": AppConfig.PERFORMANCE['max_particles_medium'], 
            "large": AppConfig.PERFORMANCE['max_particles_large'],
            "xlarge": AppConfig.PERFORMANCE['max_particles_large']
        }
        
        return particle_limits.get(screen_size, 30)
    
    def _initialize(self, dt):
        """Инициализация с отложенной загрузкой"""
        try:
            # Проверяем доступность PyGame
            global PYGAME_AVAILABLE
            try:
                import pygame
                PYGAME_AVAILABLE = True
                pygame.init()
                error_logger.log_event("PyGame initialized successfully")
            except ImportError:
                PYGAME_AVAILABLE = False
                error_logger.log_event("PyGame not available - using fallback")
            
            # Создаем поверхность для рендеринга
            self._create_render_surface()
            
            # Запускаем оптимизированный цикл рендеринга
            Clock.schedule_interval(self._unified_render, 1/60)
            
        except Exception as e:
            error_logger.log_error(e, "HybridPyGameRenderer._initialize")
            self._create_kivy_fallback()
    
    def _create_render_surface(self):
        """Создание поверхности для рендеринга"""
        if not PYGAME_AVAILABLE:
            return
            
        try:
            width = max(100, int(self.width))
            height = max(100, int(self.height))
            
            self._pg_surface = pygame.Surface((width, height), pygame.SRCALPHA)
            self._last_size = (width, height)
            
        except Exception as e:
            error_logger.log_error(e, "HybridPyGameRenderer._create_render_surface")
    
    def _create_kivy_fallback(self):
        """Создание fallback на чистом Kivy"""
        with self.canvas:
            Color(*AppConfig.COLORS['background'])
            Rectangle(pos=self.pos, size=self.size)
    
    def on_size(self, *args):
        """Обработка изменения размера с оптимизацией"""
        if self.width > 0 and self.height > 0:
            if PYGAME_AVAILABLE:
                self._create_render_surface()
            self._texture = None
    
    def _unified_render(self, dt):
        """Единый цикл рендеринга Kivy + PyGame"""
        if not PYGAME_AVAILABLE or not hasattr(self, '_pg_surface'):
            return
        
        try:
            # Оптимизация: пропускаем кадры если не активно
            if not any([self.calculation_data, self._particles, self._is_rendering]):
                return
            
            # Обновление анимаций
            self._animation_phase = (self._animation_phase + 0.015) % (2 * math.pi)
            
            # Очистка поверхности
            self._pg_surface.fill((0, 0, 0, 0))
            
            # Рендеринг компонентов
            self._render_gradient_background()
            self._render_particles()
            self._render_visualization()
            
            # Обновление текстуры Kivy
            self._update_kivy_texture()
            
        except Exception as e:
            error_logger.log_error(e, "HybridPyGameRenderer._unified_render")
    
    def _render_gradient_background(self):
        """Рендеринг градиентного фона"""
        try:
            width, height = self._pg_surface.get_size()
            
            # Адаптивный градиент based on screen size
            for y in range(0, height, 3):  # Оптимизация: рисуем каждую 3-ю линию
                progress = y / height
                r = int(30 + progress * 25)
                g = int(40 + progress * 20) 
                b = int(80 + progress * 50)
                
                pygame.draw.line(
                    self._pg_surface, 
                    (r, g, b), 
                    (0, y), 
                    (width, y)
                )
                
        except Exception as e:
            error_logger.log_error(e, "HybridPyGameRenderer._render_gradient_background")
            # === УМНАЯ СИСТЕМА ЧАСТИЦ С АВТОБАЛАНСИРОВКОЙ ===
class SmartParticleSystem:
    """Интеллектуальная система частиц с автобалансировкой производительности"""
    
    def __init__(self, max_particles=50):
        self.max_particles = max_particles
        self.particles = []
        self._performance_level = "high"  # high, medium, low
        self._frame_skip_counter = 0
        self._last_performance_check = 0
        
    def update_performance_level(self, fps, delta_time):
        """Автоматическая настройка производительности"""
        current_time = datetime.now().timestamp()
        
        # Проверяем производительность раз в секунду
        if current_time - self._last_performance_check > 1.0:
            self._last_performance_check = current_time
            
            if fps < 30:
                self._performance_level = "low"
                self.max_particles = max(10, self.max_particles // 2)
            elif fps < 50:
                self._performance_level = "medium" 
                self.max_particles = max(20, self.max_particles * 3 // 4)
            else:
                self._performance_level = "high"
                self.max_particles = min(100, self.max_particles * 4 // 3)
    
    def add_particle(self, x, y, particle_type="default"):
        """Добавление частицы с учетом текущей производительности"""
        if len(self.particles) >= self.max_particles:
            # Удаляем самую старую частицу
            if self.particles:
                self.particles.pop(0)
        
        particle = {
            'x': x, 'y': y,
            'vx': random.uniform(-1, 1),
            'vy': random.uniform(-2, 0),
            'life': 1.0,
            'max_life': random.uniform(1.0, 3.0),
            'size': random.uniform(1.0, 4.0),
            'color': self._get_particle_color(particle_type),
            'type': particle_type,
            'creation_time': datetime.now().timestamp()
        }
        
        self.particles.append(particle)
    
    def _get_particle_color(self, particle_type):
        """Цвета частиц в единой цветовой схеме"""
        colors = {
            "default": (100, 150, 255),
            "energy": (255, 200, 100),
            "sparkle": (255, 255, 200),
            "glow": (150, 200, 255)
        }
        return colors.get(particle_type, (100, 150, 255))
    
    def update(self, delta_time):
        """Обновление частиц с оптимизацией"""
        self._frame_skip_counter += 1
        
        # Пропускаем каждый второй кадр в режиме low performance
        if self._performance_level == "low" and self._frame_skip_counter % 2 == 0:
            return
        
        new_particles = []
        current_time = datetime.now().timestamp()
        
        for p in self.particles:
            # Обновление физики
            p['x'] += p['vx']
            p['y'] += p['vy']
            p['vy'] += 0.05  # гравитация
            
            # Уменьшение времени жизни
            age = current_time - p['creation_time']
            p['life'] = 1.0 - (age / p['max_life'])
            
            # Сохраняем только "живые" частицы
            if p['life'] > 0:
                new_particles.append(p)
        
        self.particles = new_particles
    
    def render(self, surface):
        """Рендеринг частиц с учетом производительности"""
        if self._performance_level == "low":
            # В режиме low рисуем только каждую вторую частицу
            particles_to_render = self.particles[::2]
        else:
            particles_to_render = self.particles
        
        for p in particles_to_render:
            alpha = int(255 * p['life'])
            color = (*p['color'], alpha)
            
            if p['type'] == 'sparkle':
                # Мерцающие частицы
                sparkle_intensity = 0.5 + 0.5 * math.sin(p['creation_time'] * 10)
                size = p['size'] * sparkle_intensity
                pygame.draw.circle(surface, color, (int(p['x']), int(p['y'])), int(size))
            else:
                pygame.draw.circle(surface, color, (int(p['x']), int(p['y'])), int(p['size']))

# === ПРОДОЛЖЕНИЕ HYBRID PYGAME RENDERER ===
    def _render_particles(self):
        """Рендеринг умных частиц"""
        if not hasattr(self, '_particle_system'):
            self._particle_system = SmartParticleSystem(self._max_particles)
        
        # Автобалансировка производительности
        self._particle_system.update_performance_level(60, 1/60)  # TODO: реальные значения FPS
        
        # Добавление новых частиц
        current_time = datetime.now().timestamp()
        if current_time - self._particle_timer > 0.1 and len(self._particle_system.particles) < self._max_particles:
            width, height = self._pg_surface.get_size()
            for _ in range(2):  # Добавляем по 2 частицы за раз
                x = random.uniform(0, width)
                self._particle_system.add_particle(x, height + 10, random.choice(["default", "sparkle"]))
            self._particle_timer = current_time
        
        # Обновление и рендеринг
        self._particle_system.update(1/60)
        self._particle_system.render(self._pg_surface)
    
    def _render_visualization(self):
        """Профессиональная визуализация конусов"""
        if not self.calculation_data:
            self._render_default_cone()
            return
        
        try:
            width, height = self._pg_surface.get_size()
            center_x, center_y = width // 2, height // 2
            
            if self.visualization_mode == "cone":
                self._render_cone_scheme(center_x, center_y)
            elif self.visualization_mode == "development":
                self._render_development_scheme(center_x, center_y)
            elif self.visualization_mode == "hybrid":
                self._render_hybrid_scheme(center_x, center_y)
                
        except Exception as e:
            error_logger.log_error(e, "HybridPyGameRenderer._render_visualization")
            self._render_default_cone()
    
    def _render_default_cone(self):
        """Визуализация конуса по умолчанию"""
        try:
            width, height = self._pg_surface.get_size()
            center_x, center_y = width // 2, height // 2
            
            # Анимированный конус
            scale = AdaptiveMetrics.get_scale_factor()
            base_width = int(80 * scale + 8 * math.sin(self._animation_phase * 2))
            cone_height = int(100 * scale)
            
            points = [
                (center_x, center_y - cone_height // 2),
                (center_x - base_width // 2, center_y + cone_height // 2),
                (center_x + base_width // 2, center_y + cone_height // 2),
            ]
            
            # Градиентная заливка
            for i in range(len(points)):
                color_value = 150 + int(50 * math.sin(self._animation_phase + i))
                pygame.draw.polygon(self._pg_surface, (100, color_value, 255, 100), points)
            
            # Контур
            pygame.draw.polygon(self._pg_surface, (80, 130, 235), points, 2)
            
        except Exception as e:
            error_logger.log_error(e, "HybridPyGameRenderer._render_default_cone")
    
    def _render_cone_scheme(self, center_x, center_y):
        """Схема конуса с расчетными параметрами"""
        try:
            D = self.calculation_data['diameter']
            H = self.calculation_data['height']
            
            # Масштабирование под размер экрана
            max_size = min(center_x, center_y) * 0.3
            base_radius = min(D / 2, max_size)
            cone_height = min(H, max_size)
            
            # Точки конуса
            apex = (center_x, center_y - cone_height // 2)
            base_left = (center_x - base_radius, center_y + cone_height // 2)
            base_right = (center_x + base_radius, center_y + cone_height // 2)
            
            points = [apex, base_left, base_right]
            
            # Рисуем конус
            pygame.draw.polygon(self._pg_surface, (100, 180, 255, 80), points)
            pygame.draw.polygon(self._pg_surface, (80, 160, 235), points, 2)
            
            # Подписи размеров
            font = pygame.font.Font(None, 24)
            diameter_text = font.render(f"D: {D}mm", True, (255, 255, 255))
            height_text = font.render(f"H: {H}mm", True, (255, 255, 255))
            
            self._pg_surface.blit(diameter_text, (center_x - 30, center_y + cone_height // 2 + 10))
            self._pg_surface.blit(height_text, (center_x + base_radius + 5, center_y - 10))
            
        except Exception as e:
            error_logger.log_error(e, "HybridPyGameRenderer._render_cone_scheme")
    
    def _render_development_scheme(self, center_x, center_y):
        """Схема развертки конуса"""
        try:
            if 'generatrix' not in self.calculation_data or 'angle' not in self.calculation_data:
                return
                
            radius = self.calculation_data['generatrix']
            angle = self.calculation_data['angle']
            
            # Масштабирование
            max_radius = min(center_x, center_y) * 0.4
            display_radius = min(radius, max_radius)
            display_angle = min(angle, 270)  # Ограничиваем угол
            
            # Преобразуем углы
            start_angle = math.radians(-display_angle / 2)
            end_angle = math.radians(display_angle / 2)
            
            # Радиальные линии
            pygame.draw.line(self._pg_surface, (100, 200, 255),
                            (center_x, center_y),
                            (center_x + display_radius * math.cos(start_angle), 
                             center_y + display_radius * math.sin(start_angle)), 2)
            
            pygame.draw.line(self._pg_surface, (100, 200, 255),
                            (center_x, center_y),
                            (center_x + display_radius * math.cos(end_angle), 
                             center_y + display_radius * math.sin(end_angle)), 2)
            
            # Дуга развертки
            points = []
            steps = 30
            for i in range(steps + 1):
                t = i / steps
                current_angle = start_angle + t * (end_angle - start_angle)
                points.append((
                    center_x + display_radius * math.cos(current_angle),
                    center_y + display_radius * math.sin(current_angle)
                ))
            
            if len(points) > 1:
                pygame.draw.lines(self._pg_surface, (100, 200, 255), False, points, 2)
            
            # Подписи
            font = pygame.font.Font(None, 24)
            angle_text = font.render(f"φ: {angle:.1f}°", True, (255, 255, 255))
            radius_text = font.render(f"R: {radius:.1f}mm", True, (255, 255, 255))
            
            self._pg_surface.blit(angle_text, (center_x - 30, center_y - display_radius - 30))
            self._pg_surface.blit(radius_text, (center_x + 10, center_y - 20))
            
        except Exception as e:
            error_logger.log_error(e, "HybridPyGameRenderer._render_development_scheme")
    
    def _render_hybrid_scheme(self, center_x, center_y):
        """Гибридная схема - конус и развертка вместе"""
        try:
            # Рисуем оба представления с смещением
            self._render_cone_scheme(center_x - 100, center_y)
            self._render_development_scheme(center_x + 100, center_y)
            
            # Соединительная линия
            pygame.draw.line(self._pg_surface, (150, 150, 255, 100),
                            (center_x - 50, center_y),
                            (center_x + 50, center_y), 2)
                            
        except Exception as e:
            error_logger.log_error(e, "HybridPyGameRenderer._render_hybrid_scheme")
    
    def _update_kivy_texture(self):
        """Обновление Kivy текстуры с оптимизацией"""
        if not PYGAME_AVAILABLE or not hasattr(self, '_pg_surface'):
            return
            
        try:
            # Создаем или обновляем текстуру
            if self._texture is None:
                self._texture = Texture.create(size=self._pg_surface.get_size())
                with self.canvas:
                    Color(1, 1, 1, 1)
                    self.rect = Rectangle(texture=self._texture, pos=self.pos, size=self.size)
            
            # Конвертируем PyGame surface в Kivy texture
            pg_string = pygame.image.tostring(self._pg_surface, 'RGBA')
            self._texture.blit_buffer(pg_string, colorfmt='rgba', bufferfmt='ubyte')
            
            # Обновляем позицию и размер
            self.rect.pos = self.pos
            self.rect.size = self.size
            
        except Exception as e:
            error_logger.log_error(e, "HybridPyGameRenderer._update_kivy_texture")
            self._create_kivy_fallback()
    
    def show_calculation(self, diameter, height, generatrix=None, angle=None, mode="cone"):
        """Отображение расчетных данных"""
        self.calculation_data = {
            'diameter': diameter,
            'height': height,
            'generatrix': generatrix,
            'angle': angle
        }
        self.visualization_mode = mode
        self._is_rendering = True

# === СИСТЕМА ВАЛИДАЦИИ ВХОДНЫХ ДАННЫХ ===
class InputValidator:
    """Комплексная система валидации входных данных"""
    
    @staticmethod
    def validate_number(value, field_name, min_val=None, max_val=None):
        """Валидация числового значения"""
        try:
            # Преобразование в float
            num_value = float(value)
            
            # Проверка на NaN и бесконечность
            if math.isnan(num_value) or math.isinf(num_value):
                return False, f"{field_name}: недопустимое числовое значение"
            
            # Проверка диапазона
            if min_val is not None and num_value < min_val:
                return False, f"{field_name}: должно быть не меньше {min_val}"
            
            if max_val is not None and num_value > max_val:
                return False, f"{field_name}: должно быть не больше {max_val}"
            
            return True, num_value
            
        except ValueError:
            return False, f"{field_name}: должно быть числом"
        except Exception as e:
            error_logger.log_error(e, f"InputValidator.validate_number ({field_name})")
            return False, f"Ошибка проверки {field_name}"
    
    @staticmethod
    def validate_cone_parameters(diameter, height, cut_param, segments, cut_type):
        """Комплексная валидация параметров конуса"""
        errors = []
        validated_data = {}
        
        # Валидация диаметра
        success, result = InputValidator.validate_number(
            diameter, "Диаметр", 
            min_val=AppConfig.LIMITS['min_diameter'],
            max_val=AppConfig.LIMITS['max_diameter']
        )
        if success:
            validated_data['diameter'] = result
        else:
            errors.append(result)
        
        # Валидация высоты
        success, result = InputValidator.validate_number(
            height, "Высота", min_val=1, max_val=10000
        )
        if success:
            validated_data['height'] = result
        else:
            errors.append(result)
        
        # Валидация параметра среза
        if cut_type == "slant":
            success, result = InputValidator.validate_number(
                cut_param, "Угол среза", min_val=0, max_val=90
            )
        else:
            success, result = InputValidator.validate_number(
                cut_param, "Высота среза", min_val=0, max_val=float(height) if height else 10000
            )
        
        if success:
            validated_data['cut_param'] = result
        else:
            errors.append(result)
        
        # Валидация количества сегментов
        success, result = InputValidator.validate_number(
            segments, "Количество сегментов",
            min_val=AppConfig.LIMITS['min_segments'],
            max_val=AppConfig.LIMITS['max_segments']
        )
        if success:
            validated_data['segments'] = int(result)
        else:
            errors.append(result)
        
        # Дополнительные проверки
        if not errors:
            # Проверка соотношения размеров
            if validated_data['diameter'] / validated_data['height'] > 10:
                errors.append("Слишком большое соотношение диаметра к высоте")
            
            if validated_data['diameter'] / validated_data['height'] < 0.1:
                errors.append("Слишком маленькое соотношение диаметра к высоте")
        
        return validated_data, errors

# === УЛУЧШЕННЫЙ ЭКРАН КАЛЬКУЛЯТОРА ===
class ProfessionalCalculatorScreen(ProfessionalScreen):
    """Профессиональный экран калькулятора с идеальной интеграцией"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = 'calculator'
        self.cut_type = "slant"
        self.current_calculation = None
        self.validator = InputValidator()
        
    def setup_ui(self):
        """Создание профессионального интерфейса"""
        main_layout = FloatLayout()
        
        # Фон с интегрированным рендерером
        self.renderer = HybridPyGameRenderer()
        main_layout.add_widget(self.renderer)
        
        # Основной контент
        content = self._create_content_layout()
        main_layout.add_widget(content)
        
        self.add_widget(main_layout)
        self._setup_default_values()
    
    def _create_content_layout(self):
        """Создание основного контента"""
        content = BoxLayout(
            orientation='vertical',
            padding=AdaptiveMetrics.get_padding(),
            spacing=AdaptiveMetrics.adaptive_dp(15),
            size_hint=(0.95, 0.95),
            pos_hint={'center_x': 0.5, 'center_y': 0.5}
        )
        
        # Заголовок
        content.add_widget(self._create_header())
        
        # Карточка типа среза
        content.add_widget(self._create_cut_type_card())
        
        # Карточка ввода параметров
        content.add_widget(self._create_input_card())
        
        # Панель действий
        content.add_widget(self._create_action_panel())
        
        # Карточка результатов
        self.results_card = self._create_results_card()
        content.add_widget(self.results_card)
        
        return content
    
    def _create_header(self):
        """Создание профессионального заголовка"""
        header = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=AdaptiveMetrics.get_button_height(),
            spacing=AdaptiveMetrics.adaptive_dp(10)
        )
        
        # Кнопка назад
        back_btn = self.create_professional_button(
            '← Назад (Esc)', 'secondary', self.on_back_press,
            size_hint=(None, None)
        )
        back_btn.width = AdaptiveMetrics.adaptive_dp(120)
        
        # Заголовок
        title_layout = BoxLayout(orientation='vertical', spacing=AdaptiveMetrics.adaptive_dp(2))
        title = Label(
            text='[b]ПРОФЕССИОНАЛЬНЫЙ КАЛЬКУЛЯТОР[/b]',
            font_size=AdaptiveMetrics.adaptive_sp(18),
            markup=True,
            color=AppConfig.COLORS['light']
        )
        subtitle = Label(
            text=f'Версия {AppConfig.VERSION} • Интегрированный рендеринг',
            font_size=AdaptiveMetrics.adaptive_sp(10),
            color=AppConfig.COLORS['light'][:3] + (0.8,)
        )
        title_layout.add_widget(title)
        title_layout.add_widget(subtitle)
        
        # Инструменты
        tools_layout = BoxLayout(
            orientation='horizontal',
            size_hint_x=None,
            width=AdaptiveMetrics.adaptive_dp(120),
            spacing=AdaptiveMetrics.adaptive_dp(5)
        )
        
        clear_btn = self.create_professional_button(
            '🗑️ Очистить', 'danger', self.clear_all,
            size_hint=(None, None)
        )
        clear_btn.width = AdaptiveMetrics.adaptive_dp(100)
        tools_layout.add_widget(clear_btn)
        
        header.add_widget(back_btn)
        header.add_widget(title_layout)
        header.add_widget(tools_layout)
        
        return header
    
    def _create_cut_type_card(self):
        """Карточка выбора типа среза"""
        card = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            height=AdaptiveMetrics.adaptive_dp(100),
            spacing=AdaptiveMetrics.adaptive_dp(8),
            padding=AdaptiveMetrics.adaptive_dp(15)
        )
        
        # Фон карточки
        with card.canvas.before:
            Color(*AppConfig.COLORS['dark'][:3] + (0.8,))
            self.cut_card_bg = RoundedRectangle(
                pos=card.pos, size=card.size,
                radius=[AdaptiveMetrics.adaptive_dp(12)]
            )
        
        card.bind(pos=self._update_card_bg, size=self._update_card_bg)
        
        # Заголовок
        title = Label(
            text='[b]ТИП РАЗРЕЗА КОНУСА[/b]',
            font_size=AdaptiveMetrics.adaptive_sp(16),
            markup=True,
            size_hint_y=None,
            height=AdaptiveMetrics.adaptive_dp(25),
            color=AppConfig.COLORS['light']
        )
        
        # Кнопки выбора
        btn_layout = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=AdaptiveMetrics.get_button_height(),
            spacing=AdaptiveMetrics.adaptive_dp(10)
        )
        
        self.slant_btn = self.create_professional_button(
            '🔺 КОСОЙ РАЗРЕЗ', 'primary', lambda x: self.set_cut_type("slant")
        )
        self.parallel_btn = self.create_professional_button(
            '📏 ПАРАЛЛЕЛЬНЫЙ', 'secondary', lambda x: self.set_cut_type("parallel")
        )
        
        btn_layout.add_widget(self.slant_btn)
        btn_layout.add_widget(self.parallel_btn)
        
        card.add_widget(title)
        card.add_widget(btn_layout)
        
        return card
    
    def _create_input_card(self):
        """Карточка ввода параметров"""
        card = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            height=AdaptiveMetrics.adaptive_dp(280),
            spacing=AdaptiveMetrics.adaptive_dp(12),
            padding=AdaptiveMetrics.adaptive_dp(20)
        )
        
        with card.canvas.before:
            Color(*AppConfig.COLORS['dark'][:3] + (0.8,))
            self.input_card_bg = RoundedRectangle(
                pos=card.pos, size=card.size,
                radius=[AdaptiveMetrics.adaptive_dp(15)]
            )
        
        card.bind(pos=self._update_input_card_bg, size=self._update_input_card_bg)
        
        title = Label(
            text='[b]ПАРАМЕТРЫ КОНУСА[/b]',
            font_size=AdaptiveMetrics.adaptive_sp(18),
            markup=True,
            size_hint_y=None,
            height=AdaptiveMetrics.adaptive_dp(25),
            color=AppConfig.COLORS['light']
        )
        card.add_widget(title)
        
        # Поля ввода
        self._create_input_fields(card)
        
        return card
    
    def _create_input_fields(self, parent):
        """Создание полей ввода"""
        input_fields = [
            {
                "icon": "📏", 
                "hint": "Диаметр основания (мм)", 
                "attr": "diameter_input", 
                "default": "300",
                "validator": lambda x: self.validator.validate_number(x, "Диаметр", 1, 10000)
            },
            {
                "icon": "📐", 
                "hint": "Высота конуса (мм)", 
                "attr": "height_input", 
                "default": "400",
                "validator": lambda x: self.validator.validate_number(x, "Высота", 1, 10000)
            },
            {
                "icon": "✂️", 
                "hint": "Угол среза (°)", 
                "attr": "cut_param_input", 
                "default": "30",
                "validator": lambda x: self.validator.validate_number(x, "Параметр среза", 0, 90)
            },
            {
                "icon": "🔢", 
                "hint": "Количество сегментов", 
                "attr": "segments_input", 
                "default": "16",
                "validator": lambda x: self.validator.validate_number(x, "Сегменты", 8, 36)
            }
        ]
        
        for field in input_fields:
            field_layout = BoxLayout(
                orientation='horizontal',
                size_hint_y=None,
                height=AdaptiveMetrics.get_button_height(),
                spacing=AdaptiveMetrics.adaptive_dp(10)
            )
            
            # Иконка
            icon_label = Label(
                text=field["icon"],
                size_hint_x=None,
                width=AdaptiveMetrics.adaptive_dp(30),
                font_size=AdaptiveMetrics.adaptive_sp(20),
                color=AppConfig.COLORS['light']
            )
            
            # Поле ввода
            text_input = TextInput(
                hint_text=field["hint"],
                text=field["default"],
                size_hint_x=1,
                font_size=AdaptiveMetrics.adaptive_sp(16),
                background_color=(0.1, 0.1, 0.15, 1),
                foreground_color=AppConfig.COLORS['light'],
                padding=AdaptiveMetrics.adaptive_dp(10),
                multiline=False,
                write_tab=False
            )
            
            # Валидация в реальном времени
            text_input.bind(
                on_text_validate=self._validate_field,
                on_focus=self._on_field_focus
            )
            
            setattr(self, field["attr"], text_input)
            field_layout.add_widget(icon_label)
            field_layout.add_widget(text_input)
            parent.add_widget(field_layout)
    
    def _create_action_panel(self):
        """Панель действий"""
        layout = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=AdaptiveMetrics.adaptive_dp(70),
            spacing=AdaptiveMetrics.adaptive_dp(15)
        )
        
        self.calc_btn = self.create_professional_button(
            '🧮 РАССЧИТАТЬ (Enter)', 'success', self.calculate_with_animation
        )
        
        quick_clear_btn = self.create_professional_button(
            '🔄 БЫСТРАЯ ОЧИСТКА', 'warning', self.quick_clear
        )
        
        self.export_btn = self.create_professional_button(
            '💾 ЭКСПОРТ (Ctrl+S)', 'primary', self.export_calculation
        )
        self.export_btn.disabled = True
        
        layout.add_widget(self.calc_btn)
        layout.add_widget(quick_clear_btn)
        layout.add_widget(self.export_btn)
        
        return layout
    
    def _create_results_card(self):
        """Карточка результатов"""
        card = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            height=AdaptiveMetrics.adaptive_dp(300),
            spacing=AdaptiveMetrics.adaptive_dp(12),
            padding=AdaptiveMetrics.adaptive_dp(20)
        )
        
        with card.canvas.before:
            Color(*AppConfig.COLORS['dark'][:3] + (0.8,))
            self.results_card_bg = RoundedRectangle(
                pos=card.pos, size=card.size,
                radius=[AdaptiveMetrics.adaptive_dp(15)]
            )
        
        card.bind(pos=self._update_results_card_bg, size=self._update_results_card_bg)
        
        # Заголовок результатов
        header = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=AdaptiveMetrics.adaptive_dp(40)
        )
        
        title = Label(
            text='[b]РЕЗУЛЬТАТЫ РАСЧЕТА[/b]',
            font_size=AdaptiveMetrics.adaptive_sp(18),
            markup=True,
            color=AppConfig.COLORS['light']
        )
        
        self.save_btn = self.create_professional_button(
            '💾 Сохранить', 'primary', self.save_calculation,
            size_hint=(None, None)
        )
        self.save_btn.width = AdaptiveMetrics.adaptive_dp(120)
        self.save_btn.disabled = True
        
        header.add_widget(title)
        header.add_widget(self.save_btn)
        card.add_widget(header)
        
        # Область результатов
        scroll = ScrollView(do_scroll_x=False)
        
        self.result_label = Label(
            text=self._get_welcome_message(),
            font_size=AdaptiveMetrics.adaptive_sp(14),
            color=AppConfig.COLORS['light'][:3] + (0.9,),
            markup=True,
            size_hint_y=None,
            text_size=(None, None)
        )
        self.result_label.bind(texture_size=self.result_label.setter('size'))
        
        scroll.add_widget(self.result_label)
        card.add_widget(scroll)
        
        return card
    
    def _get_welcome_message(self):
        """Приветственное сообщение"""
        return f"""[b]Добро пожаловать в {AppConfig.APP_NAME} v{AppConfig.VERSION}![/b] 🎯

[b]НОВЫЕ ВОЗМОЖНОСТИ:[/b]
• 🚀 Идеальная интеграция Kivy + PyGame
• 🎨 Профессиональный UI с золотым сечением  
• 🔋 Умная оптимизация энергопотребления
• 🛡️ Глубокая валидация входных данных
• 💫 Интеллектуальная система частиц
• 📊 Три режима визуализации

[b]ГОРЯЧИЕ КЛАВИШИ:[/b]
• Enter - расчет • Esc - назад • F1 - справка • Ctrl+S - экспорт

Начните расчет, введя параметры конуса!"""
        def _update_card_bg(self, instance, value):
        """Обновление фона карточки"""
        if hasattr(self, 'cut_card_bg'):
            self.cut_card_bg.pos = instance.pos
            self.cut_card_bg.size = instance.size
    
    def _update_input_card_bg(self, instance, value):
        """Обновление фона карточки ввода"""
        if hasattr(self, 'input_card_bg'):
            self.input_card_bg.pos = instance.pos
            self.input_card_bg.size = instance.size
    
    def _update_results_card_bg(self, instance, value):
        """Обновление фона карточки результатов"""
        if hasattr(self, 'results_card_bg'):
            self.results_card_bg.pos = instance.pos
            self.results_card_bg.size = instance.size
    
    def _validate_field(self, instance):
        """Валидация поля в реальном времени"""
        try:
            field_value = instance.text.strip()
            if not field_value:
                instance.background_color = (0.1, 0.1, 0.15, 1)
                return
            
            # Определяем тип валидации по hint text
            hint = instance.hint_text
            if "Диаметр" in hint:
                success, result = self.validator.validate_number(field_value, "Диаметр", 1, 10000)
            elif "Высота" in hint:
                success, result = self.validator.validate_number(field_value, "Высота", 1, 10000)
            elif "Угол" in hint or "Высота среза" in hint:
                max_val = 90 if "Угол" in hint else float(self.height_input.text) if self.height_input.text else 10000
                success, result = self.validator.validate_number(field_value, "Параметр", 0, max_val)
            elif "Количество" in hint:
                success, result = self.validator.validate_number(field_value, "Сегменты", 8, 36)
            else:
                success = True
            
            # Визуальная обратная связь
            if success:
                instance.background_color = (0.1, 0.2, 0.1, 1)  # Зеленый при успехе
            else:
                instance.background_color = (0.2, 0.1, 0.1, 1)  # Красный при ошибке
                self.show_toast(result, 2.0, "error")
                
        except Exception as e:
            error_logger.log_error(e, "ProfessionalCalculatorScreen._validate_field")
    
    def _on_field_focus(self, instance, focused):
        """Обработка фокуса на поле ввода"""
        if not focused:
            self._validate_field(instance)
    
    def _setup_default_values(self):
        """Установка значений по умолчанию"""
        self.set_cut_type("slant")
    
    def set_cut_type(self, cut_type):
        """Установка типа среза"""
        self.cut_type = cut_type
        
        # Визуальное выделение активной кнопки
        if cut_type == "slant":
            self.slant_btn.background_color = AppConfig.COLORS['primary']
            self.parallel_btn.background_color = AppConfig.COLORS['secondary']
            self.cut_param_input.hint_text = "Угол среза (°)"
            if hasattr(self, 'cut_param_input'):
                self.cut_param_input.text = "30"
        else:
            self.parallel_btn.background_color = AppConfig.COLORS['primary']
            self.slant_btn.background_color = AppConfig.COLORS['secondary']
            self.cut_param_input.hint_text = "Высота среза (мм)"
            if hasattr(self, 'cut_param_input'):
                self.cut_param_input.text = "200"
    
    def calculate_with_animation(self, instance):
        """Расчет с профессиональной анимацией"""
        # Визуальная обратная связь
        anim = Animation(
            background_color=[c * 0.8 for c in AppConfig.COLORS['success']], 
            duration=0.1
        ) + Animation(
            background_color=AppConfig.COLORS['success'], 
            duration=0.3
        )
        anim.start(self.calc_btn)
        
        # Запуск расчета
        Clock.schedule_once(lambda dt: self._perform_calculation(), 0.2)
    
    def _perform_calculation(self):
        """Выполнение расчета с прогресс-баром"""
        # Показ прогресс-бара
        progress_overlay = self.show_progress("Начинаем расчет...")
        
        # Пошаговый расчет
        Clock.schedule_once(lambda dt: self._calculation_step_1(progress_overlay), 0.5)
    
    def _calculation_step_1(self, progress):
        """Шаг 1: Валидация данных"""
        progress.update_progress(10, "Проверка входных данных...")
        
        try:
            # Сбор данных
            diameter = self.diameter_input.text
            height = self.height_input.text
            cut_param = self.cut_param_input.text
            segments = self.segments_input.text
            
            # Комплексная валидация
            validated_data, errors = self.validator.validate_cone_parameters(
                diameter, height, cut_param, segments, self.cut_type
            )
            
            if errors:
                progress.update_progress(100, "Обнаружены ошибки!")
                Clock.schedule_once(lambda dt: self._handle_validation_errors(errors, progress), 0.5)
                return
            
            # Сохраняем валидированные данные
            self.validated_data = validated_data
            
            # Следующий шаг
            Clock.schedule_once(lambda dt: self._calculation_step_2(progress), 0.3)
            
        except Exception as e:
            error_logger.log_error(e, "ProfessionalCalculatorScreen._calculation_step_1")
            self._handle_calculation_error("Ошибка валидации данных", progress)
    
    def _calculation_step_2(self, progress):
        """Шаг 2: Основные вычисления"""
        progress.update_progress(30, "Вычисление основных параметров...")
        
        try:
            D = self.validated_data['diameter']
            H = self.validated_data['height']
            cut_param = self.validated_data['cut_param']
            n = self.validated_data['segments']
            
            # Основные расчеты
            R = D / 2
            generatrix = math.sqrt(R**2 + H**2)  # Образующая
            angle = (R / generatrix) * 360  # Угол развертки
            
            self.calculation_intermediate = {
                'diameter': D,
                'height': H, 
                'radius': R,
                'generatrix': generatrix,
                'angle': angle,
                'cut_param': cut_param,
                'segments': n
            }
            
            # Следующий шаг
            Clock.schedule_once(lambda dt: self._calculation_step_3(progress), 0.3)
            
        except Exception as e:
            error_logger.log_error(e, "ProfessionalCalculatorScreen._calculation_step_2")
            self._handle_calculation_error("Ошибка вычислений", progress)
    
    def _calculation_step_3(self, progress):
        """Шаг 3: Расчет длин развертки"""
        progress.update_progress(50, "Расчет длин для разметки...")
        
        try:
            data = self.calculation_intermediate
            L_values = []
            
            if self.cut_type == "slant":
                # Косой срез
                alpha = data['cut_param']
                for i in range(data['segments'] + 1):
                    theta = (360 / data['segments']) * i
                    L_i = data['generatrix'] * (1 - (alpha / 90) * abs(math.sin(math.radians(theta))))
                    L_values.append(L_i)
                    
                    # Обновление прогресса
                    progress_val = 50 + (i / data['segments']) * 40
                    progress.update_progress(progress_val, f"Сегмент {i+1}/{data['segments']+1}...")
                
                cut_info = f"Угол косого среза: {alpha}°"
                
            else:
                # Параллельный срез
                h_cut = data['cut_param']
                if h_cut > data['height']:
                    h_cut = data['height'] * 0.7
                    self.cut_param_input.text = str(int(h_cut))
                
                L_cut = (data['generatrix'] / data['height']) * h_cut
                L_values = [L_cut for _ in range(data['segments'] + 1)]
                cut_info = f"Высота параллельного среза: {h_cut:.1f} мм"
            
            self.calculation_results = {
                'L_values': L_values,
                'cut_info': cut_info,
                **self.calculation_intermediate
            }
            
            # Финальный шаг
            Clock.schedule_once(lambda dt: self._calculation_step_final(progress), 0.3)
            
        except Exception as e:
            error_logger.log_error(e, "ProfessionalCalculatorScreen._calculation_step_3")
            self._handle_calculation_error("Ошибка расчета развертки", progress)
    
    def _calculation_step_final(self, progress):
        """Финальный шаг: Форматирование результатов"""
        progress.update_progress(95, "Форматирование результатов...")
        
        try:
            data = self.calculation_results
            
            # Форматирование длин
            L_display = [f"L{i:02d}: {L_values[i]:.1f} мм" for i in range(len(data['L_values']))]
            
            # Создание красивого результата
            screen_profile = AdaptiveMetrics.get_screen_profile()
            
            result_text = f"""[b]🎯 РАСЧЕТ УСПЕШНО ЗАВЕРШЕН![/b] ({screen_profile['name'].upper()} screen)

{data['cut_info']}

[b]📊 ОСНОВНЫЕ ПАРАМЕТРЫ:[/b]
• Диаметр основания: {data['diameter']} мм
• Высота конуса: {data['height']} мм  
• Радиус: {data['radius']:.1f} мм
• Длина образующей: {data['generatrix']:.1f} мм
• Угол развертки: {data['angle']:.1f}°

[b]📏 ДЛИНЫ ДЛЯ РАЗМЕТКИ ({data['segments']} сегментов):[/b]
{chr(10).join(L_display[:12])}{"..." if len(L_display) > 12 else ""}

[b]💫 РЕЖИМ ВИЗУАЛИЗАЦИИ:[/b]
• Нажмите F2 для переключения между конусом/разверткой/гибридом"""

            # Обновление UI
            self.result_label.text = result_text
            self.current_calculation = {
                'diameter': data['diameter'],
                'height': data['height'],
                'cut_type': self.cut_type,
                'cut_param': data['cut_param'],
                'segments': data['segments'],
                'result': result_text,
                'L_values': data['L_values'],
                'generatrix': data['generatrix'],
                'angle': data['angle'],
                'timestamp': datetime.now().isoformat()
            }
            
            # Активация кнопок
            self.save_btn.disabled = False
            self.export_btn.disabled = False
            
            # Визуализация
            self.renderer.show_calculation(
                data['diameter'], 
                data['height'], 
                data['generatrix'], 
                data['angle'],
                "cone"
            )
            
            # Сохранение в историю
            self._save_to_history()
            
            progress.update_progress(100, "Готово!")
            
            # Завершение
            Clock.schedule_once(lambda dt: self._calculation_complete(progress), 0.5)
            
        except Exception as e:
            error_logger.log_error(e, "ProfessionalCalculatorScreen._calculation_step_final")
            self._handle_calculation_error("Ошибка форматирования", progress)
    
    def _calculation_complete(self, progress):
        """Завершение расчета"""
        self.hide_progress()
        self.show_toast("✅ Расчет успешно завершен! (Enter для повторения)", 3.0, "success")
        
        # Добавляем частицы для визуального праздника :)
        if hasattr(self.renderer, '_particle_system'):
            for _ in range(10):
                self.renderer._particle_system.add_particle(
                    random.randint(100, 700),
                    random.randint(100, 500),
                    "sparkle"
                )
    
    def _handle_validation_errors(self, errors, progress):
        """Обработка ошибок валидации"""
        self.hide_progress()
        
        error_message = "Обнаружены ошибки:\n• " + "\n• ".join(errors[:3])  # Показываем первые 3 ошибки
        self.show_toast(error_message, 4.0, "error")
        
        # Подсвечиваем проблемные поля
        for error in errors:
            if "Диаметр" in error:
                self.diameter_input.background_color = (0.8, 0.3, 0.3, 1)
            elif "Высота" in error:
                self.height_input.background_color = (0.8, 0.3, 0.3, 1)
            elif "срез" in error:
                self.cut_param_input.background_color = (0.8, 0.3, 0.3, 1)
            elif "Сегменты" in error:
                self.segments_input.background_color = (0.8, 0.3, 0.3, 1)
    
    def _handle_calculation_error(self, message, progress):
        """Обработка ошибок расчета"""
        self.hide_progress()
        self.show_toast(f"❌ {message}", 3.0, "error")
        error_logger.log_event(f"Calculation failed: {message}", "ERROR")
    
    def _save_to_history(self):
        """Сохранение расчета в историю"""
        try:
            if not hasattr(self, 'current_calculation'):
                return
            
            calc = self.current_calculation
            
            # Используем глобальное хранилище
            global store
            if store is None:
                try:
                    store = JsonStore('cone_calculator_data.json')
                except Exception as e:
                    error_logger.log_error(e, "ProfessionalCalculatorScreen._save_to_history - store init")
                    return
            
            # Загрузка существующей истории
            if store.exists('history'):
                history_data = store.get('history')['calculations']
            else:
                history_data = []
            
            # Создание новой записи
            new_entry = {
                'diameter': calc['diameter'],
                'height': calc['height'],
                'cut_type': calc['cut_type'],
                'cut_param': calc['cut_param'],
                'segments': calc['segments'],
                'L_values': calc['L_values'],
                'generatrix': calc['generatrix'],
                'angle': calc['angle'],
                'date': datetime.now().strftime("%d.%m.%Y %H:%M:%S"),
                'timestamp': calc['timestamp']
            }
            
            # Добавление и ограничение размера
            history_data.append(new_entry)
            if len(history_data) > AppConfig.LIMITS['max_history_items']:
                history_data = history_data[-AppConfig.LIMITS['max_history_items']:]
            
            # Сохранение
            store.put('history', calculations=history_data)
            
            error_logger.log_event(f"Calculation saved to history: D{calc['diameter']} H{calc['height']}")
            
        except Exception as e:
            error_logger.log_error(e, "ProfessionalCalculatorScreen._save_to_history")
            self.show_toast("⚠️ Не удалось сохранить в историю", 2.0, "warning")
    
    def save_calculation(self, instance):
        """Сохранение расчета"""
        if self.current_calculation:
            self.show_toast("💾 Расчет сохранен в историю!", 2.0, "success")
        else:
            self.show_toast("❌ Нет данных для сохранения", 2.0, "error")
    
    def export_calculation(self, instance):
        """Экспорт расчета в файл"""
        if not self.current_calculation:
            self.show_toast("❌ Нет данных для экспорта", 2.0, "error")
            return
        
        try:
            calc = self.current_calculation
            
            # Форматирование содержимого
            content = f"""РЕЗУЛЬТАТ РАСЧЕТА КОНУСА
{AppConfig.APP_NAME} v{AppConfig.VERSION}
Дата расчета: {datetime.now().strftime("%d.%m.%Y %H:%M")}
{'='*50}

ОСНОВНЫЕ ПАРАМЕТРЫ:
• Диаметр основания: {calc['diameter']} мм
• Высота конуса: {calc['height']} мм
• Тип среза: {calc['cut_type']}
• Параметр среза: {calc['cut_param']}
• Количество сегментов: {calc['segments']}

РЕЗУЛЬТАТЫ РАСЧЕТА:
• Радиус основания: {calc['diameter']/2:.1f} мм
• Длина образующей: {calc['generatrix']:.1f} мм
• Угол развертки: {calc['angle']:.1f}°

ДЛИНЫ ДЛЯ РАЗМЕТКИ:
"""
            
            for i, length in enumerate(calc['L_values']):
                content += f"L{i:02d}: {length:.1f} мм\n"
            
            content += f"\n{'='*50}\nСгенерировано {AppConfig.APP_NAME} v{AppConfig.VERSION}"
            
            # Показ диалога сохранения
            self._show_export_dialog(content)
            
        except Exception as e:
            error_logger.log_error(e, "ProfessionalCalculatorScreen.export_calculation")
            self.show_toast("❌ Ошибка экспорта", 3.0, "error")
    
    def _show_export_dialog(self, content):
        """Диалог экспорта файла"""
        dialog_layout = BoxLayout(
            orientation='vertical',
            spacing=AdaptiveMetrics.adaptive_dp(10),
            padding=AdaptiveMetrics.adaptive_dp(15)
        )
        
        title = Label(
            text='[b]ЭКСПОРТ РАСЧЕТА[/b]',
            font_size=AdaptiveMetrics.adaptive_sp(18),
            markup=True,
            color=AppConfig.COLORS['light'],
            halign='center'
        )
        
        filename_input = TextInput(
            text=f'cone_calculation_{datetime.now().strftime("%Y%m%d_%H%M")}.txt',
            size_hint_y=None,
            height=AdaptiveMetrics.get_button_height(),
            font_size=AdaptiveMetrics.adaptive_sp(16),
            background_color=(0.1, 0.1, 0.15, 1),
            foreground_color=AppConfig.COLORS['light']
        )
        
        buttons_layout = BoxLayout(
            orientation='horizontal',
            spacing=AdaptiveMetrics.adaptive_dp(10),
            size_hint_y=None,
            height=AdaptiveMetrics.get_button_height()
        )
        
        cancel_btn = self.create_professional_button('ОТМЕНА', 'secondary', size_hint=(1, None))
        save_btn = self.create_professional_button('СОХРАНИТЬ', 'success', size_hint=(1, None))
        
        buttons_layout.add_widget(cancel_btn)
        buttons_layout.add_widget(save_btn)
        
        dialog_layout.add_widget(title)
        dialog_layout.add_widget(Label(
            text='Имя файла:',
            color=AppConfig.COLORS['light'],
            font_size=AdaptiveMetrics.adaptive_sp(14)
        ))
        dialog_layout.add_widget(filename_input)
        dialog_layout.add_widget(buttons_layout)
        
        popup = Popup(
            title='Экспорт результатов',
            content=dialog_layout,
            size_hint=(0.8, 0.5),
            background_color=(0.1, 0.1, 0.2, 0.95)
        )
        
        def perform_save(instance):
            try:
                filename = filename_input.text.strip()
                if not filename:
                    self.show_toast("❌ Введите имя файла!", 2.0, "error")
                    return
                
                # Добавляем расширение если нужно
                if not filename.lower().endswith('.txt'):
                    filename += '.txt'
                
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                popup.dismiss()
                self.show_toast(f"💾 Файл '{filename}' сохранен!", 3.0, "success")
                error_logger.log_event(f"Calculation exported to {filename}")
                
            except Exception as e:
                error_logger.log_error(e, "ProfessionalCalculatorScreen._show_export_dialog.perform_save")
                self.show_toast("❌ Ошибка сохранения файла!", 3.0, "error")
        
        cancel_btn.bind(on_press=popup.dismiss)
        save_btn.bind(on_press=perform_save)
        popup.open()
    
    def quick_clear(self, instance):
        """Быстрая очистка полей"""
        self.diameter_input.text = "300"
        self.height_input.text = "400"
        self.cut_param_input.text = "30" if self.cut_type == "slant" else "200"
        self.segments_input.text = "16"
        
        # Сброс визуализации
        self.result_label.text = self._get_welcome_message()
        self.save_btn.disabled = True
        self.export_btn.disabled = True
        self.current_calculation = None
        
        # Сброс подсветки полей
        for input_field in [self.diameter_input, self.height_input, self.cut_param_input, self.segments_input]:
            input_field.background_color = (0.1, 0.1, 0.15, 1)
        
        self.show_toast("🔄 Все поля очищены", 1.5, "info")
    
    def clear_all(self, instance):
        """Полная очистка"""
        self.quick_clear(instance)

# === УЛУЧШЕННЫЙ ЭКРАН ИСТОРИИ ===
class ProfessionalHistoryScreen(ProfessionalScreen):
    """Профессиональный экран истории расчетов"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = 'history'
    
    def setup_ui(self):
        """Создание интерфейса истории"""
        main_layout = FloatLayout()
        
        # Фон
        self.renderer = HybridPyGameRenderer()
        main_layout.add_widget(self.renderer)
        
        # Основной контент
        content = self._create_content_layout()
        main_layout.add_widget(content)
        
        self.add_widget(main_layout)
        
        # Загрузка истории
        Clock.schedule_once(lambda dt: self.load_history(), 0.5)
    
    def _create_content_layout(self):
        """Создание основного контента"""
        content = BoxLayout(
            orientation='vertical',
            padding=AdaptiveMetrics.get_padding(),
            spacing=AdaptiveMetrics.adaptive_dp(15),
            size_hint=(0.95, 0.9),
            pos_hint={'center_x': 0.5, 'center_y': 0.5}
        )
        
        # Заголовок
        content.add_widget(self._create_header())
        
        # Статистика
        self.stats_label = Label(
            text='Загрузка истории...',
            font_size=AdaptiveMetrics.adaptive_sp(14),
            color=AppConfig.COLORS['light'][:3] + (0.8,),
            size_hint_y=None,
            height=AdaptiveMetrics.adaptive_dp(30)
        )
        content.add_widget(self.stats_label)
        
        # Список истории
        scroll = ScrollView(do_scroll_x=False)
        self.history_list = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            spacing=AdaptiveMetrics.adaptive_dp(10),
            padding=AdaptiveMetrics.adaptive_dp(10)
        )
        self.history_list.bind(minimum_height=self.history_list.setter('height'))
        
        scroll.add_widget(self.history_list)
        content.add_widget(scroll)
        
        return content
    
    def _create_header(self):
        """Создание заголовка"""
        header = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=AdaptiveMetrics.get_button_height()
        )
        
        back_btn = self.create_professional_button(
            '← Назад (Esc)', 'secondary', self.on_back_press,
            size_hint=(None, None)
        )
        back_btn.width = AdaptiveMetrics.adaptive_dp(120)
        
        title = Label(
            text='[b]ИСТОРИЯ РАСЧЕТОВ[/b]',
            font_size=AdaptiveMetrics.adaptive_sp(22),
            markup=True,
            color=AppConfig.COLORS['light']
        )
        
        clear_btn = self.create_professional_button(
            '🗑️ Очистить', 'danger', self.clear_history,
            size_hint=(None, None)
        )
        clear_btn.width = AdaptiveMetrics.adaptive_dp(120)
        
        header.add_widget(back_btn)
        header.add_widget(title)
        header.add_widget(clear_btn)
        
        return header
    
    def load_history(self):
        """Загрузка истории расчетов"""
        self.history_list.clear_widgets()
        
        try:
            global store
            if store is None:
                self._show_empty_state("Хранилище не доступно")
                return
            
            if not store.exists('history'):
                self._show_empty_state("История расчетов пуста")
                self.stats_label.text = "Расчетов: 0"
                return
            
            history_data = store.get('history')['calculations']
            
            if not history_data:
                self._show_empty_state("История расчетов пуста")
                self.stats_label.text = "Расчетов: 0"
                return
            
            # Статистика
            total = len(history_data)
            today = datetime.now().date()
            recent = len([c for c in history_data 
                         if datetime.fromisoformat(c.get('timestamp', '2000-01-01')).date() == today])
            
            self.stats_label.text = f"Всего: {total} | Сегодня: {recent} | Показано: {min(20, total)}"
            
            # Показ последних 20 записей
            for calc in reversed(history_data[-20:]):
                self._add_history_item(calc)
                
        except Exception as e:
            error_logger.log_error(e, "ProfessionalHistoryScreen.load_history")
            self._show_empty_state("Ошибка загрузки истории")
    
    def _show_empty_state(self, message):
        """Показ состояния пустой истории"""
        empty_label = Label(
            text=f'{message}\n\nСначала выполните расчет в калькуляторе',
            color=AppConfig.COLORS['light'][:3] + (0.6,),
            font_size=AdaptiveMetrics.adaptive_sp(16),
            halign='center'
        )
        self.history_list.add_widget(empty_label)
    
    def _add_history_item(self, calculation):
        """Добавление элемента истории"""
        item_layout = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=AdaptiveMetrics.adaptive_dp(80),
            spacing=AdaptiveMetrics.adaptive_dp(10),
            padding=AdaptiveMetrics.adaptive_dp(10)
        )
        
        # Фон элемента
        with item_layout.canvas.before:
            Color(*AppConfig.COLORS['dark'][:3] + (0.8,))
            bg_rect = RoundedRectangle(
                pos=item_layout.pos, size=item_layout.size,
                radius=[AdaptiveMetrics.adaptive_dp(10)]
            )
        
        item_layout.bg_rect = bg_rect
        item_layout.bind(pos=self._update_item_bg, size=self._update_item_bg)
        
        # Информация
        info_layout = BoxLayout(orientation='vertical', size_hint_x=0.7)
        
        title = Label(
            text=f"📐 Конус D{calculation['diameter']}×H{calculation['height']}",
            font_size=AdaptiveMetrics.adaptive_sp(16),
            color=AppConfig.COLORS['light'],
            halign='left',
            text_size=(None, None)
        )
        
        details = Label(
            text=f"🔺 {calculation['cut_type']} • {calculation['segments']} сегментов",
            font_size=AdaptiveMetrics.adaptive_sp(12),
            color=AppConfig.COLORS['light'][:3] + (0.8,),
            halign='left',
            text_size=(None, None)
        )
        
        date = Label(
            text=calculation['date'],
            font_size=AdaptiveMetrics.adaptive_sp(11),
            color=AppConfig.COLORS['light'][:3] + (0.6,),
            halign='left',
            text_size=(None, None)
        )
        
        info_layout.add_widget(title)
        info_layout.add_widget(details)
        info_layout.add_widget(date)
        
        # Кнопка просмотра
        view_btn = self.create_professional_button(
            '👁️ Просмотр', 'primary', 
            lambda instance: self.view_calculation(calculation),
            size_hint=(None, None)
        )
        view_btn.width = AdaptiveMetrics.adaptive_dp(100)
        
        item_layout.add_widget(info_layout)
        item_layout.add_widget(view_btn)
        
        self.history_list.add_widget(item_layout)
    
    def _update_item_bg(self, instance, value):
        """Обновление фона элемента"""
        if hasattr(instance, 'bg_rect'):
            instance.bg_rect.pos = instance.pos
            instance.bg_rect.size = instance.size
    
    def view_calculation(self, calculation):
        """Просмотр деталей расчета"""
        content = BoxLayout(
            orientation='vertical',
            spacing=AdaptiveMetrics.adaptive_dp(10),
            padding=AdaptiveMetrics.adaptive_dp(15)
        )
        
        title = Label(
            text=f'[b]РАСЧЕТ ОТ {calculation["date"]}[/b]',
            font_size=AdaptiveMetrics.adaptive_sp(18),
            markup=True,
            color=AppConfig.COLORS['light'],
            halign='center'
        )
        
        details_text = f"""Диаметр: {calculation['diameter']} мм
Высота: {calculation['height']} мм
Тип среза: {calculation['cut_type']}
Параметр среза: {calculation['cut_param']}
Сегментов: {calculation['segments']}
Образующая: {calculation.get('generatrix', 'N/A'):.1f} мм
Угол развертки: {calculation.get('angle', 'N/A'):.1f}°"""
        
        details = Label(
            text=details_text,
            font_size=AdaptiveMetrics.adaptive_sp(14),
            color=AppConfig.COLORS['light'][:3] + (0.9,),
            halign='left'
        )
        
        close_btn = self.create_professional_button(
            'ЗАКРЫТЬ', 'primary',
            size_hint_y=None,
            height=AdaptiveMetrics.get_button_height()
        )
        
        content.add_widget(title)
        content.add_widget(details)
        content.add_widget(close_btn)
        
        popup = Popup(
            title='Детали расчета',
            content=content,
            size_hint=(0.8, 0.6),
            background_color=(0.1, 0.1, 0.2, 0.95)
        )
        
        close_btn.bind(on_press=popup.dismiss)
        popup.open()
    
    def clear_history(self, instance):
        """Очистка истории с подтверждением"""
        content = BoxLayout(
            orientation='vertical',
            spacing=AdaptiveMetrics.adaptive_dp(15),
            padding=AdaptiveMetrics.adaptive_dp(20)
        )
        
        message = Label(
            text='Вы уверены, что хотите очистить всю историю расчетов?',
            font_size=AdaptiveMetrics.adaptive_sp(16),
            color=AppConfig.COLORS['light'],
            halign='center'
        )
        
        buttons_layout = BoxLayout(
            orientation='horizontal',
            spacing=AdaptiveMetrics.adaptive_dp(15),
            size_hint_y=None,
            height=AdaptiveMetrics.get_button_height()
        )
        
        cancel_btn = self.create_professional_button('ОТМЕНА', 'secondary')
        clear_btn = self.create_professional_button('ОЧИСТИТЬ', 'danger')
        
        buttons_layout.add_widget(cancel_btn)
        buttons_layout.add_widget(clear_btn)
        
        content.add_widget(message)
        content.add_widget(buttons_layout)
        
        popup = Popup(
            title='Очистка истории',
            content=content,
            size_hint=(0.7, 0.4),
            background_color=(0.1, 0.1, 0.2, 0.95)
        )
        
        def perform_clear(btn):
            try:
                global store
                if store:
                    store.put('history', calculations=[])
                popup.dismiss()
                self.load_history()
                self.show_toast("🗑️ История очищена!", 2.0, "success")
                error_logger.log_event("History cleared by user")
            except Exception as e:
                error_logger.log_error(e, "ProfessionalHistoryScreen.clear_history.perform_clear")
                self.show_toast("❌ Ошибка очистки!", 2.0, "error")
        
        cancel_btn.bind(on_press=popup.dismiss)
        clear_btn.bind(on_press=perform_clear)
        popup.open()

# === ГЛАВНОЕ ПРИЛОЖЕНИЕ ===
class ConeCalculator(App):
    """Главное приложение с профессиональной архитектурой"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.title = f"{AppConfig.APP_NAME} v{AppConfig.VERSION}"
    
    def build(self):
        """Сборка приложения"""
        error_logger.log_event("=== APPLICATION START ===")
        error_logger.log_event(f"Starting {self.title}")
        
        # Настройка окна для разных платформ
        self._setup_window()
        
        # Инициализация хранилища
        global store
        try:
            store = JsonStore('cone_calculator_data.json')
            error_logger.log_event("JSON store initialized successfully")
        except Exception as e:
            error_logger.log_error(e, "ConeCalculator.build - store init")
            store = None
        
        # Создание менеджера экранов
        self.sm = ScreenManager(transition=FadeTransition(duration=0.3))
        
        # Добавление экранов
        self.sm.add_widget(ProfessionalCalculatorScreen(name='calculator'))
        self.sm.add_widget(ProfessionalHistoryScreen(name='history'))
        # TODO: Добавить ProfessionalSettingsScreen
        
        error_logger.log_event("All screens initialized successfully")
        
        return self.sm
    
    def _setup_window(self):
        """Настройка окна приложения"""
        try:
            profile = AdaptiveMetrics.get_screen_profile()
            
            if profile['name'] in ['large', 'xlarge']:
                # Десктопный режим
                Window.size = (1000, 700)
                Window.minimum_width = 800
                Window.minimum_height = 600
            else:
                # Мобильный режим
                Window.fullscreen = 'auto'
            
            # Настройка иконки (если есть)
            try:
                self.icon = 'icon.png'  # Будет искать в директории приложения
            except:
                pass
                
        except Exception as e:
            error_logger.log_error(e, "ConeCalculator._setup_window")
    
    def on_start(self):
        """Вызывается при запуске приложения"""
        error_logger.log_event("Application started successfully")
        self._check_system_health()
    
    def on_stop(self):
        """Вызывается при закрытии приложения"""
        error_logger.log_event("=== APPLICATION STOPPED ===")
        error_logger.log_event("")  # Пустая строка для разделения сессий
    
    def _check_system_health(self):
        """Проверка здоровья системы"""
        try:
            issues = []
            
            # Проверка хранилища
            if store is None:
                issues.append("Хранилище данных не доступно")
            
            # Проверка PyGame
            if not PYGAME_AVAILABLE:
                issues.append("PyGame не доступен - графика будет ограничена")
            
            # Проверка свободного места
            try:
                import shutil
                total, used, free = shutil.disk_usage(".")
                if free < 100 * 1024 * 1024:  # 100 MB
                    issues.append("Мало свободного места на диске")
            except:
                pass
            
            if issues:
                error_logger.log_event(f"System health issues: {', '.join(issues)}", "WARNING")
            else:
                error_logger.log_event("System health: OK")
                
        except Exception as e:
            error_logger.log_error(e, "ConeCalculator._check_system_health")

# === ТОЧКА ВХОДА ===
if __name__ == '__main__':
    try:
        # Инициализация и запуск
        error_logger.set_recovery_callback(lambda: None)  # Базовый recovery callback
        
        app = ConeCalculator()
        app.run()
        
    except Exception as e:
        # Критическая ошибка - логируем и показываем сообщение
        error_logger.log_error(e, "Main application", recoverable=False)
        
        # Простое сообщение об ошибке
        print(f"CRITICAL ERROR: {e}")
        traceback.print_exc()
        
        # Попытка показать GUI ошибки
        try:
            from kivy.app import App
            from kivy.uix.label import Label
            
            class ErrorApp(App):
                def build(self):
                    return Label(
                        text=f'Critical Error:\n{str(e)}\n\nSee logs for details.',
                        font_size=20,
                        text_size=(400, None)
                    )
            
            ErrorApp().run()
        except:
            pass  # Если даже GUI ошибки не работает