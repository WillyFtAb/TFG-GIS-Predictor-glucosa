from matplotlib.lines import Line2D
import pandas as pd
import numpy as np
from scipy import stats
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


def analisis(r_json,r_xlsx, esc = '_', n =20, guardar = True, carpeta = None, pos_ley = 'lower right'):

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
        ax1.legend(lineas + lineas2, etiquetas + etiquetas2, loc= pos_ley, fontsize='small')

        plt.tight_layout()
        if guardar:
            nombre_archivo = f'Escenario{esc}_Paciente_{i}.png' 
            plt.savefig(carpeta / nombre_archivo, dpi=300)
        plt.show()



# =============================
# FUNCIONES NOTEBOOK PIPELINE
# exceptuando auxiliares a XGboost y Arimax
# (en el propio cuaderno)
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

def normalidad(s, datos, nombre):
    """
    Comprueba la normalidad de los datos mediante el test de Shapiro.
    Imprime los resultados por pantalla (Rechazo o aceptación de H0).

    Parámetros
    ----------
    s: identificador de simulación/escenario
    datos: pd.Series
        datos sobre los que ejecutar el test de normalidad
    nombre: str
        nombre de la variable a comprobar

    
    """

    from scipy import stats
    # datos = estadisticas[estadisticas['Simulacion']==s][dato]
    shapiro_test, p_valor = stats.shapiro(datos)
    print(f'Simulación {s}: test:{shapiro_test.round(2)}  p_valor:{p_valor.round(4)}')
    if p_valor<0.05:
        print(f'\t H0 rechazada: {nombre} NO es normal')
    else:
        print(f'\t H0 aceptada: {nombre} SÍ es normal')



# ======================================================================
# GRÁFICAS
# =======================================================================
COLORES = {
    "XGBoost": "#378ADD",
    "ARIMAX":  "#EF9F27",
}

# Etiquetas corregidas
ETIQUETAS_SIM = {
    1: r"E1" + "\n" + r"HC$^-$ Ej$_0$ Err$_0$",
    2: r"E2" + "\n" + r"HC$^+$ Ej$_0$ Err$_0$",
    3: r"E3" + "\n" + r"HC$^-$ Ej$^+$ Err$_0$",
    4: r"E4" + "\n" + r"HC$^-$ Ej$_0$ Err$^+$",
    5: r"E5" + "\n" + r"HC$^+$ Ej$_0$ Err$^+$",
    6: r"E6" + "\n" + r"HC$^-$ Ej$^+$ Err$^+$",

}

ETIQUETAS_SIM_LARGA = {
    1: "E1  HC poco variable  Sin ejercicio  0% error",
    2: "E2  HC muy variable  Sin ejercicio  0% error",
    3: "E3  HC poco variable  Con ejercicio  0% error",
    4: "E4  HC poco variable  Sin ejercicio  10% error",
    5: "E5  HC muy variable  Sin ejercicio  10% error",
    6: "E6  HC poco variable  Con ejercicio  10% error",
}

# ── Preparación de datos ──────────────────────────────────────────────────────

def preparar_datos(df_res, df_tir):
    df = df_res.copy()
    df['horizonte_num'] = df['horizonte'].str.replace('min', '').astype(int)
    df['pct_B'] = df['pct_AB'] - df['pct_A']

    tir = df_tir.rename(columns={'Simulacion': 'simulacion', 'Paciente': 'paciente'})
    df = df.merge(tir, on=['simulacion', 'paciente'], how='left')
    return df


def agregar(df):
    return (
        df.groupby(["modelo", "horizonte_num", "simulacion"])
        [["MAE", "RMSE", "pct_A", "pct_B", "pct_DE"]]
        .agg(["mean", "std"])
        .reset_index()
    )


# ══════════════════════════════════════════════════════════════════════════════
# GRÁFICA 1 — Barras agrupadas MAE por simulación
# Objetivo: comparación directa entre modelos en cada condición experimental
# ══════════════════════════════════════════════════════════════════════════════

