import React from 'react';

interface SidebarWrapperProps {
  children: React.ReactNode;
}

export const SidebarWrapper: React.FC<SidebarWrapperProps> = ({ children }) => {
  return (
    <div className="flex h-screen">
      <div className="flex-1 overflow-hidden">
        {children}
      </div>
    </div>
  );
};