from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from supabase import create_client
import google.generativeai as genai
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Allow everything for testing
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 🔑 ключи
SUPABASE_URL = "https://poxydnxojhvbssxlnvrv.supabase.co"
SUPABASE_KEY = "sb_publishable_mbz3m1lisF4tHcn1CrXJ6Q_S5Q9F-5W"
GEMINI_KEY = "AIzaSyBu0Wp4sxXyUO_O1utvxNQ5nMd8TlzFlrs"

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

genai.configure(api_key=GEMINI_KEY)
model = genai.GenerativeModel("gemini-pro")

class UserData(BaseModel):
    name: str
    score: int
    subject: str

@app.post("/recommend")
async def recommend(data: UserData):
    
    # 📦 берем универы из базы
    response = supabase.table("universities").select("*").execute()
    universities = response.data

    # 📊 фильтр по баллам
    filtered = [u for u in universities if u["min_score"] <= data.score]

    # 🤖 отправка в Gemini
    prompt = f"""
    Студент: {data.name}
    Балл: {data.score}
    Предмет: {data.subject}

    Вот список университетов:
    {filtered}

    Дай лучший совет и список подходящих вузов
    """

    ai_response = model.generate_content(prompt)

    return {"answer": ai_response.text}

@app.get("/universities")
async def get_universities():
    try:
        # Query the 'universities' table
        # .select("*") fetches all columns; you can replace "*" with "id, name" for specific ones
        response = supabase.table("universitets").select("*").execute()
        
        # The data is located in the .data attribute of the response
        return response.data
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

DISTRICTS_DATA = [
    {
        "id": "bostandyq",
        "name": "Бостандыкский",
        "safety_score": 62,
        "total_buildings": 2840,
        "safety_levels": {"safe": 1100, "moderate": 1200, "warning": 400, "critical": 140},
        "school_load_pct": 124, # Превышение из-за активной застройки "выше Аль-Фараби"
        "infra_wear_pct": 48,
        "seismic_zones": 5      # Пересекается крупными разломами (напр. Диагональный)
    },
    {
        "id": "medeu",
        "name": "Медеуский",
        "safety_score": 58,
        "total_buildings": 2100,
        "safety_levels": {"safe": 800, "moderate": 750, "warning": 400, "critical": 150},
        "school_load_pct": 112,
        "infra_wear_pct": 52,
        "seismic_zones": 7      # Высокая зона риска из-за предгорий и разломов
    },
    {
        "id": "almalinskiy",
        "name": "Алмалинский",
        "safety_score": 74,
        "total_buildings": 1950,
        "safety_levels": {"safe": 1200, "moderate": 500, "warning": 180, "critical": 70},
        "school_load_pct": 105,
        "infra_wear_pct": 65,    # Самый высокий износ сетей (старый центр)
        "seismic_zones": 2
    },
    {
        "id": "auezovskiy",
        "name": "Ауэзовский",
        "safety_score": 68,
        "total_buildings": 3100,
        "safety_levels": {"safe": 1500, "moderate": 1100, "warning": 400, "critical": 100},
        "school_load_pct": 130,  # Высокая плотность населения (мкрн 1-12)
        "infra_wear_pct": 58,
        "seismic_zones": 3
    },
    {
        "id": "alatauskiy",
        "name": "Алатауский",
        "safety_score": 82,
        "total_buildings": 1800,
        "safety_levels": {"safe": 1400, "moderate": 300, "warning": 80, "critical": 20},
        "school_load_pct": 145,  # Критический дефицит мест в школах (активный рост)
        "infra_wear_pct": 32,    # Новые сети, низкий износ
        "seismic_zones": 1
    },
    {
        "id": "jetysuskiy",
        "name": "Жетысуский",
        "safety_score": 65,
        "total_buildings": 1600,
        "safety_levels": {"safe": 700, "moderate": 650, "warning": 180, "critical": 70},
        "school_load_pct": 110,
        "infra_wear_pct": 60,
        "seismic_zones": 2
    },
    {
        "id": "turksibskiy",
        "name": "Турксибский",
        "safety_score": 60,
        "total_buildings": 2400,
        "safety_levels": {"safe": 900, "moderate": 950, "warning": 400, "critical": 150},
        "school_load_pct": 108,
        "infra_wear_pct": 55,
        "seismic_zones": 3
    },
    {
        "id": "nauryzbayskiy",
        "name": "Наурызбайский",
        "safety_score": 78,
        "total_buildings": 1350,
        "safety_levels": {"safe": 1100, "moderate": 150, "warning": 80, "critical": 20},
        "school_load_pct": 138,  # Новый район, инфраструктура не успевает за жильем
        "infra_wear_pct": 28,    # Самые новые коммуникации
        "seismic_zones": 4
    }
]


