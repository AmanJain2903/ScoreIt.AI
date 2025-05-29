import axios from 'axios';

const BASE_URL = process.env.REACT_APP_BACKEND_URL || 'http://localhost:5001'; // Flask backend port

export const changePassword = async (token, oldPassword, newPassword) => {
    return axios.post(`${BASE_URL}/password/change_password`, { oldPassword, newPassword }, 
        { headers: { Authorization: `Bearer ${token}` } });
};

export const sendResetEmail = async (email) => {
    return axios.post(`${BASE_URL}/password/send_reset_email`, { email });
};

export const resetPassword = async (token, newPassword) => {
    return axios.post(`${BASE_URL}/password/reset_password`, { token, newPassword });
};