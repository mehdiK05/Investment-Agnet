import os
import json
from pprint import pprint
from google import generativeai as genai 


api_key = os.getenv("GOOGLE_API_KEY")
class GeminiInvestmentAgent:
    """Un agent d'analyse d'investissement basé sur l'API Gemini de Google."""
    
    def __init__(self, api_key=api_key):
        """Initialise l'agent avec les identifiants API."""
        # Utiliser la clé API fournie directement
        self.api_key = api_key
        if not self.api_key:
            raise ValueError("Une clé API Google est requise.")
        
        # Initialiser le client Gemini avec la clé API
        genai.configure(api_key=self.api_key)
        self.client = genai.GenerativeModel(model_name="gemini-2.0-flash")
    
    def analyze_portfolio(self, investor_profile, portfolio, stock_data):
        """
        Analyser un portefeuille d'investissement en utilisant Gemini.
        
        Paramètres:
        -----------
        investor_profile : dict
            Informations sur l'investisseur (tolérance au risque, horizon temporel)
        portfolio : list
            Liste des actions et leur poids dans le portefeuille
        stock_data : dict
            Métriques financières pour chaque action
            
        Retourne:
        --------
        dict
            Analyse structurée et recommandations du LLM
        """
        # Create the prompt
        prompt = self._create_analysis_prompt(investor_profile, portfolio, stock_data)
        
        # sending prompt to LLM
        llm_response = self._query_llm(prompt)
        
        # process the response
        analysis_results = self._process_response(llm_response)
        
        return analysis_results
    
    def _create_analysis_prompt(self, investor_profile, portfolio, stock_data):
        
        # foramt financial data 
        portfolio_text = "\n".join([
            f"- {p['ticker']}: {p['weight']*100:.1f}% of portfolio" 
            for p in portfolio
        ])
        
        stock_data_text = ""
        for ticker, data in stock_data.items():
            metrics = "\n    ".join([f"- {k}: {v}" for k, v in data.items()])
            stock_data_text += f"{ticker}:\n    {metrics}\n\n"
        
        # Create clear prompt :
        prompt = f"""
You are a financial advisor specializing in portfolio analysis. Analyze this investment portfolio for a {investor_profile['risk_tolerance']}/10 risk tolerance investor with a {investor_profile['investment_horizon']} investment horizon.

PORTFOLIO HOLDINGS:
{portfolio_text}

FINANCIAL DATA:
{stock_data_text}

Please provide your analysis in the following JSON format. Don't include any other text outside of the JSON structure:

{{
  "portfolio_summary": "Brief overall assessment of the portfolio",
  "risk_assessment": {{
    "level": "Low, Moderate, or High",
    "description": "Description of portfolio risk level"
  }},
  "issues": [
    {{
      "severity": "High/Medium/Low",
      "type": "Type of issue (Diversification/Valuation/etc)",
      "description": "Description of the issue"
    }}
  ],
  "recommendations": [
    {{
      "priority": "High/Medium/Low",
      "action": "What to do",
      "target": "Which stock or sector",
      "rationale": "Why this recommendation is important"
    }}
  ]
}}

Base your assessment on:
1. Sector diversification (no more than 30% in one sector)
2. Valuation metrics (P/E ratio > 30 is high)
3. Financial health (debt/equity > 1.5 is concerning)
4. Growth (negative revenue growth is concerning)
5. Match to investor's risk profile
"""
        return prompt
    
    def _query_llm(self, prompt):
        """Envoyer le prompt à l'API Gemini et obtenir la réponse."""
        try:
            # Utiliser le client Gemini pour générer une réponse
            response = self.client.generate_content(
                contents=prompt,
                generation_config=genai.GenerationConfig(
                    temperature=0.2,  # Température basse pour des réponses plus déterministes
                    max_output_tokens=4096
                )
            )
            return response
        except Exception as e:
            print(f"Erreur lors de l'appel à l'API Gemini: {e}")
            return {"error": str(e)}
    
    def _process_response(self, llm_response):
        """Extraire et structurer la réponse JSON de Gemini."""
        try:
            # Vérifier si une erreur est présente dans la réponse
            if hasattr(llm_response, 'error'):
                return {"error": f"API Error: {llm_response.error}"}
            
            if isinstance(llm_response, dict) and "error" in llm_response:
                return llm_response
            
            # Extraire le texte de la réponse Gemini
            text = llm_response.text
            
            # Extraire le JSON de la réponse
            # D'abord chercher le JSON entre les triple backticks
            if "```json" in text and "```" in text.split("```json")[1]:
                json_text = text.split("```json")[1].split("```")[0].strip()
            elif "```" in text and "```" in text.split("```")[1]:
                # Essayer juste les triple backticks sans 'json'
                json_text = text.split("```")[1].split("```")[0].strip()
            else:
                # Utiliser le texte entier
                json_text = text.strip()
            
            # Parser le JSON
            analysis_data = json.loads(json_text)
            return analysis_data
            
        except Exception as e:
            print(f"Erreur lors du traitement de la réponse Gemini: {e}")
            print(f"Réponse brute: {llm_response}")
            return {"error": f"Échec du traitement de la réponse Gemini: {str(e)}"}


