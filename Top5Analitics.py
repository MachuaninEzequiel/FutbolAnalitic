import numpy as np
import pandas as pd
from scipy import stats
import math
from math import pi
import matplotlib.pyplot as plt
import streamlit as st

# Lectura del DataFrame
df = pd.read_csv('Final FBRef 2023-2024.csv')

# Definir las ligas disponibles
ligas_disponibles = ['Premier League', 'La Liga', 'Serie A', 'Bundesliga', 'Ligue 1']

# Interfaz de Streamlit con sidebar
st.sidebar.markdown("<h1 style='text-align: center; font-size: 36px;'>Análisis de Mediocampistas</h1>", unsafe_allow_html=True)

# Selección de la liga en el sidebar
liga_seleccionada = st.sidebar.selectbox('Selecciona la liga', ligas_disponibles)

# Filtrar los datos según la liga seleccionada
mediocampistas = df[(df['Pos'].str.contains('MF') == True) & (df['Min'] > 840) & (df['Comp'].str.contains(liga_seleccionada) == True)].reset_index(drop=True)

lista_valores = [
    'Player',
    'Squad',
    'TklPer90',
    'TklWinPossPer90',
    'Mid3rdTklPer90',
    'Def3rdTklPer90',
    'Att3rdTklPer90',
    'DrbTklPer90',
    'DrbPastAttPer90',
    'DrbTkl%Per90',
    'DrbPastPer90',
    'BlocksPer90',
    'ShBlocksPer90',
    'PassBlocksPer90',
    'IntPer90',
    'Tkl+IntPer90',
    'ClrPer90',
    'ErrPer90',
    'RecovPer90',
    'pAdjShBlocksPer90',
    'pAdjPassBlocksPer90',
    'pAdjIntPer90',
    'pAdjDrbTklPer90',
    'pAdjTklWinPossPer90',
    'pAdjDrbPastPer90',
    'pAdjAerialWinsPer90',
    'pAdjAerialLossPer90',
]

# Grupo 1 de columnas para el primer total
grupo_1 = [
    'TklPer90',
    'TklWinPossPer90',
    'Def3rdTklPer90',
    'Mid3rdTklPer90',
    'Att3rdTklPer90',
    'DrbTklPer90',
    'DrbPastAttPer90',
    'DrbTkl%Per90',
    'DrbPastPer90',
    'BlocksPer90',
    'ShBlocksPer90',
    'PassBlocksPer90',
    'IntPer90',
    'Tkl+IntPer90',
    'ClrPer90',
    'ErrPer90',
    'RecovPer90'
]

# Grupo 2 de columnas para el segundo total
grupo_2 = [
    'pAdjShBlocksPer90',
    'pAdjPassBlocksPer90',
    'pAdjIntPer90',
    'pAdjDrbTklPer90',
    'pAdjTklWinPossPer90',
    'pAdjDrbPastPer90',
    'pAdjAerialWinsPer90',
    'pAdjAerialLossPer90'
]

mediosdef = mediocampistas[lista_valores].reset_index(drop=True).fillna(0)
jugadores = list(mediosdef.Player.unique())

# DataFrame para grupo 1
df_grupo_1 = pd.DataFrame(columns=['Nombre', 'Equipo'] + grupo_1)

# DataFrame para grupo 2
df_grupo_2 = pd.DataFrame(columns=['Nombre', 'Equipo'] + grupo_2)

for jugador in jugadores:
    player = mediosdef.loc[mediosdef['Player'] == jugador].reset_index()
    equipo = player.loc[0, 'Squad']  # Obtener el nombre del equipo

    # Calcular percentiles para el grupo 1
    player_values_grupo_1 = player.loc[0, grupo_1].values  # Obtener los valores de los parámetros del grupo 1
    percentiles_grupo_1 = []
    for x in range(len(grupo_1)):
        percentile = math.floor(stats.percentileofscore(mediosdef[grupo_1[x]], player_values_grupo_1[x]))
        percentiles_grupo_1.append(percentile)
    diccionario_grupo_1 = {'Nombre': jugador, 'Equipo': equipo}
    diccionario_grupo_1.update({grupo_1[i]: percentiles_grupo_1[i] for i in range(len(grupo_1))})
    df1 = pd.DataFrame([diccionario_grupo_1])
    df_grupo_1 = pd.concat([df_grupo_1, df1], ignore_index=True)

    # Calcular percentiles para el grupo 2
    player_values_grupo_2 = player.loc[0, grupo_2].values  # Obtener los valores de los parámetros del grupo 2
    percentiles_grupo_2 = []
    for x in range(len(grupo_2)):
        percentile = math.floor(stats.percentileofscore(mediosdef[grupo_2[x]], player_values_grupo_2[x]))
        percentiles_grupo_2.append(percentile)
    diccionario_grupo_2 = {'Nombre': jugador, 'Equipo': equipo}
    diccionario_grupo_2.update({grupo_2[i]: percentiles_grupo_2[i] for i in range(len(grupo_2))})
    df2 = pd.DataFrame([diccionario_grupo_2])
    df_grupo_2 = pd.concat([df_grupo_2, df2], ignore_index=True)

