import React from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import { useAuthStore } from '@/services/auth';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Avatar, AvatarFallback } from '@/components/ui/avatar';
import { Badge } from '@/components/ui/badge';
import { LogOut, User, Settings } from 'lucide-react';

interface UserProfileProps {}

export const UserProfile: React.FC<UserProfileProps> = () => {
  const { user, logout } = useAuthStore();
  const location = useLocation();

  const handleLogout = () => {
    logout();
  };

  if (!user) {
    return <Navigate to="/login" state={{ from: location.pathname }} replace />;
  }

  return (
    <div className="p-4">
      <Card className="max-w-md mx-auto">
        <CardHeader className="text-center">
          <Avatar className="mx-auto mb-4 h-20 w-20">
            <AvatarFallback className="text-lg">
              {user.name?.charAt(0)?.toUpperCase() || 'U'}
            </AvatarFallback>
          </Avatar>
          <CardTitle className="text-xl">{user.name}</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="space-y-2">
            <div className="flex items-center gap-2">
              <User className="h-4 w-4" />
              <span className="text-sm text-muted-foreground">Email:</span>
              <span className="text-sm">{user.email}</span>
            </div>
            <div className="flex items-center gap-2">
              <Badge variant="outline">Active</Badge>
            </div>
          </div>
          <div className="flex gap-2">
            <Button variant="outline" className="flex-1">
              <Settings className="h-4 w-4 mr-2" />
              Settings
            </Button>
            <Button 
              variant="destructive" 
              className="flex-1" 
              onClick={handleLogout}
            >
              <LogOut className="h-4 w-4 mr-2" />
              Logout
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default UserProfile;