// src/App.tsx

import React, { useEffect } from "react";
import { Toaster } from "@/components/ui/toaster";
import { Toaster as Sonner } from "@/components/ui/sonner";
import { TooltipProvider } from "@/components/ui/tooltip";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { DatabaseInitializer } from "@/components/DatabaseInitializer";
import { ProtectedRoute, PublicOnlyRoute } from "@/components/auth/ProtectedRoute";
import Index from "./pages/Index";
import Chat from "./pages/Chat";
import CodeConverter from "./pages/CodeConverter";
import CodeExplainer from "./pages/CodeExplainer";
import DocumentIngestion from "./pages/DocumentIngestion";
import KnowledgeBase from "./pages/KnowledgeBase";
import RemediationOnCoach from "./pages/RemediationValidator";
import Login from "./pages/Login";
import Register from "./pages/Register";
import NotFound from "./pages/NotFound";
import SSOCallback from "./pages/SSOCallback";
import { checkAuthStatus } from "@/services/auth"; // ✅ Import this!

// Add custom CSS for styling
import "./styles/custom.css";

const queryClient = new QueryClient();

const App = () => {
  // ✅ On mount, verify if user is authenticated via SSO
  useEffect(() => {
    checkAuthStatus();
  }, []);

  return (
    <QueryClientProvider client={queryClient}>
      <TooltipProvider>
        <DatabaseInitializer />
        <Toaster />
        <Sonner />
        <BrowserRouter>
          <Routes>
            <Route path="/" element={<Index />} />
            <Route path="/chat" element={
              <ProtectedRoute>
                <Chat />
              </ProtectedRoute>
            } />
            <Route path="/converter" element={
              <ProtectedRoute>
                <CodeConverter />
              </ProtectedRoute>
            } />
            <Route path="/explainer" element={
              <ProtectedRoute>
                <CodeExplainer />
              </ProtectedRoute>
            } />
            <Route path="/remediation" element={
              <ProtectedRoute>
                <RemediationOnCoach />
              </ProtectedRoute>
            } />
            <Route path="/ingestion" element={
              <ProtectedRoute>
                <DocumentIngestion />
              </ProtectedRoute>
            } />
            <Route path="/knowledge" element={
              <ProtectedRoute>
                <KnowledgeBase />
              </ProtectedRoute>
            } />
            <Route path="/login" element={
              <PublicOnlyRoute>
                <Login />
              </PublicOnlyRoute>
            } />
            <Route path="/register" element={
              <PublicOnlyRoute>
                <Register />
              </PublicOnlyRoute>
            } />
            <Route path="/sso/callback" element={<SSOCallback />} />
            <Route path="*" element={<NotFound />} />
          </Routes>
        </BrowserRouter>
      </TooltipProvider>
    </QueryClientProvider>
  );
};

export default App;
