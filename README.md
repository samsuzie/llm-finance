# Personal Finance Coach

An AI-powered personal finance application that helps users manage their finances, analyze spending patterns, and get personalized financial advice.

## Features

- **Transaction Management**: Upload and categorize financial transactions from CSV, Excel, or JSON files
- **Financial Analytics**: Comprehensive dashboard with spending trends, category breakdowns, and financial metrics
- **AI Financial Coach**: Chat with an AI assistant for personalized financial advice and recommendations
- **Investment Recommendations**: Get personalized investment advice based on risk assessment
- **Spending Pattern Analysis**: Identify unusual transactions and spending trends
- **Financial Predictions**: Forecast future spending based on historical data

## Tech Stack

### Backend
- **FastAPI**: Modern, fast web framework for building APIs
- **SQLAlchemy**: SQL toolkit and ORM
- **PostgreSQL**: Primary database
- **Redis**: Caching and session storage
- **OpenAI GPT**: AI-powered financial advice
- **ChromaDB**: Vector database for RAG (Retrieval Augmented Generation)
- **Pandas**: Data analysis and processing
- **Scikit-learn**: Machine learning for transaction categorization
- **PyTorch**: Deep learning for financial predictions

### Frontend
- **React**: User interface library
- **Chart.js**: Data visualization
- **Tailwind CSS**: Utility-first CSS framework
- **Axios**: HTTP client for API calls

## Installation

### Prerequisites
- Python 3.8+
- Node.js 14+
- PostgreSQL
- Redis

### Backend Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd personal-finance-coach
```

2. Create a virtual environment:
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your configuration
```

5. Set up the database:
```bash
# Create PostgreSQL database
createdb finance_coach_db

# Run migrations (if using Alembic)
alembic upgrade head
```

6. Start the backend server:
```bash
python main.py
```

### Frontend Setup

1. Navigate to frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Start the development server:
```bash
npm start
```

## Configuration

### Environment Variables

Create a `.env` file in the backend directory with the following variables:

```env
# Database
DATABASE_URL=postgresql://username:password@localhost:5432/finance_coach_db

# Redis
REDIS_URL=redis://localhost:6379

# AI/ML APIs
OPENAI_API_KEY=your_openai_api_key_here
HUGGINGFACE_API_KEY=your_huggingface_api_key_here

# Security
SECRET_KEY=your-super-secret-key-change-this-in-production
ACCESS_TOKEN_EXPIRE_MINUTES=30

# CORS
BACKEND_CORS_ORIGINS=["http://localhost:3000"]

# ChromaDB
CHROMA_DB_PATH=./chroma_db
```

## Usage

1. **Upload Transactions**: Start by uploading your transaction data in CSV, Excel, or JSON format
2. **View Dashboard**: Analyze your spending patterns, income, and financial metrics
3. **Chat with AI Coach**: Ask questions about your finances and get personalized advice
4. **Get Investment Recommendations**: Receive tailored investment suggestions based on your risk profile

## API Documentation

Once the backend is running, visit `http://localhost:8000/docs` for interactive API documentation.

## File Format Support

The application supports the following transaction file formats:

### CSV/Excel Columns
- `Amount` or `Transaction Amount`: Transaction amount (positive for income, negative for expenses)
- `Description` or `Transaction Description`: Transaction description
- `Date` or `Transaction Date`: Transaction date
- `Category` (optional): Transaction category
- `Merchant` or `Payee` (optional): Merchant name
- `Account` or `Account Type` (optional): Account type

### JSON Format
```json
{
  "transactions": [
    {
      "amount": -50.00,
      "description": "Grocery Store",
      "date": "2024-01-15",
      "category": "Groceries",
      "merchant": "Whole Foods"
    }
  ]
}
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

For support, please open an issue on GitHub or contact the development team.