# Cálculo de las puntuaciones totales
df_grupo_1['Puntuacion_Total_Grupo_1'] = df_grupo_1[grupo_1].sum(axis=1)
df_grupo_2['Puntuacion_Total_Grupo_2'] = df_grupo_2[grupo_2].sum(axis=1)

# Ordenar los DataFrames basados en las puntuaciones totales
df_grupo_1 = df_grupo_1.sort_values(by='Puntuacion_Total_Grupo_1', ascending=False).reset_index(drop=True)
df_grupo_2 = df_grupo_2.sort_values(by='Puntuacion_Total_Grupo_2', ascending=False).reset_index(drop=True)

def calcular_area_poligono(angulos, valores):
    # Convertir los ángulos y valores a coordenadas cartesianas
    x = [v * np.cos(a) for a, v in zip(angulos, valores)]
    y = [v * np.sin(a) for a, v in zip(angulos, valores)]

    # Aplicar la fórmula de Shoelace para calcular el área del polígono
    area = 0.5 * np.abs(np.dot(x, np.roll(y, 1)) - np.dot(y, np.roll(x, 1)))

    return area

# Función para crear el gráfico de radar
def crear_radar_modificado(df, grupo, nombre_grupo, jugador_seleccionado):
    categorias = grupo
    N = len(categorias)
    etiquetas_personalizadas = [f'{i+1}º' for i in range(N)]

    valores = df[categorias].values.flatten().tolist()
    valores += valores[:1]

    # Calcula los ángulos de los ejes del radar
    angulos = [n / float(N) * 2 * np.pi for n in range(N)]
    angulos += angulos[:1]

    # Inicializa el gráfico de radar
    fig, ax = plt.subplots(figsize=(12, 8), subplot_kw=dict(polar=True))

    # Dibuja los ejes con las etiquetas
    ax.plot(angulos, valores, linewidth=1, linestyle='solid')
    ax.fill(angulos, valores, 'b', alpha=0.2)
    ax.set_xticks(angulos[:-1])
    ax.set_xticklabels(etiquetas_personalizadas)
    ax.set_title(f'Gráfico de Radar - {nombre_grupo} - {jugador_seleccionado}')
    
    # Calcular el área del polígono
    area_poligono = calcular_area_poligono(angulos, valores)

    # Retornar la figura y el área del polígono
    return fig, area_poligono

# Selección de grupo y jugador en el sidebar
grupo_seleccionado = st.sidebar.selectbox('Selecciona el grupo', ['Grupo 1', 'Grupo 2'])
jugador_seleccionado = st.sidebar.selectbox('Selecciona el jugador', jugadores)

# Mostrar el gráfico en la parte principal
if grupo_seleccionado == 'Grupo 1':
    df_jugador = df_grupo_1[df_grupo_1['Nombre'] == jugador_seleccionado]
    fig, area_poligono = crear_radar_modificado(df_jugador, grupo_1, 'Grupo 1', jugador_seleccionado)
else:
    df_jugador = df_grupo_2[df_grupo_2['Nombre'] == jugador_seleccionado]
    fig, area_poligono = crear_radar_modificado(df_jugador, grupo_2, 'Grupo 2', jugador_seleccionado)

# Mostrar la figura en la parte principal
st.pyplot(fig)
st.write(f"Área del polígono: {area_poligono:.2f}")

# Botón para mostrar estadísticas
with st.expander('Estadísticas del Jugador'):
    if grupo_seleccionado == 'Grupo 1':
        df_jugador = df_grupo_1[df_grupo_1['Nombre'] == jugador_seleccionado]
    else:
        df_jugador = df_grupo_2[df_grupo_2['Nombre'] == jugador_seleccionado]
    st.table(df_jugador)
