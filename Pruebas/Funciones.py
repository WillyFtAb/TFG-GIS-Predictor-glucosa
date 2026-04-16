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
            # Copia los valores de la celda y ajusta el nuevo valor de tiempo
            df_copy.loc[idx_nuevo] = df_copy.loc[idx_orig]
            df_copy.loc[idx_nuevo, 't_min'] = round(df_copy.loc[idx_orig,'t_min']/t_muestreo)*t_muestreo
            
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

    df = df.reset_index(drop = True)
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