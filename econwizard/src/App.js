import React, { useState } from 'react';
import './App.css';
import BarChart from './barchart';
import LineChart from './linechart';
import ChatInput from './chatinput';
import { fetchChatResponse, fetchFREDData } from './chatresponse';
import NavBar from './navbar';
import FooterBar from './footerbar'; // Ensure you have a FooterBar component created


function App() {
  const [data, setData] = useState(null);
  const [lineChartData, setLineChartData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleChatSubmit = async (input) => {
    setLoading(true);
    setError('');
    try {
      const chatResponse = await fetchChatResponse(input);
      const fredCode = chatResponse.fred_code;
      if (fredCode) {
        const fredData = await fetchFREDData(fredCode);
        setData(fredData.data); // Assuming the response has the data in a 'data' key
        setLineChartData(fredData.data); // Set the line chart data
      } else {
        setData(null);
        setLineChartData(null);
      }
    } catch (error) {
      console.error('Error:', error);
      setError('Failed to fetch data. Please try again later.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="app">
      <NavBar />
      <div className="main-content">
        <ChatInput onSubmit={handleChatSubmit} />
        {loading && <div className="loading">Loading...</div>} {/* Show loading text/icon */}
        {!loading && data && (
          <>
            <BarChart data={data} />
            <LineChart data={lineChartData} />
          </>
        )}
      </div>
      <FooterBar /> {/* FooterBar added */}
    </div>
  );
}

export default App;
