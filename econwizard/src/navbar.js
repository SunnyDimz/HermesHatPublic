import React from 'react';
import './App.css'; // Import the CSS for the navigation bar, make sure the file exists
import { Link } from 'react-router-dom'; // Import the Link component from React Router
const NavBar = () => {
  return (
    <nav className="navbar">
      <Link to="/">Hermes Hat</Link>
      <div className="navbar-links">
        {/* React Router Links for client-side routing */}
        <Link to="/media">Media</Link>
        <Link to="/about">About</Link>

        {/* Regular anchor tags for server-side routing to Flask */}
        <a href="/photographs">Photography</a>
      </div>
    </nav>
  );
};

export default NavBar;
