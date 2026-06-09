import math
from datetime import datetime

from kivy.lang import Builder
from kivy.clock import Clock
from kivy.metrics import dp
from kivy.properties import (StringProperty, ListProperty,
                             BooleanProperty, NumericProperty)
from kivy.core.window import Window
from kivy.graphics import Color, Line, Ellipse
from kivy.uix.widget import Widget

from kivymd.app import MDApp
from kivymd.uix.card import MDCard
from kivymd.uix.label import MDLabel
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.pickers import MDDatePicker

Window.size = (400, 760)


# ================================================================
#  ДАННЫЕ
# ================================================================
MOCK = {
    "user": {"name": "Александр Севастьянов", "email": "aleksandr@example.com"},
    "accounts": [
        {"bank": "Сбербанк",   "last4": "4562", "balance": 156890, "color": "#21A038", "icon": "bank"},
        {"bank": "Тинькофф",   "last4": "8921", "balance":  42350, "color": "#E5B411", "icon": "credit-card"},
        {"bank": "Альфа-Банк", "last4": "3145", "balance":  28400, "color": "#EF3124", "icon": "circle"},
    ],
    "transactions": [
        {"title": "Продукты Пятёрочка", "category": "Продукты",    "bank": "Сбербанк",   "date": "2025-04-15", "time": "18:23", "amount": -2450,  "icon": "cart"},
        {"title": "Зарплата",           "category": "Доход",       "bank": "Тинькофф",   "date": "2025-04-15", "time": "09:00", "amount": 85000,  "icon": "cash-plus"},
        {"title": "Кафе Starbucks",     "category": "Рестораны",   "bank": "Альфа-Банк", "date": "2025-04-14", "time": "14:15", "amount": -450,   "icon": "coffee"},
        {"title": "Uber поездка",       "category": "Транспорт",   "bank": "Сбербанк",   "date": "2025-04-14", "time": "21:45", "amount": -320,   "icon": "taxi"},
        {"title": "Кинотеатр",          "category": "Развлечения", "bank": "Сбербанк",   "date": "2025-04-13", "time": "19:30", "amount": -700,   "icon": "movie"},
        {"title": "Магнит",             "category": "Продукты",    "bank": "Сбербанк",   "date": "2025-04-12", "time": "11:10", "amount": -2150,  "icon": "cart"},
        {"title": "Перевод другу",      "category": "Доход",       "bank": "Тинькофф",   "date": "2025-04-11", "time": "16:00", "amount": 25000,  "icon": "cash-plus"},
        {"title": "Метро",              "category": "Транспорт",   "bank": "Тинькофф",   "date": "2025-04-10", "time": "08:30", "amount": -62,    "icon": "subway"},
    ],
    "breakdown": [
        {"category": "Продукты",    "amount": 18500, "percent": 42.3, "color": "#E5616E", "emoji": "🛒"},
        {"category": "Транспорт",   "amount": 8200,  "percent": 18.8, "color": "#4C8DF0", "emoji": "🚗"},
        {"category": "Рестораны",   "amount": 6300,  "percent": 14.4, "color": "#F5C242", "emoji": "🍽️"},
        {"category": "Развлечения", "amount": 5100,  "percent": 11.7, "color": "#4FC4B8", "emoji": "🎬"},
        {"category": "Здоровье",    "amount": 3400,  "percent": 7.8,  "color": "#9B6CE0", "emoji": "💊"},
        {"category": "Прочее",      "amount": 2200,  "percent": 5.0,  "color": "#F0A030", "emoji": "📦"},
    ],
    "trends": [
        {"month": "Янв", "income": 84000, "expense": 38500},
        {"month": "Фев", "income": 85000, "expense": 41000},
        {"month": "Мар", "income": 90000, "expense": 39500},
        {"month": "Апр", "income": 86000, "expense": 41020},
    ],
    "week": [
        {"day": "Пн", "amount": 1200},
        {"day": "Вт", "amount": 900},
        {"day": "Ср", "amount": 2400},
        {"day": "Чт", "amount": 650},
        {"day": "Пт", "amount": 3200},
        {"day": "Сб", "amount": 4800},
        {"day": "Вс", "amount": 2160},
    ],
    "ai_tips": [
        {"icon": "lightbulb-on", "title": "Экономьте на продуктах",
         "text": "Вы тратите 42% бюджета на продукты. Закупайтесь раз в неделю."},
        {"icon": "trending-up",  "title": "Доход вырос",
         "text": "В этом месяце доходы выше на 12% по сравнению с прошлым."},
        {"icon": "piggy-bank",   "title": "Накопления",
         "text": "Откладывая 5000 ₽ в месяц, за год накопите 60 000 ₽."},
    ],
}

MONTHS_RU = ["янв", "фев", "мар", "апр", "май", "июн",
             "июл", "авг", "сен", "окт", "ноя", "дек"]
WEEKDAYS_RU = ["Понедельник", "Вторник", "Среда", "Четверг",
               "Пятница", "Суббота", "Воскресенье"]
HIDDEN = "₽ • • • • •"


def money(value, plus=False):
    sign = "+" if (value > 0 and plus) else ("-" if value < 0 else "")
    return f"{sign}₽{abs(int(value)):,}".replace(",", " ")


def hex_color(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)) + (1,)


def fmt_date(iso):
    d = datetime.strptime(iso, "%Y-%m-%d")
    return f"{d.day} {MONTHS_RU[d.month - 1]}"


# ================================================================
#  ВИДЖЕТЫ ГРАФИКОВ
# ================================================================
class DonutChart(Widget):
    data = ListProperty([])

    def __init__(self, **kw):
        super().__init__(**kw)
        self.bind(pos=self._draw, size=self._draw, data=self._draw)

    def _draw(self, *a):
        self.canvas.clear()
        if not self.data:
            return
        cx, cy = self.center_x, self.center_y
        radius = min(self.width, self.height) / 2 * 0.9
        thickness = radius * 0.42
        with self.canvas:
            start = 90
            for seg in self.data:
                sweep = seg["percent"] / 100.0 * 360.0
                Color(*hex_color(seg["color"]))
                Line(circle=(cx, cy, radius - thickness / 2, start, start + sweep),
                     width=thickness, cap="none")
                start += sweep
            Color(0.97, 0.98, 0.99, 1)
            inner = radius - thickness
            Ellipse(pos=(cx - inner, cy - inner), size=(inner * 2, inner * 2))


