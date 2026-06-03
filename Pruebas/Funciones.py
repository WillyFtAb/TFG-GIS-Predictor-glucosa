import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler, StandardScaler
import pandas as pd
import json
from pathlib import Path
from matplotlib import pyplot as plt

# =============================================
# FUNCIONES PARA NOTEBOOK VISUALIZACIÓN 
# DE DATOS GENERADOS POR EL SIMULADOR
# =============================================
def visualizacion_paciente(dias = None):  
    esc = int(input('Número de escenario (1-6)'))
    pac = int(input('Número de paciente (0-19)'))

    r_json = f'../py-mgipsim-main/SimulationResults/Simulacion_{esc}/simulation_settings.json'
    r_xlsx = f'../py-mgipsim-main/SimulationResults/Simulacion_{esc}/model_state_results.xlsx'
    
    with open(r_json, 'r') as f:
        data = json.load(f)

    pac_n = pd.read_excel(r_xlsx, header=0, sheet_name=pac)

    if dias is not None:
        min = dias*24*60
        comidas_time = list(filter(lambda x: int(x < min), data['inputs']['meal_carb']['start_time'][pac]))
        limite = len(comidas_time)
        comidas_mag = data['inputs']['meal_carb']['magnitude'][pac][:limite]
        
        gluc = pac_n.iloc[:min,[0,9]].copy()
        gluc.columns = ['t_min','glu_mmol']
        gluc['gluc_mg'] = round(gluc.glu_mmol*18,0).copy()

    else:
        comidas_mag = data['inputs']['meal_carb']['magnitude'][pac]
        comidas_time = np.round(data['inputs']['meal_carb']['start_time'][pac]).astype(int)  

        gluc = pac_n.iloc[:,[0,9]].copy()
        gluc.columns = ['t_min','glu_mmol']
        gluc['gluc_mg'] = round(gluc.glu_mmol*18,0).copy()
        
    fig, ax1 = plt.subplots(figsize=(12, 5))

    # Gráfica de Glucosa (Eje inferior e izquierdo)
    linea_gluc = ax1.plot(gluc.t_min, gluc.gluc_mg, label='Glucosa', color='blue', linewidth=0.5)
    ax1.set_xlabel('Tiempo (minutos)', fontsize=12)
    ax1.set_ylabel('Glucosa (mg/dL)', fontsize=12)

    # Franjas de rango objetivo en el eje de la glucosa
    ax1.axhspan(70, 180, color='green', alpha=0.2, label='Rango Objetivo')
    ax1.axhline(70, color='red', linestyle='--', linewidth=1, label='Hipoglucemia')
    ax1.axhline(180, color='orange', linestyle='--', linewidth=1, label='Hiperglucemia')

    # Crear el segundo sistema de ejes independientes (Comidas)
    # twinx() comparte el eje X (tiempo) y crea un eje Y independiente a la derecha
    ax2 = ax1.twinx()

    # Gráfica de Comidas (Eje derecho)
    linea_comidas = ax2.plot(comidas_time, comidas_mag, marker='o', linewidth=0.5, 
                            alpha=0.8, color='purple', label='Comidas principales')
    ax2.set_ylabel('Carbohidratos comida (g)', fontsize=12, color='purple')
    
    # Buscamos el valor máximo de carbohidratos (comidas)
    max_carb = max(comidas_mag) if len(comidas_mag) > 0 else 100
    # Al hacer que el límite superior del eje Y sea el DOBLE, la serie se queda en la mitad inferior
    ax2.set_ylim(0, max_carb * 2) 


    # 4. Configurar diseño general y leyendas combinadas
    plt.title(f'Escenario {esc} - Paciente {pac}', fontsize=14, pad=20)
    ax1.grid(True, linestyle=':', alpha=0.7)

    # Combinar las etiquetas de ambos ejes en una sola leyenda limpia
    lineas, etiquetas = ax1.get_legend_handles_labels()
    lineas2, etiquetas2 = ax2.get_legend_handles_labels()
    ax1.legend(lineas + lineas2, etiquetas + etiquetas2, loc='lower right', fontsize='small')

    plt.tight_layout()
    plt.show()