SEISMIC_FAULTS = [
    {
        "id": 1, 
        "name": "Заилийский разлом (Диагональный)", 
        "description": "Проходит вдоль пр. Аль-Фараби, через пл. Республики и Парк Горького.",
        "coords": [[43.218, 76.850], [43.235, 76.920], [43.250, 76.970]]
    },
    {
        "id": 2, 
        "name": "Северный разлом", 
        "description": "Проходит через озеро Сайран, вдоль ул. Кабанбай батыра до р. Малая Алматинка.",
        "coords": [[43.245, 76.865], [43.248, 76.910], [43.252, 76.955]]
    },
    {
        "id": 3, 
        "name": "Алматинский разлом", 
        "description": "Широтный разлом, проходит севернее пр. Райымбека через Жетысуский район.",
        "coords": [[43.270, 76.840], [43.275, 76.900], [43.280, 76.980]]
    },
    {
        "id": 4, 
        "name": "Северо-Западный разлом", 
        "description": "Пересекает Алатауский район, проходит через мкр. Карасу и Ожет.",
        "coords": [[43.300, 76.820], [43.325, 76.880], [43.350, 76.930]]
    },
    {
        "id": 5, 
        "name": "Коктобинский разлом", 
        "description": "Проходит в восточной части города, вдоль подножья горы Кок-Тобе.",
        "coords": [[43.210, 76.960], [43.230, 76.980], [43.255, 76.995]]
    }
]

CITY_STATS = {
    # Основная статистика застройки
    "total_buildings": 18240,
    "city_safety_index": 68.5,           # Общий индекс безопасности (0-100)
    "critical_objects_count": 824,       # Здания в красной зоне
    "renovation_queue": 156,             # Объектов на снос/реновацию
    
    # Инфраструктура и сети (ЖКХ)
    "infrastructure_health": 52.0,       # Общее состояние сетей (%)
    "water_deficit_m3": 45000,           # Суточный дефицит воды по городу
    "power_grid_load_pct": 78.4,         # Средняя нагрузка на электросети
    "heating_network_loss": 22.1,        # Потери в теплосетях (%)
    
    # Социальные показатели
    "school_seat_deficit": 32500,        # Дефицит ученических мест
    "kindergarten_waiting_list": 18400,  # Очередь в детские сады
    "hospital_bed_occupancy": 84.2,      # Загруженность больниц (%)
    
    # Сейсмика и ЧС
    "seismic_events_24h": 12,            # Микро-толчки за последние 24ч (для динамики)
    "emergency_response_avg_min": 8.5,   # Среднее время прибытия служб
    "shelter_capacity_pct": 65.0,        # Готовность убежищ к населению города
    
    # Экология и среда
    "air_quality_index_avg": 142,        # AQI (для Алматы это критически важно)
    "green_area_per_capita": 4.2,        # м2 зелени на человека (норма ~10)
    
    # Демография (для ИИ-прогнозов)
    "total_population": 2245000,
    "population_growth_rate": 2.4,       # Годовой прирост (%)
    
    # Метаданные
    "last_updated": "2026-04-03T18:00:00Z",
    "data_source": "OpenData Almaty / Digital GenPlan API"
}

MAP_CONFIG = {
    "layers": [
        {"id": "seismic", "label": "Сейсмические разломы", "active": True, "color": "#FF4D4D"},
        {"id": "infra", "label": "Износ сетей", "active": False, "color": "#FFA500"},
        {"id": "social", "label": "Социальные объекты", "active": True, "color": "#4D79FF"}
    ],
    "legend": [
        {"label": "Соответствует нормам 2026", "color": "#2ecc71", "status": "safe"},
        {"label": "Требует сейсмоусиления", "color": "#f1c40f", "status": "moderate"},
        {"label": "Риск / Износ > 70%", "color": "#e67e22", "status": "warning"},
        {"label": "Критическое / Запрещено", "color": "#e74c3c", "status": "critical"}
    ]
}