class BarChart(Widget):
    data = ListProperty([])
    max_value = NumericProperty(100)
    grid_steps = NumericProperty(4)

    def __init__(self, **kw):
        super().__init__(**kw)
        self.bind(pos=self._draw, size=self._draw,
                  data=self._draw, max_value=self._draw)

    def _draw(self, *a):
        self.canvas.clear()
        self.clear_widgets()
        if not self.data:
            return
        pad_l, pad_b, pad_t, pad_r = dp(48), dp(28), dp(10), dp(10)
        px, py = self.x + pad_l, self.y + pad_b
        pw, ph = self.width - pad_l - pad_r, self.height - pad_b - pad_t
        n = len(self.data)
        slot = pw / n
        bar_w = slot * 0.5

        from kivy.graphics import RoundedRectangle
        with self.canvas:
            for i in range(self.grid_steps + 1):
                gy = py + ph * i / self.grid_steps
                Color(0.88, 0.89, 0.92, 1)
                Line(points=[px, gy, px + pw, gy], width=1,
                     dash_length=4, dash_offset=4)
            for idx, item in enumerate(self.data):
                ratio = (item["value"] / self.max_value) if self.max_value else 0
                bh = ph * ratio
                bx = px + slot * idx + (slot - bar_w) / 2
                Color(*hex_color(item["color"]))
                RoundedRectangle(pos=(bx, py), size=(bar_w, bh),
                                 radius=[(dp(4), dp(4)), (dp(4), dp(4)), (0, 0), (0, 0)])

        for i in range(self.grid_steps + 1):
            val = self.max_value * i / self.grid_steps
            gy = py + ph * i / self.grid_steps
            lbl = MDLabel(text=f"{int(val)}", font_size="10sp", halign="right",
                          theme_text_color="Custom", text_color=(0.5, 0.52, 0.56, 1),
                          size_hint=(None, None), size=(pad_l - dp(6), dp(16)))
            lbl.pos = (self.x, gy - dp(8))
            self.add_widget(lbl)
        for idx, item in enumerate(self.data):
            cx = px + slot * idx + slot / 2
            lbl = MDLabel(text=item["label"], font_size="11sp", halign="center",
                          theme_text_color="Custom", text_color=(0.4, 0.42, 0.46, 1),
                          size_hint=(None, None), size=(slot, dp(20)))
            lbl.pos = (cx - slot / 2, self.y)
            self.add_widget(lbl)


# ================================================================
#  Карточка транзакции
# ================================================================
class TransactionCard(MDCard):
    title = StringProperty("")
    subtitle = StringProperty("")
    amount_text = StringProperty("")
    icon = StringProperty("cart")
    icon_bg = ListProperty([0.9, 0.9, 0.9, 1])
    icon_color = ListProperty([0.3, 0.3, 0.3, 1])
    amount_color = ListProperty([0.12, 0.13, 0.18, 1])


