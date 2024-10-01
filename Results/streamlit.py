import Results.streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# Cargar datos del CSV
workers_log = pd.read_csv('workers_log.csv')
pm_log = pd.read_csv('pm_log.csv')

# Función para graficar el progreso de los trabajadores
def plot_worker_progress(workers_log):
    fig, ax = plt.subplots(figsize=(10, 6))

    # Iterar sobre cada trabajador para crear su línea
    workers = workers_log['worker_id'].unique()

    for worker in workers:
        worker_data = workers_log[workers_log['worker_id'] == worker]
        time = worker_data['time']
        work_line = [1 if w else 0 for w in worker_data['work']]  # 1 si trabajó, 0 si no

        # Dibujar la línea de progreso de trabajo
        ax.plot(time, work_line, label=f'Trabajador {worker}', color='gray', linewidth=2)

        # Cambiar el color si reporta progreso (amarillo)
        progress = worker_data[worker_data['report_progress'] == True]
        ax.plot(progress['time'], [1] * len(progress), 'y', label='Reporta progreso', linewidth=2)

        # Colocar un punto rojo si escaló un problema
        escalate = worker_data[worker_data['escalate_problem'] == True]
        ax.scatter(escalate['time'], [1] * len(escalate), color='red', label='Escaló problema')

        # Colocar un punto verde si reportó un problema
        report = worker_data[worker_data['report_problem'] == True]
        ax.scatter(report['time'], [1] * len(report), color='green', label='Reportó problema')

        # Dibujar línea blanca si estaba cooperando
        cooperate = worker_data[worker_data['cooperate'] == True]
        ax.plot(cooperate['time'], [1] * len(cooperate), color='white', linewidth=2)

        # Dibujar línea azul si estaba descansando
        rest = worker_data[worker_data['rest'] == True]
        ax.plot(rest['time'], [1] * len(rest), color='blue', linewidth=2)

    ax.set_xlabel('Tiempo')
    ax.set_ylabel('Progreso de trabajo')
    ax.set_title('Progreso de los Trabajadores en el Tiempo')
    ax.legend()

    st.pyplot(fig)

# Función para graficar el log del Project Manager
def plot_pm_log(pm_log):
    st.write("### Acciones del Project Manager")

    # Grafica: Número de asignaciones por tiempo
    fig1, ax1 = plt.subplots()
    ax1.plot(pm_log['time'], pm_log['pm_assignments'], label='Asignaciones', color='orange')
    ax1.set_title('Asignaciones del Project Manager en el Tiempo')
    ax1.set_xlabel('Tiempo')
    ax1.set_ylabel('Número de Asignaciones')
    st.pyplot(fig1)

    # Grafica: Reasignaciones y cooperaciones en el tiempo
    fig2, ax2 = plt.subplots()
    ax2.plot(pm_log['time'], pm_log['pm_reassign'], label='Reasignaciones', color='purple')
    ax2.plot(pm_log['time'], pm_log['pm_cooperations'], label='Cooperaciones', color='white')
    ax2.set_title('Reasignaciones y Cooperaciones en el Tiempo')
    ax2.set_xlabel('Tiempo')
    ax2.set_ylabel('Número')
    st.pyplot(fig2)

    # Grafica: Evaluación de desempeño y motivación
    fig3, ax3 = plt.subplots()
    ax3.plot(pm_log['time'], pm_log['pm_evaluate_performance'], label='Evaluar Desempeño', color='green')
    ax3.plot(pm_log['time'], pm_log['pm_motivate'], label='Motivaciones', color='blue')
    ax3.set_title('Evaluación de Desempeño y Motivación en el Tiempo')
    ax3.set_xlabel('Tiempo')
    ax3.set_ylabel('Número de eventos')
    st.pyplot(fig3)

    # Grafica: Recursos optimizados
    fig4, ax4 = plt.subplots()
    ax4.plot(pm_log['time'], pm_log['pm_optimize'], label='Recursos Optimizados', color='brown')
    ax4.set_title('Optimización de Recursos en el Tiempo')
    ax4.set_xlabel('Tiempo')
    ax4.set_ylabel('Número de recursos optimizados')
    st.pyplot(fig4)

    # Grafica: Problemas y escalaciones
    fig5, ax5 = plt.subplots()
    ax5.plot(pm_log['time'], pm_log['problems_count'], label='Problemas Actuales', color='red')
    ax5.plot(pm_log['time'], pm_log['escalate_problem_count'], label='Problemas Escalados', color='pink')
    ax5.set_title('Problemas y Escalaciones en el Tiempo')
    ax5.set_xlabel('Tiempo')
    ax5.set_ylabel('Número de problemas')
    st.pyplot(fig5)

# Nueva gráfica para cooperation_prob
def plot_cooperation_prob(pm_log):
    fig6, ax6 = plt.subplots()
    ax6.plot(pm_log['time'], pm_log['cooperation_prob'], label='Probabilidad de Cooperación', color='cyan')
    ax6.set_title('Probabilidad de Cooperación en el Tiempo')
    ax6.set_xlabel('Tiempo')
    ax6.set_ylabel('Probabilidad')
    st.pyplot(fig6)

# Nueva gráfica para trust_in_agents
def plot_trust_in_agents(pm_log):
    fig7, ax7 = plt.subplots(figsize=(10, 6))

    # 'trust_in_agents' es una lista de tuplas (trabajador, confianza)
    for i, row in pm_log.iterrows():
        time = row['time']
        trust_in_agents = eval(row['trust_in_agents'])  # Convierte el string de tuplas a lista de tuplas
        
        # Graficar confianza de cada trabajador en el tiempo
        for worker_id, trust in trust_in_agents:
            ax7.scatter(time, trust, label=f'Trabajador {worker_id}', s=10)

    ax7.set_xlabel('Tiempo')
    ax7.set_ylabel('Confianza en los trabajadores')
    ax7.set_title('Confianza en los Trabajadores por parte del Project Manager en el Tiempo')
    ax7.legend(loc='upper left', bbox_to_anchor=(1, 1))
    st.pyplot(fig7)

# Título de la página
st.title("Simulación Multiagente: Análisis del Log")

# Sección de los trabajadores
st.header("Progreso de los Trabajadores")
plot_worker_progress(workers_log)

# Sección del Project Manager
st.header("Acciones del Project Manager")
plot_pm_log(pm_log)

# Nueva sección: Probabilidad de cooperación
st.header("Probabilidad de Cooperación del Project Manager")
plot_cooperation_prob(pm_log)

# Nueva sección: Confianza en los Trabajadores
st.header("Confianza del Project Manager en los Trabajadores")
plot_trust_in_agents(pm_log)