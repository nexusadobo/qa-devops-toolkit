import json
import os
import openai
import mlflow
from dotenv import load_dotenv

# Cargar las variables de entorno desde el archivo .env
load_dotenv()

# Configurar la clave de API de OpenAI
openai.api_key = os.getenv("OPENAI_API_KEY")

# Ruta al archivo cucumber.json
cucumber_file = "cucumber.json"

# Función para analizar el archivo Cucumber JSON
def parse_cucumber_json(file_path):
    with open(file_path, "r") as f:
        data = json.load(f)

    total_features = len(data)
    total_scenarios = 0
    total_steps = 0
    passed_steps = 0
    failed_steps = 0
    total_duration = 0

    for feature in data:
        for scenario in feature.get("elements", []):
            total_scenarios += 1
            for step in scenario.get("steps", []):
                total_steps += 1
                total_duration += step["result"]["duration"]
                if step["result"]["status"] == "passed":
                    passed_steps += 1
                elif step["result"]["status"] == "failed":
                    failed_steps += 1

    metrics = {
        "total_features": total_features,
        "total_scenarios": total_scenarios,
        "total_steps": total_steps,
        "passed_steps": passed_steps,
        "failed_steps": failed_steps,
        "total_duration_seconds": total_duration / 1_000_000_000,  # Convertir nanosegundos a segundos
        "pass_rate": (passed_steps / total_steps) * 100 if total_steps > 0 else 0
    }
    return metrics

# Función para generar un resumen utilizando OpenAI
def generate_summary(metrics):
    prompt = (
        f"Se han ejecutado {metrics['total_features']} características con un total de {metrics['total_scenarios']} escenarios. "
        f"De los {metrics['total_steps']} pasos ejecutados, {metrics['passed_steps']} pasaron y {metrics['failed_steps']} fallaron. "
        f"La duración total de las pruebas fue de {metrics['total_duration_seconds']:.2f} segundos, con una tasa de éxito del {metrics['pass_rate']:.2f}%. "
        "Proporciona un resumen ejecutivo de estos resultados y sugiere posibles áreas de mejora."
    )

    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=prompt,
        max_tokens=150
    )
    return response.choices[0].text.strip()

# Registrar métricas y resumen en MLflow
def log_results_with_openai(file_path):
    metrics = parse_cucumber_json(file_path)
    summary = generate_summary(metrics)

    # Configurar experimento en MLflow
    mlflow.set_experiment("Cucumber_E2E_Test_Analysis_with_OpenAI")

    with mlflow.start_run():
        # Registrar métricas
        for key, value in metrics.items():
            mlflow.log_metric(key, value)

        # Registrar el resumen generado por OpenAI
        mlflow.log_text(summary, "openai_summary.txt")

        # Registrar el archivo original como artefacto
        mlflow.log_artifact(file_path)

        print("Métricas y resumen registrados en MLflow:")
        print(metrics)
        print("\nResumen generado por OpenAI:")
        print(summary)

# Ejecutar el análisis
if __name__ == "__main__":
    log_results_with_openai(cucumber_file)
