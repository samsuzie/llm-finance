import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler,LabelEncoder
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error,mean_squared_error
import torch
import torch.nn as nn
from typing import Dict,List,Any,Tuple
import joblib
import os

class TimeSeriesTransformer(nn.Module):
    """transformer model for financial time series predcition"""

    def __init__(self,input_dim:int,d_model:int=512,nhead:int=8,num_layers:int=6,output_dim:int=1):
        super().__init()
        self.input_projection = nn.Linear(input_dim,d_model)
        self.positional_encoding = nn.Parameter(torch.randn(1000,d_model))

        encoder_layer = nn.TransformerEncoderLayer(
            d_mode=d_model,
            nhead=nhead,
            batch_first=True
        )
        self.transformer = nn.TransformerEncoder(encoder_layer, num_layers)
        self.output_projection = nn.Linear(d_model, output_dim)
        self.dropout = nn.Dropout(0.1)


    def forward(self,x):
        seq_len = x.size(1)
        x = self.input_projection(x)
        x += self.positional_encoding[:seq_len, :].unsqueeze(0)
        x = self.dropout(x)
        x = self.transformer(x)
        x = self.output_projection(x[:, -1, :])  # Use last timestep
        return x
    

    class FinancialTimeSeriesService:
        def __init__(self):
            self.scaler = StandardScaler()
            self.model=None
            self.device = torch.device('cuda'if torch.cuda.is_available() else 'cpu')
            self.model_path = "models/time_series_model.pth"
            self.scaler_path = "models/scaler.pkl"

        def prepare_features(self,df:pd.DataFrame)->pd.DataFrame:
            """Engineer features for time series modelling"""
            df = df.copy()
            df['date']=pd.to_datetime(df['date'])
            df = df.sort_values('date').reset_index(drop=True)

            # time based features for time based modelling
            df['day_of_week'] = df['date'].dt.dayofweek
            df['day_of_month'] = df['date'].dt.day
            df['month'] = df['date'].dt.month
            df['quarter']=df['date'].dt.quarter
            df['is_weekend']=(df['day_of_week']>=5).astype(int)
            df['is_month_end']=(df['date'].dt.day>=28).astype(int)

            # rolling stats
            df['amount_7d_mean']=df['amount'].rolling(window=7,min_periods=1).mean()
            df['amount_7d_std']= df['amount'].rolling(window=7,min_periods=1).std()
            df['amount_30d_mean'] = df['amount'].rolling(window=30, min_periods=1).mean()
            df['amount_30d_std'] = df['amount'].rolling(window=30, min_periods=1).std()
        
            for lag in [1, 7, 30]:
                df[f'amount_lag_{lag}'] = df['amount'].shift(lag)
            

            # category encoding
            le = LabelEncoder()
            df['category_encoded']=le.fit_transform(df['category'].fillna('unknown'))

            df = df.fillna(method='forward').fillna(0)


            return df 
        
        def create_sequences(self,date:np.ndarray,seq_length:int=30)->Tuple[np.ndarray,np.ndarray]:
            """Create sequences for time series prediction"""
            X,y=[],[]
            for i in range(len(data)-seq_length):
                X.append(data[i:(i+seq_length)])
                y.append(data[i+seq_length,0])
            return np.array(X),np.array(y)
        

        def train_model(self,df:pd.DataFrame)->Dict[str,Any]:
            """train the time series transformers model"""
            #prepare features
            df_features = self.prepare_features(df)
            #select features for modelling
            feature_cols=[
                'amount','day_of_week', 'day_of_month', 'month', 'quarter',
                'is_weekend', 'is_month_end', 'amount_7d_mean', 'amount_7d_std',
                'amount_30d_mean', 'amount_30d_std', 'amount_lag_1', 'amount_lag_7',
                'amount_lag_30', 'category_encoded'
            ]

            data = df_features[feature_cols].values
            #scale the data
            data_scaled = self.scaler.fit_transform(data)
            # Create sequences
            X, y = self.create_sequences(data_scaled)
            # Split data
            X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, shuffle=False
            )
            # converting into tensors
            X_train = torch.FloatTensor(X_train).to(self.device)
            X_test = torch.FloatTensor(X_test).to(self.device)
            y_train = torch.FloatTensor(y_train).to(self.device)
            y_test = torch.FloatTensor(y_test).to(self.device)

            # initalize model
            input_dim = X_train.shape[2]
            self.model = TimeSeriesTransformer(input_dim=input_dim)

            # Training parameters
            criterion = nn.MSELoss()
            optimizer = torch.optim.Adam(self.model.parameters(),lr=0.001)
            scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(optimizer,patience=10)

            # training loop
            train_losses=[]
            val_losses=[]

            for epoch in range(100):
                # Training
                self.model.train()
                train_loss=0
                # simple batch processing(you can implement Dataloader also)
                # clears the gradient if there is any present before
                optimizer.zero_grad()
                outputs = self.model(X_train)
                loss = criterion(outputs.squeeze(),y_train)
                # compute gradient of the loss with respect to each weight in model
                loss.backward()
                # update the model weights 
                optimizer.step()
                train_loss = loss.item()
                # Validation
                self.model.eval()
                # with this we turn off the operations that will compute gradients
                # as we are not training , we are just validation i.e the output is correct or not
                with torch.no_grad():
                    val_outputs = self.model(X_test)
                    val_loss = criterion(X_test.squeeze(),y_test).item()
                
                train_losses.append(train_loss)
                val_losses.append(val_loss)
                scheduler.step(val_loss)

                if epoch%10==0:
                    print(f'Epoch{epoch}:Train Loss:{train_loss:.4f},Val Loss:{val_loss:.4f}')
            

            # save model 
            os.makedirs("model",exist_ok=True)
            torch.save(self.model.state_dict(),self.model_path)
            # joblib is used to save model and then use it ,ater without retraining
            joblib.dump(self.scaler,self.scaler_path)

            #calculate metrics
            with torch.no_grad():
                y_pred = self.model(X_test).squeeze().cpu().numpy()
                y_true = y_test.cpu().numpy()

                mae = mean_absolute_error(y_true,y_pred)
                mse = mean_squared_error(y_true,y_pred)
                rmse = nq.sqrt(mse)


                return {
                    "training_completed":True,
                    "final_train_loss":train_losses[-1],
                    "final_val_loss":val_losses[-1],
                    "mae":mae,
                    "mse":mse,
                    "rmse":rmse,
                    "training_samples":len(X_train),
                    "validation_samples":len(X_test)
                }
        
        def predict(self,df:pd.DataFrame,horizon:int=30):
            # horizon simply means how far you want it to predict in future
            if self.model is None:
                self.load_model()
            

            # prepare featues
            df_features = self.prepare_features(df)

            feature_cols=[
                'amount', 'day_of_week', 'day_of_month', 'month', 'quarter',
                'is_weekend', 'is_month_end', 'amount_7d_mean', 'amount_7d_std',
                'amount_30d_mean', 'amount_30d_std', 'amount_lag_1', 'amount_lag_7',
                'amount_lag_30', 'category_encoded'
            ]

            data = df_features[feature_cols].value
            data_scaled = self.scaler.transform(data)

            last_sequence = data_scaled[-30:]
            predictions=[]

            self.model.eval()
            with torch.no_grad():
                for _ in range(horizon):
                    # prepare input tensor
                    X= torch.FloatTensor(last_sequence).unsqueeze(0).to(self.device)
                    # make predictions
                    pred = self.model(X).cpu().numpy()[0,0]
                    predictions.append(pred)
                    # Update sequence for next prediction
                    # This is a simplified approach; in practice, you'd want to update
                    # all features based on the predicted spending
                    new_row = last_sequence[-1].copy()
                    new_row[0] = pred
                    last_sequence=np.vstack([last_sequence[1:],new_row])

        
            return np.array(predictions)
        

        def load_model(self):
            """load trained model and its scaler that will contain all the scaled value and all"""
            if os.path.exists(self.model_path) and os.path.exists(self.scaler_path):
                # Load scaler first to get input dimension
                self.scaler = joblib.load(self.scaler_path)
            
                # Initialize model with correct input dimension
                input_dim = 15  # Number of features
                self.model = TimeSeriesTransformer(input_dim=input_dim).to(self.device)
                
                # Load model weights
                self.model.load_state_dict(torch.load(self.model_path, map_location=self.device))
                self.model.eval()
            else:
                raise FileNotFoundError("Model files not found. Please train the model first.")
                
