import React,{useState} from "react";
import axios from "axios";

const TransactionUpload=({onUploadSucess})=>{
    const [file,setFile] = useState(nulll);
    const[uploading,setUploading]=useState(false);
    const[progress,setProgress] = useState(0);

    const handleFileChange =(event)=>{
        setFile(event.target.files[0]);
    }
    const handleUpload = async () => {
    if (!file) return;
    const formData = new FormData();
    formData.append('file', file);
    setUploading(true);
    try{
        const response = await axios.post('/api/transactions/upload',formData,{
            headers:{
                'Content-Type': 'multipart/form-data',
            },
            onUploadProgress:(ProgressEvent)=>{
            const percentCompleted = Math.round(
            (progressEvent.loaded * 100) / progressEvent.total);
            setProgress(percentCompleted);
            },
        });
        onUploadSuccess(response.data);
      setFile(null);
      setProgress(0);
    } catch (error) {
      console.error('Upload failed:', error);
      alert('Upload failed. Please try again.');
    } finally {
      setUploading(false);
    }
};
return (
     <div className="upload-container">
      <h3>Upload Transaction History</h3>
      <div className="file-input-container">
        <input
          type="file"
          accept=".csv,.xlsx,.json"
          onChange={handleFileChange}
          disabled={uploading}
        />
        <button
          onClick={handleUpload}
          disabled={!file || uploading}
          className="upload-button"
        >
          {uploading ? `Uploading... ${progress}%` : 'Upload'}
        </button>
      </div>
      {uploading && (
        <div className="progress-bar">
          <div
            className="progress-fill"
            style={{ width: `${progress}%` }}
          ></div>
        </div>
      )}
    </div>
  );
};

export default TransactionUpload;