def grafica_barras_mae(df, guardar=False, ruta='grafica1_barras_mae.png'):
    agg = agregar(df)
    sims = sorted(df['simulacion'].unique())
    modelos = ['XGBoost', 'ARIMAX']
    x = np.arange(len(sims))
    ancho = 0.35

    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    fig.suptitle("MAE por simulación — XGBoost vs ARIMAX", fontsize=13, fontweight='bold')

    for ax, h in zip(axes, [15, 30]):
        for i, modelo in enumerate(modelos):
            datos = agg[(agg['modelo'] == modelo) & (agg['horizonte_num'] == h)]
            datos = datos.set_index('simulacion').reindex(sims)
            medias  = datos[('MAE', 'mean')].values
            errores = datos[('MAE', 'std')].values
            offset  = (i - 0.5) * ancho
            bars = ax.bar(x + offset, medias, ancho, label=modelo,
                          color=COLORES[modelo], alpha=0.85,
                          yerr=errores, capsize=4,
                          error_kw={'linewidth': 1, 'alpha': 0.6})
            for bar, val in zip(bars, medias):
                ax.text(bar.get_x() + bar.get_width() / 2,
                        bar.get_height() + 0.002,
                        f"{val:.3f}", ha='center', va='bottom',
                        fontsize=7.5, color='0.3')

        ax.set_title(f"Horizonte {h} min", fontsize=11)
        ax.set_xticks(x)
        ax.set_xticklabels([ETIQUETAS_SIM[s] for s in sims], fontsize=7.5)
        ax.set_ylabel("MAE (mg/dL)")
        ax.legend(framealpha=0.5, fontsize=9)

    fig.tight_layout()
    if guardar:
        fig.savefig(ruta, bbox_inches='tight')
    return fig


# ══════════════════════════════════════════════════════════════════════════════
# GRÁFICA 2 — Barras agrupadas RMSE por simulación
# ══════════════════════════════════════════════════════════════════════════════

def grafica_barras_rmse(df, guardar=False, ruta='grafica2_barras_rmse.png'):
    agg = agregar(df)
    sims = sorted(df['simulacion'].unique())
    modelos = ['XGBoost', 'ARIMAX']
    x = np.arange(len(sims))
    ancho = 0.35

    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    fig.suptitle("RMSE por simulación — XGBoost vs ARIMAX", fontsize=13, fontweight='bold')

    for ax, h in zip(axes, [15, 30]):
        for i, modelo in enumerate(modelos):
            datos = agg[(agg['modelo'] == modelo) & (agg['horizonte_num'] == h)]
            datos = datos.set_index('simulacion').reindex(sims)
            medias  = datos[('RMSE', 'mean')].values
            errores = datos[('RMSE', 'std')].values
            offset  = (i - 0.5) * ancho
            bars = ax.bar(x + offset, medias, ancho, label=modelo,
                          color=COLORES[modelo], alpha=0.85,
                          yerr=errores, capsize=4,
                          error_kw={'linewidth': 1, 'alpha': 0.6})
            for bar, val in zip(bars, medias):
                ax.text(bar.get_x() + bar.get_width() / 2,
                        bar.get_height() + 0.002,
                        f"{val:.3f}", ha='center', va='bottom',
                        fontsize=7.5, color='0.3')

        ax.set_title(f"Horizonte {h} min", fontsize=11)
        ax.set_xticks(x)
        ax.set_xticklabels([ETIQUETAS_SIM[s] for s in sims], fontsize=7.5)
        ax.set_ylabel("RMSE (mg/dL)")
        ax.legend(framealpha=0.5, fontsize=9)

    fig.tight_layout()
    if guardar:
        fig.savefig(ruta, bbox_inches='tight')
    return fig


# ══════════════════════════════════════════════════════════════════════════════
# GRÁFICA 3 — Boxplot con puntos individuales y media
# Objetivo: distribución de errores entre pacientes por simulación
# ══════════════════════════════════════════════════════════════════════════════