def analisis(r_json,r_xlsx, esc = '_', n =20, guardar = True, carpeta = None):

    if carpeta is None:
        carpeta = Path('Series_glucosa/')
        carpeta.mkdir(exist_ok=True)

    with open(r_json, 'r') as f:
            data = json.load(f)

    for i in range(n):      

        # Elegimos el Paciente
        paciente_idx = i

        # Extraer magnitud y tiempo de las comidas principales
        comidas_mag = data['inputs']['meal_carb']['magnitude'][paciente_idx]
        comidas_time = np.round(data['inputs']['meal_carb']['start_time'][paciente_idx]).astype(int)
        
        # ===== COMENTEADO PARA GRÁFICA MÁS SENCILLA =================
        # Extraer magnitud y tiempo de las comidas principales 
        # snacks_mag = data['inputs']['snack_carb']['magnitude'][paciente_idx]
        # snacks_time = np.round(data['inputs']['snack_carb']['start_time'][paciente_idx]).astype(int)

        # # Extraer magnitud y tiempo de los bolos de insulina
        # bolos_mag = data['inputs']['bolus_insulin']['magnitude'][paciente_idx]
        # bolos_time = np.round(data['inputs']['bolus_insulin']['start_time'][paciente_idx]).astype(int)

        # # Extraer magnitud y tiempo de la basal 
        # basal_mag = data['inputs']['basal_insulin']['magnitude'][paciente_idx]


        # Cargar datos del excel (medidas glucosa)
        pac_n = pd.read_excel(r_xlsx, header=0, sheet_name=i)
        
        # Selección de datos (t y gluc)
        gluc = pac_n.iloc[:,[0,9]].copy()
        gluc.columns = ['t_min','glu_mmol']
        gluc['gluc_mg'] = round(gluc.glu_mmol*18,0).copy()
        
        fig, ax1 = plt.subplots(figsize=(12, 5))

        # Gráfica de Glucosa (Eje inferior e izquierdo)
        linea_gluc = ax1.plot(gluc.t_min, gluc.gluc_mg, label='Glucosa', color='blue', linewidth=0.5)
        ax1.set_xlabel('Tiempo (minutos)', fontsize=12)
        ax1.set_ylabel('Glucosa (mg/dL)', fontsize=12)

        # Franjas de rango objetivo en el eje de la glucosa
        ax1.axhspan(70, 180, color='green', alpha=0.2, label='Rango Objetivo')
        ax1.axhline(70, color='red', linestyle='--', linewidth=1, label='Hipoglucemia')
        ax1.axhline(180, color='orange', linestyle='--', linewidth=1, label='Hiperglucemia')

        # Crear el segundo sistema de ejes independientes (Comidas)
        # twinx() comparte el eje X (tiempo) y crea un eje Y independiente a la derecha
        ax2 = ax1.twinx()

        # Gráfica de Comidas (Eje derecho)
        linea_comidas = ax2.plot(comidas_time, comidas_mag, marker='o', linewidth=0.5, 
                                alpha=0.8, color='purple', label='Comidas principales')
        ax2.set_ylabel('Carbohidratos comida (g)', fontsize=12, color='purple')
        
        # Buscamos el valor máximo de carbohidratos (comidas)
        max_carb = max(comidas_mag) if len(comidas_mag) > 0 else 100
        # Al hacer que el límite superior del eje Y sea el DOBLE, la serie se queda en la mitad inferior
        ax2.set_ylim(0, max_carb * 2) 


        # 4. Configurar diseño general y leyendas combinadas
        plt.title(f'Escenario {esc} - Paciente {i}', fontsize=14, pad=20)
        ax1.grid(True, linestyle=':', alpha=0.7)

        # Combinar las etiquetas de ambos ejes en una sola leyenda limpia
        lineas, etiquetas = ax1.get_legend_handles_labels()
        lineas2, etiquetas2 = ax2.get_legend_handles_labels()
        ax1.legend(lineas + lineas2, etiquetas + etiquetas2, loc='lower right', fontsize='small')

        plt.tight_layout()
        if guardar:
            nombre_archivo = f'Escenario{esc}_Paciente_{i}.png' 
            plt.savefig(carpeta / nombre_archivo, dpi=300)
        plt.show()



