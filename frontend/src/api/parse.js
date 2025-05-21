import axios from 'axios';

const BASE_URL = process.env.REACT_APP_BACKEND_URL || 'http://localhost:5001'; // Flask backend port

export const parseJD = async (formData) => {
    return axios.post(`${BASE_URL}/parse_jd`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
  };

export const parseResume = async (formData) => {
    return axios.post(`${BASE_URL}/parse_resume`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
  };