def grafica_boxplot(df, metrica='MAE', guardar=False, ruta=None):
    if ruta is None:
        ruta = f'grafica3_boxplot_{metrica.lower()}.png'
    sims = sorted(df['simulacion'].unique())
    modelos = ['XGBoost', 'ARIMAX']
    x = np.arange(len(sims))
    ancho = 0.35

    fig, axes = plt.subplots(1, 2, figsize=(16, 7), sharey=False)
    fig.suptitle(
        f'Distribución de {metrica} por simulación y horizonte\n'
        f'Boxplot con observaciones individuales (n=20 pacientes)',
        fontsize=13, fontweight='bold'
    )

    for ax, h in zip(axes, [15, 30]):
        df_h = df[df['horizonte_num'] == h]
        for i, modelo in enumerate(modelos):
            data_per_sim = [
                df_h[(df_h['simulacion'] == s) & (df_h['modelo'] == modelo)][metrica].values
                for s in sims
            ]
            posiciones = x + (i - 0.5) * ancho

            bp = ax.boxplot(
                data_per_sim,
                positions=posiciones,
                widths=0.32,
                patch_artist=True,
                showfliers=False,
                boxprops=dict(facecolor=COLORES[modelo], alpha=0.5),
                medianprops=dict(color='black', linewidth=2),
                whiskerprops=dict(linewidth=1.2),
                capprops=dict(linewidth=1.2),
            )

            for pos, datos in zip(posiciones, data_per_sim):
                # Puntos individuales con jitter
                jitter = np.random.uniform(-0.08, 0.08, size=len(datos))
                ax.scatter(pos + jitter, datos,
                           color=COLORES[modelo], alpha=0.6, s=25, zorder=3)
                # Media como diamante
                ax.scatter(pos, np.mean(datos),
                           marker='D', color='white',
                           edgecolors=COLORES[modelo],
                           s=60, zorder=5, linewidths=1.5)

        ax.set_title(f'Horizonte {h} min', fontsize=11)
        ax.set_xticks(x)
        ax.set_xticklabels([ETIQUETAS_SIM[s] for s in sims], fontsize=7.5)
        ax.set_xlabel('Simulación', fontsize=11)
        ax.set_ylabel(f'{metrica} (mg/dL)', fontsize=11)
        ax.grid(axis='y', linestyle='--', alpha=0.3)

        legend_elements = [
            Line2D([0], [0], color=COLORES[m], lw=4, label=m) for m in modelos
        ] + [
            Line2D([0], [0], color='black', lw=2, label='Mediana'),
            Line2D([0], [0], marker='D', color='w',
                   markerfacecolor='gray', markeredgecolor='gray',
                   markersize=8, lw=0, label='Media'),
        ]
        ax.legend(handles=legend_elements, loc='upper right',
                  title='Modelos', fontsize=9)

    fig.tight_layout()
    if guardar:
        fig.savefig(ruta, bbox_inches='tight')
    return fig



# ══════════════════════════════════════════════════════════════════════════════
# GRÁFICA 5 — Degradación del error al aumentar el horizonte
# Objetivo: qué modelo mantiene mejor su precisión al ampliar el horizonte
# ══════════════════════════════════════════════════════════════════════════════

