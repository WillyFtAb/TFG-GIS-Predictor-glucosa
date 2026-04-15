import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler, StandardScaler

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
            # Copy the nearest row as base (preserves blood_glucose, t_min, etc.)
            df_copy.loc[idx_nuevo] = df_copy.loc[idx_orig]
            
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