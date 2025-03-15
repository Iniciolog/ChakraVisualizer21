import streamlit as st

# Настройка страницы
st.set_page_config(
    page_title="KIRLIAN PLATFORM",
    page_icon="🔮",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'About': """
        ### KIRLIAN PLATFORM
        **Разработано в НИЦ Инициологии и трансперсональной психологии**
        
        Streamlit v1.43.1
        """
    }
)

# Пользовательский CSS
with open('styles.css') as f:
    css_content = f.read()
    
# Добавляем инлайн CSS для элементов с темным оформлением
additional_css = """
<style>
/* Force dark theme for dropdowns and other elements */
div[data-baseweb="select"], 
div[data-baseweb="popover"],
div[data-baseweb="menu"],
div[role="listbox"],
ul[role="listbox"],
li[role="option"] {
    background-color: #14142B !important;
    color: #E0E0E0 !important;
}

/* Override any inline styles that might use white backgrounds */
[style*="background-color: rgb(255, 255, 255)"],
[style*="background-color:#fff"],
[style*="background-color: #ffffff"],
[style*="background: white"],
[style*="background:white"] {
    background-color: #0E0E20 !important;
}

/* Header area fix */
header[data-testid="stHeader"] {
    background-color: #0E0E20 !important;
}

/* Центрирование содержимого */
.centered-content {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    height: 80vh;
    text-align: center;
}

.platform-title {
    font-size: 4rem;
    font-weight: 700;
    margin-bottom: 2rem;
    background: linear-gradient(45deg, #7B68EE, #00BFFF, #9370DB);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    text-shadow: 0 0 5px rgba(123, 104, 238, 0.2);
}

.platform-subtitle {
    font-size: 1.8rem;
    font-weight: 400;
    margin-bottom: 3rem;
    color: #E0E0E0;
}

.labs-section {
    margin-top: 2rem;
    display: flex;
    justify-content: center;
    flex-wrap: wrap;
    gap: 2rem;
}

.lab-card {
    width: 300px;
    padding: 1.5rem;
    border-radius: 15px;
    background: linear-gradient(145deg, #191930, #14142B);
    border: 1px solid rgba(255, 255, 255, 0.1);
    display: flex;
    flex-direction: column;
    align-items: center;
    transition: transform 0.3s, box-shadow 0.3s;
    box-shadow: 0 8px 16px rgba(0, 0, 0, 0.2);
}

.lab-card:hover {
    transform: translateY(-10px);
    box-shadow: 0 12px 24px rgba(0, 0, 0, 0.4);
}

.lab-icon {
    font-size: 3rem;
    margin-bottom: 1rem;
}

.lab-title {
    font-size: 1.5rem;
    font-weight: 600;
    margin-bottom: 0.5rem;
    color: #F8F8F8;
}

.lab-description {
    font-size: 1rem;
    color: #BCBCBC;
    text-align: center;
}
</style>
"""

# Применяем CSS
st.markdown(f'<style>{css_content}</style>{additional_css}', unsafe_allow_html=True)

# Создаем контейнер с центрированным содержимым
st.markdown("""
<div class="centered-content">
    <h1 class="platform-title">KIRLIAN PLATFORM</h1>
    <h2 class="platform-subtitle">Инновационная платформа для исследования энергетического поля человека</h2>
    
    <div class="labs-section">
        <a href="Bioresonans_Lab" style="text-decoration: none;">
            <div class="lab-card">
                <div class="lab-icon">🔬</div>
                <div class="lab-title">Bioresonans Lab</div>
                <div class="lab-description">
                    Анализ биорезонансной диагностики и визуализация энергетического поля человека
                </div>
            </div>
        </a>
        
        <a href="1_GRV_Lab" style="text-decoration: none;">
            <div class="lab-card">
                <div class="lab-icon">🔮</div>
                <div class="lab-title">GRV Lab</div>
                <div class="lab-description">
                    Газоразрядная визуализация пальцев рук и интерпретация энергетического состояния
                </div>
            </div>
        </a>
    </div>
</div>
""", unsafe_allow_html=True)

# Информация о версии внизу страницы
st.markdown("""
<div style="position: fixed; bottom: 20px; width: 100%; text-align: center; color: #888; font-size: 0.8rem;">
    KIRLIAN PLATFORM © 2025 | Версия 1.0.0
</div>
""", unsafe_allow_html=True)