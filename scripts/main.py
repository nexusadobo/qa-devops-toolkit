import json
import os
from openai import OpenAI
from dotenv import load_dotenv

# Cargar el archivo .env
load_dotenv()

class CypressAnalyzer:
    def __init__(self):
        self.client = OpenAI()

    def read_cypress_results(self, json_path):
        """Lee y parsea el archivo JSON de resultados de Cypress"""
        with open(json_path, 'r') as file:
            return json.load(file)

    def analyze_test_results(self, results):
        """Analiza los resultados usando OpenAI"""
        # Prepara el resumen de los resultados
        summary = self._prepare_summary(results)

        response = self.client.chat.completions.create(
            model="gpt-4",
            messages=[{
                "role": "user",
                "content": f"""Analiza estos resultados de pruebas E2E de Cypress y proporciona:
                1. Patrones comunes en fallos
                2. Sugerencias de mejora
                3. Áreas de riesgo potencial

                Resultados: {summary}"""
            }],
            temperature=0.7
        )

        return response.choices[0].message.content

    def _prepare_summary(self, results):
        """Prepara un resumen estructurado de los resultados"""
        summary = {
            "total_tests": 0,
            "passed": 0,
            "failed": 0,
            "failures": []
        }

        for test in results.get("results", []):
            summary["total_tests"] += 1
            if test.get("state") == "passed":
                summary["passed"] += 1
            else:
                summary["failed"] += 1
                summary["failures"].append({
                    "title": test.get("title"),
                    "error": test.get("error", {}).get("message", "No error message"),
                    "duration": test.get("duration")
                })

        return summary


def main():

    analyzer = CypressAnalyzer()
    results = analyzer.read_cypress_results("cucumberArtifacts/cucumber.json")
    analysis = analyzer.analyze_test_results(results)

    print("\nAnálisis de Resultados:")
    print(analysis)


if __name__ == "__main__":
    main()