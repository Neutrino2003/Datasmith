import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { Layout } from './components/Layout/Layout';
import { ChatInterface } from './components/Chat/ChatInterface';



const App = () => {
  return (
    <Router>
      <Layout>
        <Routes>
          <Route path="/" element={<ChatInterface />} />
          <Route path="*" element={<ChatInterface />} />
        </Routes>
      </Layout>
    </Router>
  );
};

export default App;
