import axios from 'axios';

const BASE_URL = process.env.REACT_APP_BACKEND_URL || 'http://localhost:5001'; // Flask backend port

export const registerUser = async (name, email, password) => {
  return axios.post(`${BASE_URL}/auth/register`, { name, email, password });
};

export const loginUser = async (email, password) => {
  return axios.post(`${BASE_URL}/auth/login`, { email, password });
};

export const deleteUser = async (token, password) => {
  if (!token) {
    throw new Error('No token found');
  }
  return axios.post(`${BASE_URL}/auth/delete`, { password }, { headers: { Authorization: `Bearer ${token}` } });
};

export const googleLogin = async (access_token) => {
  return axios.post(`${BASE_URL}/auth/google`, { access_token });
};

export const updateUser = async (token) => {
  return axios.post(`${BASE_URL}/auth/update`, {}, {
    headers: { Authorization: `Bearer ${token}` }
  });
};

export const sendEmail = async (email) => {
  return axios.post(`${BASE_URL}/auth/send_email`, { email });
};

export const verifyEmail = async (token) => {
  return axios.get(`${BASE_URL}/auth/verify_email?token=${token}`);
};

