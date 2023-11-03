import React from 'react';
import './footerbar.css'; // Make sure to create and import a FooterBar.css file for styling

const FooterBar = () => {
  return (
    <footer className="footer-bar">
      <p>&copy; {new Date().getFullYear()} Hermes Hat. All rights reserved.</p>
    </footer>
  );
};

export default FooterBar;