def grafica_degradacion(df, metrica='MAE', guardar=False, ruta=None):
    if ruta is None:
        ruta = f'grafica5_degradacion_{metrica.lower()}.png'
    agg = agregar(df)
    sims = sorted(df['simulacion'].unique())
    modelos = ['XGBoost', 'ARIMAX']
    x = np.arange(len(sims))
    ancho = 0.35
    estilos = {'XGBoost': '-o', 'ARIMAX': '--s'}

    fig, axes = plt.subplots(1, 2, figsize=(13, 5))
    fig.suptitle(
        f'Degradación del {metrica} al ampliar el horizonte de predicción',
        fontsize=13, fontweight='bold'
    )

    # Panel izquierdo: valores absolutos por horizonte
    ax = axes[0]
    for modelo in modelos:
        for sim in sims:
            subset = agg[(agg['modelo'] == modelo) & (agg['simulacion'] == sim)].sort_values('horizonte_num')
            ax.plot(subset['horizonte_num'].values,
                    subset[(metrica, 'mean')].values,
                    estilos[modelo], color=COLORES[modelo],
                    alpha=0.5, linewidth=1.2, markersize=5,
                    label=modelo if sim == sims[0] else '_')
    ax.set_title(f'{metrica} absoluto por horizonte', fontsize=11)
    ax.set_xticks([15, 30])
    ax.set_xlabel('Horizonte (min)')
    ax.set_ylabel(f'{metrica} (mg/dL)')
    ax.legend(framealpha=0.5, fontsize=9)

    # Panel derecho: ratio de degradación (valor_30 / valor_15)
    ax2 = axes[1]
    for i, modelo in enumerate(modelos):
        ratios = []
        for sim in sims:
            v15 = agg[(agg['modelo']==modelo)&(agg['horizonte_num']==15)&(agg['simulacion']==sim)][(metrica,'mean')].values[0]
            v30 = agg[(agg['modelo']==modelo)&(agg['horizonte_num']==30)&(agg['simulacion']==sim)][(metrica,'mean')].values[0]
            ratios.append(v30 / v15)
        offset = (i - 0.5) * ancho
        bars = ax2.bar(x + offset, ratios, ancho,
                       label=modelo, color=COLORES[modelo], alpha=0.85)
        for bar, val in zip(bars, ratios):
            ax2.text(bar.get_x() + bar.get_width() / 2,
                     bar.get_height() + 0.01,
                     f'×{val:.2f}', ha='center', va='bottom',
                     fontsize=8, color='0.3')

    ax2.axhline(1.0, color='0.4', linestyle='--', linewidth=1,
                label='Sin degradación (×1.0)')
    ax2.set_title(f'Ratio {metrica}₃₀ / {metrica}₁₅', fontsize=11)
    ax2.set_xticks(x)
    ax2.set_xticklabels([ETIQUETAS_SIM[s] for s in sims], fontsize=7.5)
    ax2.set_ylabel('Ratio (adimensional)')
    ax2.legend(framealpha=0.5, fontsize=9)

    fig.tight_layout()
    if guardar:
        fig.savefig(ruta, bbox_inches='tight')
    return fig


# ══════════════════════════════════════════════════════════════════════════════
# GRÁFICA 6 — Zonas Clarke: barras apiladas por simulación y modelo
# Objetivo: validez clínica de las predicciones
# ══════════════════════════════════════════════════════════════════════════════

def grafica_clarke(df, horizonte=15, guardar=False, ruta=None):
    if ruta is None:
        ruta = f'grafica6_clarke_{horizonte}min.png'
    sims = sorted(df['simulacion'].unique())
    modelos = ['XGBoost', 'ARIMAX']
    x = np.arange(len(sims))
    colores_zona = {'Zona A': '#378ADD', 'Zona B': '#85B7EB', 'Zona D/E': '#E24B4A'}

    agg2 = (df[df['horizonte_num'] == horizonte]
            .groupby(['modelo', 'simulacion'])[['pct_A', 'pct_B', 'pct_DE']]
            .mean().reset_index())

    fig, axes = plt.subplots(1, 2, figsize=(13, 5), sharey=True)
    fig.suptitle(
        f'Distribución zonas Clarke error grid — horizonte {horizonte} min',
        fontsize=13, fontweight='bold'
    )

    for ax, modelo in zip(axes, modelos):
        datos = agg2[agg2['modelo'] == modelo].set_index('simulacion').reindex(sims)
        za  = datos['pct_A'].values
        zb  = datos['pct_B'].values
        zde = datos['pct_DE'].values

        ax.bar(x, za,  label='Zona A',   color=colores_zona['Zona A'],   alpha=0.9)
        ax.bar(x, zb,  bottom=za,        label='Zona B',   color=colores_zona['Zona B'],   alpha=0.9)
        ax.bar(x, zde, bottom=za + zb,   label='Zona D/E', color=colores_zona['Zona D/E'], alpha=0.9)

        for j, (va, vb, vde) in enumerate(zip(za, zb, zde)):
            ax.text(j, va / 2, f'{va:.1f}%',
                    ha='center', va='center', fontsize=8.5,
                    color='white', fontweight='bold')
            if vb > 0.2:
                ax.text(j, va + vb / 2, f'{vb:.1f}%',
                        ha='center', va='center', fontsize=8, color='#0C447C')

        ax.set_title(modelo, fontsize=11)
        ax.set_xticks(x)
        ax.set_xticklabels([ETIQUETAS_SIM[s] for s in sims], fontsize=7.5)
        ax.set_ylabel('% predicciones')
        ax.set_ylim(0, 105)
        ax.legend(framealpha=0.5, fontsize=9)

    fig.tight_layout()
    if guardar:
        fig.savefig(ruta, bbox_inches='tight')
    return fig