# Exemple d'utilisation de l'agent Gemini
def demonstrate_gemini_agent():
    """Exécuter une démonstration de l'agent basé sur Gemini."""
    print("Analyse de portefeuille d'investissement avec Gemini")
    print("===================================================")
    
    # Créer l'agent Gemini avec la clé API directement
    # Remplacez ceci par votre clé API réelle
    api_key = "AIzaSyA6kTThSnSSnuB_sTwGTNKzVIOFjO_KhOc"  # ← REMPLACEZ CECI PAR VOTRE VRAIE CLÉ API
    
    try:
        agent = GeminiInvestmentAgent(api_key)
    except ValueError as e:
        print(f"Erreur: {e}")
        print("Pour exécuter cette démo, vous avez besoin d'une clé API Google.")
        return
    
    # Exemple de profil d'investisseur
    investor_profile = {
        "risk_tolerance": 7,  # Échelle de 1 à 10
        "investment_horizon": "long-term"  # short-term, medium-term, ou long-term
    }
    
    # Exemple de portefeuille
    portfolio = [
        {"ticker": "AAPL", "weight": 0.25},  # 25% du portefeuille
        {"ticker": "MSFT", "weight": 0.20},  # 20% du portefeuille
        {"ticker": "JPM", "weight": 0.15},   # 15% du portefeuille
        {"ticker": "NEE", "weight": 0.25},   # 25% du portefeuille
        {"ticker": "PG", "weight": 0.15}     # 15% du portefeuille
    ]
    
    # Exemple de données d'actions
    stock_data = {
        "AAPL": {
            "p_e_ratio": 28.5,
            "debt_equity": 1.2,
            "revenue_growth": 0.08,  # 8% de croissance
            "beta": 1.2
        },
        "MSFT": {
            "p_e_ratio": 32.1,
            "debt_equity": 0.5,
            "revenue_growth": 0.12,  # 12% de croissance
            "beta": 1.1
        },
        "JPM": {
            "p_e_ratio": 14.2,
            "debt_equity": 1.5,
            "revenue_growth": 0.04,  # 4% de croissance
            "beta": 1.3
        },
        "NEE": {
            "p_e_ratio": 35.8,
            "debt_equity": 1.4,
            "revenue_growth": -0.02,  # -2% de croissance (déclin)
            "beta": 0.7
        },
        "PG": {
            "p_e_ratio": 25.3,
            "debt_equity": 0.6,
            "revenue_growth": 0.03,  # 3% de croissance
            "beta": 0.6
        }
    }
    
    print("\nEnvoi des données du portefeuille à Gemini pour analyse...")
    
    try:
        # Exécuter l'analyse Gemini
        results = agent.analyze_portfolio(investor_profile, portfolio, stock_data)
        
        # Afficher les résultats
        print("\nRésultats de l'analyse:")
        print("----------------------")
        pprint(results)
        
        return results
    except Exception as e:
        print(f"Erreur lors de l'exécution de l'analyse: {e}")


# Exécuter la démonstration si le script est exécuté directement
if __name__ == "__main__":
    demonstrate_gemini_agent()