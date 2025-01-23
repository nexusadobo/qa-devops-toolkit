import json
import mlflow

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

# Registrar métricas en MLflow
def log_cucumber_results(file_path):
    metrics = parse_cucumber_json(file_path)

    # Configurar experimento en MLflow
    mlflow.set_experiment("Cucumber_E2E_Test_Analysis")

    with mlflow.start_run():
        # Registrar métricas
        for key, value in metrics.items():
            mlflow.log_metric(key, value)

        # Registrar el archivo original como artefacto
        mlflow.log_artifact(file_path)

        print("Métricas registradas en MLflow:")
        print(metrics)

# Ejecutar el análisis
if __name__ == "__main__":
    log_cucumber_results(cucumber_file)