# =============================
# FUNCIONES NOTEBOOK PIPELINE
# =============================




def remuestrear(df, columnas, t_muestreo: int):
    """
    Desplaza valores de múltiples columnas hacia sus múltiplos de t_muestreo
    más cercanos y elimina las posiciones originales.
    """
    df_copy = df.copy()
    
    # 1. Identificar índices que no son múltiplos
    mascara_desalineados = (df_copy.index % t_muestreo != 0)
    indices_originales = df_copy.index[mascara_desalineados]
    
    # 2. Calcular nuevos índices para todos los desalineados a la vez
    indices_nuevos = (np.round(indices_originales / t_muestreo) * t_muestreo).astype(int)

    for idx_orig, idx_nuevo in zip(indices_originales, indices_nuevos):
        # Asegurar que el índice destino existe
        if idx_nuevo not in df_copy.index:
            # Copia los valores de la celda y ajusta el nuevo valor de tiempo
            df_copy.loc[idx_nuevo] = df_copy.loc[idx_orig]
            df_copy.loc[idx_nuevo, 't_min'] = round(df_copy.loc[idx_orig,'t_min']/t_muestreo)*t_muestreo
        
        else: 
            # Mover valores para todas las columnas especificadas
            for col in columnas:
                valor = df_copy.at[idx_orig, col]
                if valor != 0:
                    df_copy.at[idx_nuevo, col] += valor
                    df_copy.at[idx_orig, col] = 0
    
    # 3. Se queda con los indices de interes

    df_limpio = df_copy[df_copy.index % t_muestreo == 0]
                
    return df_limpio

def escalar(df, columnas = ['gluc_mg', 'glu_mmol', 'meal_carb', 'snack_carb', 'bolus_insulin', 'basal_insulin','running_speed' ]):
    df_resultado = df.copy()
    scaler = MinMaxScaler()
    df_resultado[columnas] = scaler.fit_transform(df_resultado[columnas])
    return df_resultado

def estandarizar(df, columnas = ['gluc_mg', 'glu_mmol', 'meal_carb', 'snack_carb', 'bolus_insulin', 'basal_insulin','running_speed' ]):
    df_resultado = df.copy()
    scaler = StandardScaler()
    df_resultado[columnas] = scaler.fit_transform(df_resultado[columnas])
    return df_resultado

def estadisticas_rango(df, nombre_col = 'gluc_mg', lim = [0, 70, 181, 700], n_rang = ['TBR','TIR','TAR']):
    est =pd.DataFrame()
    columna = nombre_col

    # Definir los límites de los rangos (bins)
    # Esto creará los rangos por defecto: (0-70], (70-181], (181-700]
    limites = lim

    # Definir etiquetas
    nombres_rangos = n_rang

    # Clasificar los valores de la columna en los rangos usando pd.cut()
    est['Tiempo_en_rango'] = pd.cut(df[columna], bins=limites, labels=nombres_rangos)

    # Calcular el porcentaje
    porcentajes = est['Tiempo_en_rango'].value_counts(normalize=True) * 100

    porcentajes_dic = {'TIR':[round(porcentajes['TIR'],2)],
                      'TAR':[round(porcentajes['TAR'],2)],
                      'TBR':[round(porcentajes['TBR'],2)]}
    return porcentajes_dic