DISTRICTS_EXTENDED = [
    {
        "id": "bostandyq",
        "name": "Бостандыкский",
        "safety_score": 62,
        "safety_badge": "Warning",
        "total_buildings": 2840,
        "comparison_data": [
            {"category": "Сейсмика", "district": 62, "city_avg": 68},
            {"category": "Инфраструктура", "district": 52, "city_avg": 48},
            {"category": "Школы", "district": 76, "city_avg": 70},
            {"category": "Экология", "district": 45, "city_avg": 55}
        ],
        "safety_levels": {"safe": 1100, "moderate": 1200, "warning": 400, "critical": 140},
        "description": "Район с интенсивной высотной застройкой. Риски связаны с близостью к предгорным разломам и высокой нагрузкой на теплосети."
    },
    {
        "id": "medeu",
        "name": "Медеуский",
        "safety_score": 58,
        "safety_badge": "Critical Risk",
        "total_buildings": 2100,
        "comparison_data": [
            {"category": "Сейсмика", "district": 45, "city_avg": 68},
            {"category": "Инфраструктура", "district": 42, "city_avg": 48},
            {"category": "Школы", "district": 85, "city_avg": 70},
            {"category": "Экология", "district": 70, "city_avg": 55}
        ],
        "safety_levels": {"safe": 800, "moderate": 750, "warning": 400, "critical": 150},
        "description": "Элитный район с опасным рельефом. Высокая концентрация тектонических разломов требует жесткого контроля этажности."
    },
    {
        "id": "almalinskiy",
        "name": "Алмалинский",
        "safety_score": 74,
        "safety_badge": "Stable",
        "total_buildings": 1950,
        "comparison_data": [
            {"category": "Сейсмика", "district": 78, "city_avg": 68},
            {"category": "Инфраструктура", "district": 35, "city_avg": 48},
            {"category": "Школы", "district": 68, "city_avg": 70},
            {"category": "Экология", "district": 30, "city_avg": 55}
        ],
        "safety_levels": {"safe": 1200, "moderate": 500, "warning": 180, "critical": 70},
        "description": "Исторический центр. Главная проблема — критический износ инженерных сетей (водопровод и канализация) и смог."
    },
    {
        "id": "auezovskiy",
        "name": "Ауэзовский",
        "safety_score": 68,
        "safety_badge": "Moderate",
        "total_buildings": 3100,
        "comparison_data": [
            {"category": "Сейсмика", "district": 72, "city_avg": 68},
            {"category": "Инфраструктура", "district": 45, "city_avg": 48},
            {"category": "Школы", "district": 50, "city_avg": 70},
            {"category": "Экология", "district": 40, "city_avg": 55}
        ],
        "safety_levels": {"safe": 1500, "moderate": 1100, "warning": 400, "critical": 100},
        "description": "Спальный район с самой высокой плотностью населения. Наблюдается острый дефицит мест в государственных школах."
    },
    {
        "id": "alatauskiy",
        "name": "Алатауский",
        "safety_score": 82,
        "safety_badge": "Safe Zone",
        "total_buildings": 1800,
        "comparison_data": [
            {"category": "Сейсмика", "district": 88, "city_avg": 68},
            {"category": "Инфраструктура", "district": 75, "city_avg": 48},
            {"category": "Школы", "district": 35, "city_avg": 70},
            {"category": "Экология", "district": 60, "city_avg": 55}
        ],
        "safety_levels": {"safe": 1400, "moderate": 300, "warning": 80, "critical": 20},
        "description": "Новый индустриальный район. Сейсмически стабилен, имеет новые коммуникации, но инфраструктура (школы/больницы) не успевает за ростом."
    },
    {
        "id": "nauryzbayskiy",
        "name": "Наурызбайский",
        "safety_score": 78,
        "safety_badge": "Developing",
        "total_buildings": 1350,
        "comparison_data": [
            {"category": "Сейсмика", "district": 70, "city_avg": 68},
            {"category": "Инфраструктура", "district": 85, "city_avg": 48},
            {"category": "Школы", "district": 40, "city_avg": 70},
            {"category": "Экология", "district": 75, "city_avg": 55}
        ],
        "safety_levels": {"safe": 1100, "moderate": 150, "warning": 80, "critical": 20},
        "description": "Активно застраиваемый район. Хорошая экология и новые сети, однако транспортная доступность остается слабой."
    }
]

