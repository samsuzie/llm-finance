import pandas as pd
import json
from typing import Dict, Any
import io
from datetime import datetime

class FileProcessor:
    def __init__(self):
        self.required_columns = ['amount', 'description', 'date']
        self.column_mappings = {
            # Common variations of column names
            'Amount': 'amount',
            'AMOUNT': 'amount',
            'Transaction Amount': 'amount',
            'Debit': 'amount',
            'Credit': 'amount',
            
            'Description': 'description',
            'DESCRIPTION': 'description',
            'Transaction Description': 'description',
            'Memo': 'description',
            'Details': 'description',
            
            'Date': 'date',
            'DATE': 'date',
            'Transaction Date': 'date',
            'Posted Date': 'date',
            'Posting Date': 'date',
            
            'Category': 'category',
            'CATEGORY': 'category',
            'Transaction Category': 'category',
            
            'Merchant': 'merchant',
            'MERCHANT': 'merchant',
            'Payee': 'merchant',
            'Vendor': 'merchant',
            
            'Account': 'account_type',
            'Account Type': 'account_type',
            'ACCOUNT': 'account_type'
        }

    def process_csv(self, file_content: io.StringIO) -> pd.DataFrame:
        """Process CSV file and return standardized DataFrame"""
        try:
            df = pd.read_csv(file_content)
            return self._standardize_dataframe(df)
        except Exception as e:
            raise ValueError(f"Error processing CSV file: {str(e)}")

    def process_excel(self, file_content: io.BytesIO) -> pd.DataFrame:
        """Process Excel file and return standardized DataFrame"""
        try:
            df = pd.read_excel(file_content)
            return self._standardize_dataframe(df)
        except Exception as e:
            raise ValueError(f"Error processing Excel file: {str(e)}")

    def process_json(self, file_content: io.StringIO) -> pd.DataFrame:
        """Process JSON file and return standardized DataFrame"""
        try:
            data = json.load(file_content)
            
            # Handle different JSON structures
            if isinstance(data, list):
                df = pd.DataFrame(data)
            elif isinstance(data, dict):
                if 'transactions' in data:
                    df = pd.DataFrame(data['transactions'])
                elif 'data' in data:
                    df = pd.DataFrame(data['data'])
                else:
                    # Assume the dict itself contains the data
                    df = pd.DataFrame([data])
            else:
                raise ValueError("Unsupported JSON structure")
            
            return self._standardize_dataframe(df)
        except Exception as e:
            raise ValueError(f"Error processing JSON file: {str(e)}")

    def _standardize_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """Standardize column names and data types"""
        # Make a copy to avoid modifying original
        df = df.copy()
        
        # Rename columns using mapping
        df = df.rename(columns=self.column_mappings)
        
        # Check for required columns
        missing_columns = [col for col in self.required_columns if col not in df.columns]
        if missing_columns:
            raise ValueError(f"Missing required columns: {missing_columns}")
        
        # Clean and standardize data
        df = self._clean_data(df)
        
        return df

    def _clean_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean and standardize the data"""
        # Remove completely empty rows
        df = df.dropna(how='all')
        
        # Clean amount column
        if 'amount' in df.columns:
            df['amount'] = self._clean_amount_column(df['amount'])
        
        # Clean date column
        if 'date' in df.columns:
            df['date'] = self._clean_date_column(df['date'])
        
        # Clean description column
        if 'description' in df.columns:
            df['description'] = df['description'].astype(str).str.strip()
            df['description'] = df['description'].replace('nan', '')
        
        # Clean optional columns
        for col in ['category', 'merchant', 'account_type']:
            if col in df.columns:
                df[col] = df[col].astype(str).str.strip()
                df[col] = df[col].replace('nan', '')
        
        # Remove rows with missing required data
        df = df.dropna(subset=['amount', 'date', 'description'])
        
        # Reset index
        df = df.reset_index(drop=True)
        
        return df

    def _clean_amount_column(self, amount_series: pd.Series) -> pd.Series:
        """Clean and convert amount column to numeric"""
        # Convert to string first to handle various formats
        amounts = amount_series.astype(str)
        
        # Remove common currency symbols and formatting
        amounts = amounts.str.replace('$', '', regex=False)
        amounts = amounts.str.replace(',', '', regex=False)
        amounts = amounts.str.replace('(', '-', regex=False)  # Handle negative amounts in parentheses
        amounts = amounts.str.replace(')', '', regex=False)
        amounts = amounts.str.strip()
        
        # Convert to numeric
        amounts = pd.to_numeric(amounts, errors='coerce')
        
        return amounts

    def _clean_date_column(self, date_series: pd.Series) -> pd.Series:
        """Clean and convert date column to datetime"""
        # Try to parse dates with multiple formats
        date_formats = [
            '%Y-%m-%d',
            '%m/%d/%Y',
            '%m-%d-%Y',
            '%d/%m/%Y',
            '%d-%m-%Y',
            '%Y/%m/%d',
            '%m/%d/%y',
            '%m-%d-%y',
            '%d/%m/%y',
            '%d-%m-%y'
        ]
        
        dates = None
        for fmt in date_formats:
            try:
                dates = pd.to_datetime(date_series, format=fmt, errors='coerce')
                if not dates.isna().all():
                    break
            except:
                continue
        
        # If no format worked, try pandas' automatic parsing
        if dates is None or dates.isna().all():
            dates = pd.to_datetime(date_series, errors='coerce')
        
        return dates

    def validate_data(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Validate the processed data and return validation results"""
        validation_results = {
            'is_valid': True,
            'errors': [],
            'warnings': [],
            'stats': {}
        }
        
        # Check for required columns
        missing_columns = [col for col in self.required_columns if col not in df.columns]
        if missing_columns:
            validation_results['is_valid'] = False
            validation_results['errors'].append(f"Missing required columns: {missing_columns}")
        
        # Check data quality
        if len(df) == 0:
            validation_results['is_valid'] = False
            validation_results['errors'].append("No valid transactions found in file")
        
        # Check for invalid amounts
        if 'amount' in df.columns:
            invalid_amounts = df['amount'].isna().sum()
            if invalid_amounts > 0:
                validation_results['warnings'].append(f"{invalid_amounts} transactions have invalid amounts")
        
        # Check for invalid dates
        if 'date' in df.columns:
            invalid_dates = df['date'].isna().sum()
            if invalid_dates > 0:
                validation_results['warnings'].append(f"{invalid_dates} transactions have invalid dates")
        
        # Generate stats
        validation_results['stats'] = {
            'total_transactions': len(df),
            'date_range': {
                'start': str(df['date'].min()) if 'date' in df.columns and not df['date'].isna().all() else None,
                'end': str(df['date'].max()) if 'date' in df.columns and not df['date'].isna().all() else None
            },
            'amount_range': {
                'min': float(df['amount'].min()) if 'amount' in df.columns and not df['amount'].isna().all() else None,
                'max': float(df['amount'].max()) if 'amount' in df.columns and not df['amount'].isna().all() else None
            }
        }
        
        return validation_results