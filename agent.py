
import os
import json
import requests
from pprint import pprint
from dotenv import load_dotenv
import os

load_dotenv()  # Load variables from .env file
api_key = os.getenv("GOOGLE_API_KEY")

class GeminiInvestmentAgent:
    
    def __init__(self, api_key=None):
        
        self.api_key = api_key 
        if not self.api_key:
            raise ValueError("Google API key is required.")
        
        # Gemini API endpoint
        self.api_endpoint = "https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent"
    
    def analyze_portfolio(self, investor_profile, portfolio, stock_data):
        """
        Analyze an investment portfolio using Gemini.
        
        Parameters:
        -----------
        investor_profile : dict
            Information about the investor (risk tolerance, time horizon)
        portfolio : list
            List of stocks and their weights in the portfolio
        stock_data : dict
            Financial metrics for each stock
            
        Returns:
        --------
        dict
            Structured analysis and recommendations from the LLM
        """
        # Step 1: Create a prompt for the LLM
        prompt = self._create_analysis_prompt(investor_profile, portfolio, stock_data)
        
        # Step 2: Send the prompt to the Gemini API
        llm_response = self._query_llm(prompt)
        
        # Step 3: Process the response into structured data
        analysis_results = self._process_response(llm_response)
        
        return analysis_results
    
    def _create_analysis_prompt(self, investor_profile, portfolio, stock_data):
        """Create a well-structured prompt for Gemini."""
        # Format the financial data nicely for the prompt
        portfolio_text = "\n".join([
            f"- {p['ticker']}: {p['weight']*100:.1f}% of portfolio" 
            for p in portfolio
        ])
        
        # Format stock data for each holding
        stock_data_text = ""
        for ticker, data in stock_data.items():
            metrics = "\n    ".join([f"- {k}: {v}" for k, v in data.items()])
            stock_data_text += f"{ticker}:\n    {metrics}\n\n"
        
        # Create the prompt with clear instructions - Gemini works well with structured prompts
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
        """Send the prompt to the Gemini API and get the response."""
        # Build the API URL with the API key
        api_url = f"{self.api_endpoint}?key={self.api_key}"
        
        # Create the request payload
        payload = {
            "contents": [
                {
                    "parts": [
                        {
                            "text": prompt
                        }
                    ]
                }
            ],
            "generationConfig": {
                "temperature": 0.2,  # Low temperature for more deterministic outputs
                "maxOutputTokens": 4096
            }
        }
        
        headers = {
            "Content-Type": "application/json"
        }
        
        try:
            response = requests.post(api_url, headers=headers, json=payload)
            response.raise_for_status()  # Raise exception for 4XX/5XX responses
            return response.json()
        except Exception as e:
            print(f"Error calling Gemini API: {e}")
            return {"error": str(e)}
    
    def _process_response(self, llm_response):
        """Extract and structure Gemini's JSON response."""
        try:
            # Extract content from the Gemini API response structure
            # Check if there's an error in the response
            if "error" in llm_response:
                return {"error": f"API Error: {llm_response['error']['message']}"}
            
            # Extract the text from Gemini's response format
            candidates = llm_response.get("candidates", [])
            if not candidates:
                return {"error": "No content returned from Gemini API"}
            
            content = candidates[0].get("content", {})
            parts = content.get("parts", [])
            if not parts:
                return {"error": "No parts found in Gemini response"}
            
            text = parts[0].get("text", "")
            
            # Extract JSON from the response
            # First look for JSON between triple backticks
            if "```json" in text and "```" in text.split("```json")[1]:
                json_text = text.split("```json")[1].split("```")[0].strip()
            elif "```" in text and "```" in text.split("```")[1]:
                # Try just the triple backticks without 'json'
                json_text = text.split("```")[1].split("```")[0].strip()
            else:
                # Just use the whole text
                json_text = text.strip()
            
            # Parse the JSON
            analysis_data = json.loads(json_text)
            return analysis_data
            
        except Exception as e:
            print(f"Error processing Gemini response: {e}")
            print(f"Raw response: {llm_response}")
            return {"error": f"Failed to process Gemini response: {str(e)}"}


# Example usage of the Gemini agent
def demonstrate_gemini_agent():
    """Run a demonstration of the Gemini-powered agent."""
    print("Investment Portfolio Analysis using Gemini")
    print("=========================================")
    
    # Create the Gemini agent
    # You would need to set GOOGLE_API_KEY env var or pass your API key here
    try:
        agent = GeminiInvestmentAgent()
    except ValueError as e:
        print(f"Error: {e}")
        print("To run this demo, you need a Google API key.")
        return
    
    # Sample investor profile
    investor_profile = {
        "risk_tolerance": 7,  # Scale of 1-10
        "investment_horizon": "long-term"  # short-term, medium-term, or long-term
    }
    
    # Sample portfolio
    portfolio = [
        {"ticker": "AAPL", "weight": 0.25},  # 25% of portfolio
        {"ticker": "MSFT", "weight": 0.20},  # 20% of portfolio
        {"ticker": "JPM", "weight": 0.15},   # 15% of portfolio
        {"ticker": "NEE", "weight": 0.25},   # 25% of portfolio
        {"ticker": "PG", "weight": 0.15}     # 15% of portfolio
    ]
    
    # Sample stock data
    stock_data = {
        "AAPL": {
            "p_e_ratio": 28.5,
            "debt_equity": 1.2,
            "revenue_growth": 0.08,  # 8% growth
            "beta": 1.2
        },
        "MSFT": {
            "p_e_ratio": 32.1,
            "debt_equity": 0.5,
            "revenue_growth": 0.12,  # 12% growth
            "beta": 1.1
        },
        "JPM": {
            "p_e_ratio": 14.2,
            "debt_equity": 1.5,
            "revenue_growth": 0.04,  # 4% growth
            "beta": 1.3
        },
        "NEE": {
            "p_e_ratio": 35.8,
            "debt_equity": 1.4,
            "revenue_growth": -0.02,  # -2% growth (decline)
            "beta": 0.7
        },
        "PG": {
            "p_e_ratio": 25.3,
            "debt_equity": 0.6,
            "revenue_growth": 0.03,  # 3% growth
            "beta": 0.6
        }
    }
    
    print("\nSending portfolio data to Gemini for analysis...")
    
    try:
        # Run the Gemini analysis
        results = agent.analyze_portfolio(investor_profile, portfolio, stock_data)
        
        # Display the results
        print("\nAnalysis Results:")
        print("----------------")
        pprint(results)
        
        return results
    except Exception as e:
        print(f"Error running analysis: {e}")


# Run the demonstration if the script is executed directly
if __name__ == "__main__":
    demonstrate_gemini_agent()