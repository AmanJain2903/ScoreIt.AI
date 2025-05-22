import axios from 'axios';

const BASE_URL = process.env.REACT_APP_BACKEND_URL || 'http://localhost:5001'; // Flask backend port

export const fetchConfig = async () => {
  return axios.get(`${BASE_URL}/get_model_config`);
};