# ══════════════════════════════════════════════════════════════════════════════
# GRÁFICA 8 — Scatter métrica vs TIR por simulación (6 filas × 2 modelos)
# Objetivo: correlación entre estabilidad glucémica y error del predictor
# ══════════════════════════════════════════════════════════════════════════════

def grafica_scatter_tir(df, metrica='MAE', horizonte=15, guardar=False, ruta=None):
    if ruta is None:
        ruta = f'grafica8_scatter_{metrica.lower()}_tir_{horizonte}min.png'
    sims = sorted(df['simulacion'].unique())
    modelos = ['XGBoost', 'ARIMAX']
    df_h = df[df['horizonte_num'] == horizonte]

    fig, axes = plt.subplots(6, 2, figsize=(12, 22))
    fig.suptitle(
        f'{metrica} vs TIR por paciente — horizonte {horizonte} min\n'
        'Cada punto = 1 paciente · línea = regresión lineal · r = Spearman',
        fontsize=13, fontweight='bold', y=1.01
    )

    for row, sim in enumerate(sims):
        for col, modelo in enumerate(modelos):
            ax = axes[row][col]
            subset = df_h[(df_h['simulacion'] == sim) & (df_h['modelo'] == modelo)]
            tir_vals = subset['TIR'].values
            met_vals = subset[metrica].values

            ax.scatter(tir_vals, met_vals, color=COLORES[modelo],
                       alpha=0.75, s=50, zorder=3,
                       edgecolors='white', linewidths=0.5)

            slope, intercept, _, _, _ = stats.linregress(tir_vals, met_vals)
            x_line = np.linspace(tir_vals.min(), tir_vals.max(), 100)
            ax.plot(x_line, slope * x_line + intercept,
                    color=COLORES[modelo], linewidth=1.8,
                    linestyle='--', alpha=0.8)

            r_sp, p_sp = stats.spearmanr(tir_vals, met_vals)
            p_str = f"p={p_sp:.3f}" if p_sp >= 0.001 else "p<0.001"
            sig = " *" if p_sp < 0.05 else ""
            ax.text(0.97, 0.95, f"r={r_sp:.2f}\n{p_str}{sig}",
                    transform=ax.transAxes, ha='right', va='top', fontsize=9,
                    bbox=dict(boxstyle='round,pad=0.3',
                              facecolor='white', edgecolor='0.8', alpha=0.8))

            if row == 0:
                ax.set_title(modelo, fontsize=11, fontweight='bold',
                             color=COLORES[modelo])
            if col == 0:
                ax.set_ylabel(f"{ETIQUETAS_SIM_LARGA[sim]}\n{metrica} (mg/dL)", fontsize=8)
            if row == 5:
                ax.set_xlabel('TIR (%)', fontsize=10)

    fig.tight_layout()
    if guardar:
        fig.savefig(ruta, bbox_inches='tight')
    return fig


# ══════════════════════════════════════════════════════════════════════════════
# GRÁFICA 9 — Scatter agregado (media sobre simulaciones) métrica vs TIR
# Objetivo: visión global de la correlación TIR-error por modelo
# ══════════════════════════════════════════════════════════════════════════════

