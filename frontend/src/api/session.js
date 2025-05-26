import axios from 'axios';

const BASE_URL = process.env.REACT_APP_BACKEND_URL || 'http://localhost:5001'; // Flask backend port

export const createSession = async (email, token) => {
  return axios.post(`${BASE_URL}/session/create`, { email, token });
};

export const deleteSession = async (email, token) => {
  return axios.post(`${BASE_URL}/session/delete`, { email, token });
};

export const deleteAllSessions = async (email) => {
  return axios.post(`${BASE_URL}/session/delete_all`, { email });
};

export const checkSession = async (email, token) => {
  return axios.post(`${BASE_URL}/session/check`, { email, token });
};

export const logoutAllSessions = async (email, token) => {
  return axios.post(`${BASE_URL}/session/logout_all`, { email, token });
};