# ================================================================
#  KV
# ================================================================
KV = '''
<HeaderBox@MDBoxLayout>:
    orientation: "vertical"
    size_hint_y: None
    height: self.minimum_height
    padding: dp(20), dp(38), dp(20), dp(20)
    spacing: dp(4)
    md_bg_color: 0.29, 0.44, 0.93, 1
    radius: [0, 0, 28, 28]

<NavButton@MDBoxLayout>:
    orientation: "vertical"
    icon: ""
    text: ""
    screen: ""
    MDIconButton:
        icon: root.icon
        pos_hint: {"center_x": 0.5}
        theme_icon_color: "Custom"
        icon_color: (0.29,0.44,0.93,1) if app.current == root.screen else (0.6,0.62,0.66,1)
        on_release: app.switch_screen(root.screen)
    MDLabel:
        text: root.text
        halign: "center"
        font_size: "10sp"
        theme_text_color: "Custom"
        text_color: (0.29,0.44,0.93,1) if app.current == root.screen else (0.6,0.62,0.66,1)

<BottomBar@MDCard>:
    size_hint_y: None
    height: dp(70)
    md_bg_color: 1,1,1,1
    elevation: 3
    radius: [0]
    MDBoxLayout:
        NavButton:
            text: "Главная"
            icon: "home"
            screen: "home"
        NavButton:
            text: "Операции"
            icon: "receipt"
            screen: "operations"
        NavButton:
            text: "Статистика"
            icon: "chart-bar"
            screen: "statistics"
        NavButton:
            text: "ИИ"
            icon: "star-four-points"
            screen: "ai"
        NavButton:
            text: "Профиль"
            icon: "account"
            screen: "profile"

<TransactionCard>:
    orientation: "horizontal"
    size_hint_y: None
    height: dp(84)
    padding: dp(14)
    spacing: dp(12)
    radius: [22]
    md_bg_color: 1, 1, 1, 1
    elevation: 1.5
    MDCard:
        size_hint: None, None
        size: dp(50), dp(50)
        radius: [25]
        md_bg_color: root.icon_bg
        pos_hint: {"center_y": 0.5}
        elevation: 0
        MDIconButton:
            icon: root.icon
            theme_icon_color: "Custom"
            icon_color: root.icon_color
            pos_hint: {"center_x": .5, "center_y": .5}
    MDBoxLayout:
        orientation: "vertical"
        pos_hint: {"center_y": 0.5}
        MDLabel:
            text: root.title
            bold: True
            font_size: "15sp"
            theme_text_color: "Custom"
            text_color: 0.12, 0.13, 0.18, 1
            shorten: True
            shorten_from: "right"
        MDLabel:
            text: root.subtitle
            font_size: "11sp"
            theme_text_color: "Custom"
            text_color: 0.55, 0.57, 0.62, 1
    MDLabel:
        text: root.amount_text
        halign: "right"
        bold: True
        font_size: "16sp"
        size_hint_x: None
        width: dp(95)
        pos_hint: {"center_y": 0.5}
        theme_text_color: "Custom"
        text_color: root.amount_color

<StatTab@MDCard>:
    text: ""
    key: ""
    size_hint_y: None
    height: dp(40)
    radius: [14]
    elevation: 0
    md_bg_color: (1,1,1,1) if app.stat_tab == self.key else (0,0,0,0)
    on_release: app.set_stat_tab(root.key)
    MDLabel:
        text: root.text
        halign: "center"
        bold: app.stat_tab == root.key
        font_size: "14sp"
        theme_text_color: "Custom"
        text_color: (0.29,0.44,0.93,1) if app.stat_tab == root.key else (0.5,0.52,0.58,1)

MDScreenManager:
    id: sm

    MDScreen:
        name: "home"
        md_bg_color: 0.96, 0.97, 0.99, 1
        MDBoxLayout:
            orientation: "vertical"
            HeaderBox:
                # ----- Верхняя строка: баланс + плюс -----
                MDBoxLayout:
                    adaptive_height: True
                    MDBoxLayout:
                        orientation: "vertical"
                        adaptive_height: True
                        MDLabel:
                            text: "Общий баланс"
                            font_size: "14sp"
                            adaptive_height: True
                            theme_text_color: "Custom"
                            text_color: 1,1,1,0.85
                        MDBoxLayout:
                            adaptive_height: True
                            spacing: dp(8)
                            MDLabel:
                                id: home_balance
                                text: "0 ₽"
                                font_size: "34sp"
                                bold: True
                                halign: "left"
                                shorten: True
                                text_size: self.width, None
                                size_hint_y: None
                                height: self.texture_size[1]
                                theme_text_color: "Custom"
                                text_color: 1, 1, 1, 1
                            MDIconButton:
                                id: eye_btn
                                icon: "eye-off"
                                pos_hint: {"center_y": 0.5}
                                theme_icon_color: "Custom"
                                icon_color: 1,1,1,0.9
                                on_release: app.toggle_amounts()
                    Widget:
                    MDCard:
                        size_hint: None, None
                        size: dp(46), dp(46)
                        radius: [23]
                        md_bg_color: 1,1,1,0.22
                        elevation: 0
                        pos_hint: {"center_y": 0.5}
                        MDIconButton:
                            icon: "plus"
                            theme_icon_color: "Custom"
                            icon_color: 1,1,1,1
                            pos_hint: {"center_x": .5, "center_y": .5}
                # ----- Доход / Расходы -----
                MDBoxLayout:
                    adaptive_height: True
                    spacing: dp(12)
                    padding: 0, dp(14), 0, 0
                    MDCard:
                        orientation: "vertical"
                        size_hint_y: None
                        height: dp(82)
                        padding: dp(12)
                        spacing: dp(2)
                        radius: [18]
                        md_bg_color: 1,1,1,0.18
                        elevation: 0
                        MDBoxLayout:
                            adaptive_height: True
                            spacing: dp(6)
                            MDIconButton:
                                icon: "arrow-bottom-left"
                                theme_icon_color: "Custom"
                                icon_color: 1,1,1,0.9
                                size_hint: None, None
                                size: dp(20), dp(20)
                                pos_hint: {"center_y": 0.5}
                            MDLabel:
                                text: "Доход"
                                font_size: "12sp"
                                theme_text_color: "Custom"
                                text_color: 1,1,1,0.85
                                pos_hint: {"center_y": 0.5}
                        MDLabel:
                            id: home_income
                            text: "—"
                            font_size: "18sp"
                            bold: True
                            adaptive_height: True
                            theme_text_color: "Custom"
                            text_color: 1,1,1,1
                    MDCard:
                        orientation: "vertical"
                        size_hint_y: None
                        height: dp(82)
                        padding: dp(12)
                        spacing: dp(2)
                        radius: [18]
                        md_bg_color: 1,1,1,0.18
                        elevation: 0
                        MDBoxLayout:
                            adaptive_height: True
                            spacing: dp(6)
                            MDIconButton:
                                icon: "arrow-top-right"
                                theme_icon_color: "Custom"
                                icon_color: 1,1,1,0.9
                                size_hint: None, None
                                size: dp(20), dp(20)
                                pos_hint: {"center_y": 0.5}
                            MDLabel:
                                text: "Расходы"
                                font_size: "12sp"
                                theme_text_color: "Custom"
                                text_color: 1,1,1,0.85
                                pos_hint: {"center_y": 0.5}
                        MDLabel:
                            id: home_expenses
                            text: "—"
                            font_size: "18sp"
                            bold: True
                            adaptive_height: True
                            theme_text_color: "Custom"
                            text_color: 1,1,1,1
            ScrollView:
                MDBoxLayout:
                    orientation: "vertical"
                    adaptive_height: True
                    padding: dp(16)
                    spacing: dp(14)
                    # ----- Мои счета -----
                    MDBoxLayout:
                        adaptive_height: True
                        MDLabel:
                            text: "Мои счета"
                            font_size: "18sp"
                            bold: True
                            adaptive_height: True
                            theme_text_color: "Custom"
                            text_color: 0.12,0.13,0.18,1
                        MDLabel:
                            text: "Все"
                            font_size: "14sp"
                            bold: True
                            halign: "right"
                            adaptive_height: True
                            theme_text_color: "Custom"
                            text_color: 0.29,0.44,0.93,1
                    MDBoxLayout:
                        id: home_accounts
                        orientation: "vertical"
                        adaptive_height: True
                        spacing: dp(14)
                    # ----- Последние операции -----
                    MDBoxLayout:
                        adaptive_height: True
                        padding: 0, dp(6), 0, 0
                        MDLabel:
                            text: "Последние операции"
                            font_size: "18sp"
                            bold: True
                            adaptive_height: True
                            theme_text_color: "Custom"
                            text_color: 0.12,0.13,0.18,1
                        MDLabel:
                            text: "Все"
                            font_size: "14sp"
                            bold: True
                            halign: "right"
                            adaptive_height: True
                            theme_text_color: "Custom"
                            text_color: 0.29,0.44,0.93,1
                    MDBoxLayout:
                        id: home_transactions
                        orientation: "vertical"
                        adaptive_height: True
                        spacing: dp(12)
                                       # ----- ИИ Совет -----
                    MDCard:
                        orientation: "horizontal"
                        size_hint_y: None
                        height: dp(150)
                        padding: dp(16)
                        spacing: dp(14)
                        radius: [20]
                        md_bg_color: app.hex("#F1EEFB")
                        elevation: 0
                        MDCard:
                            size_hint: None, None
                            size: dp(48), dp(48)
                            radius: [16]
                            md_bg_color: app.hex("#8B3FE8")
                            elevation: 0
                            pos_hint: {"top": 1}
                            MDIconButton:
                                icon: "trending-up"
                                theme_icon_color: "Custom"
                                icon_color: 1,1,1,1
                                pos_hint: {"center_x": .5, "center_y": .5}
                        MDBoxLayout:
                            orientation: "vertical"
                            spacing: dp(8)
                            pos_hint: {"center_y": 0.5}
                            MDBoxLayout:
                                adaptive_height: True
                                spacing: dp(8)
                                MDLabel:
                                    text: "ИИ Совет"
                                    bold: True
                                    font_size: "16sp"
                                    adaptive_height: True
                                    size_hint_x: None
                                    width: self.texture_size[0]
                                    theme_text_color: "Custom"
                                    text_color: 0.12,0.13,0.18,1
                                MDCard:
                                    size_hint: None, None
                                    size: dp(54), dp(22)
                                    radius: [11]
                                    md_bg_color: app.hex("#8B3FE8")
                                    elevation: 0
                                    pos_hint: {"center_y": 0.5}
                                    MDLabel:
                                        text: "Новое"
                                        halign: "center"
                                        font_size: "11sp"
                                        theme_text_color: "Custom"
                                        text_color: 1,1,1,1
                                Widget:
                            MDLabel:
                                text: "Вы можете сэкономить до \u20BD9 197/мес, следуя нашим рекомендациям"
                                font_size: "13sp"
                                adaptive_height: True
                                theme_text_color: "Custom"
                                text_color: 0.45,0.47,0.52,1
                            MDCard:
                                size_hint: None, None
                                size: dp(120), dp(36)
                                radius: [12]
                                md_bg_color: 1,1,1,1
                                line_color: app.hex("#8B3FE8")
                                elevation: 0
                                MDLabel:
                                    text: "Подробнее"
                                    halign: "center"
                                    bold: True
                                    font_size: "13sp"
                                    theme_text_color: "Custom"
                                    text_color: app.hex("#8B3FE8")
            BottomBar:

    MDScreen:
        name: "operations"
        md_bg_color: 0.96, 0.97, 0.99, 1
        MDBoxLayout:
            orientation: "vertical"
            HeaderBox:
                MDBoxLayout:
                    adaptive_height: True
                    MDLabel:
                        text: "Операции"
                        font_size: "26sp"
                        bold: True
                        adaptive_height: True
                        theme_text_color: "Custom"
                        text_color: 1,1,1,1
                    Widget:
                    MDCard:
                        size_hint: None, None
                        size: dp(46), dp(46)
                        radius: [23]
                        md_bg_color: 1,1,1,0.22
                        elevation: 0
                        pos_hint: {"center_y": 0.5}
                        MDIconButton:
                            icon: "calendar-month"
                            theme_icon_color: "Custom"
                            icon_color: 1,1,1,1
                            pos_hint: {"center_x": .5, "center_y": .5}
                            on_release: app.open_calendar()
                MDBoxLayout:
                    id: filter_row
                    adaptive_height: True
                    spacing: dp(8)
                    padding: 0, dp(10), 0, 0
                MDBoxLayout:
                    adaptive_height: True
                    spacing: dp(12)
                    padding: 0, dp(12), 0, 0
                    MDCard:
                        orientation: "vertical"
                        size_hint_y: None
                        height: dp(72)
                        padding: dp(12)
                        radius: [18]
                        md_bg_color: 1,1,1,0.18
                        elevation: 0
                        MDLabel:
                            text: "Доходы"
                            font_size: "12sp"
                            adaptive_height: True
                            theme_text_color: "Custom"
                            text_color: 1,1,1,0.85
                        MDLabel:
                            id: op_income
                            text: "—"
                            font_size: "20sp"
                            bold: True
                            adaptive_height: True
                            theme_text_color: "Custom"
                            text_color: 1,1,1,1
                    MDCard:
                        orientation: "vertical"
                        size_hint_y: None
                        height: dp(72)
                        padding: dp(12)
                        radius: [18]
                        md_bg_color: 1,1,1,0.18
                        elevation: 0
                        MDLabel:
                            text: "Расходы"
                            font_size: "12sp"
                            adaptive_height: True
                            theme_text_color: "Custom"
                            text_color: 1,1,1,0.85
                        MDLabel:
                            id: op_expenses
                            text: "—"
                            font_size: "20sp"
                            bold: True
                            adaptive_height: True
                            theme_text_color: "Custom"
                            text_color: 1,1,1,1
            MDBoxLayout:
                adaptive_height: True
                padding: dp(16), dp(12), dp(16), dp(4)
                MDTextField:
                    id: search_field
                    hint_text: "Поиск операций..."
                    mode: "round"
                    on_text: app.apply_filter()
            ScrollView:
                size_hint_y: None
                height: dp(48)
                do_scroll_y: False
                MDBoxLayout:
                    id: categories_box
                    adaptive_width: True
                    spacing: dp(8)
                    padding: dp(16), 0
            ScrollView:
                MDBoxLayout:
                    id: tx_list
                    orientation: "vertical"
                    adaptive_height: True
                    padding: dp(16), dp(6), dp(16), dp(16)
                    spacing: dp(12)
            BottomBar:

    MDScreen:
        name: "statistics"
        md_bg_color: 0.96, 0.97, 0.99, 1
        MDBoxLayout:
            orientation: "vertical"
            HeaderBox:
                MDLabel:
                    text: "Статистика"
                    font_size: "26sp"
                    bold: True
                    adaptive_height: True
                    theme_text_color: "Custom"
                    text_color: 1,1,1,1
                MDLabel:
                    text: "Анализ ваших финансов"
                    font_size: "14sp"
                    adaptive_height: True
                    theme_text_color: "Custom"
                    text_color: 1,1,1,0.85
            MDCard:
                size_hint_y: None
                height: dp(52)
                radius: [16]
                md_bg_color: 0.91, 0.92, 0.95, 1
                elevation: 0
                padding: dp(6)
                MDBoxLayout:
                    spacing: dp(4)
                    StatTab:
                        text: "Категории"
                        key: "categories"
                    StatTab:
                        text: "Тренды"
                        key: "trends"
                    StatTab:
                        text: "Неделя"
                        key: "week"
            ScrollView:
                MDBoxLayout:
                    id: stats_box
                    orientation: "vertical"
                    adaptive_height: True
                    padding: dp(16)
                    spacing: dp(14)
            BottomBar:

    MDScreen:
        name: "ai"
        md_bg_color: 0.96, 0.97, 0.99, 1
        MDBoxLayout:
            orientation: "vertical"
            HeaderBox:
                MDLabel:
                    text: "ИИ-помощник"
                    font_size: "26sp"
                    bold: True
                    adaptive_height: True
                    theme_text_color: "Custom"
                    text_color: 1,1,1,1
                MDLabel:
                    text: "Умные советы по финансам"
                    font_size: "14sp"
                    adaptive_height: True
                    theme_text_color: "Custom"
                    text_color: 1,1,1,0.85
            ScrollView:
                MDBoxLayout:
                    id: ai_box
                    orientation: "vertical"
                    adaptive_height: True
                    padding: dp(16)
                    spacing: dp(14)
            BottomBar:

    MDScreen:
        name: "profile"
        md_bg_color: 0.96, 0.97, 0.99, 1
        MDBoxLayout:
            orientation: "vertical"
            HeaderBox:
                MDLabel:
                    text: "Профиль"
                    font_size: "26sp"
                    bold: True
                    adaptive_height: True
                    theme_text_color: "Custom"
                    text_color: 1,1,1,1
            ScrollView:
                MDBoxLayout:
                    id: profile_box
                    orientation: "vertical"
                    adaptive_height: True
                    padding: dp(16)
                    spacing: dp(14)
            BottomBar:
'''