def grafica_scatter_tir_agregado(df, metrica='MAE', guardar=False, ruta=None):
    if ruta is None:
        ruta = f'grafica9_scatter_{metrica.lower()}_tir_agregado.png'
    modelos = ['XGBoost', 'ARIMAX']

    fig, axes = plt.subplots(1, 2, figsize=(13, 5), sharey=False)
    fig.suptitle(
        f'{metrica} vs TIR — media sobre las 6 simulaciones\n'
        'Cada punto = 1 paciente',
        fontsize=13, fontweight='bold'
    )

    for ax, h in zip(axes, [15, 30]):
        df_h = df[df['horizonte_num'] == h]
        agg_pac = (df_h.groupby(['modelo', 'paciente'])[[metrica, 'TIR']]
                   .mean().reset_index())

        for modelo in modelos:
            subset = agg_pac[agg_pac['modelo'] == modelo]
            tir_vals = subset['TIR'].values
            met_vals = subset[metrica].values

            ax.scatter(tir_vals, met_vals, color=COLORES[modelo],
                       alpha=0.75, s=60, zorder=3,
                       edgecolors='white', linewidths=0.5, label=modelo)

            slope, intercept, _, _, _ = stats.linregress(tir_vals, met_vals)
            x_line = np.linspace(tir_vals.min(), tir_vals.max(), 100)
            ax.plot(x_line, slope * x_line + intercept,
                    color=COLORES[modelo], linewidth=1.8,
                    linestyle='--', alpha=0.8)

            r_sp, p_sp = stats.spearmanr(tir_vals, met_vals)
            p_str = f"p={p_sp:.3f}" if p_sp >= 0.001 else "p<0.001"
            sig = " *" if p_sp < 0.05 else ""
            y_pos = 0.95 if modelo == 'XGBoost' else 0.78
            ax.text(0.97, y_pos,
                    f"{modelo}: r={r_sp:.2f}, {p_str}{sig}",
                    transform=ax.transAxes, ha='right', va='top',
                    fontsize=9, color=COLORES[modelo],
                    bbox=dict(boxstyle='round,pad=0.3',
                              facecolor='white',
                              edgecolor=COLORES[modelo], alpha=0.7))

        ax.set_title(f'Horizonte {h} min', fontsize=11)
        ax.set_xlabel('TIR (%)', fontsize=11)
        ax.set_ylabel(f'{metrica} (mg/dL)', fontsize=11)
        ax.legend(framealpha=0.5, fontsize=9)

    fig.tight_layout()
    if guardar:
        fig.savefig(ruta, bbox_inches='tight')
    return fig


# ══════════════════════════════════════════════════════════════════════════════
# GRÁFICA 10 — Tabla de correlaciones Spearman (métrica vs TIR)
# Objetivo: resumen estadístico de todas las correlaciones
# ══════════════════════════════════════════════════════════════════════════════

def grafica_tabla_spearman(df, metrica='MAE', guardar=False, ruta=None):
    if ruta is None:
        ruta = f'grafica10_spearman_{metrica.lower()}.png'
    sims    = sorted(df['simulacion'].unique())
    modelos = ['XGBoost', 'ARIMAX']

    col_labels = []
    for h in [15, 30]:
        for modelo in modelos:
            col_labels.append(f"{modelo}\n{h} min")

    filas        = []
    cell_colors  = []

    for sim in sims:
        fila       = [ETIQUETAS_SIM[sim]]
        col_colors = ['#f0f0f0']
        for h in [15, 30]:
            for modelo in modelos:
                subset = df[(df['simulacion'] == sim) &
                            (df['horizonte_num'] == h) &
                            (df['modelo'] == modelo)]
                r_sp, p_sp = stats.spearmanr(subset['TIR'].values,
                                             subset[metrica].values)
                p_str = f"p={p_sp:.3f}" if p_sp >= 0.001 else "p<0.001"
                txt   = f"r={r_sp:.2f}\n{p_str}"
                if p_sp < 0.05:
                    txt += " *"
                fila.append(txt)
                if p_sp < 0.05:
                    # verde = correlación negativa (mayor TIR → menor error, deseable)
                    # rojo  = correlación positiva
                    c = '#d4edda' if r_sp < 0 else '#fde8e8'
                else:
                    c = '#ffffff'
                col_colors.append(c)
        filas.append(fila)
        cell_colors.append(col_colors)

    fig, ax = plt.subplots(figsize=(12, 4.5))
    ax.axis('off')

    tabla = ax.table(
        cellText=filas,
        colLabels=['Simulación'] + col_labels,
        cellLoc='center',
        loc='center',
        cellColours=cell_colors,
    )
    tabla.auto_set_font_size(False)
    tabla.set_fontsize(8.5)
    tabla.scale(1, 2.4)

    for j in range(len(col_labels) + 1):
        tabla[0, j].set_facecolor('#2c3e50')
        tabla[0, j].set_text_props(color='white', fontweight='bold')

    ax.set_title(
        f'Correlaciones Spearman — {metrica} vs TIR\n'
        'Verde: correlación negativa significativa (mayor TIR → menor error)  '
        'Rojo: positiva significativa  * p<0.05',
        fontsize=10, pad=20
    )
    fig.tight_layout()
    if guardar:
        fig.savefig(ruta, bbox_inches='tight')
    return fig