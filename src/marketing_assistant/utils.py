import os
from PyPDF2 import PdfReader
import json
import traceback
import pandas as pd

def read_file(file):
    """Read text from PDF file"""
    if file is None:
        return ""
    
    if file.name.endswith('.pdf'):
        try:
            pdf_reader = PdfReader(file)
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text()
            return text
        except Exception as e:
            raise Exception(f"Error reading PDF file: {str(e)}")
    return ""

def read_sales_data(file):
    if file.name.endswith(".csv"):
        try:
            df = pd.read_csv(file)
            sales_summary = {
                "total_sales": df["amount"].sum() if "amount" in df.columns else 0,
                "avg_transaction": df["amount"].mean() if "amount" in df.columns else 0,
                "customer_count": len(df["customer_id"].unique()) if "customer_id" in df.columns else 0,
                "top_products": df["product"].value_counts().head(5).to_dict() if "product" in df.columns else {}
            }
            return sales_summary
        except Exception as e:
            raise Exception(f"Error reading CSV file: {str(e)}")
    else:
        return None

def analyze_marketing_results(text):
    """Analyze marketing results from PDF text"""
    try:
        return {
            "text": text,
            "word_count": len(text.split()),
            "has_numbers": any(char.isdigit() for char in text)
        }
    except Exception as e:
        raise Exception(f"Error analyzing marketing results: {str(e)}")


