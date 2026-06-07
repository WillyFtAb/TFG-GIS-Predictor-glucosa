import pandas as pd
import numpy as np
import json

def juntar_datos(r_json, r_xlsx, n=20):
    with open(r_json, 'r') as f:
        data = json.load(f)

    diccionario_pacientes = {}

    for i in range(n):
        # 1. Carga de datos
        pac_n = pd.read_excel(r_xlsx, header=0, sheet_name=i)
        
        gluc = pac_n.iloc[:, [0, 9]].copy()
        gluc.columns = ['t_min', 'glu_mmol']
        gluc['gluc_mg'] = (gluc['glu_mmol'] * 18).round(0)

        # Inicializar columnas en 0
        columnas_eventos = ['meal_carb', 'snack_carb', 'bolus_insulin', 'basal_insulin', 'running_speed']
        for col in columnas_eventos:
            gluc[col] = 0.0

        # --- Extracción de datos del JSON ---
        paciente_idx = i
        
        # Comidas, snacks y bolos (Eventos puntuales)
        comidas_mag = data['inputs']['meal_carb']['magnitude'][paciente_idx]
        comidas_time = np.round(data['inputs']['meal_carb']['start_time'][paciente_idx]).astype(int)
        
        snacks_mag = data['inputs']['snack_carb']['magnitude'][paciente_idx]
        snacks_time = np.round(data['inputs']['snack_carb']['start_time'][paciente_idx]).astype(int)

        bolos_mag = data['inputs']['bolus_insulin']['magnitude'][paciente_idx]
        bolos_time = np.round(data['inputs']['bolus_insulin']['start_time'][paciente_idx]).astype(int)

        # Basal
        basal_mag = data['inputs']['basal_insulin']['magnitude'][paciente_idx]
        basal_time = list(range(0, 43200, 1440))

        # Ejercicio (Evento con duración)
        ejercicio_mag = data['inputs']['running_speed']['magnitude'][paciente_idx]
        ejercicio_time = np.round(data['inputs']['running_speed']['start_time'][paciente_idx]).astype(int)

        # --- Mapeo de Eventos ---

        # Función para eventos de un solo punto (comidas, snacks, bolos)
        def mapear_puntual(df, tiempos, magnitudes, columna):
            mapping = dict(zip(tiempos, magnitudes))
            # Usamos update para no perder los ceros en las filas que no coinciden
            df[columna] = df['t_min'].map(mapping).fillna(df[columna])

        mapear_puntual(gluc, comidas_time, comidas_mag, 'meal_carb')
        mapear_puntual(gluc, snacks_time, snacks_mag, 'snack_carb')
        mapear_puntual(gluc, bolos_time, bolos_mag, 'bolus_insulin')

        # Lógica especial para Basal
        for t in basal_time:
            gluc.loc[gluc['t_min'] == t, 'basal_insulin'] = basal_mag[0] * 24

        # Lógica para el ejericicio
        for t_start, mag in zip(ejercicio_time, ejercicio_mag):
            # Marcamos las filas donde t_min esté entre t_start y t_start + 29
            # (Suponiendo que cada fila es 1 minuto, esto cubre 30 filas/minutos)
            gluc.loc[(gluc['t_min'] >= t_start) & (gluc['t_min'] < t_start + 30), 'running_speed'] = mag

        diccionario_pacientes[f"p_{i}"] = gluc

    return diccionario_pacientes

import pickle

if __name__ == "__main__":
    for i in range(1,7):
        r_json = f'../py-mgipsim-main/SimulationResults/Simulacion_{i}/simulation_settings.json'
        r_xlsx =f'../py-mgipsim-main/SimulationResults/Simulacion_{i}/model_state_results.xlsx'

        print('Empezando: ', i)
        diccionario_pacientes = juntar_datos(r_json= r_json, r_xlsx= r_xlsx)
        print('Diccionario ', i, 'creado' )

        # Nombre del archivo donde guardaremos todo
        nombre_archivo = f"../Simulaciones/sim_{i}_data.pkl"

        with open(nombre_archivo, 'wb') as f:
            pickle.dump(diccionario_pacientes, f)
        print('Pickle ', i, 'creado' )
