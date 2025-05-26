// pages/VerifyEmail.js
import React, { useEffect, useState } from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';
import { verifyEmail } from '../api/auth';

const VerifyEmail = () => {
  const [searchParams] = useSearchParams();
  const token = searchParams.get('token');
  const navigate = useNavigate();
  const [message, setMessage] = useState('Verifying...');

  useEffect(() => {
    const verify = async () => {
      try {
        const res = await verifyEmail(token);
        setMessage(res.data.message);
        setTimeout(() => navigate('/auth'), 100);
      } catch (err) {
        setMessage(err.response?.data?.error || 'Verification failed');
      }
    };
    if (token) verify();
  }, [token, navigate]);

  return <div>{message}</div>;
};

export default VerifyEmail;