def crear_features (df: pd.DataFrame):
    """
    Añade características exógenas retardadas al DataFrame y devuelve
    la serie objetivo (y) y el DataFrame con variables exógenas (exog) por separado.

    Para cada variable en EXOG_VARS (excepto insulina basal), añadimos su valor acumulado cada 20 min hasta t-240 min. 
    como columnas separadas. 
    Esto proporciona al modelo información explícita sobre lo ocurrido en las últimas 4 horas con una
    resolución de 20 minutos.

    Se descartan los primeros 240 minutos de filas porque sus columnas de retardo
    contendrían NaN (no hay suficiente historial).

    Parámetros
    ----------
    df: pd.DataFrame
        DataFrame preparado a una frecuencia de 5 minutos.

    Devuelve
    -------
    y: pd.Series
        Serie objetivo de glucosa en sangre.
    exog: pd.DataFrame
        Todas las características exógenas, incluidas las columnas rezagadas.

    """
    df = df.copy()
    df['basal_-24h'] = df['basal_insulin'].rolling(window=287, closed='left', min_periods = 0).sum()

    for col in ['meal_carb', 'snack_carb', 'bolus_insulin', 'running_speed']:

        df[f'{col}_-20m'] = df[col].rolling(window=4, closed='left').sum()
        df[f'{col}_-40m'] = df[col].rolling(window=8, closed='left').sum() - df[col].rolling(window=4, closed='left').sum()
        df[f'{col}_-60m'] = df[col].rolling(window=12, closed='left').sum() - df[col].rolling(window=8, closed='left').sum()
        df[f'{col}_-80m'] = df[col].rolling(window=16, closed='left').sum() - df[col].rolling(window=12, closed='left').sum()
        df[f'{col}_-100m'] = df[col].rolling(window=20, closed='left').sum() - df[col].rolling(window=16, closed='left').sum()
        df[f'{col}_-120m'] = df[col].rolling(window=24, closed='left').sum() - df[col].rolling(window=20, closed='left').sum()
        df[f'{col}_-140m'] = df[col].rolling(window=28, closed='left').sum() - df[col].rolling(window=24, closed='left').sum()
        df[f'{col}_-160m'] = df[col].rolling(window=32, closed='left').sum() - df[col].rolling(window=28, closed='left').sum()
        df[f'{col}_-180m'] = df[col].rolling(window=36, closed='left').sum() - df[col].rolling(window=32, closed='left').sum()
        df[f'{col}_-200m'] = df[col].rolling(window=40, closed='left').sum() - df[col].rolling(window=36, closed='left').sum()
        df[f'{col}_-220m'] = df[col].rolling(window=44, closed='left').sum() - df[col].rolling(window=40, closed='left').sum()
        df[f'{col}_-240m'] = df[col].rolling(window=48, closed='left').sum() - df[col].rolling(window=44, closed='left').sum()

    df = df.dropna()

    return df['gluc_mg'], df.drop(columns=['gluc_mg'])

def indexar_temp(df: pd.DataFrame, start:str = '2026-01-01'):
    """
    Convierte una columna de tiempo relativo en un DatetimeIndex y remuestrea el DataFrame.

    Esta función toma un DataFrame con una columna 't_min' (minutos transcurridos), 
    genera una estampa de tiempo absoluta sumando esos minutos a una fecha de inicio, 
    y establece dicha estampa como el nuevo índice con una frecuencia de 5 minutos.

    Parámetros
    ----------
        df (pd.DataFrame): El DataFrame original que debe contener la columna 't_min'.
        start (str, opcional): Fecha de inicio en formato 'YYYY-MM-DD'. 
            Por defecto es '2026-01-01'.

    Devuelve
    --------
        pd.DataFrame: Una copia del DataFrame original con:
            - Un DatetimeIndex basado en el tiempo transcurrido.
            - Frecuencia fija de 5 minutos ("5min").
            - La columna 't_min' eliminada.
    """
    df = df.copy()
    df.index = pd.to_datetime(start) + pd.to_timedelta(df['t_min'], unit='min')
    df = df.drop(columns=['t_min'])
    df = df.asfreq("5min")

    return df