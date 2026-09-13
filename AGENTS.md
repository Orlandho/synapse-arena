# Reglas de Orquestación y Delimitación para el Agente Jules en Synapse Arena

Este repositorio (`synapse-arena`) implementa un simulador de vida artificial y enjambres cibernéticos a 60 FPS con redes neuronales continuas y algoritmos genéticos.

El agente autónomo **Jules** de Google actúa como programador delegado en la nube para implementar nuevas capacidades sensoriales, optimizaciones de física y visualizaciones.

---

## 🏛️ Mapa de Responsabilidades para Jules

```mermaid
flowchart TD
    subgraph OrquestacionJules ["Flujo de Delegación a Jules"]
        Issue["GitHub Issue (Etiqueta: jules)"]
        Jules["Sesión del Agente Jules"]
        PR["Pull Request con Pruebas Validadas"]
        Issue --> Jules
        Jules --> PR
    end

    subgraph ModulosPermitidos ["Módulos Modificables"]
        Engine["Motor de Evolución y Redes\n(src/synapse_evolution_engine.py)"]
        Mesh["Migración Espacial\n(src/arena_distributed_mesh.py)"]
        CanvasUI["Simulador Canvas 60 FPS\n(index.html)"]
        Tests["Suites de Pruebas\n(tests/test_*.py)"]
        
        Jules --> Engine
        Jules --> Mesh
        Jules --> CanvasUI
        Jules --> Tests
    end

    subgraph ZonaProtegida ["Zona Protegida"]
        Workflows["Workflows de CI/CD\n(.github/workflows/*)"]
        Lic["Licencia MIT\n(LICENSE)"]
        
        Jules -. "Restricción" .-> Workflows
        Jules -. "Restricción" .-> Lic
    end
```

### 1. Áreas de Programación Permitidas:
- `index.html`: Renderizado Canvas, nuevos modos interactivos de simulación, shaders y audio Web Audio.
- `src/synapse_evolution_engine.py`: Mutaciones genéticas, cálculo vectorial y funciones de aptitud.
- `src/arena_distributed_mesh.py`: Serialización genómica y lógica de migración espacial.
- `tests/`: Nuevas pruebas unitarias o de integración.

### 2. Estándar de Pruebas:
Cualquier Pull Request generado por Jules debe pasar limpiamente:
```bash
python -m unittest discover -s tests
```
