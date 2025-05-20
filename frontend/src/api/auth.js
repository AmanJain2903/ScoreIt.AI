import axios from 'axios';

const BASE_URL = process.env.REACT_APP_BACKEND_URL || 'http://localhost:5001'; // Flask backend port

export const registerUser = async (name, email, password) => {
  return axios.post(`${BASE_URL}/register`, { name, email, password });
};

export const loginUser = async (email, password) => {
  return axios.post(`${BASE_URL}/login`, { email, password });
};

export const deleteUser = async (email, password) => {
  return axios.post(`${BASE_URL}/delete`, { email, password });
};