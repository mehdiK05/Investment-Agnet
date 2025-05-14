# streamlit_app/app.py
import sys
import os
import json
import pandas as pd
import streamlit as st

# Add the parent directory to the path so we can import the agent
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from agent import GeminiInvestmentAgent

# Configuration de la page Streamlit
st.set_page_config(
    page_title="Analyse de Portefeuille d'Investissement IA",
    page_icon="📊",
    layout="wide"
)

# API KEY prédéfinie (ne pas demander à l'utilisateur de l'entrer)
API_KEY = "AIzaSyA6kTThSnSSnuB_sTwGTNKzVIOFjO_KhOc"  # Votre clé API Gemini

# Fonction pour créer un design plus propre
def local_css():
    st.markdown("""
    <style>
        .block-container {
            padding-top: 2rem;
            padding-bottom: 2rem;
        }
        h1, h2, h3 {
            margin-top: 1rem;
            margin-bottom: 1rem;
        }
        .stAlert {
            margin-top: 1rem;
            margin-bottom: 1rem;
        }
        .priority-high, .severity-high {
            color: #ff4b4b;
            font-weight: bold;
        }
        .priority-medium, .severity-medium {
            color: #ffa64b;
            font-weight: bold;
        }
        .priority-low, .severity-low {
            color: #4bd964;
            font-weight: bold;
        }
        .card {
            background-color: #f9f9f9;
            border-radius: 10px;
            padding: 20px;
            margin-bottom: 20px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }
        /* Style spécifique pour que le texte soit visible sur fond sombre */
        .card-content {
            color: #000;
            background-color: #f9f9f9;
            padding: 15px;
            border-radius: 8px;
            margin-top: 10px;
        }
    </style>
    """, unsafe_allow_html=True)

