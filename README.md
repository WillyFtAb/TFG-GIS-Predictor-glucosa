# Predictor de glucosa 

**Autor**: Guillermo de la Fuente Abajo  
**Tutor**: Antonio Jesús Canepa Oneto  
**Universidad**: Universidad de Burgos  
**Titulación**: Grado en Ingeniería de la Salud  
**Curso académico**: 2025/2026  

---

## Introducción
La diabetes mellitus (DM) es un tipo de patologías endocrino-metabólicas crónicas que se caracterizan por la presencia de una cantidad elevada de glucosa en la sangre de las personas que la padecen a consecuencia de la falta de insulina
o el mal funcionamiento de dicha hormona.  
La Diabetes Tipo 1 (DT1) es una enfermedad crónica autoinmune en la que el sistema inmunitario destruye las células beta situadas en los islotes de Langerhans, en el páncreas, eliminando la producción de insulina.
Esto obliga a los pacientes a depender de insulina externa de por vida para procesar la glucosa y evitar complicaciones graves. Representa entre el 5-10% de los casos totales de diabetes. En España se estima que viven unas 160.000 personas con DMT1.

Actualmente existen 2 formas de administración de la insulina:

  - **Sistema de asa cerrada (bomba de insulina):** Sistemas avanzados que integran un sensor de glucosa continuo (CGM) con una bomba de infusión. Mediante algoritmos, el sistema ajusta automáticamente parte de la insulina necesaria. Sólo es necesario que el paciente introduzca
    las ingestas de hidratos de carbono.
  - **Múltiples Dosis Diarias (MDI):** El paciente administra manualmente insulina basal (acción lenta) y bolos (acción rápida) mediante plumas de insulina.
    Este método requiere un esfuerzo cognitivo constante, ya que el usuario debe calcular dosis basándose en carbohidratos, ejercicio y niveles actuales de glucosa.


Aunque la tecnología de asa cerrada está avanzando, una gran parte de la población con DT1 en España y el mundo sigue utilizando Múltiples Dosis Diarias (MDI).

Este repositorio desarrolla un predictor que anticipa los niveles de glucosa en un horizonte de 15 a 30 minutos.
El objetivo es proporcionar una "ventana de seguridad" que permita al paciente actuar antes de que ocurra una hipoglucemia o hiperglucemia, facilitando el control metabólico sin necesidad de una bomba de insulina.
