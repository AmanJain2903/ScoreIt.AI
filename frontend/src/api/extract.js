import axios from 'axios';

const BASE_URL = process.env.REACT_APP_BACKEND_URL || 'http://localhost:5001'; // Flask backend port

export const extractJD = async (formData) => {
    return axios.post(`${BASE_URL}/extract_jd`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
  };

  export const extractResume = async (formData) => {
    return axios.post(`${BASE_URL}/extract_resume`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
  };
