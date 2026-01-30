import random
import copy

def solve_schedule():
    # Datos de los equipos por division
    divisions = {
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

    # Partidos ya jugados (J1 y J2) para forzar en el calendario
    # Formato: (Equipo1, Equipo2)
    history = {
        "ORO": [
            # J1
            ("Bailarinas Disfrazadas", "Curu Curu"), ("Maysak", "Popper Rangers"),
            ("Gangshit", "Clubes 0"), ("Latinos", "Cachorros"), ("3men2kbrones", "Basteros"),
            # J2
            ("Rulo FC", "Curu Curu"), ("Bailarinas Disfrazadas", "Cachorros"),
            ("Maysak", "Basteros"), ("Gangshit", "3men2kbrones"), ("Latinos", "Clubes 0")
        ],
        "PLATA": [
            # J1
            ("La Flaca FC", "MDK"), ("Castigos", "Paraliticos FC"), ("HSG", "BrigadaAM"),
            ("RedCross Rangers", "Birrareal"), ("Mandarina Ortopedica", "Tecno SJ"),
            # J2
            ("Piernas Tiernas", "MDK"), ("La Flaca FC", "BrigadaAM"),
            ("Castigos", "Birrareal"), ("HSG", "Mandarina Ortopedica"), ("RedCross Rangers", "Tecno SJ")
        ],
        "BRONCE": [
            # J1
            ("Jagger de Munich", "Zona 0"), ("Los Golfos", "Balmax FC"),
            ("Estrellas de Mahou FC", "Deportivo Cunaos"), ("NautiCastle", "Rontevedra LK"),
            ("Inafuma Ibeben", "Bakalao"),
            # J2
            ("Centollo FC", "Deportivo Cunaos"), ("Inafuma Ibeben", "Estrellas de Mahou FC"),
            ("Rontevedra LK", "Zona 0"), ("NautiCastle", "Jagger de Munich"), ("Balmax FC", "Bakalao")
        ]
    }

    full_schedule_output = ""

    for div_name, teams in divisions.items():
        # 1. Generar todos los emparejamientos posibles (sin duplicados A vs B == B vs A)
        all_possible_matches = []
        for i in range(len(teams)):
            for j in range(i + 1, len(teams)):
                all_possible_matches.append(tuple(sorted((teams[i], teams[j]))))
        
        # 2. Identificar partidos ya jugados y eliminarlos del pool disponible
        played_matches = []
        pre_filled_rounds = {1: [], 2: []}
        
        # Cargar historia J1
        for i in range(5):
            m = tuple(sorted(history[div_name][i]))
            played_matches.append(m)
            pre_filled_rounds[1].append(m)
            if m in all_possible_matches:
                all_possible_matches.remove(m)

        # Cargar historia J2
        for i in range(5, 10):
            m = tuple(sorted(history[div_name][i]))
            played_matches.append(m)
            pre_filled_rounds[2].append(m)
            if m in all_possible_matches:
                all_possible_matches.remove(m)

        # 3. Funcion recursiva para encontrar las jornadas 3 a 11
        final_schedule = {}

        def get_resting_team(matches_in_round, all_teams_in_div):
            playing = set()
            for m in matches_in_round:
                playing.add(m[0])
                playing.add(m[1])
            resting = list(set(all_teams_in_div) - playing)
            return resting[0] if resting else "Error"

        def solve_rounds(current_round, remaining_matches):
            if current_round > 11:
                return {} # Base case: solution found
            
            # Intentar encontrar 5 partidos compatibles
            # Heuristica: Aleatoriedad para evitar patrones repetitivos que lleven a callejon sin salida
            available = list(remaining_matches)
            random.shuffle(available)
            
            # Algoritmo simple de backtracking para llenar UNA jornada
            def fill_round(matches_picked, pool_index):
                if len(matches_picked) == 5:
                    return matches_picked
                
                for i in range(pool_index, len(available)):
                    match = available[i]
                    # Verificar si los equipos ya juegan en esta jornada
                    teams_playing = set(team for m in matches_picked for team in m)
                    if match[0] not in teams_playing and match[1] not in teams_playing:
                        res = fill_round(matches_picked + [match], i + 1)
                        if res:
                            return res
                return None

            round_matches = fill_round([], 0)
            
            if round_matches:
                # Si logramos llenar la jornada, avanzamos a la siguiente
                new_remaining = [m for m in remaining_matches if m not in round_matches]
                future_rounds = solve_rounds(current_round + 1, new_remaining)
                if future_rounds is not None:
                    future_rounds[current_round] = round_matches
                    return future_rounds
            
            return None # Backtrack

        # Ejecutar solver (puede requerir un par de intentos por la aleatoriedad, pero con N=11 es rapido)
        solution = None
        attempts = 0
        while solution is None and attempts < 1000:
            solution = solve_rounds(3, all_possible_matches)
            attempts += 1
        
        if not solution:
            full_schedule_output += f"Error: No se pudo generar calendario para {div_name}\n"
            continue

        # Combinar J1, J2 y la solucion
        final_schedule = pre_filled_rounds
        final_schedule.update(solution)

        # Generar texto de salida
        full_schedule_output += f"\n## DIVISION {div_name}\n\n"
        
        # Validacion de conteo
        team_counts = {t: 0 for t in teams}
        
        for r in range(1, 12):
            matches = final_schedule[r]
            rest_team = get_resting_team(matches, teams)
            full_schedule_output += f"**JORNADA {r}** (Descansa: {rest_team})\n"
            for m in matches:
                full_schedule_output += f"* {m[0]} vs {m[1]}\n"
                team_counts[m[0]] += 1
                team_counts[m[1]] += 1
            full_schedule_output += "\n"

        # Validacion final
        full_schedule_output += f"**Validacion {div_name}:**\n"
        errors = False
        for t, c in team_counts.items():
            if c != 10:
                full_schedule_output += f"- ERROR: {t} juega {c} partidos.\n"
                errors = True
        if not errors:
            full_schedule_output += "- OK: Todos los equipos juegan 10 partidos.\n"
        full_schedule_output += "---\n"

    print(full_schedule_output)

if __name__ == "__main__":
    solve_schedule()