# ================================================================
#  ПРИЛОЖЕНИЕ
# ================================================================
class MoneyHubApp(MDApp):
    current = StringProperty("home")
    stat_tab = StringProperty("categories")
    amounts_hidden = BooleanProperty(False)

    CAT_STYLE = {
        "Продукты":     ("#FFF1DC", "#F0A030"),
        "Доход":        ("#DEF6E4", "#21A038"),
        "Транспорт":    ("#E6EDFD", "#4C7DF0"),
        "Рестораны":    ("#FFE9DD", "#FF8C42"),
        "Развлечения":  ("#F1E6FA", "#A66CD6"),
        "Здоровье":     ("#F1E6FA", "#9B6CE0"),
    }

    # вспомогательный метод, чтобы использовать hex-цвета прямо в KV
    def hex(self, h):
        return hex_color(h)

    def build(self):
        self.theme_cls.theme_style = "Light"
        self.theme_cls.primary_palette = "Blue"
        self._active_cat = "Все"
        self._selected_date = None
        self.root_widget = Builder.load_string(KV)
        return self.root_widget

    def on_start(self):
        Clock.schedule_once(lambda *a: self.refresh_all(), 0)

    # ---------- общее ----------
    def fmt(self, value, plus=False):
        return HIDDEN if self.amounts_hidden else money(value, plus)

    def toggle_amounts(self):
        self.amounts_hidden = not self.amounts_hidden
        self.root_widget.ids["eye_btn"].icon = "eye" if self.amounts_hidden else "eye-off"
        self.refresh_all()

    def switch_screen(self, name):
        self.current = name
        self.root_widget.current = name
        if name == "statistics":
            self.render_statistics()
        elif name == "operations":
            self.render_transactions()
        elif name == "home":
            self.render_home()

    def refresh_all(self):
        self.render_home()
        self.build_categories()
        self.render_transactions()
        self.render_statistics()
        self.render_ai()
        self.render_profile()

    # =================== ГЛАВНАЯ ===================
    def render_home(self):
        ids = self.root_widget.ids
        total = sum(a["balance"] for a in MOCK["accounts"])
        ids["home_balance"].text = self.fmt(total)

        # доход / расходы за месяц (по всем операциям)
        income = sum(t["amount"] for t in MOCK["transactions"] if t["amount"] > 0)
        expenses = sum(-t["amount"] for t in MOCK["transactions"] if t["amount"] < 0)
        ids["home_income"].text = self.fmt(income)
        ids["home_expenses"].text = self.fmt(expenses)

        # счета
        box = ids["home_accounts"]
        box.clear_widgets()
        for acc in MOCK["accounts"]:
            box.add_widget(self._account_card(acc))

        # последние операции (3 штуки)
        tx_box = ids["home_transactions"]
        tx_box.clear_widgets()
        latest = sorted(MOCK["transactions"],
                        key=lambda x: (x["date"], x["time"]), reverse=True)[:3]
        for t in latest:
            tx_box.add_widget(self._tx_card(t))

    def _account_card(self, acc):
        from kivymd.uix.button import MDIconButton
        card = MDCard(orientation="horizontal", size_hint_y=None, height=dp(84),
                      padding=dp(14), spacing=dp(12), radius=[24],
                      md_bg_color=(1, 1, 1, 1), elevation=1.5)
        icon_box = MDCard(size_hint=(None, None), size=(dp(52), dp(52)), radius=[26],
                          md_bg_color=hex_color(acc["color"]),
                          pos_hint={"center_y": 0.5}, elevation=0)
        icon_box.add_widget(MDIconButton(icon=acc["icon"], theme_icon_color="Custom",
                                         icon_color=(1, 1, 1, 1),
                                         pos_hint={"center_x": .5, "center_y": .5}))
        card.add_widget(icon_box)
        col = MDBoxLayout(orientation="vertical", pos_hint={"center_y": 0.5})
        col.add_widget(MDLabel(text=acc["bank"], bold=True, font_size="16sp",
                               theme_text_color="Custom", text_color=(0.12, 0.13, 0.18, 1)))
        col.add_widget(MDLabel(text=f"•• •• •• {acc['last4']}", font_size="12sp",
                               theme_text_color="Custom", text_color=(0.55, 0.57, 0.62, 1)))
        card.add_widget(col)
        card.add_widget(MDLabel(text=self.fmt(acc["balance"]), halign="right", bold=True,
                                font_size="16sp", size_hint_x=None, width=dp(110),
                                pos_hint={"center_y": 0.5}, theme_text_color="Custom",
                                text_color=hex_color(acc["color"])))
        return card

    # =================== КАЛЕНДАРЬ ===================
    def open_calendar(self):
        picker = MDDatePicker()
        picker.bind(on_save=self._on_date_pick)
        picker.open()

    def _on_date_pick(self, instance, value, date_range):
        self._selected_date = value.isoformat()
        self.render_transactions()

    def clear_date(self):
        self._selected_date = None
        self.render_transactions()

    # =================== ОПЕРАЦИИ ===================
    def build_categories(self):
        from kivymd.uix.button import MDRaisedButton, MDFlatButton
        box = self.root_widget.ids["categories_box"]
        box.clear_widgets()
        cats = ["Все"] + sorted({t["category"] for t in MOCK["transactions"]})
        for cat in cats:
            if cat == self._active_cat:
                btn = MDRaisedButton(text=cat, md_bg_color=hex_color("#4C7DF0"))
            else:
                btn = MDFlatButton(text=cat, md_bg_color=(1, 1, 1, 1),
                                   theme_text_color="Custom",
                                   text_color=(0.4, 0.42, 0.48, 1),
                                   line_color=(0.85, 0.86, 0.9, 1))
            btn.size_hint_x = None
            btn.height = dp(36)
            btn.bind(on_release=lambda b, c=cat: self.set_category(c))
            box.add_widget(btn)

    def set_category(self, cat):
        self._active_cat = cat
        self.build_categories()
        self.render_transactions()

    def apply_filter(self):
        self.render_transactions()

    def render_transactions(self):
        ids = self.root_widget.ids
        data = list(MOCK["transactions"])
        if self._selected_date:
            data = [t for t in data if t["date"] == self._selected_date]
        if self._active_cat != "Все":
            data = [t for t in data if t["category"] == self._active_cat]
        query = ids["search_field"].text.strip().lower()
        if query:
            data = [t for t in data
                    if query in t["title"].lower() or query in t["category"].lower()]

        income = sum(t["amount"] for t in data if t["amount"] > 0)
        expenses = sum(-t["amount"] for t in data if t["amount"] < 0)
        ids["op_income"].text = self.fmt(income)
        ids["op_expenses"].text = self.fmt(expenses)

        self._render_date_label()

        box = ids["tx_list"]
        box.clear_widgets()
        if not data:
            box.add_widget(MDLabel(text="Ничего не найдено", halign="center",
                                   font_size="15sp", size_hint_y=None, height=dp(60),
                                   theme_text_color="Custom",
                                   text_color=(0.55, 0.57, 0.62, 1)))
            return
        for t in sorted(data, key=lambda x: (x["date"], x["time"]), reverse=True):
            box.add_widget(self._tx_card(t))

    def _render_date_label(self):
        from kivymd.uix.button import MDIconButton
        row = self.root_widget.ids["filter_row"]
        row.clear_widgets()
        if self._selected_date:
            d = datetime.strptime(self._selected_date, "%Y-%m-%d")
            wd = WEEKDAYS_RU[d.weekday()]
            row.add_widget(MDLabel(text=f"📅 {d.day} {MONTHS_RU[d.month-1]} {d.year}  •  {wd}",
                                   font_size="13sp", adaptive_height=True,
                                   pos_hint={"center_y": 0.5}, theme_text_color="Custom",
                                   text_color=(1, 1, 1, 0.95)))
            clear = MDIconButton(icon="close-circle", theme_icon_color="Custom",
                                 icon_color=(1, 1, 1, 0.9), pos_hint={"center_y": 0.5})
            clear.bind(on_release=lambda b: self.clear_date())
            row.add_widget(clear)
        else:
            row.add_widget(MDLabel(text="Все операции", font_size="13sp",
                                   adaptive_height=True, theme_text_color="Custom",
                                   text_color=(1, 1, 1, 0.9)))

    def _tx_card(self, t):
        bg_hex, ic_hex = self.CAT_STYLE.get(t["category"], ("#ECECEC", "#666666"))
        is_income = t["amount"] > 0
        return TransactionCard(
            title=t["title"],
            subtitle=f"{t['category']} • {fmt_date(t['date'])} • {t['time']}",
            amount_text=self.fmt(t["amount"], plus=True),
            icon=t["icon"],
            icon_bg=list(hex_color(bg_hex)),
            icon_color=list(hex_color(ic_hex)),
            amount_color=list(hex_color("#21A038")) if is_income else [0.12, 0.13, 0.18, 1],
        )

    # =================== СТАТИСТИКА ===================
    def set_stat_tab(self, key):
        self.stat_tab = key
        self.render_statistics()

    def render_statistics(self):
        box = self.root_widget.ids["stats_box"]
        box.clear_widgets()
        income = sum(t["amount"] for t in MOCK["transactions"] if t["amount"] > 0)
        expenses = sum(-t["amount"] for t in MOCK["transactions"] if t["amount"] < 0)
        row = MDBoxLayout(adaptive_height=True, spacing=dp(12))
        row.add_widget(self._summary("Доходы", self.fmt(income), "#21A038", "arrow-down"))
        row.add_widget(self._summary("Расходы", self.fmt(expenses), "#EF3124", "arrow-up"))
        box.add_widget(row)

        if self.stat_tab == "categories":
            self._render_tab_categories(box)
        elif self.stat_tab == "trends":
            self._render_tab_trends(box)
        else:
            self._render_tab_week(box)

    def _summary(self, title, value, color, icon):
        from kivymd.uix.button import MDIconButton
        card = MDCard(orientation="horizontal", size_hint_y=None, height=dp(80),
                      padding=dp(14), spacing=dp(10), radius=[20],
                      md_bg_color=(1, 1, 1, 1), elevation=1.5)
        dot = MDCard(size_hint=(None, None), size=(dp(40), dp(40)), radius=[20],
                     md_bg_color=hex_color(color), pos_hint={"center_y": 0.5}, elevation=0)
        dot.add_widget(MDIconButton(icon=icon, theme_icon_color="Custom",
                                    icon_color=(1, 1, 1, 1),
                                    pos_hint={"center_x": .5, "center_y": .5}))
        card.add_widget(dot)
        col = MDBoxLayout(orientation="vertical", pos_hint={"center_y": 0.5})
        col.add_widget(MDLabel(text=title, font_size="12sp", adaptive_height=True,
                               theme_text_color="Custom", text_color=(0.55, 0.57, 0.62, 1)))
        col.add_widget(MDLabel(text=value, bold=True, font_size="17sp",
                               adaptive_height=True, theme_text_color="Custom",
                               text_color=hex_color(color)))
        card.add_widget(col)
        return card

    def _dot_label(self, text, color):
        row = MDBoxLayout(size_hint_x=None, width=dp(100), spacing=dp(6))
        dot = MDCard(size_hint=(None, None), size=(dp(12), dp(12)), radius=[6],
                     md_bg_color=hex_color(color), pos_hint={"center_y": 0.5}, elevation=0)
        row.add_widget(dot)
        row.add_widget(MDLabel(text=text, font_size="12sp", theme_text_color="Custom",
                               text_color=(0.4, 0.42, 0.48, 1), pos_hint={"center_y": 0.5}))
        return row

    # ---- КАТЕГОРИИ ----
    def _render_tab_categories(self, box):
        total = sum(i["amount"] for i in MOCK["breakdown"])
        chart_card = MDCard(orientation="vertical", size_hint_y=None, height=dp(300),
                            padding=dp(16), radius=[22], md_bg_color=(1, 1, 1, 1),
                            elevation=1.5)
        chart_card.add_widget(MDLabel(text="Расходы по категориям", bold=True,
                                      font_size="17sp", size_hint_y=None, height=dp(28),
                                      theme_text_color="Custom",
                                      text_color=(0.12, 0.13, 0.18, 1)))
        wrap = Widget(size_hint_y=None, height=dp(210))
        donut = DonutChart(data=[{"percent": i["percent"], "color": i["color"]}
                                 for i in MOCK["breakdown"]])
        wrap.add_widget(donut)
        center = MDBoxLayout(orientation="vertical", size_hint=(None, None),
                             size=(dp(120), dp(60)))
        center.add_widget(MDLabel(text="Всего", halign="center", font_size="12sp",
                                  theme_text_color="Custom", text_color=(0.55, 0.57, 0.62, 1)))
        center.add_widget(MDLabel(text=self.fmt(total), halign="center", bold=True,
                                  font_size="18sp", theme_text_color="Custom",
                                  text_color=(0.12, 0.13, 0.18, 1)))
        wrap.add_widget(center)

        def _sync(*a):
            donut.size = wrap.size
            donut.pos = wrap.pos
            center.center = wrap.center
        wrap.bind(pos=_sync, size=_sync)
        chart_card.add_widget(wrap)
        box.add_widget(chart_card)

        for item in MOCK["breakdown"]:
            box.add_widget(self._legend_row(item))

    def _legend_row(self, item):
        card = MDCard(orientation="horizontal", size_hint_y=None, height=dp(58),
                      padding=dp(14), spacing=dp(12), radius=[16],
                      md_bg_color=(1, 1, 1, 1), elevation=1)
        dot = MDCard(size_hint=(None, None), size=(dp(14), dp(14)), radius=[7],
                     md_bg_color=hex_color(item["color"]), pos_hint={"center_y": 0.5},
                     elevation=0)
        card.add_widget(dot)
        card.add_widget(MDLabel(text=f"{item['emoji']}  {item['category']}",
                                font_size="15sp", pos_hint={"center_y": 0.5},
                                theme_text_color="Custom", text_color=(0.12, 0.13, 0.18, 1)))
        col = MDBoxLayout(orientation="vertical", size_hint_x=None, width=dp(110),
                          pos_hint={"center_y": 0.5})
        col.add_widget(MDLabel(text=self.fmt(item["amount"]), halign="right", bold=True,
                               font_size="14sp", theme_text_color="Custom",
                               text_color=(0.12, 0.13, 0.18, 1)))
        col.add_widget(MDLabel(text=f"{item['percent']}%", halign="right", font_size="11sp",
                               theme_text_color="Custom", text_color=(0.55, 0.57, 0.62, 1)))
        card.add_widget(col)
        return card

    # ---- ТРЕНДЫ ----
    def _render_tab_trends(self, box):
        max_v = max(max(t["income"], t["expense"]) for t in MOCK["trends"])
        max_v = math.ceil(max_v / 20000) * 20000

        card = MDCard(orientation="vertical", size_hint_y=None, height=dp(290),
                      padding=dp(16), spacing=dp(8), radius=[22],
                      md_bg_color=(1, 1, 1, 1), elevation=1.5)
        card.add_widget(MDLabel(text="Расходы по месяцам", bold=True, font_size="17sp",
                                size_hint_y=None, height=dp(26), theme_text_color="Custom",
                                text_color=(0.12, 0.13, 0.18, 1)))
        leg = MDBoxLayout(adaptive_height=True, size_hint_y=None, height=dp(22))
        leg.add_widget(self._dot_label("Расходы", "#EF3124"))
        leg.add_widget(Widget())
        card.add_widget(leg)
        chart = BarChart(size_hint_y=None, height=dp(200), max_value=max_v)
        chart.data = [{"label": t["month"], "value": t["expense"], "color": "#EF3124"}
                      for t in MOCK["trends"]]
        card.add_widget(chart)
        box.add_widget(card)

        card2 = MDCard(orientation="vertical", size_hint_y=None, height=dp(250),
                       padding=dp(16), spacing=dp(8), radius=[22],
                       md_bg_color=(1, 1, 1, 1), elevation=1.5)
        card2.add_widget(MDLabel(text="Доходы по месяцам", bold=True, font_size="17sp",
                                 size_hint_y=None, height=dp(26), theme_text_color="Custom",
                                 text_color=(0.12, 0.13, 0.18, 1)))
        chart2 = BarChart(size_hint_y=None, height=dp(190), max_value=max_v)
        chart2.data = [{"label": t["month"], "value": t["income"], "color": "#21A038"}
                       for t in MOCK["trends"]]
        card2.add_widget(chart2)
        box.add_widget(card2)

    # ---- НЕДЕЛЯ ----
    def _render_tab_week(self, box):
        total = sum(d["amount"] for d in MOCK["week"])
        avg = total // len(MOCK["week"])
        peak = max(MOCK["week"], key=lambda d: d["amount"])

        row = MDBoxLayout(adaptive_height=True, spacing=dp(12))
        row.add_widget(self._summary("За неделю", self.fmt(total), "#4C7DF0", "calendar-week"))
        row.add_widget(self._summary("В среднем/день", self.fmt(avg), "#9B6CE0", "chart-line"))
        box.add_widget(row)

        card = MDCard(orientation="vertical", size_hint_y=None, height=dp(290),
                      padding=dp(16), spacing=dp(8), radius=[22],
                      md_bg_color=(1, 1, 1, 1), elevation=1.5)
        card.add_widget(MDLabel(text="Расходы по дням недели", bold=True, font_size="17sp",
                                size_hint_y=None, height=dp(26), theme_text_color="Custom",
                                text_color=(0.12, 0.13, 0.18, 1)))
        max_v = math.ceil(max(d["amount"] for d in MOCK["week"]) / 1000) * 1000
        chart = BarChart(size_hint_y=None, height=dp(220), max_value=max_v)
        chart.data = [{"label": d["day"], "value": d["amount"], "color": "#4C8DF0"}
                      for d in MOCK["week"]]
        card.add_widget(chart)
        box.add_widget(card)

        peak_card = MDCard(orientation="horizontal", size_hint_y=None, height=dp(70),
                           padding=dp(16), spacing=dp(12), radius=[18],
                           md_bg_color=hex_color("#FFF1DC"), elevation=1)
        peak_card.add_widget(MDLabel(text="🔥", font_size="26sp", size_hint_x=None,
                                     width=dp(40), pos_hint={"center_y": 0.5}))
        col = MDBoxLayout(orientation="vertical", pos_hint={"center_y": 0.5})
        col.add_widget(MDLabel(text="Самый расходный день", bold=True, font_size="14sp",
                               theme_text_color="Custom", text_color=(0.12, 0.13, 0.18, 1)))
        col.add_widget(MDLabel(text=f"{peak['day']} — {self.fmt(peak['amount'])}",
                               font_size="12sp", theme_text_color="Custom",
                               text_color=(0.55, 0.50, 0.40, 1)))
        peak_card.add_widget(col)
        box.add_widget(peak_card)

    # =================== ИИ ===================
    def render_ai(self):
        box = self.root_widget.ids["ai_box"]
        box.clear_widgets()
        for tip in MOCK["ai_tips"]:
            box.add_widget(self._ai_card(tip))

    def _ai_card(self, tip):
        from kivymd.uix.button import MDIconButton
        card = MDCard(orientation="horizontal", size_hint_y=None, height=dp(120),
                      padding=dp(16), spacing=dp(14), radius=[22],
                      md_bg_color=(1, 1, 1, 1), elevation=1.5)
        icon_box = MDCard(size_hint=(None, None), size=(dp(50), dp(50)), radius=[25],
                          md_bg_color=hex_color("#E6EDFD"), pos_hint={"center_y": 0.5},
                          elevation=0)
        icon_box.add_widget(MDIconButton(icon=tip["icon"], theme_icon_color="Custom",
                                         icon_color=hex_color("#4C7DF0"),
                                         pos_hint={"center_x": .5, "center_y": .5}))
        card.add_widget(icon_box)
        col = MDBoxLayout(orientation="vertical", spacing=dp(4), pos_hint={"center_y": 0.5})
        col.add_widget(MDLabel(text=tip["title"], bold=True, font_size="16sp",
                               adaptive_height=True, theme_text_color="Custom",
                               text_color=(0.12, 0.13, 0.18, 1)))
        col.add_widget(MDLabel(text=tip["text"], font_size="13sp", adaptive_height=True,
                               theme_text_color="Custom", text_color=(0.45, 0.47, 0.52, 1)))
        card.add_widget(col)
        return card

    # =================== ПРОФИЛЬ ===================
    def render_profile(self):
        box = self.root_widget.ids["profile_box"]
        box.clear_widgets()
        u = MOCK["user"]
        from kivymd.uix.button import MDIconButton

        # шапка профиля
        header = MDCard(orientation="vertical", size_hint_y=None, height=dp(200),
                        padding=dp(20), radius=[24], md_bg_color=hex_color("#4C7DF0"),
                        spacing=dp(8))
        avatar = MDCard(size_hint=(None, None), size=(dp(76), dp(76)), radius=[38],
                        md_bg_color=(1, 1, 1, 0.25), pos_hint={"center_x": 0.5},
                        elevation=0)
        avatar.add_widget(MDIconButton(icon="account", theme_icon_color="Custom",
                                       icon_color=(1, 1, 1, 1), icon_size="38sp",
                                       pos_hint={"center_x": .5, "center_y": .5}))
        header.add_widget(avatar)
        header.add_widget(MDLabel(text=u["name"], bold=True, font_size="20sp",
                                  halign="center", adaptive_height=True,
                                  theme_text_color="Custom", text_color=(1, 1, 1, 1)))
        header.add_widget(MDLabel(text=u["email"], font_size="13sp", halign="center",
                                  adaptive_height=True, theme_text_color="Custom",
                                  text_color=(1, 1, 1, 0.85)))
        box.add_widget(header)

        # пункты меню
        menu = [
            ("account-edit",      "Личные данные",     "Имя, телефон, e-mail"),
            ("bank-plus",         "Подключить банк",    "Добавить новый счёт"),
            ("bell-outline",      "Уведомления",        "Push и e-mail оповещения"),
            ("shield-lock",       "Безопасность",       "Пароль, биометрия, PIN"),
            ("eye-off-outline",   "Скрывать суммы",     "Маскировать баланс"),
            ("help-circle",       "Помощь",             "Поддержка и FAQ"),
        ]
        for icon, title, sub in menu:
            box.add_widget(self._profile_row(icon, title, sub))

        # выход
        from kivymd.uix.button import MDRaisedButton
        logout = MDRaisedButton(text="Выйти из аккаунта",
                                md_bg_color=hex_color("#EF3124"),
                                size_hint=(1, None), height=dp(50),
                                pos_hint={"center_x": 0.5})
        logout.bind(on_release=lambda b: self.logout())
        box.add_widget(logout)

    def _profile_row(self, icon, title, sub):
        from kivymd.uix.button import MDIconButton
        card = MDCard(orientation="horizontal", size_hint_y=None, height=dp(68),
                      padding=dp(14), spacing=dp(12), radius=[18],
                      md_bg_color=(1, 1, 1, 1), elevation=1)
        icon_box = MDCard(size_hint=(None, None), size=(dp(42), dp(42)), radius=[21],
                          md_bg_color=hex_color("#E6EDFD"), pos_hint={"center_y": 0.5},
                          elevation=0)
        icon_box.add_widget(MDIconButton(icon=icon, theme_icon_color="Custom",
                                         icon_color=hex_color("#4C7DF0"),
                                         pos_hint={"center_x": .5, "center_y": .5}))
        card.add_widget(icon_box)
        col = MDBoxLayout(orientation="vertical", pos_hint={"center_y": 0.5})
        col.add_widget(MDLabel(text=title, bold=True, font_size="15sp",
                               adaptive_height=True, theme_text_color="Custom",
                               text_color=(0.12, 0.13, 0.18, 1)))
        col.add_widget(MDLabel(text=sub, font_size="11sp", adaptive_height=True,
                               theme_text_color="Custom", text_color=(0.55, 0.57, 0.62, 1)))
        card.add_widget(col)
        card.add_widget(MDIconButton(icon="chevron-right", theme_icon_color="Custom",
                                     icon_color=(0.7, 0.72, 0.76, 1),
                                     pos_hint={"center_y": 0.5}))
        return card

    def logout(self):
        print("TODO: выход из аккаунта / переход на экран входа")


# ================================================================
#  ЗАПУСК
# ================================================================
if __name__ == "__main__":
    MoneyHubApp().run()