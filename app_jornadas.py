import streamlit as st
import random
import copy
import time

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(
    page_title="Generador de Ligas",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- ESTILOS VISUALES (PREMIUM UI) ---
st.markdown("""
<style>
    /* Estilo general moderno */
    .stApp {
        background: linear-gradient(to bottom right, #0F172A, #1E293B);
        color: #E2E8F0;
        font-family: 'Inter', sans-serif;
    }
    
    /* Encabezados */
    h1, h2, h3 {
        color: #38BDF8 !important;
        font-weight: 700;
        letter-spacing: -0.5px;
    }
    
    h1 {
        background: -webkit-linear-gradient(45deg, #38BDF8, #818CF8);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 30px;
    }

    /* Cards para las jornadas */
    .jornada-card {
        background-color: #1E293B;
        border: 1px solid #334155;
        border-radius: 12px;
        padding: 16px;
        margin-bottom: 16px;
        transition: transform 0.2s, box-shadow 0.2s;
    }
    .jornada-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
        border-color: #38BDF8;
    }
    
    .match-row {
        display: grid;
        grid-template-columns: 1fr auto 1fr;
        gap: 15px;
        align-items: center;
        padding: 10px 0;
        border-bottom: 1px solid #334155;
    }
    .match-row:last-child {
        border-bottom: none;
    }
    
    .team-name {
        font-weight: 500;
        color: #F1F5F9;
        font-size: 0.95rem;
    }

    .match-row > span:first-child {
        text-align: right;
    }

    .match-row > span:last-child {
        text-align: left;
    }
    
    .vs-badge {
        color: #94A3B8;
        font-size: 0.75em;
        font-weight: 700;
        background: #0F172A;
        padding: 3px 8px;
        border-radius: 8px;
        border: 1px solid #334155;
        letter-spacing: 1px;
    }

    /* Botones */
    .stButton>button {
        background: linear-gradient(90deg, #38BDF8, #818CF8);
        color: white;
        border: none;
        padding: 0.6rem 1.5rem;
        border-radius: 8px;
        font-weight: 600;
        transition: all 0.3s ease;
        width: 100%;
    }
    .stButton>button:hover {
        opacity: 0.9;
        transform: scale(1.02);
        box-shadow: 0 4px 12px rgba(56, 189, 248, 0.3);
    }

    /* Sidebar */
    [data-testid="stSidebar"] {
        background-color: #0F172A;
        border-right: 1px solid #334155;
    }
    
    /* Inputs */
    .stTextArea textarea {
        background-color: #1E293B;
        color: #F1F5F9;
        border: 1px solid #475569;
        border-radius: 8px;
    }
    .stTextArea textarea:focus {
        border-color: #38BDF8;
        box-shadow: 0 0 0 1px #38BDF8;
    }

    .descansa-tag {
        display: inline-block;
        background-color: #334155;
        color: #94A3B8;
        padding: 2px 8px;
        border-radius: 4px;
        font-size: 0.8em;
        margin-left: 10px;
    }
</style>
""", unsafe_allow_html=True)

# --- DATOS POR DEFECTO ---
DEFAULT_DIVISIONS = {
    "ORO": [
        "Rulo FC", "Bailarinas Disfrazadas", "Curu Curu", "Maysak", 
        "Popper Rangers", "Gangshit", "Clubes 0", "Latinos", 
        "Cachorros", "3men2kbrones", "Basteros"
    ],
    "PLATA": [
        "Piernas Tiernas", "La Flaca FC", "MDK", "Castigos", 
        "Paraliticos FC", "HSG", "BrigadaAM", "RedCross Rangers", 
        "Birrareal", "Mandarina Ortopedica", "Tecno SJ"
    ],
    "BRONCE": [
        "Centollo FC", "Jagger de Munich", "Zona 0", "Los Golfos", 
        "Balmax FC", "Estrellas de Mahou FC", "Deportivo Cunaos", 
        "NautiCastle", "Rontevedra LK", "Inafuma Ibeben", "Bakalao"
    ]
}

# --- LÓGICA DEL ALGORITMO ---

def parse_teams(text_input):
    """Convierte el texto de entrada en una lista de equipos"""
    return [line.strip() for line in text_input.split('\n') if line.strip()]

def solve_division_schedule(div_name, teams, history_matches):
    """Genera el calendario para una división específica"""
    
    # 1. Generar todos los emparejamientos posibles
    all_possible_matches = []
    for i in range(len(teams)):
        for j in range(i + 1, len(teams)):
            all_possible_matches.append(tuple(sorted((teams[i], teams[j]))))
    
    # 2. Procesar partidos ya jugados
    played_matches = []
    pre_filled_rounds = {1: [], 2: []}
    
    # Validar que los equipos del historial existan
    valid_history = []
    for m in history_matches:
        t1, t2 = m
        if t1 in teams and t2 in teams:
            valid_history.append(tuple(sorted(m)))
    
    # Asignar a jornadas 1 y 2
    # Asumimos que los primeros 5 son J1 y los siguientes 5 son J2 (según lógica original)
    # Si hay más o menos, trataremos de adaptarnos, pero mantenemos la lógica original si es posible
    
    j1_matches = valid_history[:5]
    j2_matches = valid_history[5:10] if len(valid_history) >= 10 else []
    
    for m in j1_matches:
        pre_filled_rounds[1].append(m)
        if m in all_possible_matches: all_possible_matches.remove(m)
            
    for m in j2_matches:
        pre_filled_rounds[2].append(m)
        if m in all_possible_matches: all_possible_matches.remove(m)
            
    # Función auxiliar para descansar
    def get_resting_team(matches_in_round, all_teams_in_div):
        playing = set()
        for m in matches_in_round:
            playing.add(m[0])
            playing.add(m[1])
        resting = list(set(all_teams_in_div) - playing)
        return resting[0] if resting else "Error"

    # Solver recursivo
    def solve_rounds(current_round, remaining_matches):
        if current_round > 11:
            return {}
        
        available = list(remaining_matches)
        random.shuffle(available)
        
        def fill_round(matches_picked, pool_index):
            if len(matches_picked) == 5:
                return matches_picked
            
            for i in range(pool_index, len(available)):
                match = available[i]
                teams_playing = set(team for m in matches_picked for team in m)
                if match[0] not in teams_playing and match[1] not in teams_playing:
                    res = fill_round(matches_picked + [match], i + 1)
                    if res: return res
            return None

        round_matches = fill_round([], 0)
        
        if round_matches:
            new_remaining = [m for m in remaining_matches if m not in round_matches]
            future_rounds = solve_rounds(current_round + 1, new_remaining)
            if future_rounds is not None:
                future_rounds[current_round] = round_matches
                return future_rounds
        
        return None

    # Ejecutar solver con reintentos
    solution = None
    attempts = 0
    max_attempts = 1500  # Aumentado para robustez
    
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    while solution is None and attempts < max_attempts:
        if attempts % 100 == 0:
            status_text.text(f"Calculando {div_name}... Intento {attempts}")
            progress_bar.progress(min(attempts / 500, 1.0))
            
        solution = solve_rounds(3, all_possible_matches)
        attempts += 1
    
    progress_bar.empty()
    status_text.empty()
    
    if not solution:
        return None, f"No se pudo encontrar solución para {div_name} tras {max_attempts} intentos."

    final_schedule = pre_filled_rounds
    final_schedule.update(solution)
    
    # Formatear resultado
    result_data = []
    
    for r in range(1, 12):
        if r in final_schedule:
            matches = final_schedule[r]
            rest_team = get_resting_team(matches, teams)
            result_data.append({
                "jornada": r,
                "matches": matches,
                "descansa": rest_team
            })
            
    return result_data, None

# --- UI PRINCIPAL ---

st.title("⚽ Generador de Calendario de Ligas")
st.markdown("Genera automáticamente los emparejamientos para tus divisiones asegurando que todos jueguen contra todos y descansen una vez.")

with st.sidebar:
    st.header("⚙️ Configuración")
    st.info("Edita los equipos de cada división abajo. Un equipo por línea.")
    
    teams_oro = st.text_area("🏆 División ORO", value="\n".join(DEFAULT_DIVISIONS["ORO"]), height=200)
    teams_plata = st.text_area("🥈 División PLATA", value="\n".join(DEFAULT_DIVISIONS["PLATA"]), height=200)
    teams_bronce = st.text_area("🥉 División BRONCE", value="\n".join(DEFAULT_DIVISIONS["BRONCE"]), height=200)

# Botón principal
if st.button("🚀 Generar Calendario Completo", use_container_width=True):
    
    # Historial Hardcoded (Igual que en script original, pero podría hacerse editable si se prefiere)
    # Por simplicidad mantenemos el historial fijo, ya que es extenso de copiar/pegar en UI
    # Si el usuario cambia los nombres de equipos, esto podría fallar si no coiniciden.
    # En una versión avanzada, haríamos selectores dinámicos.
    
    HISTORY = {
        "ORO": [
            ("Bailarinas Disfrazadas", "Curu Curu"), ("Maysak", "Popper Rangers"),
            ("Gangshit", "Clubes 0"), ("Latinos", "Cachorros"), ("3men2kbrones", "Basteros"),
            ("Rulo FC", "Curu Curu"), ("Bailarinas Disfrazadas", "Cachorros"),
            ("Maysak", "Basteros"), ("Gangshit", "3men2kbrones"), ("Latinos", "Clubes 0")
        ],
        "PLATA": [
            ("La Flaca FC", "MDK"), ("Castigos", "Paraliticos FC"), ("HSG", "BrigadaAM"),
            ("RedCross Rangers", "Birrareal"), ("Mandarina Ortopedica", "Tecno SJ"),
            ("Piernas Tiernas", "MDK"), ("La Flaca FC", "BrigadaAM"),
            ("Castigos", "Birrareal"), ("HSG", "Mandarina Ortopedica"), ("RedCross Rangers", "Tecno SJ")
        ],
        "BRONCE": [
            ("Jagger de Munich", "Zona 0"), ("Los Golfos", "Balmax FC"),
            ("Estrellas de Mahou FC", "Deportivo Cunaos"), ("NautiCastle", "Rontevedra LK"),
            ("Inafuma Ibeben", "Bakalao"),
            ("Centollo FC", "Deportivo Cunaos"), ("Inafuma Ibeben", "Estrellas de Mahou FC"),
            ("Rontevedra LK", "Zona 0"), ("NautiCastle", "Jagger de Munich"), ("Balmax FC", "Bakalao")
        ]
    }
    
    divisions_input = {
        "ORO": parse_teams(teams_oro),
        "PLATA": parse_teams(teams_plata),
        "BRONCE": parse_teams(teams_bronce)
    }

    tabs = st.tabs(["🏆 ORO", "🥈 PLATA", "🥉 BRONCE"])
    
    for i, (div_name, tab) in enumerate(zip(["ORO", "PLATA", "BRONCE"], tabs)):
        with tab:
            teams = divisions_input[div_name]
            
            # Validación básica
            if len(teams) != 11:
                st.warning(f"⚠️ La división {div_name} tiene {len(teams)} equipos. Se recomiendan 11 para este algoritmo.")
            
            with st.spinner(f"Generando calendario para {div_name}..."):
                schedule, error = solve_division_schedule(div_name, teams, HISTORY.get(div_name, []))
            
            if error:
                st.error(error)
            else:
                st.success(f"✅ Calendario generado exitosamente para {div_name}")
                
                # Renderizar resultados en Grid
                col1, col2 = st.columns(2)
                
                for idx, jornada in enumerate(schedule):
                    target_col = col1 if idx % 2 == 0 else col2
                    
                    with target_col:
                        with st.container():
                            st.markdown(f"""
                            <div class="jornada-card">
                                <h3>Jornada {jornada['jornada']} <span class="descansa-tag">💤 Descansa: {jornada['descansa']}</span></h3>
                            """, unsafe_allow_html=True)
                            
                            for m in jornada['matches']:
                                st.markdown(f"""
                                <div class="match-row">
                                    <span class="team-name">{m[0]}</span>
                                    <span class="vs-badge">VS</span>
                                    <span class="team-name">{m[1]}</span>
                                </div>
                                """, unsafe_allow_html=True)
                            
                            st.markdown("</div>", unsafe_allow_html=True)

else:
    st.info("👈 Edita los equipos en el menú lateral y presiona 'Generar Calendario' para comenzar.")