MARKERS_MOCK = [
    # --- ШКОЛЫ И СОЦ. ОБЪЕКТЫ (ОБРАЗОВАНИЕ) ---
    {"id": "sh-12", "type": "school", "name": "Гимназия №12", "coords": [43.248, 76.945], "status": "critical", "load": 142, "capacity": 800, "details": "Превышение проектной мощности на 42%."},
    {"id": "sh-nish", "type": "school", "name": "НИШ ФМН", "coords": [43.222, 76.878], "status": "safe", "load": 95, "capacity": 900, "details": "Нагрузка в норме."},
    {"id": "sh-178", "type": "school", "name": "Лицей №178", "coords": [43.285, 76.855], "status": "warning", "load": 125, "capacity": 1200, "details": "Район Алатау, дефицит мест."},
    {"id": "sh-175", "type": "school", "name": "Гимназия №175", "coords": [43.212, 76.840], "status": "critical", "load": 156, "capacity": 600, "details": "Наурызбайский р-н, критический перегруз."},
    {"id": "sh-1", "type": "school", "name": "Гимназия №1", "coords": [43.255, 76.935], "status": "moderate", "load": 110, "capacity": 1000, "details": "Плановая загрузка."},

    # --- МЕДИЦИНСКИЕ ОБЪЕКТЫ ---
    {"id": "hosp-7", "type": "hospital", "name": "ГКБ №7 (Калкаман)", "coords": [43.228, 76.820], "status": "warning", "load": 88, "details": "Высокая нагрузка на приемный покой."},
    {"id": "hosp-centr", "type": "hospital", "name": "Центральная ГКБ", "coords": [43.235, 76.930], "status": "safe", "load": 72, "details": "Сейсмоусиление проведено в 2024 г."},

    # --- СЕЙСМИЧЕСКИЕ ЗОНЫ И РАЗЛОМЫ (⚠️) ---
    {"id": "fz-1", "type": "fault_zone", "name": "Заилийский разлом (Центр)", "coords": [43.220, 76.860], "status": "critical", "danger_level": "9.5 баллов", "restriction": "Запрет высотного строительства."},
    {"id": "fz-2", "type": "fault_zone", "name": "Алматинский разлом (Север)", "coords": [43.275, 76.910], "status": "warning", "danger_level": "9.0 баллов", "restriction": "Ограничение до 9 этажей."},
    {"id": "fz-3", "type": "fault_zone", "name": "Предгорный разлом", "coords": [43.195, 76.940], "status": "critical", "danger_level": "10 баллов", "restriction": "Зона тектонического влияния."},
    {"id": "fz-4", "type": "fault_zone", "name": "Диагональный разлом (Запад)", "coords": [43.240, 76.830], "status": "warning", "danger_level": "9.0 баллов", "restriction": "Спец. ТУ на фундамент."},

    # --- ИНФРАСТРУКТУРА (ЭЛЕКТРИЧЕСТВО / ВОДА) ---
    {"id": "inf-1", "type": "utility", "name": "ПС-110А 'Южная'", "coords": [43.210, 76.905], "status": "critical", "load": 92, "details": "Трансформаторы на пределе. Нет резерва для новых ЖК."},
    {"id": "inf-3", "type": "utility", "name": "ТЭЦ-2 (Узел распределения)", "coords": [43.305, 76.815], "status": "warning", "load": 84, "details": "Требуется модернизация котлов."},
    {"id": "inf-4", "type": "utility", "name": "Насосная станция 'Сайран'", "coords": [43.242, 76.868], "status": "safe", "load": 65, "details": "Запас мощности по водоснабжению."},

    # --- ЖИЛЫЕ ОБЪЕКТЫ (ДЛЯ СРАВНЕНИЯ) ---
    {"id": "res-1", "type": "residential", "name": "Мкр. Самал-2, д. 5", "coords": [43.232, 76.955], "status": "safe", "year_built": 1998, "seismic": "9 баллов"},
    {"id": "res-2", "type": "residential", "name": "ЖК 'Esentai City'", "coords": [43.205, 76.925], "status": "safe", "year_built": 2022, "seismic": "10 баллов"},
    {"id": "res-3", "type": "residential", "name": "Панельный дом (Аксай-4)", "coords": [43.238, 76.845], "status": "moderate", "year_built": 1985, "seismic": "7-8 баллов"},
    {"id": "res-4", "type": "residential", "name": "Ветхий дом (Сейфуллина-Райымбека)", "coords": [43.265, 76.920], "status": "critical", "year_built": 1948, "details": "Аварийное состояние. Реновация в 2026."},

    # --- НОВЫЕ ПРОЕКТЫ (НА РАССМОТРЕНИИ) ---
    {"id": "new-1", "type": "project", "name": "Проект 'Skyline Almaty'", "coords": [43.218, 76.890], "status": "warning", "floors": 18, "details": "Ожидание AI-вердикта по сейсмике."},
    {"id": "new-2", "type": "project", "name": "ЖК 'Green Park'", "coords": [43.310, 76.850], "status": "safe", "floors": 5, "details": "Одобрено: низкая плотность."}
]

@app.get("/api/v1/dashboard/init")
async def get_dashboard_init():
    """
    Главный эндпоинт для инициализации дашборда.
    Отдает статистику, конфиг слоев и список районов.
    """
    return {
        "stats": CITY_STATS,
        "config": MAP_CONFIG,
        "districts": DISTRICTS_EXTENDED
    }

@app.get("/api/v1/map/elements")
async def get_map_elements(layer: Optional[str] = None):
    """
    Отдает гео-данные для карты: разломы и маркеры объектов.
    Можно фильтровать по слоям.
    """
    return {
        "faults": SEISMIC_FAULTS,
        "markers": MARKERS_MOCK
    }

@app.get("/api/v1/districts/{district_id}")
async def get_district_details(district_id: str):
    """
    Детальная информация по конкретному району для Side Panel.
    """
    district = next((d for d in DISTRICTS_EXTENDED if d["id"] == district_id), None)
    if district:
        return district
    return {"error": "District not found"}