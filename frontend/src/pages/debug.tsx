import React from 'react';

export default function Debug() {
  return (
    <div className="min-h-screen bg-gray-900 p-8">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-3xl font-bold text-white mb-6">Debug Page</h1>
        <div className="bg-gray-800 p-6 rounded-lg">
          <h2 className="text-xl font-semibold text-purple-300 mb-4">Environment Information</h2>
          <div className="space-y-2 text-gray-300">
            <p><strong>API Base URL:</strong> {process.env.NEXT_PUBLIC_API_BASE_URL || 'Not set'}</p>
            <p><strong>Node Environment:</strong> {process.env.NODE_ENV}</p>
            <p><strong>Vercel URL:</strong> {process.env.VERCEL_URL || 'Not deployed'}</p>
          </div>
        </div>
      </div>
    </div>
  );
}