# Fonction principale de l'application
def main():
    local_css()
    
    # Titre de l'application
    st.title("Analyse de Portefeuille d'Investissement avec IA")
    st.markdown("Utilisez l'intelligence artificielle pour analyser et optimiser votre portefeuille d'investissement.")
    
    # Initialisation des données de session
    if 'portfolio' not in st.session_state:
        st.session_state.portfolio = [{"ticker": "", "weight": 0}]
    if 'financial_data' not in st.session_state:
        st.session_state.financial_data = {}
    if 'analysis_results' not in st.session_state:
        st.session_state.analysis_results = None

    # Créer les onglets
    tab1, tab2, tab3 = st.tabs(["Configuration", "Portefeuille & Données", "Résultats d'Analyse"])
    
    with tab1:
        st.header("Configuration")
        
        # Afficher la clé API comme pré-configurée (sans demander à l'utilisateur)
        st.info("L'API Gemini est configurée automatiquement. Aucune clé API n'est requise.")
        
        st.header("Profil d'Investisseur")
        col1, col2 = st.columns(2)
        with col1:
            risk_tolerance = st.slider("Tolérance au Risque", min_value=1, max_value=10, value=5, step=1, 
                                     help="1 = Risque très faible, 10 = Risque très élevé")
        with col2:
            investment_horizon = st.selectbox("Horizon d'Investissement", 
                                             ["short-term", "medium-term", "long-term"],
                                             format_func=lambda x: {
                                                 "short-term": "Court terme (< 2 ans)",
                                                 "medium-term": "Moyen terme (2-5 ans)",
                                                 "long-term": "Long terme (> 5 ans)"
                                             }[x])
    
    with tab2:
        st.header("Actions du Portefeuille")
        
        # Fonction pour ajouter une action
        def add_stock():
            st.session_state.portfolio.append({"ticker": "", "weight": 0})
        
        # Fonction pour supprimer une action
        def delete_stock(index):
            ticker = st.session_state.portfolio[index]["ticker"]
            if ticker in st.session_state.financial_data:
                del st.session_state.financial_data[ticker]
            del st.session_state.portfolio[index]
        
        # Afficher les actions existantes et permettre l'ajout/suppression
        portfolio_data = []
        
        for i, stock in enumerate(st.session_state.portfolio):
            col1, col2, col3 = st.columns([3, 2, 1])
            with col1:
                ticker = st.text_input(f"Ticker #{i+1}", value=stock["ticker"], key=f"ticker_{i}")
            with col2:
                weight = st.number_input(f"Poids (%) #{i+1}", min_value=0.0, max_value=100.0, value=float(stock["weight"]), step=1.0, key=f"weight_{i}")
            with col3:
                if len(st.session_state.portfolio) > 1:
                    if st.button("Supprimer", key=f"delete_{i}"):
                        delete_stock(i)
                        st.experimental_rerun()
            
            # Mettre à jour les données du portefeuille
            st.session_state.portfolio[i]["ticker"] = ticker
            st.session_state.portfolio[i]["weight"] = weight
            
            if ticker:
                portfolio_data.append({"ticker": ticker, "weight": weight / 100})
                
                # Assurer que ce ticker existe dans les données financières
                if ticker not in st.session_state.financial_data:
                    st.session_state.financial_data[ticker] = {
                        "p_e_ratio": 0.0,
                        "debt_equity": 0.0,
                        "revenue_growth": 0.0,
                        "beta": 0.0
                    }
        
        # Bouton pour ajouter une nouvelle action
        if st.button("+ Ajouter une action"):
            add_stock()
            st.experimental_rerun()
        
        # Vérifier si la somme des poids est égale à 100%
        total_weight = sum(stock["weight"] for stock in st.session_state.portfolio)
        if abs(total_weight - 100) > 1:
            st.warning(f"La somme des poids doit être égale à 100%. Actuellement: {total_weight:.1f}%")
        
        # Afficher les données financières pour chaque action
        st.header("Données Financières")
        
        for ticker in [stock["ticker"] for stock in st.session_state.portfolio if stock["ticker"]]:
            st.subheader(ticker)
            col1, col2 = st.columns(2)
            with col1:
                # Correction: Assurer que tous les paramètres numériques sont du même type (float)
                p_e_ratio = st.number_input(f"Ratio P/E ({ticker})", 
                                         min_value=0.0, step=0.1, format="%.1f",
                                         value=float(st.session_state.financial_data[ticker].get("p_e_ratio", 0.0)),
                                         key=f"pe_{ticker}")
                
                revenue_growth = st.number_input(f"Croissance du CA ({ticker})", 
                                              min_value=-1.0, max_value=1.0, step=0.01, format="%.2f",
                                              value=float(st.session_state.financial_data[ticker].get("revenue_growth", 0.0)),
                                              key=f"growth_{ticker}",
                                              help="En décimal: 0.08 pour 8%, -0.05 pour -5%")
            with col2:
                debt_equity = st.number_input(f"Ratio Dette/Capitaux propres ({ticker})", 
                                           min_value=0.0, step=0.1, format="%.1f",
                                           value=float(st.session_state.financial_data[ticker].get("debt_equity", 0.0)),
                                           key=f"debt_{ticker}")
                
                beta = st.number_input(f"Beta ({ticker})", 
                                    min_value=0.0, step=0.1, format="%.1f",
                                    value=float(st.session_state.financial_data[ticker].get("beta", 0.0)),
                                    key=f"beta_{ticker}")
            
            # Mettre à jour les données financières
            st.session_state.financial_data[ticker] = {
                "p_e_ratio": p_e_ratio,
                "debt_equity": debt_equity,
                "revenue_growth": revenue_growth,
                "beta": beta
            }
        
        # Bouton pour lancer l'analyse
        if st.button("Analyser mon portefeuille", type="primary"):
            # Vérifier les données
            if abs(total_weight - 100) > 1:
                st.error(f"La somme des poids doit être égale à 100%. Actuellement: {total_weight:.1f}%")
            elif not portfolio_data:
                st.error("Veuillez ajouter au moins une action à votre portefeuille.")
            else:
                with st.spinner("Analyse en cours, veuillez patienter..."):
                    try:
                        # Créer l'agent et effectuer l'analyse
                        agent = GeminiInvestmentAgent(API_KEY)
                        
                        # Préparer les données
                        investor_profile = {
                            "risk_tolerance": risk_tolerance,
                            "investment_horizon": investment_horizon
                        }
                        
                        # Filtrer les données financières pour n'inclure que les tickers du portefeuille
                        valid_tickers = [stock["ticker"] for stock in portfolio_data]
                        stock_data = {ticker: data for ticker, data in st.session_state.financial_data.items() 
                                    if ticker in valid_tickers}
                        
                        # Effectuer l'analyse
                        results = agent.analyze_portfolio(investor_profile, portfolio_data, stock_data)
                        
                        # Vérifier les résultats
                        if "error" in results:
                            st.error(f"Erreur lors de l'analyse: {results['error']}")
                        else:
                            st.session_state.analysis_results = results
                            st.success("Analyse terminée avec succès!")
                            st.markdown("Cliquez sur l'onglet 'Résultats d'Analyse' pour voir les résultats.")
                    except Exception as e:
                        st.error(f"Une erreur s'est produite: {str(e)}")
    
    with tab3:
        st.header("Résultats d'Analyse")
        
        if st.session_state.analysis_results:
            results = st.session_state.analysis_results
            
            # Résumé du portefeuille - CORRIGÉ
            st.subheader("Résumé du Portefeuille")
            st.markdown(f"""
            <div class="card">
                <div class="card-content">{results.get('portfolio_summary', 'Aucun résumé disponible.')}</div>
            </div>
            """, unsafe_allow_html=True)
            
            # Évaluation des risques - CORRIGÉ
            st.subheader("Évaluation des Risques")
            risk_level = results['risk_assessment']['level']
            risk_color = {
                "Low": "green",
                "Moderate": "orange",
                "High": "red"
            }.get(risk_level, "blue")
            
            risk_description = results['risk_assessment'].get('description', 'Aucune description disponible.')
            
            st.markdown(f"""
            <div class="card">
                <div><strong>Niveau de risque:</strong> <span style='color:{risk_color};'>{risk_level}</span></div>
                <div class="card-content">{risk_description}</div>
            </div>
            """, unsafe_allow_html=True)
            
            # Problèmes identifiés - CORRIGÉ
            st.subheader("Problèmes Identifiés")
            
            if results.get('issues') and len(results['issues']) > 0:
                for issue in results['issues']:
                    severity = issue.get('severity', 'Medium')
                    issue_type = issue.get('type', 'Inconnu')
                    description = issue.get('description', 'Aucune description disponible.')
                    
                    severity_class = f"severity-{severity.lower()}"
                    
                    st.markdown(f"""
                    <div class="card">
                        <div><span class='{severity_class}'>{severity}</span> - <strong>{issue_type}</strong></div>
                        <div class="card-content">{description}</div>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.info("Aucun problème majeur identifié.")
            
            # Recommandations - CORRIGÉ
            st.subheader("Recommandations")
            
            if results.get('recommendations') and len(results['recommendations']) > 0:
                for rec in results['recommendations']:
                    priority = rec.get('priority', 'Medium')
                    action = rec.get('action', 'Action non spécifiée')
                    target = rec.get('target', 'Cible non spécifiée')
                    rationale = rec.get('rationale', 'Aucune justification disponible.')
                    
                    priority_class = f"priority-{priority.lower()}"
                    
                    st.markdown(f"""
                    <div class="card">
                        <div><span class='{priority_class}'>{priority}</span> - <strong>{action}: {target}</strong></div>
                        <div class="card-content">{rationale}</div>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.info("Aucune recommandation spécifique.")
                
            # Bouton pour télécharger les résultats en JSON
            st.download_button(
                label="💾 Télécharger le rapport (JSON)", 
                data=json.dumps(results, indent=2),
                file_name="analyse_portefeuille.json",
                mime="application/json"
            )
        else:
            st.info("Aucun résultat d'analyse disponible. Veuillez configurer votre portefeuille et lancer une analyse.")

if __name__ == "__main__":
    main()