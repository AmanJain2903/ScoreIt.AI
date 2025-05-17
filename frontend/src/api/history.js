import axios from 'axios';

const BASE_URL = 'http://localhost:5001/history'; // Flask backend port


export const addHistory = async (email, resume_text, resume_json, jd_text, jd_json, match_report) => {
    return axios.post(`${BASE_URL}/add`, { email, resume_text, resume_json, jd_text, jd_json, match_report });
};

export const getHistory = async (email) => {
    return axios.post(`${BASE_URL}/get_all`, { email });
};

export const deleteAll = async (email) => {
    return axios.delete(`${BASE_URL}/delete_all`, { data: { email } });
};

export const deleteOne = async (email, match_id) => {
    return axios.delete(`${BASE_URL}/delete_one`, {
        data: { email, match_id },
        headers: {
            'Content-Type': 'application/json'
        }
    });
};