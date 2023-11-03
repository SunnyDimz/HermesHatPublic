// This file would contain functions to interact with your backend.
// For example:
// ChatAPI.js
export const fetchChatResponse = async (input) => {
    try {
      const response = await fetch('/api/economics-chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ input: input }),
      });
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      const result = await response.json();
      return result;
    } catch (error) {
      console.error('Error fetching chat response:', error);
      throw error; // Rethrow the error so it can be caught by the calling function
    }
  };
  
  
 // ChatAPI.js
export const fetchFREDData = async (fredCode) => {
    try {
      const response = await fetch(`/api/mongo-query?fred_code=${encodeURIComponent(fredCode)}`);
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      const result = await response.json();
      return result;
    } catch (error) {
      console.error('Error fetching FRED data:', error);
      throw error; // Rethrow the error so it can be caught by the calling function
    }
  };
  