import React from 'react';
import './Header.css'; // Ensure this CSS file is in the same directory as your component

const Header = () => {
  return (
    <header className="header">
      <div className="logo">
        Scientific Cruises - SPC
      </div>
      <nav>
        <a href="/">Home</a>
        <a href="/cruises">Cruises</a>
        <a href="/admin/login/" className="admin-login">User Login</a> {/* Link to the Django admin login */}
      </nav>
    </header>
  );
}

export default Header;
