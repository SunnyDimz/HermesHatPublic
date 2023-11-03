import React, { useState } from 'react';

const ChatInput = ({ onSubmit }) => {
  const [inputValue, setInputValue] = useState('');

  const handleInputChange = (e) => {
    setInputValue(e.target.value);
  };

  const handleFormSubmit = (e) => {
    e.preventDefault();
    onSubmit(inputValue);
    setInputValue(''); // Clear the input after submitting
  };

  return (
    <form onSubmit={handleFormSubmit}>
      <input
        type="text"
        value={inputValue}
        onChange={handleInputChange}
        placeholder="Ask a question about economics..."
      />
      <button type="submit">Submit</button>
    </form>
  );
};

export default ChatInput;
