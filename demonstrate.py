api_key = os.getenv("GOOGLE_API_KEY")
from pprint import pprint
def demonstrate_gemini_agent():
    """Exécuter une démonstration de l'agent basé sur Gemini."""
    print("Analyse de portefeuille d'investissement avec Gemini")
    print("===================================================")
    
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
        
        
        print("\nRésultats de l'analyse:")
        print("----------------------")
        pprint(results)
        
        return results
    except Exception as e:
        print(f"Erreur lors de l'exécution de l'analyse: {e}")


if __name__ == "__main__":
    demonstrate_gemini_agent()