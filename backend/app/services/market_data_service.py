import requests
import pandas as pd
from typing import Dict,Any,List
import yfinance as yf
from datetime import datetime,timedelta


class MarketDataService:
    def __init__(self,alpha_vantage_api_key:str=None):
        self.alpha_vantage_api_key = alpha_vantage_api_key

    def get_stock_price(self,symbol:str)->Dict[str,Any]:
        """Get current stock price and basic info"""
        try:
            # ticker lets you extract the stock level of any company
            ticker = yf.Ticker(symbol)
            info = ticker.info
            history = ticker.history(period="1d")

            return {
                "symbol":symbol,
                "current_price":info.get("currentPrice",0),
                "previous_close":info.get("previousClose",0),
                "day_change":((info.get("currentPrice",0)-info.get("previousClose",0))/info.get("previousClose",1))*100,
                "volume": info.get("volume", 0),
                "market_cap": info.get("marketCap", 0),
                "pe_ratio": info.get("trailingPE", 0),
                "company_name": info.get("longName", symbol)
            }
        
        except Exception as e:
            return {"error":f"Failed to fetch data for {symbol}:{str(e)} "}
        
    def get_market_overview(self)->Dict[str,Any]:
        """Get major market indices overview"""
        indices = ["^GSPC", "^DJI", "^IXIC", "^RUT"]  # S&P 500, Dow, NASDAQ, Russell 2000
        overview = {}
        
        for index in indices:
            try:
                ticker = yf.Ticker(index)
                history = ticker.history(period="2d")
                
                if len(history) >= 2:
                    current = history.iloc[-1]["Close"]
                    previous = history.iloc[-2]["Close"]
                    change = current - previous
                    change_percent = (change / previous) * 100
                    
                    overview[index] = {
                        "price": current,
                        "change": change,
                        "change_percent": change_percent
                    }
            except Exception as e:
                overview[index] = {"error": str(e)}
        
        return overview
    

    def get_sector_performance(self) -> Dict[str, Any]:
        """Get sector ETF performance"""
        sectors = {
            "Technology": "XLK",
            "Healthcare": "XLV", 
            "Financials": "XLF",
            "Consumer Discretionary": "XLY",
            "Communication Services": "XLC",
            "Industrials": "XLI",
            "Consumer Staples": "XLP",
            "Energy": "XLE",
            "Utilities": "XLU",
            "Real Estate": "XLRE",
            "Materials": "XLB"
        }
        
        performance = {}
        for sector, etf in sectors.items():
            try:
                ticker = yf.Ticker(etf)
                history = ticker.history(period="1mo")
                
                if len(history) >= 2:
                    current = history.iloc[-1]["Close"]
                    month_ago = history.iloc[0]["Close"]
                    change_percent = ((current - month_ago) / month_ago) * 100
                    
                    performance[sector] = {
                        "etf": etf,
                        "current_price": current,
                        "month_change_percent": change_percent
                    }
            except Exception as e:
                performance[sector] = {"error": str(e)}
        
        return performance
